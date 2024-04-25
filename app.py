"""Основной файл приложения. Тут визуализация объединяется с логикой."""

from functools import partial
from typing import List
from collections import deque

import settings
from protocol import CPU, RAM, CacheController
from visualization.cache_grid import CacheGrid
from visualization.main_window import MainWindow
from visualization.ram_grid import RAMGrid

mw = MainWindow()

# Инициализируем систему
ram = RAM(size=settings.RAM_SIZE)
cpus = [CPU() for _ in range(settings.CPU_COUNT)]
cache_controller = CacheController(
    ram, cpus, settings.CACH_CACHLINES_COUNT, settings.CACH_CHANNELS_COUNT
)


def synchronize_caches(cpus: List[CPU], cache_grids: List[CacheGrid]):
    """Синхронизирует состояние кэшей с визуализацией."""
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
                        policy_counter=cach_line.not_used_counter,
                    )


def synchronize_ram(ram: RAM, ram_grid: RAMGrid):
    """Синхронизирует состояние оперативной памяти с визуализацией."""
    for i, v in enumerate(ram.data):
        ram_grid.write(value=v, address=i)


def reset():
    for cpu in cpus:
        cpu.cache.reset()
    ram.reset()

    mw.reset()


mw.set_reset_callback(reset)


# Обрабатываем пользовательский ввод
task_queue = deque()
tick_counter = 0


def tick():
    global tick_counter
    tick_counter += 1

    while task_queue:
        mw.address_bus.reset()

        operation_type, cpu_index, address = task_queue.popleft()

        if operation_type == "R":
            mw.cpu_to_cache_read_buses[cpu_index].run_arrow_up()

            if cpus[cpu_index].cache.get_cache_line_by_address(address=address):
                mw.cpu_to_cache_write_buses[cpu_index].run_arrow_down()
            else:
                mw.address_bus.activate()

            print(f"READ: {cpu_index = }, {address = }")
            cpus[cpu_index].read(address)

        elif operation_type == "W":
            print(f"WRITE: {cpu_index = }, {address = }")
            cpus[cpu_index].increment(address)

        synchronize_caches(cpus, mw.cache_grids)
        synchronize_ram(ram, mw.ram_grid)

    mw.root.after(settings.TICK_MS, tick)


def read_callback(cpu_index: int, address: int):
    """Функция вызывается, когда пользователь нажимает на кнопку чтения."""
    task_queue.append(("R", cpu_index, address))


def write_callback(cpu_index: int, address: int):
    """Функция вызывается, когда пользователь нажимает на кнопку записи."""
    task_queue.append(("W", cpu_index, address))


# Привязываем нажатие на кнопки к колбэкам
for cpu_index, cpu_btn in enumerate(mw.cpu_btns):
    cpu_btn.read_callback = partial(read_callback, cpu_index)
    cpu_btn.write_callback = partial(write_callback, cpu_index)

# Запускаем приложение
mw.root.after(settings.TICK_MS, tick)
mw.mainloop()
