"""Визуализация шин (HorizontalArrow) и переходов (VerticalArrow).

Демо:
python arrows.py
"""

import tkinter as tk
from enum import Enum


class Color(Enum):
    BACKGROUND = (240, 240, 240)
    BLACK = (32, 32, 32)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    PINK = (255, 0, 255)


class VerticalArrow:
    def __init__(
        self,
        canvas: tk.Canvas,
        x: int,
        y: int,
        length: int,
        active_color: Color = Color.RED,
        default_color: Color = Color.BLACK,
    ):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.length = length
        self.active_color = active_color
        self.default_color = default_color

        self.arrow = self.canvas.create_line(
            self.x,
            self.y + self.length,
            self.x,
            self.y,
            arrow=tk.BOTH,
            fill="#%02x%02x%02x" % self.default_color.value,
            width=10,
            arrowshape=(20, 20, 10),
        )
        self.animation_arrow = self.canvas.create_line(
            self.x,
            self.y + self.length,
            self.x,
            self.y + self.length,
            arrow=tk.LAST,
            fill="#%02x%02x%02x" % self.active_color.value,
            width=10,
            arrowshape=(20, 20, 10),
        )

    def reset(self):
        self.canvas.itemconfig(
            self.arrow, fill="#%02x%02x%02x" % self.default_color.value
        )

        self.canvas.coords(
            self.animation_arrow,
            self.x,
            self.y + self.length,
            self.x,
            self.y + self.length,
        )

        self.canvas.update()

    def _fade_arrow(self, percentage):
        color = "#%02x%02x%02x" % (
            int(
                self.default_color.value[0]
                + (Color.BACKGROUND.value[0] - self.default_color.value[0]) * percentage
            ),
            int(
                self.default_color.value[1]
                + (Color.BACKGROUND.value[1] - self.default_color.value[1]) * percentage
            ),
            int(
                self.default_color.value[2]
                + (Color.BACKGROUND.value[2] - self.default_color.value[2]) * percentage
            ),
        )
        self.canvas.itemconfig(self.arrow, fill=color)

    def run_arrow_up(self):
        self.reset()

        def animate(percentage):
            new_y = self.y + self.length * (1 - percentage)

            self.canvas.coords(
                self.animation_arrow,
                self.x,
                self.y + self.length,
                self.x,
                new_y,
            )

            self._fade_arrow(percentage)

            if percentage < 1:
                self.canvas.after(15, lambda: animate(percentage + 0.01))

        animate(0)

    def run_arrow_down(self):
        self.reset()

        def animate(percentage):
            new_y = self.y + self.length * percentage

            self.canvas.coords(
                self.animation_arrow,
                self.x,
                self.y,
                self.x,
                new_y,
            )

            self._fade_arrow(percentage)

            if percentage < 1:
                self.canvas.after(15, lambda: animate(percentage + 0.01))

        animate(0)


class HorizontalArrow:
    def __init__(
        self,
        canvas: tk.Canvas,
        name: str,
        x: int,
        y: int,
        length: int,
        active_color: Color = Color.RED,
        default_color: Color = Color.BLACK,
    ):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.length = length
        self.active_color = active_color
        self.default_color = default_color

        self.arrow = self.canvas.create_line(
            self.x,
            self.y,
            self.x + self.length,
            self.y,
            arrow=tk.BOTH,
            fill="#%02x%02x%02x" % self.default_color.value,
            width=10,
            arrowshape=(20, 20, 10),
        )

        self.label = tk.Label(
            self.canvas, text=name, fg="#%02x%02x%02x" % self.active_color.value
        )
        self.label.place(x=self.x + 20, y=self.y - 27)

    def reset(self):
        self.canvas.itemconfig(
            self.arrow, fill="#%02x%02x%02x" % self.default_color.value
        )

        self.canvas.update()

    def activate(self):
        self.reset()
        self.canvas.itemconfig(
            self.arrow, fill="#%02x%02x%02x" % self.active_color.value
        )


if __name__ == "__main__":
    # Пример использования
    root = tk.Tk()
    root.title("Examples of VerticalArrow")

    canvas = tk.Canvas(root, width=400, height=500)
    canvas.pack()

    vertical_arrows = [
        VerticalArrow(canvas, 100, 100, 200, Color.RED),
        VerticalArrow(canvas, 200, 100, 200, Color.BLUE),
        VerticalArrow(canvas, 300, 100, 200, Color.PINK),
    ]

    horizontal_arrows = [
        HorizontalArrow(canvas, "DATA BUS", 80, 350, 240, Color.RED),
        HorizontalArrow(canvas, "ADDRESS BUS", 80, 400, 240, Color.BLUE),
        HorizontalArrow(canvas, "SHARED", 80, 450, 240, Color.PINK),
    ]

    def loop_animation():
        for arrow in vertical_arrows:
            root.after(0, arrow.reset)
            root.after(1000, arrow.run_arrow_up)
            root.after(4000, arrow.reset)
            root.after(5000, arrow.run_arrow_down)

        for i, arrow in enumerate(horizontal_arrows):
            root.after(1000 * (i + 1), arrow.activate)
            root.after(1000 * (i + 3), arrow.reset)

        root.after(8000, loop_animation)

    loop_animation()

    root.mainloop()
