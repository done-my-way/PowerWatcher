import unittest
from importlib import import_module
from multiprocessing import Process, Pipe
from time import sleep
from unittest.mock import patch


class FirstTest(unittest.TestCase):
    pw = import_module('power_watcher')
    pw = pw.power_watcher

    def test_value_container(self):
        container = self.pw._ValueContainer()
        self.assertEqual(container.value, 0)
        container.update(7)
        self.assertEqual(container.value, 7)
        container.update(0.45)
        self.assertEqual(container.value, 0.45)

    def test_process_killer(self):
        def f(sender):
            killer = self.pw._GracefulKiller()
            while killer.kill_now is False:
                pass
            sender.send(killer)

        recv_end, send_end = Pipe(False)
        watcher = Process(target=f, args=(send_end,))
        watcher.start()
        sleep(1)
        watcher.terminate()
        kn = recv_end.recv()
        self.assertEqual(kn.kill_now, True)

    @patch('power_watcher.power_watcher.nvmlInit')
    @patch('power_watcher.power_watcher.nvmlDeviceGetHandleByIndex')
    @patch('power_watcher.power_watcher.nvmlDeviceGetPowerUsage', return_value=3600 * 1000 * 1000)
    def test_context_manager(self, mock_init, mock_handle, mock_power):
        recv_end, send_end = Pipe(False)
        watcher = Process(target=self.pw._watch_power, args=(None, send_end, False))
        watcher.start()
        sleep(1)
        watcher.terminate()
        self.assertEqual(recv_end.recv(), 1.0)
