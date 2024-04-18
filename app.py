"""Тут визуализация объединяется с логикой."""

from functools import partial
from typing import List

import settings
from protocol import CPU, RAM, CacheController
from visualization.cache_grid import CacheGrid
from visualization.main_window import MainWindow
from visualization.ram_grid import RAMGrid

mw = MainWindow()

# LOGIC
ram = RAM(size=16)
cpus = [CPU(f"CPU #{i}") for i in range(settings.CPU_COUNT)]
cache_controller = CacheController(
    ram, cpus, settings.CACH_CACHLINES_COUNT, settings.CACH_CHANNELS_COUNT
)


def synchronize_caches(cpus: List[CPU], cache_grids: List[CacheGrid]):
    for cpu_index in range(settings.CPU_COUNT):
        for channel_index, channel in enumerate(cpus[cpu_index].cache.channels):
            for cach_line_index, cach_line in enumerate(channel):
                if cach_line.state is not None:
                    cache_grids[cpu_index].update_cache_line(
                        channel_index=channel_index,
                        cache_line_index=cach_line_index,
                        state=cach_line.state,
                        address=cach_line.address,
                        data=cach_line.data,
                    )


def synchronize_ram(ram: RAM, ram_grid: RAMGrid):
    for i, v in enumerate(ram.data):
        ram_grid.write(value=v, address=i)


def read_callback(cpu_index, address):
    print(f"READ: {cpu_index = }, {address = }")

    cpus[cpu_index].read(address)

    synchronize_caches(cpus, mw.cache_grids)
    synchronize_ram(ram, mw.ram_grid)


def write_callback(cpu_index, address):
    print(f"WRITE: {cpu_index = }, {address = }")

    cpus[cpu_index].increment(address)

    synchronize_caches(cpus, mw.cache_grids)
    synchronize_ram(ram, mw.ram_grid)


for cpu_index, cpu_btn in enumerate(mw.cpu_btns):
    cpu_btn.read_callback = partial(read_callback, cpu_index)
    cpu_btn.write_callback = partial(write_callback, cpu_index)


mw.mainloop()
