"""Визуализация кэша процессора.

Демо:
python cache_grid.py
"""

import tkinter as tk


class CacheGrid:
    def __init__(
        self, parent, name, x, y, width, height, channels_count, cache_lines_count
    ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.channels_count = channels_count
        self.cache_lines_count = cache_lines_count

        self.default_state = "I"
        self.default_empty = "--"

        self.frame = tk.LabelFrame(parent, text=" " + name + " ")
        self.frame.place(x=x, y=y, width=width, height=height)

        for i in range(channels_count):
            tk.Label(self.frame, text=str(i), borderwidth=1, relief="solid").grid(
                row=i * cache_lines_count,
                column=0,
                rowspan=cache_lines_count,
                sticky="nsew",
            )

        self.labels = []

        for row in range(channels_count * cache_lines_count):
            self.labels.append([])
            for col in range(1, 5):
                text = self.default_state if col == 1 else self.default_empty
                label = tk.Label(self.frame, text=text, borderwidth=1, relief="solid")
                label.grid(
                    row=row, column=col, rowspan=1, sticky="nsew", padx=0, pady=0
                )
                self.labels[row].append(label)

        # Конфигурация веса строк и столбцов для растягивания
        for i in range(channels_count * cache_lines_count):
            self.frame.rowconfigure(i, weight=1)

        self.frame.columnconfigure(0, weight=2)
        self.frame.columnconfigure(1, weight=3)
        self.frame.columnconfigure(2, weight=6)
        self.frame.columnconfigure(3, weight=6)
        self.frame.columnconfigure(4, weight=6)

    def reset(self):
        for state_label, address_label, data_label, counter_label in self.labels:
            state_label.config(text=self.default_state)
            address_label.config(text=self.default_empty)
            data_label.config(text=self.default_empty)
            counter_label.config(text=self.default_empty)

    def update_cache_line(
        self, channel_index, cache_line_index, state, address, data, policy_counter
    ):
        state_label, address_label, data_label, policy_counter_label = self.labels[
            channel_index * self.cache_lines_count + cache_line_index
        ]

        state_label.config(text=str(state))
        address_label.config(text=str(address))
        data_label.config(text=str(data))
        policy_counter_label.config(text=str(policy_counter))


if __name__ == "__main__":
    # Пример использования
    root = tk.Tk()
    root.geometry("400x400")
    grid = CacheGrid(root, "Cache", 20, 20, 200, 150, 2, 2)

    root.after(3000, lambda: grid.update_cache_line(0, 1, "E", "a1", "00", 1))

    root.after(5000, lambda: grid.update_cache_line(1, 0, "S", "a0", "11", 1))

    root.after(7000, grid.reset)

    root.mainloop()
