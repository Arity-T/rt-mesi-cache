"""Основной файл приложения. Тут визуализация объединяется с логикой."""

from functools import partial
from typing import List
from collections import deque

import settings
from protocol import CPU, RAM, Cache, CacheController
from visualization.cache_grid import CacheGrid
from visualization.main_window import MainWindow
from visualization.ram_grid import RAMGrid

mw = MainWindow()

index_dont = 0
b2 = True

# Инициализируем систему
def cpu_read_callback(cpu_index, b):
    print("cpu_read_callback")
    mw.cpu_to_cache_read_buses[cpu_index].run_arrow_up()
    global b2
    if b:
        if b2:
            mw.root.after(7500, lambda: mw.cpu_to_cache_write_buses[cpu_index].run_arrow_down())
    else:
        mw.root.after(1500, lambda: mw.cpu_to_cache_write_buses[cpu_index].run_arrow_down())
    b2 = True


def cpu_write_callback(cpu_index):
    print("cpu_write_callback")
    mw.cpu_to_cache_read_buses[cpu_index].run_arrow_up()
    mw.cpu_to_cache_write_buses[cpu_index].run_arrow_up()
    global b2
    b2 = False


def cache_read_callback(cpu_index,b):
    pass


def cache_write_callback(cpu_index):
    pass


def ram_read_callback():
    print("ram_read_callback")
    mw.root.after(4500, lambda: mw.ram_to_data_bus.run_arrow_up())


def ram_write_callback():
    print("ram_write_callback")
    mw.root.after(1500, lambda: mw.cache_to_data_buses[index_dont].run_arrow_up())
    mw.root.after(3000, lambda: mw.data_bus.activate())
    mw.root.after(3000, lambda: mw.ram_to_address_bus.run_arrow_down())
    mw.root.after(3000, lambda: mw.ram_to_data_bus.run_arrow_down())


def read_miss_callback(cpu_index, b = 0):
    print("read_miss_callback")
    
    mw.increment_counter()
    mw.root.after(3000, lambda: mw.address_bus.activate())
    
    for i, bus in enumerate(mw.cache_to_address_buses):
        if i == cpu_index:
            mw.root.after(1500, lambda bus=bus: bus.run_arrow_up())
            global index_dont
            index_dont = cpu_index
        else:
            mw.root.after(3000, lambda bus=bus: bus.run_arrow_down())

    mw.root.after(3000, lambda: mw.ram_to_address_bus.run_arrow_down())

    if b == 1:
        mw.root.after(4500, lambda: mw.ram_to_data_bus.run_arrow_up())
        mw.root.after(6000, lambda: mw.data_bus.activate())
        mw.root.after(6000, lambda: mw.cache_to_data_buses[cpu_index].run_arrow_down())
    
    if b == 2:
        mw.root.after(1500, lambda: mw.cache_to_data_buses[cpu_index].run_arrow_up())
        mw.root.after(3000, lambda: mw.data_bus.activate())
        mw.root.after(3000, lambda: mw.ram_to_data_bus.run_arrow_down())
        mw.root.after(4500, lambda: mw.ram_to_data_bus.run_arrow_up())
        mw.root.after(6000, lambda: mw.cache_to_data_buses[cpu_index].run_arrow_down())


def intervention_callback(cpu_index):
    ...
    #mw.data_bus.activate()
    #mw.cache_to_data_buses[cpu_index].run_arrow_up()


def state_callback(cpu_index, list):
    print("state_callback")

    mw.root.after(6000, lambda: mw.shared_bus.activate())
    for i, bus in enumerate(mw.cache_to_shared_buses):
        if i == cpu_index:
            mw.root.after(6000, lambda bus=bus: bus.run_arrow_down())
        else:
            if i in list:
                mw.root.after(4500, lambda bus=bus: bus.run_arrow_up())
            


ram = RAM(
    size=settings.RAM_SIZE,
    read_callback=ram_read_callback,
    write_callback=ram_write_callback,
)

cpus = []

for cpu_index in range(settings.CPU_COUNT):
    cpu = CPU(
        index=cpu_index,
        read_callback=partial(cpu_read_callback, cpu_index),
        write_callback=partial(cpu_write_callback, cpu_index),
    )
    cpu.cache = Cache(
        settings.CACH_CACHLINES_COUNT,
        settings.CACH_CHANNELS_COUNT,
        partial(cache_read_callback, cpu_index),
        partial(cache_write_callback, cpu_index),
    )
    cpus.append(cpu)

cache_controller = CacheController(
    ram,
    cpus,
    settings.CACH_CACHLINES_COUNT,
    settings.CACH_CHANNELS_COUNT,
    read_miss_callback,
    intervention_callback,
    state_callback,
)


def synchronize_caches(cpus: List[CPU], cache_grids: List[CacheGrid]):
    """Синхронизирует состояние кэшей с визуализацией."""
    for cpu_index in range(settings.CPU_COUNT):
        for channel_index, channel in enumerate(cpus[cpu_index].cache.channels):
            for cach_line_index, cach_line in enumerate(channel):
                if cach_line.state is not None:
                    address_to_bin = int(bin(cach_line.address)[2:])
                    cache_grids[cpu_index].update_cache_line(
                        channel_index=channel_index,
                        cache_line_index=cach_line_index,
                        state=cach_line.state,
                        address=address_to_bin,
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
            #print(f"READ: {cpu_index = }, {address = }")
            cpus[cpu_index].read(address)

        elif operation_type == "W":
            #print(f"WRITE: {cpu_index = }, {address = }")
            cpus[cpu_index].increment(address)

        synchronize_caches(cpus, mw.cache_grids)
        synchronize_ram(ram, mw.ram_grid)

    mw.root.after(settings.TICK_MS, tick)


def read_callback(cpu_index: int, address: int):
    """Функция вызывается, когда пользователь нажимает на кнопку чтения."""
    mw.reset_buses()
    task_queue.append(("R", cpu_index, address))


def write_callback(cpu_index: int, address: int):
    """Функция вызывается, когда пользователь нажимает на кнопку записи."""
    mw.reset_buses()
    task_queue.append(("W", cpu_index, address))


# Привязываем нажатие на кнопки к колбэкам
for cpu_index, cpu_btn in enumerate(mw.cpu_btns):
    cpu_btn.read_callback = partial(read_callback, cpu_index)
    cpu_btn.write_callback = partial(write_callback, cpu_index)

# Запускаем приложение
mw.root.after(settings.TICK_MS, tick)
mw.mainloop()
