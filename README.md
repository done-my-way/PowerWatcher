# PowerWatcher

Python3 context manager to log power consumption of an ML-pipeline running on a Nvidia-GPU.

## Installation

pip install power-consumption

## Usage

```{python}
from power_watcher import PowerWatcher


with PowerWatcher() as pw:
    ...
    your pipeline
    ...

total_consumption = pw.total  # total power consumption
```

repo: https://github.com/WGussev/PowerWatcher