import tkinter as tk
from functools import partial
from typing import List

from arrows import Color, HorizontalArrow
from cache_grid import CacheGrid
from cpu_buttons import CPUButtons
from ram_grid import RAMGrid
from protocol import RAM, CacheController, CPU


CPU_COUNT = 4
CACH_CHANNELS_COUNT = 2
CACH_CACHLINES_COUNT = 2
RAM_SIZE = 16

WINDOW_SIZE = (1500, 800)
TOP_LEFT_CORNER = (20, 0)
BOTTOM_RIGHT_CORNER = (1480, 780)

BUS_LENGTH = WINDOW_SIZE[0] - TOP_LEFT_CORNER[0] * 2
CPU_Y_COORD = TOP_LEFT_CORNER[1] + 180
CPU_X_COORDS = [TOP_LEFT_CORNER[0] + 125 + 250 * i for i in range(CPU_COUNT)]
RAM_Y_COORD = TOP_LEFT_CORNER[1] + 180

root = tk.Tk()
root.title("MESI visualization")
root.geometry(f"{WINDOW_SIZE[0]}x{WINDOW_SIZE[1]}")

canvas = tk.Canvas(root, width=WINDOW_SIZE[0], height=WINDOW_SIZE[1])
canvas.pack()


# MAIN BUSES
data_bus = HorizontalArrow(
    canvas,
    "DATA BUS",
    x=TOP_LEFT_CORNER[0],
    y=TOP_LEFT_CORNER[1] + 30,
    length=BUS_LENGTH,
    active_color=Color.RED,
)
address_bus = HorizontalArrow(
    canvas,
    "ADDRESS BUS",
    x=TOP_LEFT_CORNER[0],
    y=TOP_LEFT_CORNER[1] + 80,
    length=BUS_LENGTH,
    active_color=Color.BLUE,
)
shared_bus = HorizontalArrow(
    canvas,
    "SHARED",
    x=TOP_LEFT_CORNER[0],
    y=TOP_LEFT_CORNER[1] + 130,
    length=BUS_LENGTH,
    active_color=Color.PINK,
)

# RAM
ram_grid = RAMGrid(
    root,
    "RAM",
    x=BOTTOM_RIGHT_CORNER[0] - 300,
    y=RAM_Y_COORD,
    width=200,
    height=500,
    size=RAM_SIZE,
)

# CACHE + CPUs
cache_grids: List[CacheGrid] = []
cpu_btns: List[CPUButtons] = []


for cpu_index in range(CPU_COUNT):
    cache_grids.append(
        CacheGrid(
            root,
            f"CACHE {cpu_index}",
            x=CPU_X_COORDS[cpu_index],
            y=CPU_Y_COORD,
            width=170,
            height=100,
            channels_count=CACH_CHANNELS_COUNT,
            cache_lines_count=CACH_CACHLINES_COUNT,
        )
    )

    cpu_btns.append(
        CPUButtons(
            root,
            f"CPU {cpu_index}",
            x=CPU_X_COORDS[cpu_index],
            y=CPU_Y_COORD + cache_grids[-1].height + 50,
            rows=16,
        )
    )


# LOGIC
ram = RAM(size=16)
cpus = [CPU(f"CPU #{i}") for i in range(CPU_COUNT)]
cache_controller = CacheController(ram, cpus, CACH_CACHLINES_COUNT, CACH_CHANNELS_COUNT)


def synchronize_caches(cpus: List[CPU], cache_grids: List[CacheGrid]):
    for cpu_index in range(CPU_COUNT):
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

    synchronize_caches(cpus, cache_grids)


def write_callback(cpu_index, address):
    print(f"WRITE: {cpu_index = }, {address = }")

    cpus[cpu_index].increment(address)

    synchronize_caches(cpus, cache_grids)
    synchronize_ram(ram, ram_grid)


for cpu_index, cpu_btn in enumerate(cpu_btns):
    cpu_btn.read_callback = partial(read_callback, cpu_index)
    cpu_btn.write_callback = partial(write_callback, cpu_index)


root.mainloop()
