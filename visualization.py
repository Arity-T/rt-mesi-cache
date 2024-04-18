import tkinter as tk
from typing import List

import settings
from arrows import Color, HorizontalArrow
from cache_grid import CacheGrid
from cpu_buttons import CPUButtons
from ram_grid import RAMGrid


class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(settings.TITLE)
        self.root.geometry(f"{settings.WINDOW_SIZE[0]}x{settings.WINDOW_SIZE[1]}")

        self.canvas = tk.Canvas(
            self.root, width=settings.WINDOW_SIZE[0], height=settings.WINDOW_SIZE[1]
        )
        self.canvas.pack()

        self.draw_buses()
        self.draw_ram()
        self.draw_cpus()

    def mainloop(self):
        self.root.mainloop()

    def draw_buses(self):
        self.data_bus = HorizontalArrow(
            self.canvas,
            "DATA BUS",
            x=settings.TOP_LEFT_CORNER[0],
            y=settings.TOP_LEFT_CORNER[1] + 30,
            length=settings.BUS_LENGTH,
            active_color=Color.RED,
        )
        self.address_bus = HorizontalArrow(
            self.canvas,
            "ADDRESS BUS",
            x=settings.TOP_LEFT_CORNER[0],
            y=settings.TOP_LEFT_CORNER[1] + 80,
            length=settings.BUS_LENGTH,
            active_color=Color.BLUE,
        )
        self.shared_bus = HorizontalArrow(
            self.canvas,
            "SHARED",
            x=settings.TOP_LEFT_CORNER[0],
            y=settings.TOP_LEFT_CORNER[1] + 130,
            length=settings.BUS_LENGTH,
            active_color=Color.PINK,
        )

    def draw_ram(self):
        self.ram_grid = RAMGrid(
            self.root,
            "RAM",
            x=settings.BOTTOM_RIGHT_CORNER[0] - 300,
            y=settings.RAM_Y_COORD,
            width=200,
            height=500,
            size=settings.RAM_SIZE,
        )

    def draw_cpus(self):
        self.cache_grids: List[CacheGrid] = []
        self.cpu_btns: List[CPUButtons] = []

        for cpu_index in range(settings.CPU_COUNT):
            self.cache_grids.append(
                CacheGrid(
                    self.root,
                    f"CACHE {cpu_index}",
                    x=settings.CPU_X_COORDS[cpu_index],
                    y=settings.CPU_Y_COORD,
                    width=170,
                    height=100,
                    channels_count=settings.CACH_CHANNELS_COUNT,
                    cache_lines_count=settings.CACH_CACHLINES_COUNT,
                )
            )

            self.cpu_btns.append(
                CPUButtons(
                    self.root,
                    f"CPU {cpu_index}",
                    x=settings.CPU_X_COORDS[cpu_index],
                    y=settings.CPU_Y_COORD + self.cache_grids[-1].height + 50,
                    rows=16,
                )
            )
