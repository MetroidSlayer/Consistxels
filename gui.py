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

import sys
import json
from tkinter import messagebox
import threading


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

        self.handle_input_thread = threading.Thread(target=self.handle_input, daemon=True)
        self.handle_input_thread.start()

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()

    def update_progress(self, value, header_text, info_text):
        self.frames["LayerSelect"].update_progress(value, header_text, info_text)

    # def generate_begin(self):
        

    def on_close(self, root):
        # ask if want to save if curr frame has modified work

        # self.frames["LayerSelect"].cancel_process(True)

        root.destroy()
    
    
    def handle_input(self):
        # print(json.dumps({"type": "print", "val": "gothere"}), flush=True)
        while True:
            try:
                line = sys.stdin.readline()
                
                # print(json.dumps({"type": "print", "val": line}), flush=True)
                if line:
                    # print(json.dumps({"type": "print", "val": "gothere2"}), flush=True)
                    line = line.strip()
                    # print(json.dumps({"type": "print", "val": "gothere3"}), flush=True)

                    try:
                        # print(json.dumps({"type": "print", "val": "gothere4"}), flush=True)
                        data = json.loads(line)
                        type = data.get("type")
                        value = data.get("value")
                        header_text = data.get("header_text")
                        info_text = data.get("info_text")
                        # print(json.dumps({"type": "print", "val": "gothere5"}), flush=True)

                        # print(line)                
                        match type:
                            case "generate":
                                # print(json.dumps({"type": "print", "val": "gothere6"}), flush=True)
                                self.frames["LayerSelect"].generate_begin()
                                # print(json.dumps({"type": "print", "val": "gothere7"}), flush=True)
                                self.update_progress(0, "", "Initializing...")
                                # print(json.dumps({"type": "print", "val": "gothere8"}), flush=True)
                            case "update":
                                if self.winfo_toplevel().focus_get() != None:
                                    self.update_progress(value, header_text, info_text)
                            case "error":
                                self.frames["LayerSelect"].generate_end()
                                self.update_progress(0, "", "Error")
                                messagebox.showerror("Error", line)
                                # return
                            case "done":
                                self.frames["LayerSelect"].generate_end()
                                self.update_progress(value, header_text, info_text)
                                messagebox.showinfo(header_text, info_text)
                                # self.update_progress(0, "", "Initializing...")
                                # return
                            # case _:
                            #     print(line, flush=True)
                    except json.JSONDecodeError:
                        # print(("Malformed output to generate stdin:", line), flush=True)
                        print(json.dumps({"type": "error", "val": ("Malformed output to generate stdin:", line)}), flush=True)
                        
            except Exception as e:
                print(json.dumps({"type": "error", "val": f"Exception in gui handle_input: {e}\nLine that caused exception: {line}"}), flush=True)
                # break



        # # print(json.dumps({"type": "print", "val": "gothere"}), flush=True)
        # for line in sys.stdin:
        #     # print(json.dumps({"type": "print", "val": "gothere2"}), flush=True)
        #     # print(json.dumps({"type": "print", "val": line}), flush=True)
        #     line = line.strip()
        #     # print(json.dumps({"type": "print", "val": line}), flush=True)
        #     # print(json.dumps({"type": "print", "val": ""}), flush=True)

        #     try:

        #         data = json.loads(line)
        #         type = data.get("type")
        #         value = data.get("value")
        #         header_text = data.get("header_text")
        #         info_text = data.get("info_text")

        #         # print(line)                
        #         match type:
        #             case "generate":
        #                 self.frames[1].generate_begin()
        #                 self.update_progress(0, "", "Initializing...")
        #             case "update":
        #                 self.update_progress(value, header_text, info_text)
        #             case "error":
        #                 self.frames[1].generate_end()
        #                 messagebox.showerror("Error", line)
        #                 return
        #             case "done":
        #                 self.frames[1].generate_end()
        #                 messagebox.showinfo(header_text, info_text)
        #                 return
        #             case _:
        #                 print(line, flush=True)
        #     except json.JSONDecodeError:
        #         # print(("Malformed output to generate stdin:", line), flush=True)
        #         print(json.dumps({"type": "error", "val": ("Malformed output to generate stdin:", line)}), flush=True)

def main():
    root = tk.Tk()
    app = ConsistxelsApp(root)
    app.pack(fill="both", expand=True)

    root.protocol("WM_DELETE_WINDOW", lambda r=root: app.on_close(r))

    root.mainloop()

# run main
if __name__ == "__main__":
    main()