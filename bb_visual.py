import tkinter as tk
from tkinter import font
import tkinter.ttk as ttk

from enum import Enum


class Endianness(Enum):
    A = "rows: ↑, columns: →"
    B = "rows: ↓, columns: →"
    C = "rows: ↑, columns: ←"
    D = "rows: ↓, columns: ←"

    def row_label(self, index):
        if self.name == "A" or self.name == "C":
            return 7 - index
        else:
            return index

    def col_label(self, index):
        if self.name == "A" or self.name == "B":
            return index
        else:
            return 7 - index

    def bit(self, row, col):
        match self:
            case Endianness.A:
                return 1 << 8 * (7 - row) + col
            case Endianness.B:
                return 1 << 8 * row + col
            case Endianness.C:
                return 1 << 8 * (7 - row) + 7 - col
            case Endianness.D:
                return 1 << 8 * row + 7 - col


class U64:
    def __init__(self, value):
        self.value = value & 0xFFFFFFFFFFFFFFFF

    def __lshift__(self, other):
        return U64(self.value << other)

    def __rshift__(self, other):
        return U64(self.value >> other)

    def __invert__(self):
        return U64(~self.value)

    def __repr__(self):
        return f"U64({self.value})"

    def __str__(self):
        return str(self.value)


class Bitboard(tk.Frame):
    def __init__(self, master, initial_bitboard: int, endianness: Endianness):
        super().__init__(master)
        self.bitboard = initial_bitboard
        # self.endianness = tk.StringVar(value="0")  # Initialize with endianness 0
        self.endianness = endianness

        self.create_widgets()
        self.update_labels()

    def create_widgets(self):
        # Create the binary entry
        self.binary_entry = tk.Entry(self, width=66, justify="center", font=custom_font)
        self.binary_entry.pack()
        # Create the main 8x8 board
        self.canvas = tk.Canvas(
            self, width=400, height=400, borderwidth=0, highlightthickness=0
        )
        self.canvas.pack()

        self.cells = []
        cell_size = 40
        label_offset = cell_size // 2

        for row in range(10):
            cell_row = []
            for col in range(10):
                x1 = col * cell_size
                y1 = row * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size

                if row == 0 or row == 9 or col == 0 or col == 9:
                    # Create label for the outer edges
                    label_text = ""
                    if row == 0 and col != 0 and col != 9:
                        label_text = str(self.endianness.col_label(col - 1))
                    elif row == 9 and col != 0 and col != 9:
                        label_text = str(self.endianness.col_label(col - 1))
                    elif col == 0 and row != 0 and row != 9:
                        label_text = str(self.endianness.row_label(row - 1))
                    elif col == 9 and row != 0 and row != 9:
                        label_text = str(self.endianness.row_label(row - 1))

                    label = self.canvas.create_text(
                        x1 + label_offset, y1 + label_offset, text=label_text
                    )
                    cell_row.append(label)
                else:
                    # Create cell rectangle for the inner grid
                    cell = self.canvas.create_rectangle(
                        x1, y1, x2, y2, outline="gray", fill="white"
                    )
                    self.canvas.tag_bind(
                        cell,
                        "<Button-1>",
                        lambda event, r=row - 1, c=col - 1: self.toggle_bit(r, c),
                    )
                    cell_row.append(cell)

            self.cells.append(cell_row)
        self.update_cell_colors()

        # Create the hexadecimal entry
        self.hex_entry = tk.Entry(self, width=18, justify="center", font=custom_font)
        self.hex_entry.pack()

        # Create the endianness options
        self.endianness_label = tk.Label(self, text="Endianness:")
        self.endianness_label.pack()

        self.endianness_combo = ttk.Combobox(
            self,
            values=[
                Endianness.A.value,
                Endianness.B.value,
                Endianness.C.value,
                Endianness.D.value,
            ],
            textvariable=self.endianness,
        )
        self.endianness_combo.pack()
        self.endianness_combo.bind("<<ComboboxSelected>>", self.update_combo)

        # Create the control buttons
        self.reset_button = tk.Button(self, text="Reset", command=self.reset_bitboard)
        self.reset_button.pack()

        self.set_all_button = tk.Button(self, text="Set All", command=self.set_all_bits)
        self.set_all_button.pack()

        self.inverse_button = tk.Button(self, text="~", command=self.inverse_bitboard)
        self.inverse_button.pack()

        self.shift_left_button = tk.Button(
            self, text="<<", command=self.shift_bits_left
        )
        self.shift_left_button.pack()

        self.shift_right_button = tk.Button(
            self, text=">>", command=self.shift_bits_right
        )
        self.shift_right_button.pack()

        # Bind events to update the bitboard when the entries change
        self.hex_entry.bind("<KeyRelease>", self.update_bitboard_from_hex)
        self.binary_entry.bind("<KeyRelease>", self.update_bitboard_from_binary)

    def toggle_bit(self, row, col):
        # Toggle the corresponding bit on the bitboard
        bit = self.endianness.bit(row, col)
        self.bitboard ^= bit

        self.update_labels()
        self.update_cell_colors()
        self.update_entries()

    def update_combo(self, event=None):
        self.update_labels()
        self.update_cell_colors()

    def update_labels(self, event=None):
        match self.endianness_combo.get():
            case Endianness.A.value:
                self.endianness = Endianness.A
            case Endianness.B.value:
                self.endianness = Endianness.B
            case Endianness.C.value:
                self.endianness = Endianness.C
            case Endianness.D.value:
                self.endianness = Endianness.D

        for row in range(8):
            canvas_row = row + 1
            label_text = str(self.endianness.row_label(row))
            self.canvas.itemconfig(self.cells[canvas_row][0], text=label_text)
            self.canvas.itemconfig(self.cells[canvas_row][9], text=label_text)

        for col in range(8):
            canvas_col = col + 1
            label_text = str(self.endianness.col_label(col))
            self.canvas.itemconfig(self.cells[0][canvas_col], text=label_text)
            self.canvas.itemconfig(self.cells[9][canvas_col], text=label_text)

    def update_cell_colors(self):
        # Update the colors of the cells based on the bitboard value
        for row in range(8):
            for col in range(8):
                bit = self.endianness.bit(row, col)
                is_set = bool(self.bitboard & bit)
                color = "black" if is_set else "white"
                self.canvas.itemconfig(self.cells[row + 1][col + 1], fill=color)

    def update_entries(self):
        # Update the hex and binary entries with the current bitboard value
        self.update_hex_entry()
        self.update_binary_entry()

    def update_hex_entry(self):
        self.hex_entry.delete(0, tk.END)
        self.hex_entry.insert(tk.END, hex(self.bitboard))

    def update_binary_entry(self):
        self.binary_entry.delete(0, tk.END)
        self.binary_entry.insert(tk.END, bin(self.bitboard))

    def update_bitboard_from_hex(self, event):
        # Update the bitboard based on the hex entry value
        try:
            hex_value = self.hex_entry.get()
            self.bitboard = int(hex_value, 16)
        except ValueError:
            pass

        self.update_labels()
        self.update_cell_colors()
        self.update_binary_entry()

    def update_bitboard_from_binary(self, event):
        # Update the bitboard based on the binary entry value
        try:
            binary_value = self.binary_entry.get()
            self.bitboard = int(binary_value, 2)
        except ValueError:
            pass

        self.update_labels()
        self.update_cell_colors()
        self.update_hex_entry()

    def reset_bitboard(self):
        # Reset the bitboard to all zeros
        self.bitboard = 0

        self.update_labels()
        self.update_cell_colors()
        self.update_entries()

    def inverse_bitboard(self):
        # Inverse the bitboard bitwise
        self.bitboard = ~self.bitboard
        self.update_labels()
        self.update_cell_colors()
        self.update_entries()

    def set_all_bits(self):
        # Set all bits of the bitboard to ones
        self.bitboard = 0xFFFFFFFFFFFFFFFF

        self.update_labels()
        self.update_cell_colors()
        self.update_entries()

    def shift_bits_left(self):
        # Shift all bits of the bitboard to the left
        self.bitboard <<= 1

        self.update_labels()
        self.update_cell_colors()
        self.update_entries()

    def shift_bits_right(self):
        # Shift all bits of the bitboard to the right
        self.bitboard >>= 1

        self.update_labels()
        self.update_cell_colors()
        self.update_entries()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Bitboard Visualization")

    # List of font candidates
    font_candidates = [
        "Source Code Pro",
        "SF Mono",
        "Menlo",
        "Consolas",
        "Roboto Mono",
        "Noto Sans Mono",
        "JetBrains Mono",
        "Liberation Mono",
        "Hack",
        "Fira Code",
        "Ubuntu Mono",
        "IBM Plex Mono",
        "DejaVu Sans Mono",
        "Andale Mono",
        "Monospace",
        "Courier New",
    ]

    # Find the first available font from the candidates
    custom_font = None
    for font_candidate in font_candidates:
        if font_candidate in font.families():
            custom_font = (font_candidate,)
            break
    gui = Bitboard(root, 0, Endianness.A)
    gui.pack()
    gui.mainloop()
