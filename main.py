import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(1)  # PER_MONITOR_AWARE

import tkinter as tk
from menu_mainmenu import Menu_MainMenu
from menu_layerselect import Menu_LayerSelect
from menu_loadjson import Menu_LoadJson

from shared import on_global_click
# import shared

# from generate import get_x_range

class ConsistxelsApp(tk.Frame):
    def __init__(self, root):
        super().__init__()
        
        # self.root = root
        root.title("Consistxels")

        # for x in get_x_range(0, 10, True, False):
        #     print(x)

        # Set window attributes
        root.geometry("1680x768")         # window size
        # root.configure(bg = '#303030') # bg color

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

        root.configure(bg=self.bg_color)

        # def on_global_click(event):
        #     # Get the widget under the cursor
        #     clicked_widget = root.winfo_containing(event.x_root, event.y_root)

        #     # If the widget doesn't accept focus, or is the root/frame background, clear focus
        #     if clicked_widget is root or isinstance(clicked_widget, tk.Frame):
        #         print("gothere")
        #         root.focus_set()
                

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

def main():
    root = tk.Tk()
    app = ConsistxelsApp(root)
    app.pack(fill="both", expand=True)
    root.mainloop()

# run main
if __name__ == "__main__":
    main()