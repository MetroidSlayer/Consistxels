# import json
import os
# import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import scripts.gui.gui_shared as gui_shared
from scripts.gui.gui_shared import add_widget
from scripts.classes.tooltip import ToolTip
# from scripts.shared import consistxels_version

class Menu_EditSheetData(tk.Frame):
    def __init__(self, master, change_menu_callback, load_path = None): # TODO change load to only accept sheetdata_generated json type
        super().__init__(master) # Initialize menu's tkinter widget

        self.json_path = load_path
        self.input_folder_path = None # Input folder path must be stored so images can be loaded later
        self.json_data : dict = None
        
        self.configure(bg=gui_shared.bg_color) # Change bg color
        self.after(0, self.setup_ui, change_menu_callback, load_path) # .setup_ui() in .after() to prevent ugly flickering

    def setup_ui(self, change_menu_callback, load_path = None):

        # Header
        # TODO: AT SOME POINT, make header and other common stuff part of a common menu class that the specific menus can inherit from
        self.header = tk.Frame(self, bg=gui_shared.bg_color)
        self.header.pack(fill="x", padx=2)

        # Header left:
        
        # Load button
        self.load_button = tk.Button(self.header, text="📁 Load", bg=gui_shared.button_bg, fg=gui_shared.fg_color, command=self.load_json)
        self.load_button.pack(padx=(12,10), pady=10, side="left")
        ToolTip(self.load_button, "Load a .json file containing sprite sheet data. Must be located in the same folder as its pose images.")

        # Header right:

        # Back button
        self.back_button = tk.Button(self.header, text="Back to Main Menu", bg=gui_shared.button_bg, fg=gui_shared.fg_color, command=lambda: change_menu_callback("Main"))
        self.back_button.pack(side="right", padx=10, pady=10)
        ToolTip(self.back_button, "...Come on, this one is self explanatory.", False, True, 2000)

        # Main contents:

        # Main frame
        self.main_frame = tk.Frame(self, bg=gui_shared.bg_color)
        self.main_frame.pack(fill="both", expand=True)

        # Menus inside paned window so they can be resized
        main_paned_window = tk.PanedWindow(self.main_frame, bg=gui_shared.bg_color, opaqueresize=False, sashrelief="flat", sashwidth=16, bd=0)
        main_paned_window.pack(fill="both", expand=True)

        # Left frame
        self.main_left_frame = tk.Frame(main_paned_window, bg=gui_shared.bg_color, highlightthickness=1, highlightbackground=gui_shared.secondary_fg)
        self.main_left_frame.pack(side="left", fill="y", padx=10)
        self.main_left_frame.pack_propagate(False)

        # Right frame
        self.main_right_frame = tk.Frame(main_paned_window, bg=gui_shared.bg_color, highlightthickness=1, highlightbackground=gui_shared.secondary_fg)
        self.main_right_frame.pack(side="right", fill="y", padx=10)
        self.main_right_frame.pack_propagate(False)

        # Add menus to paned window, define behavior
        main_paned_window.add(self.main_left_frame, minsize=400, stretch="never")
        main_paned_window.add(self.main_right_frame, minsize=400, stretch="always")

        # Left frame:

        left_paned_window = tk.PanedWindow(self.main_left_frame, bg=gui_shared.bg_color, opaqueresize=False, sashrelief="flat", sashwidth=16, bd=0)
        left_paned_window.pack(fill="both", expand=True)

        # Layer list:

        # layer scrollable frame
        self.layer_canvas_frame = tk.Frame(self.main_left_frame, bg=gui_shared.bg_color, highlightthickness=1, highlightbackground=gui_shared.secondary_fg)
        self.layer_canvas_frame.pack(fill="both", expand=True) # grid instead? WAIT no these need to be panedwindow

        self.layer_canvas = tk.Canvas(self.layer_canvas_frame, bg=gui_shared.bg_color, highlightthickness=0, width=0)
        # self.layer_scrollbar
        # self.layer_scrollable_frame

        # layer list frame
        # layer list entry frames

        # Pose list:

        # input box for search
        # search button
        # info popup button

        # pose scrollable frame
        # pose list frame
        # pose list entry frames

        if load_path: self.load_json(load_path)
    
    def load_json(self, load_path):
        if not load_path:
            pass
        if load_path:
            pass