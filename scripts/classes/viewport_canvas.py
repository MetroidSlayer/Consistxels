import tkinter as tk
from PIL import Image, ImageTk

# A modified Canvas that supports panning with the mouse and zooming with the mousewheel.
# Attempts to make this light performance-wise by only upscaling the visible portion of the image.
class ViewportCanvas(tk.Canvas):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)#, cursor="hand2"

        # For displaying the image
        self.full_image = None
        self._tk_image = None
        self._image_id = None

        # Zoom/position vals
        self.zoom = 1.0
        self.min_zoom = 0.25
        self.max_zoom = 10.0
        self.offset_x = 0.0  # in image-space units
        self.offset_y = 0.0

        # Mouse events
        self.bind("<MouseWheel>", self._on_mousewheel)
        self.bind("<ButtonPress-1>", self._start_pan)
        self.bind("<B1-Motion>", self._do_pan)
        self.bind("<Configure>", lambda e: self.redraw())

        self._pan_start = None

    # Set the image. If none, clear current image.
    def set_image(self, pil_image = None):
        if pil_image: self.full_image = pil_image.convert("RGBA")
        else: self.full_image = None

        # Maybe check if image is a diff size and only change zoom/offset if so? idk
        self.zoom = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.redraw()

    # Runs upon mousewheel input, and zooms
    def _on_mousewheel(self, event):
        factor = 1.1 if event.delta > 0 else 1 / 1.1
        self.zoom_at(factor, event.x, event.y)

    # Runs upon mouse click; stores initial mouse position
    def _start_pan(self, event):
        self._pan_start = (event.x, event.y)

    # By looking at both the initial mouse position, as set above, and the amount of dragging being done by the mouse, modify position
    def _do_pan(self, event):
        if self._pan_start:
            dx = (event.x - self._pan_start[0]) / self.zoom
            dy = (event.y - self._pan_start[1]) / self.zoom
            self.offset_x -= dx
            self.offset_y -= dy
            self._pan_start = (event.x, event.y)
            self.redraw()

    # Zoom in, and do so relative to the mouse position
    def zoom_at(self, factor, canvas_x, canvas_y):
        if not self.full_image:
            return

        image_x = self.offset_x + canvas_x / self.zoom
        image_y = self.offset_y + canvas_y / self.zoom

        new_zoom = max(self.min_zoom, min(self.zoom * factor, self.max_zoom))
        if new_zoom == self.zoom:
            return

        self.zoom = new_zoom
        self.offset_x = image_x - canvas_x / self.zoom
        self.offset_y = image_y - canvas_y / self.zoom
        self.redraw()

    # Redraw the stored image
    def redraw(self):
        if not self.full_image:
            # print(self.cget('cursor'))
            # self.config(cursor="")
            # self.config(cursor=None)
            # self.config(cursor="arrow")
            # TODO: make cursor revert to normal if no image is drawn. (none of the above methods work)
            return
        
        self.config(cursor="hand2") # Set cursor. (Now that I think about it, could probably go in set_image(), huh)

        # Get the canvas's total size
        canvas_w = self.winfo_width()
        canvas_h = self.winfo_height()

        # Get the image's size
        img_w, img_h = self.full_image.size

        # Get the amount of the image that will be visible given the current zoom
        view_w = canvas_w / self.zoom
        view_h = canvas_h / self.zoom

        # Clamp the offsets based on how much of the image is visible
        self.offset_x = max(0, min(self.offset_x, img_w - view_w))
        self.offset_y = max(0, min(self.offset_y, img_h - view_h))

        # Find the edges of the view
        x0 = int(self.offset_x)
        y0 = int(self.offset_y)
        x1 = int(min(img_w, self.offset_x + view_w)) + (1 if view_w < img_w else 0) # 1 is added if zoomed in enough that the whole img isn't visible, to prevent
        y1 = int(min(img_h, self.offset_y + view_h)) + (1 if view_h < img_h else 0) # the right/bottom edges of the visible portion from being noticeably cut off

        if x1 <= x0 or y1 <= y0: # i.e. if the edges are really messed up
            return

        region = self.full_image.crop((x0, y0, x1, y1)) # The actual image inside the visible portion
        scaled = region.resize( # Resize the visible image according to the zoom
            (int((x1 - x0) * self.zoom), int((y1 - y0) * self.zoom)),
            Image.Resampling.NEAREST
        )
        self._tk_image = ImageTk.PhotoImage(scaled) # Set the stored ImageTk.PhotoImage for display

        if self._image_id is None: # Create or replace the image
            self._image_id = self.create_image(0, 0, image=self._tk_image, anchor="nw")
        else:
            self.itemconfig(self._image_id, image=self._tk_image)

        # Determine draw position
        draw_x = 0
        draw_y = 0
        disp_w = img_w * self.zoom
        disp_h = img_h * self.zoom

        if disp_w < canvas_w:
            draw_x = (canvas_w - disp_w) // 2
        else:
            draw_x = -int((self.offset_x % 1) * self.zoom)

        if disp_h < canvas_h:
            draw_y = (canvas_h - disp_h) // 2
        else:
            draw_y = -int((self.offset_y % 1) * self.zoom)

        self.coords(self._image_id, draw_x, draw_y)
        
        if self._x_scroll: # Not perfect; dragging the scrollbar leads to weird, unintuitive results. Realistically, scrollbar size should only be modified if a zoom happens, not if any scrolling happens, right?
            img_w = self.full_image.width
            view_w = self.winfo_width() / self.zoom
            
            lo = self.offset_x / img_w
            hi = min(1.0, lo + view_w / img_w)

            self._x_scroll.set(lo, hi)

        if self._y_scroll:
            img_h = self.full_image.height
            view_h = self.winfo_height() / self.zoom

            lo = self.offset_y / img_h
            hi = min(1.0, lo + view_h / img_h)

            self._y_scroll.set(lo, hi)

    # At the top of ViewportCanvas class
    def connect_scrollbars(self, x_scrollbar=None, y_scrollbar=None):
        self._x_scroll = x_scrollbar
        self._y_scroll = y_scrollbar
        if x_scrollbar:
            self.config(xscrollcommand=self._on_xscroll)
        if y_scrollbar:
            self.config(yscrollcommand=self._on_yscroll)

    # Scrollbar callbacks: update scrollbar positions
    def _on_xscroll(self, *args):
        if self._x_scroll:
            self._x_scroll.set(*args)

    def _on_yscroll(self, *args):
        if self._y_scroll:
            self._y_scroll.set(*args)

    # Called by scrollbars to move viewport
    def scroll_x(self, *args):
        if self.full_image:
            canvas_w = self.winfo_width()
            view_w = canvas_w / self.zoom
            img_w = self.full_image.width

            lo = float(args[1]) if args[0] == 'moveto' else None
            if args[0] == 'moveto' and lo is not None:
                self.offset_x = lo * (img_w - view_w)
            elif args[0] == 'scroll':
                units = int(args[1])
                self.offset_x += units * view_w * 0.1

            self.redraw()

    # Same as above
    def scroll_y(self, *args):
        if self.full_image:
            canvas_h = self.winfo_height()
            view_h = canvas_h / self.zoom
            img_h = self.full_image.height
            lo = float(args[1]) if args[0] == 'moveto' else None
            if args[0] == 'moveto' and lo is not None:
                self.offset_y = lo * (img_h - view_h)
            elif args[0] == 'scroll':
                units = int(args[1])
                self.offset_y += units * view_h * 0.1

            self.redraw()

