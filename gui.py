import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(1)  # PER_MONITOR_AWARE

import tkinter as tk
from menu_mainmenu import Menu_MainMenu
from menu_layerselect import Menu_LayerSelect
from menu_loadjson import Menu_LoadJson

from shared import on_global_click
# import shared

# from generate import get_x_range
# from generate import generate_all

# import threading

# import json
# import sys
# import tempfile
# import subprocess
# import multiprocessing


class ConsistxelsApp(tk.Frame):
    def __init__(self, root):
        super().__init__()
        
        # self.root = root
        root.title("Consistxels")

        # Set window attributes
        root.geometry("1680x768")         # window size
        root.configure(bg = '#303030') # bg color

        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.bg_color = "#2e2e2e"
        self.fg_color = "#ffffff"
        self.secondary_bg = "#3a3a3a"
        self.button_bg = "#444"
        
        root.configure(bg=self.bg_color)
                

        root.bind_all("<Button-1>", on_global_click, add="+")
        # root.bind_class("Canvas", "<Button-1>", on_global_click, add="+")

        self.frames = {
            "Main": Menu_MainMenu(self.container, self.show_frame),
            "LayerSelect": Menu_LayerSelect(self.container, self.show_frame),
            "LoadJson": Menu_LoadJson(self.container, self.show_frame)
        }

        for frame in self.frames.values():
            frame.place(relwidth=1, relheight=1)

        self.show_frame("Main")

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()

    def update_progress(self, value, header_text, info_text):
        self.frames[1].update_progress(value, header_text, info_text)

    def on_close(self, root):
        # ask if want to save if curr frame has modified work

        self.frames["LayerSelect"].cancel_process(True)

        root.destroy()

def main():
    root = tk.Tk()
    app = ConsistxelsApp(root)
    app.pack(fill="both", expand=True)

    root.protocol("WM_DELETE_WINDOW", lambda r=root: app.on_close(r))

    root.mainloop()

# run main
if __name__ == "__main__":
    main()