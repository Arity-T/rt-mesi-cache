import tkinter as tk


class RAMGrid:
    def __init__(self, parent, name, x, y, width, height, size):
        self.size = size

        self.default_empty = "0"

        self.frame = tk.LabelFrame(parent, text=" " + name + " ")
        self.frame.place(x=x, y=y, width=width, height=height)

        self.labels = []

        for row in range(self.size):
            address_label = tk.Label(
                self.frame, text=f"#{row}", borderwidth=1, relief="solid"
            )
            address_label.grid(row=row, column=0, sticky="nsew", padx=0, pady=0)

            label = tk.Label(
                self.frame, text=self.default_empty, borderwidth=1, relief="solid"
            )
            label.grid(row=row, column=1, rowspan=1, sticky="nsew", padx=0, pady=0)
            self.labels.append(label)

        # Конфигурация веса строк и столбцов для растягивания
        for i in range(self.size):
            self.frame.rowconfigure(i, weight=1)

        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=2)

    def reset(self):
        for label in self.labels:
            label.config(text=self.default_empty)

    def write(self, value, address):
        self.labels[address].config(text=str(value))


if __name__ == "__main__":
    # Пример использования
    root = tk.Tk()
    root.geometry("400x400")
    grid = RAMGrid(root, "RAM", 20, 20, 200, 300, 16)

    root.after(2000, lambda: grid.write(10, 0))

    root.after(4000, lambda: grid.write(20, 1))

    root.after(7000, grid.reset)

    root.mainloop()
