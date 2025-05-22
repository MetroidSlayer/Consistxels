import os
import tkinter as tk
from tkinter import filedialog, colorchooser
# from PIL import Image, ImageTk, ImageOps
from PIL import Image, ImageTk
from generate import GenerateJSON
from tooltip import ToolTip

class Menu_LayerSelect(tk.Frame):
    def __init__(self, master, show_frame_callback):
        super().__init__(master)

        # self.root = root
        # self.root.title("Consistxels: Layer Selection")

        self.bg_color = "#2e2e2e"
        self.fg_color = "#ffffff"
        self.secondary_bg = "#3a3a3a"
        self.button_bg = "#444"
        # self.button_fg = "#fff"

        # Track images and border
        self.image_data = []  # List of dicts: {path, name, thumbnail, img_obj}
        self.border_image = None
        self.border_path = None
        self.border_color = "#00007f"

        # self.root.configure(bg=self.bg_color)
        self.configure(bg=self.bg_color)

        self.setup_ui(show_frame_callback)

    def setup_ui(self, show_frame_callback):

        # Top frame for controls
        # self.top_frame = tk.Frame(self.root, bg=self.bg_color)
        self.top_frame = tk.Frame(self, bg=self.bg_color)
        self.top_frame.pack(fill="x", padx=10, pady=5)

        add_images_button = tk.Button(self.top_frame, text="Add Images", command=self.add_images, bg=self.button_bg, fg=self.fg_color)
        add_images_button.pack(side="left", padx=5)
        ToolTip(add_images_button, "Add one more more images.")

        choose_border_button = tk.Button(self.top_frame, text="Choose Border", command=self.add_border, bg=self.button_bg, fg=self.fg_color)
        choose_border_button.pack(side="left", padx=5)
        ToolTip(choose_border_button, "Choose an image file containing the borders of the sprites' poses. This will be searched in order to find the poses and generate the data.")

        self.border_label = tk.Label(self.top_frame, text="No border selected", bg=self.bg_color, fg=self.fg_color)
        self.border_label.pack(side="left", padx=5)

        tk.Label(self.top_frame, text="Border Color:", bg=self.bg_color, fg=self.fg_color).pack(side="left", padx=(20, 5))
        # self.color_entry = tk.Entry(self.top_frame, width=10)
        # self.color_entry.insert(0, self.border_color)
        # self.color_entry.pack(side="left")

        # TODO: replace with hex entry, because this color picker doesn't seem to have one
        self.border_color_swatch = tk.Canvas(self.top_frame, width=20, height=20, bg=self.border_color,
        highlightthickness=1, highlightbackground="black")
        self.border_color_swatch.pack(side="left", padx=5)

        pick_border_color_button = tk.Button(self.top_frame, text="Pick Border Color", command=self.pick_color, bg=self.button_bg, fg=self.fg_color)
        pick_border_color_button.pack(side="left", padx=5)
        ToolTip(pick_border_color_button, "Pick the color that will be interpreted as the border.")

        back_button = tk.Button(self.top_frame, text="Back to Main Menu", bg=self.button_bg, fg=self.fg_color, command=lambda: show_frame_callback("Main"))
        back_button.pack(side="right", padx=5)
        ToolTip(back_button, "...Come on, this one is self explanatory.", False, True, 2000)

        # Main frame split left/right
        # self.main_frame = tk.Frame(self.root, bg=self.bg_color)
        self.main_frame = tk.Frame(self, bg=self.bg_color)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=(0, 5))

        # Left scrollable frame for image entries
        self.left_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.left_frame.pack(side="left", fill="y", padx=(5, 10))

        self.canvas = tk.Canvas(self.left_frame, width=400, bg=self.bg_color, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.left_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.bg_color)

        self.scrollable_frame.bind(
            "<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="y")
        self.scrollbar.pack(side="right", fill="y")

        # Mousewheel scrolling
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

        # Right canvas for preview
        self.preview_canvas = tk.Canvas(self.main_frame, width=400, height=400, bg="#222222")
        # self.preview_canvas.bind("<Configure>", self.update_preview)

        self.preview_canvas.pack(side="left", fill="both", expand=True)
        ToolTip(self.preview_canvas, '''A preview image of all the layers you've added, in order.''')

        # Footer frame
        # self.footer = tk.Frame(self.root, bg=self.bg_color)
        self.footer = tk.Frame(self, bg=self.bg_color)
        self.footer.pack(fill="x", pady=5)
        self.footer.pack_propagate(True)

        self.update_preview_button = tk.Button(self.footer, text="Update Preview", command=self.update_preview, bg=self.button_bg, fg=self.fg_color)
        self.update_preview_button.pack(side="left", padx=5, pady=5)
        ToolTip(self.update_preview_button, "Update the preview image that contains all layers ordered as shown. (May take a while if you have a lot of images)\n\nIf the button is yellow, changes have been made, and the preview can be updated.", True)

        self.generate_button = tk.Button(self.footer, text="Generate JSON", command=self.generate_output, bg=self.button_bg, fg=self.fg_color)
        self.generate_button.pack(side="left", padx=5, pady=5)
        ToolTip(self.generate_button, "Generate JSON data! (May take a while)", True)

        # tk.Button(self.footer, text="Zoom In", command=lambda: self.change_zoom(1.1)).pack(side="right", padx=5)
        # tk.Button(self.footer, text="Zoom Out", command=lambda: self.change_zoom(0.9)).pack(side="right")

        # self.zoom_level = 1.0

    def on_mousewheel(self, event):
        delta = -1 * (event.delta // 120)
        self.canvas.yview_scroll(delta, "units")

    def pick_color(self):
        color = colorchooser.askcolor(title="Pick Background Color")[1]
        if color:
            # self.color_entry.delete(0, tk.END)
            # self.color_entry.insert(0, color)

            # self.border_color_

            # self.update_colors(color)
            self.update_border_color(color)

    def update_border_color(self, color):
        self.border_color = color
        self.border_color_swatch.configure(bg=color)

    def add_images(self):
        paths = filedialog.askopenfilenames(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        for path in paths:
            filename = os.path.basename(path)
            name = os.path.splitext(filename)[0]
            image = Image.open(path)
            thumb = image.copy()
            thumb.thumbnail((64, 64))
            photo = ImageTk.PhotoImage(thumb)
            self.image_data.append({"path": path, "name": name, "img": image, "thumb": photo})
        self.redraw_image_entries()
        # self.update_preview()
        self.update_preview_button.configure(bg="#ffff00", fg="#000000")

    def add_border(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if path:
            self.border_image = Image.open(path)
            self.border_path = path
            self.border_label.config(text=os.path.basename(path))
            # self.update_preview()
            self.update_preview_button.configure(bg="#ffff00", fg="#000000")

    def move_image(self, index, direction):
        new_index = index + direction
        if 0 <= new_index < len(self.image_data):
            self.image_data[index], self.image_data[new_index] = self.image_data[new_index], self.image_data[index]
            self.redraw_image_entries()
            # self.update_preview()
            self.update_preview_button.configure(bg="#ffff00", fg="#000000")

    def delete_image(self, index):
        del self.image_data[index]
        self.redraw_image_entries()
        # self.update_preview()
        self.update_preview_button.configure(bg="#ffff00", fg="#000000")

    def redraw_image_entries(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for i, data in enumerate(self.image_data):
            frame = tk.Frame(
                self.scrollable_frame,
                bg=self.secondary_bg,
                relief=tk.RIDGE,
                bd=2,
                padx=5,
                pady=5
            )

            frame.pack(fill="x", anchor="w", pady=2, padx=(10, 0))
            # frame.pack_propagate(True)

            tk.Label(frame, text=f"Layer {i+1}", bg=self.secondary_bg, fg=self.fg_color).grid(row=0, column=1, sticky="w")

            img_label = tk.Label(frame, image=data["thumb"], bg=self.secondary_bg)
            img_label.grid(row=0, column=0, rowspan=2, padx=5)

            tk.Label(frame, text="Name:", bg=self.secondary_bg, fg=self.fg_color).grid(row=1, column=1, sticky="e")
            name_entry = tk.Entry(frame, width=15)
            name_entry.insert(0, data["name"])
            name_entry.grid(row=1, column=2, sticky="w")

            def save_name(e, entry=data, entry_widget=name_entry):
                entry["name"] = entry_widget.get()

            name_entry.bind("<FocusOut>", save_name)

            x_button = tk.Button(frame, text="X", fg="red", command=lambda idx=i: self.delete_image(idx), bg=self.secondary_bg)
            x_button.grid(row=0, column=3, rowspan=2, padx=5)
            ToolTip(x_button, f"Delete layer {i+1}")

            up_button = tk.Button(frame, text="↑", command=lambda idx=i: self.move_image(idx, -1), bg=self.secondary_bg, fg=self.fg_color)
            up_button.grid(row=0, column=4)
            ToolTip(up_button, f"Reorder layer {i+1} upwards")

            down_button = tk.Button(frame, text="↓", command=lambda idx=i: self.move_image(idx, 1), bg=self.secondary_bg, fg=self.fg_color)
            down_button.grid(row=1, column=4, padx=5)
            ToolTip(down_button, f"Reorder layer {i+1} downwards")

    def update_preview(self):
        self.update_preview_button.configure(bg=self.button_bg, fg=self.fg_color)

        width = self.preview_canvas.winfo_width()
        height = self.preview_canvas.winfo_height()
        composite = Image.new("RGBA", (width, height), (0, 0, 0, 0))

        def paste_center(base, img):
            img_ratio = min(width / img.width, height / img.height)
            new_size = (int(img.width * img_ratio), int(img.height * img_ratio))
            
            # zoomed_size = (int(img.width * self.zoom_level), int(img.height * self.zoom_level))
            # resized = img.resize(zoomed_size, Image.Resampling.LANCZOS)

            resized = img.resize(new_size, Image.Resampling.LANCZOS)

            offset = ((width - new_size[0]) // 2, (height - new_size[1]) // 2)
            base.paste(resized, offset, resized if resized.mode == 'RGBA' else None)

        if self.border_image:
            paste_center(composite, self.border_image)
        for item in reversed(self.image_data):
            paste_center(composite, item["img"])

        self.preview_image = ImageTk.PhotoImage(composite)
        self.preview_canvas.delete("all")
        self.preview_canvas.create_image(width // 2, height // 2, image=self.preview_image)

    # def change_zoom(self, factor):
    #     self.zoom_level *= factor
    #     self.update_preview()

    def generate_output(self):
        # border image
        # border color
        # image info list:
        # - image
        # - name

        image_info = []
        for data in self.image_data:
            image_info.append({"path": data["path"], "name": data["name"]})
        
        GenerateJSON(self.border_path, self.border_color, image_info)