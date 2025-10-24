#!/usr/bin/env python3
"""
WinampGera - A modern music player with neon-green geometric tech theme
"""
import tkinter as tk
from tkinter import filedialog, messagebox
import vlc
import os
import sys


class WinampGera:
    def __init__(self, root):
        self.root = root
        self.root.title("WinampGera Music Player")
        self.root.geometry("600x400")
        self.root.configure(bg="#0a0a0a")
        self.root.resizable(False, False)
        
        # VLC instance and player
        self.vlc_instance = vlc.Instance()
        self.player = self.vlc_instance.media_player_new()
        
        # Current file
        self.current_file = None
        self.is_playing = False
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        """Create the user interface with neon-green geometric theme"""
        # Title Label
        title_label = tk.Label(
            self.root,
            text="WINAMP GERA",
            font=("Courier New", 24, "bold"),
            bg="#0a0a0a",
            fg="#00ff41"
        )
        title_label.pack(pady=20)
        
        # File display frame
        file_frame = tk.Frame(self.root, bg="#1a1a1a", bd=2, relief=tk.RIDGE)
        file_frame.pack(padx=20, pady=10, fill=tk.X)
        
        self.file_label = tk.Label(
            file_frame,
            text="No file loaded",
            font=("Courier New", 10),
            bg="#1a1a1a",
            fg="#00ff41",
            anchor="w",
            padx=10,
            pady=10
        )
        self.file_label.pack(fill=tk.X)
        
        # Control buttons frame
        control_frame = tk.Frame(self.root, bg="#0a0a0a")
        control_frame.pack(pady=20)
        
        # Button style
        button_style = {
            "font": ("Courier New", 12, "bold"),
            "bg": "#1a1a1a",
            "fg": "#00ff41",
            "activebackground": "#00ff41",
            "activeforeground": "#0a0a0a",
            "bd": 2,
            "relief": tk.RAISED,
            "width": 10,
            "height": 2,
            "cursor": "hand2"
        }
        
        # Open file button
        self.open_btn = tk.Button(
            control_frame,
            text="OPEN",
            command=self.open_file,
            **button_style
        )
        self.open_btn.grid(row=0, column=0, padx=5)
        
        # Play button
        self.play_btn = tk.Button(
            control_frame,
            text="PLAY",
            command=self.play_pause,
            **button_style
        )
        self.play_btn.grid(row=0, column=1, padx=5)
        
        # Stop button
        self.stop_btn = tk.Button(
            control_frame,
            text="STOP",
            command=self.stop,
            **button_style
        )
        self.stop_btn.grid(row=0, column=2, padx=5)
        
        # Volume frame
        volume_frame = tk.Frame(self.root, bg="#0a0a0a")
        volume_frame.pack(pady=20, padx=40, fill=tk.X)
        
        volume_label = tk.Label(
            volume_frame,
            text="VOLUME",
            font=("Courier New", 10, "bold"),
            bg="#0a0a0a",
            fg="#00ff41"
        )
        volume_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Volume slider
        self.volume_slider = tk.Scale(
            volume_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            command=self.change_volume,
            bg="#1a1a1a",
            fg="#00ff41",
            troughcolor="#0a0a0a",
            activebackground="#00ff41",
            highlightbackground="#0a0a0a",
            bd=2,
            relief=tk.RIDGE,
            length=300,
            width=20,
            sliderlength=30,
            sliderrelief=tk.RAISED
        )
        self.volume_slider.set(70)
        self.volume_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Status bar
        status_frame = tk.Frame(self.root, bg="#1a1a1a", bd=2, relief=tk.RIDGE)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = tk.Label(
            status_frame,
            text="Ready | Supports: MP3, WAV, FLAC",
            font=("Courier New", 8),
            bg="#1a1a1a",
            fg="#00ff41",
            anchor="w",
            padx=10,
            pady=5
        )
        self.status_label.pack(fill=tk.X)
        
        # Geometric decorative elements
        canvas = tk.Canvas(self.root, width=600, height=50, bg="#0a0a0a", highlightthickness=0)
        canvas.pack(pady=10)
        
        # Draw geometric shapes
        for i in range(0, 600, 60):
            canvas.create_line(i, 25, i+30, 25, fill="#00ff41", width=2)
            canvas.create_rectangle(i+35, 20, i+45, 30, outline="#00ff41", width=2)
            
    def open_file(self):
        """Open file dialog to select audio file"""
        filetypes = (
            ('Audio Files', '*.mp3 *.wav *.flac'),
            ('MP3 Files', '*.mp3'),
            ('WAV Files', '*.wav'),
            ('FLAC Files', '*.flac'),
            ('All Files', '*.*')
        )
        
        filename = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=filetypes
        )
        
        if filename:
            self.current_file = filename
            self.load_file(filename)
            
    def load_file(self, filename):
        """Load audio file into VLC player"""
        try:
            media = self.vlc_instance.media_new(filename)
            self.player.set_media(media)
            
            # Update UI
            basename = os.path.basename(filename)
            self.file_label.config(text=f"Loaded: {basename}")
            self.status_label.config(text=f"Ready to play: {basename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")
            
    def play_pause(self):
        """Toggle play/pause"""
        if not self.current_file:
            messagebox.showwarning("No File", "Please open an audio file first")
            return
            
        if self.is_playing:
            self.player.pause()
            self.play_btn.config(text="PLAY")
            self.status_label.config(text="Paused")
            self.is_playing = False
        else:
            self.player.play()
            self.play_btn.config(text="PAUSE")
            basename = os.path.basename(self.current_file)
            self.status_label.config(text=f"Playing: {basename}")
            self.is_playing = True
            
    def stop(self):
        """Stop playback"""
        self.player.stop()
        self.play_btn.config(text="PLAY")
        self.is_playing = False
        if self.current_file:
            basename = os.path.basename(self.current_file)
            self.status_label.config(text=f"Stopped: {basename}")
        else:
            self.status_label.config(text="Ready | Supports: MP3, WAV, FLAC")
            
    def change_volume(self, value):
        """Change volume level"""
        volume = int(float(value))
        self.player.audio_set_volume(volume)
        
    def on_closing(self):
        """Cleanup when closing the application"""
        self.player.stop()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = WinampGera(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
