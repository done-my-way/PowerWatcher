"""
PowerWatcher -- python3 context manager to log power consumption of any ML-pipeline running on a Nvidia GPU.
"""
import signal
import time
from datetime import datetime
from multiprocessing import Process, Pipe
from multiprocessing.connection import Connection
from pathlib import Path

from pynvml import nvmlDeviceGetPowerUsage, nvmlDeviceGetHandleByIndex, nvmlInit


class _GracefulKiller:
    """
    SIGINT and SIGTERM catcher.
    Modifies process interruption behaviour: the kill_now flag is set to True instead of actually exiting the process.
    taken from: https://stackoverflow.com/questions/18499497/how-to-process-sigterm-signal-gracefully
    """

    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        """
        Set kill_now flag.

        :param signum: required by signal.signal, not used directly
        :param frame: required by signal.signal, not used directly
        :return:
        """
        self.kill_now = True


class _ValueContainer:
    """Container to return values from a context manager."""

    def __init__(self):
        self.value = 0

    def update(self, value):
        """
        Update stored value.
        :param value: a value to store.
        :return:
        """
        self.value = value


def _watch_power(logfile: Path = None, sender: Connection = None, display: bool = False):
    """
    Poll GPU and log/display current power consumption.
    Update frequency: every 1 second.

    :param logfile: logfile path (the file will be created/overwritten).
    :param sender: sender-end connection.
    :param display: display consumption in terminal.
    :return: None
    """

    total = 0
    killer = _GracefulKiller()

    nvmlInit()
    handle = nvmlDeviceGetHandleByIndex(0)

    if logfile is not None:
        f = open(logfile, 'w')
    while not killer.kill_now:  # exit gracefully
        power = int(nvmlDeviceGetPowerUsage(handle)) / 1000  # strangely nvidia outputs milliwatts
        total += power / 3600 / 1000  # convert to kWh
        if display:
            print(f'\r{datetime.now().strftime("%H:%M:%S")} {total:.5f} kWh so far', end='')
        if logfile is not None:
            f.write(f'{datetime.now()} {power}\n')
        time.sleep(1)
    print(total)
    if display:
        print('', end='\n')
    if sender is not None:
        sender.send(total)


class PowerWatcher:
    """
    Context manager to track pipeline energy consumption.
    Update frequency: every 1 second.

    with PowerWatcher() as pw:
        ...
        your pipeline
        ...
    pw.total  # get results
    """

    def __init__(self, logfile: Path = None, display: bool = False):
        """
        :param logfile: logfile path.
        :param display: display consumption in the terminal.
        """
        self.logfile = logfile
        self.display = display
        self.total = _ValueContainer()

    def __enter__(self):
        """Run upon entering the context."""
        return self.start()

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Run on context exit.
        :param exc_type: required by Context Manager syntax but not really used here
        :param exc_value: required by Context Manager syntax but not really used
        :param traceback: required by Context Manager syntax but not really used
        :return:
        """
        self.stop()

    def start(self):
        """Start manually."""
        self.recv_end, send_end = Pipe(False)
        self.watcher = Process(target=_watch_power, args=(self.logfile, send_end, self.display,))
        self.watcher.start()
        return self.total

    def stop(self):
        """Stop manually."""
        self.watcher.terminate()
        self.total.update(self.recv_end.recv())