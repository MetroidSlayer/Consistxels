import tkinter as tk
# from tooltip import ToolTip

class Menu_MainMenu(tk.Frame):
    def __init__(self, master, show_frame_callback):
        super().__init__(master)

        self.bg_color = "#2e2e2e"
        self.fg_color = "#ffffff"
        self.secondary_bg = "#3a3a3a"
        self.button_bg = "#444"

        self.configure(bg=self.bg_color)

        tk.Label(self, text="Main Menu", bg=self.bg_color, fg=self.fg_color).pack()
        tk.Button(self, text="Go to Layer Select", bg=self.button_bg, fg=self.fg_color, command=lambda: show_frame_callback("LayerSelect")).pack()