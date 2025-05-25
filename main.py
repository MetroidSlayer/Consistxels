import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(1)  # PER_MONITOR_AWARE

import tkinter as tk
from menu_mainmenu import Menu_MainMenu
from menu_layerselect import Menu_LayerSelect
from menu_loadjson import Menu_LoadJson

class ConsistxelsApp(tk.Frame):
    def __init__(self, root):
        super().__init__()
        
        self.root = root
        self.root.title("Consistxels")
        
        # Set window attributes
        self.root.geometry("900x768")         # window size
        # self.root.configure(bg = '#303030') # bg color

        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.bg_color = "#2e2e2e"
        self.fg_color = "#ffffff"
        self.secondary_bg = "#3a3a3a"
        self.button_bg = "#444"
        # self.button_fg = "#fff"

        # Track images and border
        # self.image_data = []  # List of dicts: {path, name, thumbnail, img_obj}
        # self.border_image = None
        # self.border_path = None
        # self.border_color = "#00007f"

        self.root.configure(bg=self.bg_color)

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

def main():
    root = tk.Tk()
    app = ConsistxelsApp(root)
    app.pack(fill="both", expand=True)
    root.mainloop()

# run main
if __name__ == "__main__":
    main()