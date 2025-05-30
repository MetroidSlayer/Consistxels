import tkinter as tk

def on_global_click(event):
    widget = event.widget.winfo_containing(event.x_root, event.y_root)
    if widget is None or isinstance(widget, (tk.Frame, tk.Canvas, tk.Label)):
        widget.winfo_toplevel().focus_set()

# might want to add constants for UI colors here???


# bg_color = "#2e2e2e"
# fg_color = "#ffffff"
# secondary_bg = "#3a3a3a"
# button_bg = "#444"