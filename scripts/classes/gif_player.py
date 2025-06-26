import tkinter as tk
from PIL import Image, ImageSequence, ImageTk

# A widget inheriting from tk.Label made to play .gif files
class GifPlayer(tk.Label):
    def __init__(self, master, gif_path, loop=True, initial_delay=0, scale=None, resampling = Image.Resampling.LANCZOS, *args, **kwargs):
        
        # Initialize tkinter stuff
        super().__init__(master, *args, **kwargs)

        # Set vars
        self.gif = Image.open(gif_path)
        self.loop = loop
        self.scale = scale
        self.resampling = resampling

        # Prepare frames
        self.frames, self.delays = self._load_frames_and_delays()
        self.frame_index = 0

        # Start animation, with initial delay
        self.animate(initial_delay)

    # Load frame and timing data from .gif file
    def _load_frames_and_delays(self):
        frames = []
        delays = []
        
        for frame in ImageSequence.Iterator(self.gif):
            img = frame.convert("RGBA")
            
            # Resize, based on chosen scale and resampling
            if self.scale:
                img = img.resize((img.size[0] * self.scale, img.size[1] * self.scale), self.resampling)
            
            frames.append(ImageTk.PhotoImage(img))
            
            delay = frame.info.get("duration", 100) # Frame-specific delay (default to 100ms if missing or 0)
            delays.append(max(1, delay))  # Prevent 0ms delays
        
        return frames, delays

    # Animate by changing current image
    def animate(self, added_delay = 0):
        self.config(image=self.frames[self.frame_index]) # Change frame image
        delay = self.delays[self.frame_index] + added_delay # Get delay before next frame, plus any additional desired delay

        if self.loop or (self.frame_index + 1 < len(self.frames)): # Stop from running again if not looping & at end of animation
            self.frame_index = (self.frame_index + 1) % len(self.frames) # Update frame index
            self.after(delay, self.animate) # Run again
        