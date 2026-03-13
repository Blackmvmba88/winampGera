#!/usr/bin/env python3
"""Retro-styled audio player scaffold for tkinter + python-vlc."""

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
ACCENT = "#00FF41"
BG = "#0A0A0A"
PANEL = "#161616"


class WinampStylePlayer:
    def __init__(self, root: "tk.Tk") -> None:
        if vlc is None:
            raise RuntimeError("python-vlc is required to run this player.")

        self.root = root
        self.root.title("Winamp Style Player")
        self.root.geometry("620x360")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        self.vlc_instance = None
        self.player = None
        self.current_file = None
        self.is_playing = False
        self.pending_volume = 70
        self._volume_job = None
        self._share_reset_job = None

        self._build_ui()

    def _build_ui(self) -> None:
        title = tk.Label(
            self.root,
            text="WINAMP STYLE",
            font=("Courier New", 24, "bold"),
            bg=BG,
            fg=ACCENT,
        )
        title.pack(pady=18)

        self.file_label = tk.Label(
            self.root,
            text="NO FILE LOADED",
            font=("Courier New", 10),
            anchor="w",
            bg=PANEL,
            fg=ACCENT,
            padx=12,
            pady=12,
            relief=tk.RIDGE,
            bd=2,
        )
        self.file_label.pack(fill=tk.X, padx=20)

        controls = tk.Frame(self.root, bg=BG)
        controls.pack(pady=20)

        button_style = {
            "font": ("Courier New", 11, "bold"),
            "bg": PANEL,
            "fg": ACCENT,
            "activebackground": ACCENT,
            "activeforeground": BG,
            "width": 9,
            "height": 2,
            "bd": 2,
            "relief": tk.RAISED,
        }

        self.open_btn = tk.Button(controls, text="OPEN", command=self.open_file, **button_style)
        self.open_btn.grid(row=0, column=0, padx=5)

        self.play_btn = tk.Button(controls, text="PLAY", command=self.play_pause, **button_style)
        self.play_btn.grid(row=0, column=1, padx=5)

        self.stop_btn = tk.Button(controls, text="STOP", command=self.stop, **button_style)
        self.stop_btn.grid(row=0, column=2, padx=5)

        self.share_btn = tk.Button(controls, text="SHARE", command=self.share_track, **button_style)
        self.share_btn.grid(row=0, column=3, padx=5)

        volume_row = tk.Frame(self.root, bg=BG)
        volume_row.pack(fill=tk.X, padx=36, pady=(0, 18))

        tk.Label(
            volume_row,
            text="VOLUME",
            font=("Courier New", 10, "bold"),
            bg=BG,
            fg=ACCENT,
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.volume_slider = tk.Scale(
            volume_row,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            command=self.change_volume,
            bg=PANEL,
            fg=ACCENT,
            troughcolor=BG,
            activebackground=ACCENT,
            highlightbackground=BG,
            relief=tk.RIDGE,
            bd=2,
            length=320,
        )
        self.volume_slider.set(self.pending_volume)
        self.volume_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.volume_slider.bind("<ButtonRelease-1>", self.flush_volume_change)

        self.status_label = tk.Label(
            self.root,
            text="READY | MP3 WAV FLAC",
            font=("Courier New", 9),
            anchor="w",
            bg=PANEL,
            fg=ACCENT,
            padx=12,
            pady=8,
            relief=tk.RIDGE,
            bd=2,
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        canvas = tk.Canvas(self.root, width=620, height=44, bg=BG, highlightthickness=0)
        canvas.pack(pady=8)
        for i in range(0, 620, 62):
            canvas.create_line(i, 22, i + 30, 22, fill=ACCENT, width=2)
            canvas.create_rectangle(i + 36, 16, i + 48, 28, outline=ACCENT, width=2)

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
        if filename:
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
            self.file_label.config(text=f"LOADED: {basename}")
            self.status_label.config(text=f"READY TO PLAY: {basename}")
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
            self.play_btn.config(text="PLAY")
            self.status_label.config(text="PAUSED")
            self.is_playing = False
            return

        player.play()
        self.play_btn.config(text="PAUSE")
        self.status_label.config(text=f"PLAYING: {os.path.basename(self.current_file)}")
        self.is_playing = True

    def stop(self) -> None:
        if self.player is not None:
            self.player.stop()
        self.play_btn.config(text="PLAY")
        self.is_playing = False
        self.status_label.config(text="STOPPED" if self.current_file else "READY | MP3 WAV FLAC")

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

    def share_track(self) -> None:
        if not self.current_file:
            messagebox.showwarning("No Track", "Load a track before sharing it.")
            return

        track_name = os.path.splitext(os.path.basename(self.current_file))[0]
        payload = f"NOW PLAYING: {track_name}\nPowered by a retro desktop player."

        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(payload)
            self.root.update_idletasks()
        except tk.TclError as exc:
            messagebox.showerror("Share failed", str(exc))
            return

        self.share_btn.config(text="COPIED")
        self.status_label.config(text=f"SHARE READY: {track_name}")
        if self._share_reset_job is not None:
            self.root.after_cancel(self._share_reset_job)
        self._share_reset_job = self.root.after(1800, self._reset_share_button)

    def _reset_share_button(self) -> None:
        self.share_btn.config(text="SHARE")
        self._share_reset_job = None


def main() -> None:
    if tk is None:
        raise RuntimeError("tkinter is required to run this player.")
    if vlc is None:
        raise RuntimeError("python-vlc is required to run this player.")

    root = tk.Tk()
    app = WinampStylePlayer(root)
    root.protocol("WM_DELETE_WINDOW", root.destroy)
    root.mainloop()


if __name__ == "__main__":
    main()
