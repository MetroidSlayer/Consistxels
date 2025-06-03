import tkinter as tk
# from tooltip import ToolTip

# debug
from PIL import Image, ImageChops
from tkinter import filedialog

class Menu_MainMenu(tk.Frame):
    def __init__(self, master, show_frame_callback):
        super().__init__(master)

        self.bg_color = "#2e2e2e"
        self.fg_color = "#ffffff"
        # self.secondary_bg = "#3a3a3a"
        self.button_bg = "#444"

        self.configure(bg=self.bg_color)

        tk.Label(self, text="Main Menu", bg=self.bg_color, fg=self.fg_color).pack()
        tk.Button(self, text="Go to Layer Select", bg=self.button_bg, fg=self.fg_color, command=lambda: show_frame_callback("LayerSelect")).pack()
        tk.Button(self, text="Go to Load Json", bg=self.button_bg, fg=self.fg_color, command=lambda: show_frame_callback("LoadJson")).pack()

        tk.Button(self, text="Verify that Two Images are Identical", bg=self.button_bg, fg=self.fg_color, command=verify_identical).pack()
        tk.Button(self, text="Generate Rotated Images", bg=self.button_bg, fg=self.fg_color, command=generate_rotated_images).pack()

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



