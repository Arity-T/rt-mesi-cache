"""Интерфейс для взаимодействия пользователя и процессора.

Демо:
python cpu_buttons.py
"""

import tkinter as tk


class CPUButtons:
    def __init__(self, root, name, x, y, rows, read_callback=None, write_callback=None):
        self.x = x
        self.y = y
        self.rows = rows
        self.read_callback = read_callback
        self.write_callback = write_callback

        self.frame = tk.LabelFrame(root, text=" " + name + " ")
        self.frame.place(x=x, y=y)

        self.create_buttons()

    def create_buttons(self):
        for i in range(self.rows):
            pady = (0, 3) if i == self.rows - 1 else 0
            read_button = tk.Button(
                self.frame,
                text=f"read #{i}",
                width=10,
                command=lambda i=i: self.read_callback(i),
            )
            read_button.grid(row=i, column=0, padx=(2, 0), pady=pady)

            write_button = tk.Button(
                self.frame,
                text=f"write #{i}",
                width=10,
                command=lambda i=i: self.write_callback(i),
            )
            write_button.grid(row=i, column=1, padx=(0, 3), pady=pady)


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("400x400")
    root.title("CPU Interface")

    def read_callback(index):
        print(f"Read button pressed for index {index}")

    def write_callback(index):
        print(f"Write button pressed for index {index}")

    CPUButtons(root, "CPU 0", 100, 100, 5, read_callback, write_callback)

    root.mainloop()
