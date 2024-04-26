import tkinter as tk
from typing import List

import settings

from .arrows import Color, HorizontalArrow, VerticalArrow
from .cache_grid import CacheGrid
from .cpu_buttons import CPUButtons
from .ram_grid import RAMGrid


class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(settings.TITLE)
        self.root.geometry(f"{settings.WINDOW_SIZE[0]}x{settings.WINDOW_SIZE[1]}")

        self.canvas = tk.Canvas(
            self.root, width=settings.WINDOW_SIZE[0], height=settings.WINDOW_SIZE[1]
        )
        self.canvas.pack()

        self._draw_buses()
        self._draw_ram()
        self._draw_cpus()

        self.reset_btn = tk.Button(
            self.root,
            text="Reset",
            width=27,
            command=lambda: print("hello"),
        )
        self.reset_btn.place(
            x=settings.BOTTOM_RIGHT_CORNER[0] - 300,
            y=settings.BOTTOM_RIGHT_CORNER[1] - 85,
        )

    def set_reset_callback(self, callback):
        self.reset_btn.config(command=callback)

    def mainloop(self):
        self.root.mainloop()

    def reset_buses(self):
        self.data_bus.reset()
        self.address_bus.reset()
        self.shared_bus.reset()
        self.ram_to_address_bus.reset()
        self.ram_to_data_bus.reset()

        for cpu_index in range(settings.CPU_COUNT):
            self.cache_to_address_buses[cpu_index].reset()
            self.cache_to_data_buses[cpu_index].reset()
            self.cache_to_shared_buses[cpu_index].reset()

            self.cpu_to_cache_read_buses[cpu_index].reset()
            self.cpu_to_cache_write_buses[cpu_index].reset()

    def reset(self):
        self.reset_buses()
        self.ram_grid.reset()

        for cpu_index in range(settings.CPU_COUNT):
            self.cache_grids[cpu_index].reset()

    def _draw_buses(self):
        self.data_bus = HorizontalArrow(
            self.canvas,
            "DATA BUS",
            x=settings.TOP_LEFT_CORNER[0],
            y=settings.BUSES_Y_COORDS[0],
            length=settings.BUS_LENGTH,
            active_color=Color.RED,
        )
        self.address_bus = HorizontalArrow(
            self.canvas,
            "ADDRESS BUS",
            x=settings.TOP_LEFT_CORNER[0],
            y=settings.BUSES_Y_COORDS[1],
            length=settings.BUS_LENGTH,
            active_color=Color.BLUE,
        )
        self.shared_bus = HorizontalArrow(
            self.canvas,
            "SHARED",
            x=settings.TOP_LEFT_CORNER[0],
            y=settings.BUSES_Y_COORDS[2],
            length=settings.BUS_LENGTH,
            active_color=Color.PINK,
        )

    def _draw_ram(self):
        self.ram_to_data_bus = VerticalArrow(
            self.canvas,
            x=settings.BOTTOM_RIGHT_CORNER[0] - 162,
            y=settings.BUSES_Y_COORDS[0] + 5,
            length=settings.RAM_Y_COORD - settings.BUSES_Y_COORDS[0] - 5,
            active_color=Color.RED,
        )

        self.ram_to_address_bus = VerticalArrow(
            self.canvas,
            x=settings.BOTTOM_RIGHT_CORNER[0] - 260,
            y=settings.BUSES_Y_COORDS[1] + 5,
            length=settings.RAM_Y_COORD - settings.BUSES_Y_COORDS[1] - 5,
            active_color=Color.BLUE,
        )

        self.ram_grid = RAMGrid(
            self.root,
            "RAM",
            x=settings.BOTTOM_RIGHT_CORNER[0] - 300,
            y=settings.RAM_Y_COORD,
            width=200,
            height=500,
            size=settings.RAM_SIZE,
        )

    def _draw_cpus(self):
        self.cache_grids: List[CacheGrid] = []
        self.cpu_btns: List[CPUButtons] = []

        self.cache_to_data_buses: List[VerticalArrow] = []
        self.cache_to_address_buses: List[VerticalArrow] = []
        self.cache_to_shared_buses: List[VerticalArrow] = []

        self.cpu_to_cache_read_buses: List[VerticalArrow] = []
        self.cpu_to_cache_write_buses: List[VerticalArrow] = []

        for cpu_index in range(settings.CPU_COUNT):
            self.cache_to_data_buses.append(
                VerticalArrow(
                    self.canvas,
                    x=settings.CPU_X_COORDS[cpu_index] + 105,
                    y=settings.BUSES_Y_COORDS[0] + 5,
                    length=settings.CPU_Y_COORD - settings.BUSES_Y_COORDS[0] - 5,
                    active_color=Color.RED,
                )
            )

            self.cache_to_address_buses.append(
                VerticalArrow(
                    self.canvas,
                    x=settings.CPU_X_COORDS[cpu_index] + 63,
                    y=settings.BUSES_Y_COORDS[1] + 5,
                    length=settings.CPU_Y_COORD - settings.BUSES_Y_COORDS[1] - 5,
                    active_color=Color.BLUE,
                )
            )
            self.cache_to_shared_buses.append(
                VerticalArrow(
                    self.canvas,
                    x=settings.CPU_X_COORDS[cpu_index] + 31,
                    y=settings.BUSES_Y_COORDS[2] + 5,
                    length=settings.CPU_Y_COORD - settings.BUSES_Y_COORDS[2] - 5,
                    active_color=Color.PINK,
                )
            )

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

            self.cpu_to_cache_read_buses.append(
                VerticalArrow(
                    self.canvas,
                    x=settings.CPU_X_COORDS[cpu_index] + 63,
                    y=settings.CPU_Y_COORD + self.cache_grids[-1].height,
                    length=settings.CPU_TO_CACHE_BUSES_LENGTH,
                    active_color=Color.BLUE,
                )
            )

            self.cpu_to_cache_write_buses.append(
                VerticalArrow(
                    self.canvas,
                    x=settings.CPU_X_COORDS[cpu_index] + 105,
                    y=settings.CPU_Y_COORD + self.cache_grids[-1].height,
                    length=settings.CPU_TO_CACHE_BUSES_LENGTH,
                    active_color=Color.RED,
                )
            )

            self.cpu_btns.append(
                CPUButtons(
                    self.root,
                    f"CPU {cpu_index}",
                    x=settings.CPU_X_COORDS[cpu_index],
                    y=settings.CPU_Y_COORD
                    + self.cache_grids[-1].height
                    + settings.CPU_TO_CACHE_BUSES_LENGTH,
                    rows=16,
                )
            )
