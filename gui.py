import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(1)  # PER_MONITOR_AWARE

import tkinter as tk
from menu_mainmenu import Menu_MainMenu
from menu_layerselect import Menu_LayerSelect
from menu_loadjson import Menu_LoadJson

# from shared import on_global_click
import gui_shared

import sys
import json
from tkinter import messagebox
import threading
# import time

class ConsistxelsApp(tk.Frame):
    def __init__(self, root):
        super().__init__()
        
        # self.root = root
        root.title("Consistxels")

        # Set window attributes
        root.geometry("1680x768")        # window size
        root.configure(bg = '#303030') # bg color

        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        
        root.configure(bg=gui_shared.bg_color)

        root.bind_all("<Button-1>", gui_shared.on_global_click, add="+")
        # root.bind_class("Canvas", "<Button-1>", on_global_click, add="+")

        self.frames = {
            "Main": Menu_MainMenu(self.container, self.show_frame),
            "LayerSelect": Menu_LayerSelect(self.container, self.show_frame),
            "LoadJson": Menu_LoadJson(self.container, self.show_frame)
        }

        for frame in self.frames.values():
            frame.place(relwidth=1, relheight=1)

        self.show_frame("Main")

        self.handle_input_thread = threading.Thread(target=self.handle_input, daemon=True)
        self.handle_input_thread.start()

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()

    def update_progress(self, value, header_text, info_text):
        self.frames["LayerSelect"].update_progress(value, header_text, info_text)

    def on_close(self, root):
        # ask if want to save if curr frame has modified work

        root.destroy()
    
    
    def handle_input(self):
        while True:
            try:
                # something to iterate through all lines, if the sleep stuff is there at the bottom of the function
                line = sys.stdin.readline()
                
                if line:
                    line = line.strip()

                    try:
                        data = json.loads(line)
                        type = data.get("type")
                        value = data.get("value")
                        header_text = data.get("header_text")
                        info_text = data.get("info_text")
                        
                        match type:
                            case "generate_pose_data": # could theoretically do this stuff when a generate button is pressed, but this acts as a sort of acknowledgement, i think?
                                self.frames["LayerSelect"].generate_began()
                                self.update_progress(0, "", "Initializing...")
                            case "generate_layer_image":
                                pass
                            case "generate_all_layer_images":
                                pass
                            case "generate_sheet_image":
                                pass
                            case "generate_updated_pose_images":
                                pass
                            case "update":
                                if self.winfo_toplevel().focus_get() != None:
                                    self.update_progress(value, header_text, info_text)
                            case "error":
                                self.frames["LayerSelect"].generate_ended()
                                self.update_progress(0, "", "Error")
                                messagebox.showerror("Error", line)
                            case "done":
                                self.frames["LayerSelect"].generate_ended()
                                self.update_progress(value, header_text, info_text)
                                messagebox.showinfo(header_text, info_text)
                            case "cancel":
                                self.frames["LayerSelect"].generate_ended()
                                self.update_progress(None, "", "Cancelled")
                            # case _:
                            #     print(line, flush=True)
                    except json.JSONDecodeError:
                        print(json.dumps({"type": "error", "val": ("Malformed output to generate stdin:", line)}), flush=True)
                        
            except Exception as e:
                print(json.dumps({"type": "error", "val": f"Exception in gui handle_input: {e}\nLine that caused exception: {line}"}), flush=True)

def main():
    root = tk.Tk()
    app = ConsistxelsApp(root)
    app.pack(fill="both", expand=True)

    root.protocol("WM_DELETE_WINDOW", lambda r=root: app.on_close(r))

    root.mainloop()

# run main
if __name__ == "__main__":
    main()