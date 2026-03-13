#!/usr/bin/env python3
"""Minimal desktop audio player scaffold for tkinter + python-vlc apps."""

from __future__ import annotations

import os

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox
except ImportError:
    tk = None
    filedialog = None
    messagebox = None

try:
    import vlc
except ImportError:
    vlc = None

SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".flac"}


class SimpleAudioPlayer:
    def __init__(self, root: "tk.Tk") -> None:
        if vlc is None:
            raise RuntimeError("python-vlc is required to run this player.")

        self.root = root
        self.root.title("Simple Audio Player")
        self.root.geometry("520x240")
        self.root.configure(bg="#111111")

        self.vlc_instance = None
        self.player = None
        self.current_file = None
        self.is_playing = False
        self.pending_volume = 70
        self._volume_job = None

        self._build_ui()

    def _build_ui(self) -> None:
        title = tk.Label(
            self.root,
            text="Simple Audio Player",
            font=("Helvetica", 18, "bold"),
            bg="#111111",
            fg="#f5f5f5",
        )
        title.pack(pady=(16, 10))

        self.file_label = tk.Label(
            self.root,
            text="No file loaded",
            anchor="w",
            bg="#222222",
            fg="#f5f5f5",
            padx=10,
            pady=10,
        )
        self.file_label.pack(fill=tk.X, padx=16)

        controls = tk.Frame(self.root, bg="#111111")
        controls.pack(pady=16)

        self.open_btn = tk.Button(controls, text="Open", width=10, command=self.open_file)
        self.open_btn.grid(row=0, column=0, padx=4)

        self.play_btn = tk.Button(controls, text="Play", width=10, command=self.play_pause)
        self.play_btn.grid(row=0, column=1, padx=4)

        self.stop_btn = tk.Button(controls, text="Stop", width=10, command=self.stop)
        self.stop_btn.grid(row=0, column=2, padx=4)

        volume_row = tk.Frame(self.root, bg="#111111")
        volume_row.pack(fill=tk.X, padx=16, pady=(0, 12))

        tk.Label(volume_row, text="Volume", bg="#111111", fg="#f5f5f5").pack(side=tk.LEFT)
        self.volume_slider = tk.Scale(
            volume_row,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            command=self.change_volume,
            length=280,
        )
        self.volume_slider.set(self.pending_volume)
        self.volume_slider.pack(side=tk.LEFT, padx=(10, 0), fill=tk.X, expand=True)
        self.volume_slider.bind("<ButtonRelease-1>", self.flush_volume_change)

        self.status_label = tk.Label(
            self.root,
            text="Ready | Supports: MP3, WAV, FLAC",
            anchor="w",
            bg="#222222",
            fg="#f5f5f5",
            padx=10,
            pady=8,
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def _ensure_player(self):
        if self.player is not None:
            return self.player

        self.vlc_instance = vlc.Instance()
        self.player = self.vlc_instance.media_player_new()
        self.player.audio_set_volume(self.pending_volume)
        return self.player

    def open_file(self) -> None:
        filename = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=(
                ("Audio Files", "*.mp3 *.wav *.flac"),
                ("All Files", "*.*"),
            ),
        )
        if not filename:
            return

        self.load_file(filename)

    def load_file(self, filename: str) -> bool:
        try:
            extension = os.path.splitext(filename)[1].lower()
            if extension not in SUPPORTED_EXTENSIONS:
                raise ValueError("Unsupported audio format.")
            if not os.path.isfile(filename):
                raise FileNotFoundError("Audio file not found.")

            player = self._ensure_player()
            media = self.vlc_instance.media_new(filename)
            player.set_media(media)
            self.current_file = filename

            basename = os.path.basename(filename)
            self.file_label.config(text=f"Loaded: {basename}")
            self.status_label.config(text=f"Ready to play: {basename}")
            return True
        except Exception as exc:
            messagebox.showerror("Load failed", str(exc))
            return False

    def play_pause(self) -> None:
        if not self.current_file:
            messagebox.showwarning("No File", "Open an audio file first.")
            return

        player = self._ensure_player()
        if self.is_playing:
            player.pause()
            self.play_btn.config(text="Play")
            self.status_label.config(text="Paused")
            self.is_playing = False
            return

        player.play()
        self.play_btn.config(text="Pause")
        self.status_label.config(text=f"Playing: {os.path.basename(self.current_file)}")
        self.is_playing = True

    def stop(self) -> None:
        if self.player is not None:
            self.player.stop()

        self.play_btn.config(text="Play")
        self.is_playing = False
        self.status_label.config(text="Stopped" if self.current_file else "Ready | Supports: MP3, WAV, FLAC")

    def change_volume(self, value: str) -> None:
        try:
            volume = int(float(value))
        except (TypeError, ValueError):
            return

        self.pending_volume = max(0, min(100, volume))

        if self._volume_job is not None:
            self.root.after_cancel(self._volume_job)
        self._volume_job = self.root.after(75, self._apply_volume)

    def _apply_volume(self) -> None:
        self._volume_job = None
        if self.player is not None:
            self.player.audio_set_volume(self.pending_volume)

    def flush_volume_change(self, _event=None) -> None:
        if self._volume_job is not None:
            self.root.after_cancel(self._volume_job)
            self._volume_job = None
        self._apply_volume()


def main() -> None:
    if tk is None:
        raise RuntimeError("tkinter is required to run this player.")
    if vlc is None:
        raise RuntimeError("python-vlc is required to run this player.")

    root = tk.Tk()
    app = SimpleAudioPlayer(root)
    root.protocol("WM_DELETE_WINDOW", root.destroy)
    root.mainloop()


if __name__ == "__main__":
    main()
