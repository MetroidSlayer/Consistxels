import tkinter as tk
# from tooltip import ToolTip

import gui_shared

# debug
from PIL import Image, ImageChops
from tkinter import filedialog

class Menu_MainMenu(tk.Frame):
    def __init__(self, master, change_menu_callback):
        super().__init__(master)

        # gui_shared.bg_color = "#2e2e2e"
        # gui_shared.fg_color = "#ffffff"
        # # self.secondary_bg = "#3a3a3a"
        # gui_shared.button_bg = "#444"

        self.configure(bg=gui_shared.bg_color)

        tk.Label(self, text="Main Menu", bg=gui_shared.bg_color, fg=gui_shared.fg_color).pack()

        def open_menu_with_path(menu):
            path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("Json File", "*.json")])
            if path:
                change_menu_callback(menu, path)

        tk.Label(self, text="Generate Pose Data:", bg=gui_shared.bg_color, fg=gui_shared.fg_color).pack(pady=(20,0))
        tk.Button(self, text="New", bg=gui_shared.button_bg, fg=gui_shared.fg_color, command=lambda: change_menu_callback("LayerSelect")).pack()
        tk.Button(self, text="Load layer select json", bg=gui_shared.button_bg, fg=gui_shared.fg_color, command=lambda: open_menu_with_path("LayerSelect")).pack()
        
        tk.Label(self, text="Load & Export Spritesheets with Pose Data:", bg=gui_shared.bg_color, fg=gui_shared.fg_color).pack(pady=(20,0))
        # tk.Button(self, text="Go to Load Json", bg=gui_shared.button_bg, fg=gui_shared.fg_color, command=lambda: change_menu_callback("LoadJson")).pack()
        tk.Button(self, text="Load pose data json", bg=gui_shared.button_bg, fg=gui_shared.fg_color, command=lambda: open_menu_with_path("LoadJson")).pack()

        tk.Label(self, text="Other Tools:", bg=gui_shared.bg_color, fg=gui_shared.fg_color).pack(pady=(20,0))
        tk.Button(self, text="Verify that Two Images are Identical", bg=gui_shared.button_bg, fg=gui_shared.fg_color, command=verify_identical).pack()
        tk.Button(self, text="Generate Rotated Images", bg=gui_shared.button_bg, fg=gui_shared.fg_color, command=generate_rotated_images).pack()

        # Generate Pose Data:
        # Create, label, and order a sprite sheet's layers, and decide how the sheet will be searched.
        # Then, generate data on every pose in every layer, so that replacing every instance of a pose is much easier.
        #
        # After generating data, you can edit individual pose images. To see your changes reflected in the sprite sheet,
        # load the accompanying .json file in "Export Sprite Sheets".
        # 
        # If you don't want to edit each image individually, you
        # can generate a sheet with only unique images in "Export Sprite Sheets" - it's more convenient than opening up a
        # bunch of tiny files.
        #
        # New
        # Load .json

        # Export Sprite Sheets:
        # Using data generated in "Generate Pose Data", export 
        # Load .json

        # 

def verify_identical():
    img1_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if img1_path == None: return
    img2_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if img2_path == None: return

    with Image.open(img1_path) as img1, Image.open(img2_path) as img2:
        

        result = img1.tobytes() == img2.tobytes()

        if not result:
            difference = ImageChops.difference(img1, img2)
            result = (difference.getbbox() == None)
            if not result:
                # difference.show()
                difference_path = filedialog.asksaveasfilename(defaultextension=".png")
                try:
                    difference.save(difference_path)
                except:
                    pass

        print(result)
    
def generate_rotated_images():
    path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    with Image.open(path) as img:
        img_rot90_path = filedialog.asksaveasfilename(defaultextension=".png")
        img_rot180_path = filedialog.asksaveasfilename(defaultextension=".png")
        img_rot270_path = filedialog.asksaveasfilename(defaultextension=".png")
        img.transpose(Image.Transpose.ROTATE_90).save(img_rot90_path)
        img.transpose(Image.Transpose.ROTATE_180).save(img_rot180_path)
        img.transpose(Image.Transpose.ROTATE_270).save(img_rot270_path)



