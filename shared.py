import tkinter as tk

def on_global_click(event):
    widget = event.widget.winfo_containing(event.x_root, event.y_root)
    if widget is None or isinstance(widget, (tk.Frame, tk.Canvas, tk.Label)):
        widget.winfo_toplevel().focus_set()