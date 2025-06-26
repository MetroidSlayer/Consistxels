import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(1) # Makes sure window is scaled properly for monitor's resolution

import sys
import json
import threading

import tkinter as tk
from tkinter import messagebox

import gui.gui_shared as gui_shared
from gui.menu_mainmenu import Menu_MainMenu
from gui.menu_layerselect import Menu_LayerSelect
from gui.menu_exportsheet import Menu_ExportSheet
from gui.menu_othertools import Menu_OtherTools

# Class containing GUI
class ConsistxelsApp(tk.Frame):
    def __init__(self, root):
        super().__init__() # Initialize window's tkinter widget
        
        # Set window attributes
        root.title("Consistxels") # Title
        root.geometry("1680x968") # Window size
        root.configure(bg=gui_shared.bg_color) # BG color

        # Main container 
        self.container = tk.Frame(self, bg=gui_shared.bg_color) # TEST! didn't need bg= before? not sure why
        self.container.pack(fill="both", expand=True)

        # Bind widgets to a function that makes Entries change color when focused/unfocused
        root.bind_all("<Button-1>", gui_shared.on_global_click, add="+")

        # Keeps track of whether or not the window is focused, and sends this info to main process. That way, the main process can avoid sending gui updates
        # unless absolutely necessary.
        root.bind("<FocusIn>", self._on_root_focus_in)
        root.bind("<FocusOut>", self._on_root_focus_out)

        # Prepare different menu stuff, change menu to menu_mainmenu
        self.unsaved_changes = False
        self.curr_menu = None
        self.change_menu("Main")

        # Start thread for handling incoming info from main process
        self.handle_input_thread = threading.Thread(target=self.handle_input, daemon=True)
        self.handle_input_thread.start()

    # Change menu
    def change_menu(self, new_menu = "Main", arg = None): # Parameter 'arg' usually (or rather, always, at least for now) refers to a path for the menu to load
        if self.check_quit() != None: # Check that the current menu does not have unsaved changes
            
            self.unsaved_changes = False # Ensure that the new menu is not 
            
            for widget in self.container.winfo_children(): # Destroy current menu entirely
                widget.destroy()
            
            new_menu_widget : tk.Frame = None # TODO test. added ': tk.Frame', don't know if it's gonna cause issues. It SHOULDN'T, but idk how Python works

            match new_menu: # Create new menu widget
                case "Main":
                    new_menu_widget = Menu_MainMenu(self.container, self.change_menu)
                case "LayerSelect":
                    new_menu_widget = Menu_LayerSelect(self.container, self.change_menu, self.set_unsaved_changes, arg)
                case "ExportSheet":
                    new_menu_widget = Menu_ExportSheet(self.container, self.change_menu, arg)
                case "OtherTools":
                    new_menu_widget = Menu_OtherTools(self.container, self.change_menu)
                case _:
                    print("nonexistent menu chosen")
                    raise Exception # I don't know which specific exception to raise 
            
            new_menu_widget.place(relwidth=1, relheight=1) # Place menu
            self.curr_menu = new_menu_widget # Assign class variable

    # Set self.unsaved_changes, so that GUI can properly avoid losing work
    def set_unsaved_changes(self, new_unsaved_changes):
        self.unsaved_changes = new_unsaved_changes

    # True = 'save and quit', False = 'don't save, do quit', None = 'don't save, don't quit'
    def check_quit(self):
        if self.unsaved_changes:
            ans = messagebox.askyesnocancel("Warning! Unsaved changes", "Save changes before closing?")
            if ans:
                if not self.curr_menu.save_changes(): ans = None
            return ans
        return False

    # Update progress in current menu. (Maybe just call this directly? I dunno)
    def update_progress(self, value, header_text, info_text):
        self.curr_menu.update_progress(value, header_text, info_text)

    # Handle closing GUI, asking if want to save, etc.
    def on_close(self, root):
        # ask if want to save if curr frame has modified work
        if self.check_quit() != None:
            root.destroy()
    
    # Handle incoming info, sent from main process through this process's stdin
    # TODO: still need to think of a way for this to not run constantly when the menu's not focused. It works FINE for now, but there's likely still a performance hit, since this is running constantly.
    def handle_input(self):
        while True:
            try:
                # If I put sleep stuff at the bottom of the function, I'll need to add something to read all lines and get to the last one
                line = sys.stdin.readline()
                
                if line:
                    line = line.strip() # Format line

                    try:
                        # Get vars
                        data = json.loads(line)
                        type = data.get("type")
                        value = data.get("value") # Percentage to display in progress bar
                        header_text = data.get("header_text") # Used to show information
                        info_text = data.get("info_text") # Used to show secondary information if there is a header, and primary information if there isn't
                        
                        if type in ["generate_sheet_data", "generate_sheet_image", "generate_layer_images", "generate_external_filetype", "generate_updated_pose_images"]:
                            self.curr_menu.generate_begun() # Format current menu; disable generate button, enable cancel button, etc.
                            self.update_progress(0, "", "Initializing...")
                        else:
                            match type:
                                case "update":
                                    if self.winfo_toplevel().focus_get() != None:
                                        self.update_progress(value, header_text, info_text)
                                case "error":
                                    self.curr_menu.generate_ended()
                                    self.update_progress(0, "", "Error")
                                    messagebox.showerror(header_text, info_text)
                                case "done":
                                    self.curr_menu.generate_ended()
                                    self.update_progress(value, header_text, info_text)
                                    messagebox.showinfo(header_text, info_text)
                                case "cancel":
                                    self.curr_menu.generate_ended()
                                    self.update_progress(None, "", "Cancelled")
                    except json.JSONDecodeError:
                        print(json.dumps({"type": "error", "val": ("Malformed output to generate stdin:", line)}), flush=True)
            except Exception as e:
                print(json.dumps({"type": "error", "val": f"Exception in gui handle_input: {e}\nLine that caused exception: {line}"}), flush=True)
    
    # Inform main process of window focus

    def _on_root_focus_in(self, _event):
        print(json.dumps({"type": "root_focus", "val": True}), flush=True)
    
    def _on_root_focus_out(self, _event):
        print(json.dumps({"type": "root_focus", "val": False}), flush=True)

# Main function for this subprocess
def main():
    # Create window & app interface
    root = tk.Tk()
    app = ConsistxelsApp(root)
    app.pack(fill="both", expand=True)

    root.protocol("WM_DELETE_WINDOW", lambda r=root: app.on_close(r)) # Connect window closing to relevant function

    root.mainloop() # Start main loop

# Run main
# TODO is there some way to make it raise an exception if ran as the main process? idk, maybe if I pass a command line arg, but this isn't a huge deal
if __name__ == "__main__":
    main()