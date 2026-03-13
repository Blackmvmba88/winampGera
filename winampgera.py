#!/usr/bin/env python3
"""
WinampGera - A modern music player with neon-green geometric tech theme
"""
import json
import math
import os
import queue
import sys
import threading
import time
from datetime import datetime, timezone

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
AUDIO_FILE_TYPES = (
    ("Audio Files", "*.mp3 *.wav *.flac"),
    ("MP3 Files", "*.mp3"),
    ("WAV Files", "*.wav"),
    ("FLAC Files", "*.flac"),
    ("All Files", "*.*"),
)
PROGRESS_UPDATE_MS = 350
VOLUME_DEBOUNCE_MS = 75
SEEK_RANGE = 1000
SEEK_STEP_MS = 5000
VOLUME_STEP = 5
PLAYLIST_EMPTY_TEXT = "No file loaded"
STATUS_READY_TEXT = "Ready | Supports: MP3, WAV, FLAC"
RECENT_TRACK_LIMIT = 5
RECENT_EMPTY_TEXT = "No recent tracks yet"


class WinampGera:
    SHARE_URL = "https://github.com/Blackmvmba88/winampGera"
    ANALYTICS_FILE = "winampgera_metrics.json"
    STATE_FILE = "winampgera_state.json"

    def __init__(self, root):
        if vlc is None:
            raise RuntimeError(
                "python-vlc is required to launch WinampGera. Install dependencies from requirements.txt."
            )

        self.root = root
        self.root.title("WinampGera Music Player")
        self.root.geometry("920x720")
        self.root.configure(bg="#0a0a0a")
        self.root.minsize(860, 680)

        self.vlc_instance = None
        self.player = None

        self.current_file = None
        self.current_index = -1
        self.playlist = []
        self.recent_tracks = []
        self.is_playing = False
        self.pending_volume = 70
        self.pending_seek_ratio = 0
        self._volume_update_job = None
        self._share_reset_job = None
        self._progress_job = None
        self._load_token = 0
        self._last_known_length_ms = 0
        self._last_player_state = None
        self._user_dragging_seek = False
        self._visualizer_phase = 0.0
        self._ui_tasks = queue.Queue()

        self.setup_ui()
        self.bind_shortcuts()
        self.restore_state()
        self.track_event("app_started")
        self.schedule_progress_poll()

    def setup_ui(self):
        """Create the user interface with neon-green geometric theme."""
        title_label = tk.Label(
            self.root,
            text="WINAMP GERA",
            font=("Courier New", 26, "bold"),
            bg="#0a0a0a",
            fg="#00ff41",
        )
        title_label.pack(pady=(18, 10))

        content_frame = tk.Frame(self.root, bg="#0a0a0a")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=18, pady=(0, 12))

        left_panel = tk.Frame(content_frame, bg="#0a0a0a")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12))

        right_panel = tk.Frame(content_frame, bg="#0a0a0a")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH)

        info_frame = tk.Frame(left_panel, bg="#1a1a1a", bd=2, relief=tk.RIDGE)
        info_frame.pack(fill=tk.X, pady=(0, 10))

        self.file_label = tk.Label(
            info_frame,
            text=PLAYLIST_EMPTY_TEXT,
            font=("Courier New", 11),
            bg="#1a1a1a",
            fg="#00ff41",
            anchor="w",
            padx=10,
            pady=12,
        )
        self.file_label.pack(fill=tk.X)

        controls_frame = tk.Frame(left_panel, bg="#0a0a0a")
        controls_frame.pack(fill=tk.X, pady=(0, 10))

        button_style = {
            "font": ("Courier New", 11, "bold"),
            "bg": "#1a1a1a",
            "fg": "#00ff41",
            "activebackground": "#00ff41",
            "activeforeground": "#0a0a0a",
            "bd": 2,
            "relief": tk.RAISED,
            "width": 9,
            "height": 2,
            "cursor": "hand2",
        }

        self.open_btn = tk.Button(
            controls_frame,
            text="OPEN",
            command=self.open_file,
            **button_style,
        )
        self.open_btn.grid(row=0, column=0, padx=4, pady=4)

        self.folder_btn = tk.Button(
            controls_frame,
            text="FOLDER",
            command=self.open_folder,
            **button_style,
        )
        self.folder_btn.grid(row=0, column=1, padx=4, pady=4)

        self.prev_btn = tk.Button(
            controls_frame,
            text="PREV",
            command=self.play_previous,
            **button_style,
        )
        self.prev_btn.grid(row=0, column=2, padx=4, pady=4)

        self.play_btn = tk.Button(
            controls_frame,
            text="PLAY",
            command=self.play_pause,
            **button_style,
        )
        self.play_btn.grid(row=0, column=3, padx=4, pady=4)

        self.stop_btn = tk.Button(
            controls_frame,
            text="STOP",
            command=self.stop,
            **button_style,
        )
        self.stop_btn.grid(row=0, column=4, padx=4, pady=4)

        self.next_btn = tk.Button(
            controls_frame,
            text="NEXT",
            command=self.play_next,
            **button_style,
        )
        self.next_btn.grid(row=0, column=5, padx=4, pady=4)

        self.share_btn = tk.Button(
            controls_frame,
            text="SHARE",
            command=self.share_current_track,
            **button_style,
        )
        self.share_btn.grid(row=1, column=0, padx=4, pady=4)

        self.clear_btn = tk.Button(
            controls_frame,
            text="CLEAR",
            command=self.clear_playlist,
            **button_style,
        )
        self.clear_btn.grid(row=1, column=1, padx=4, pady=4)

        progress_frame = tk.Frame(left_panel, bg="#1a1a1a", bd=2, relief=tk.RIDGE)
        progress_frame.pack(fill=tk.X, pady=(0, 10))

        progress_header = tk.Frame(progress_frame, bg="#1a1a1a")
        progress_header.pack(fill=tk.X, padx=10, pady=(10, 2))

        self.current_time_label = tk.Label(
            progress_header,
            text="00:00",
            font=("Courier New", 10, "bold"),
            bg="#1a1a1a",
            fg="#00ff41",
        )
        self.current_time_label.pack(side=tk.LEFT)

        self.duration_label = tk.Label(
            progress_header,
            text="00:00",
            font=("Courier New", 10, "bold"),
            bg="#1a1a1a",
            fg="#00ff41",
        )
        self.duration_label.pack(side=tk.RIGHT)

        self.progress_slider = tk.Scale(
            progress_frame,
            from_=0,
            to=SEEK_RANGE,
            orient=tk.HORIZONTAL,
            showvalue=False,
            command=self.on_seek_drag,
            bg="#1a1a1a",
            fg="#00ff41",
            troughcolor="#0a0a0a",
            activebackground="#00ff41",
            highlightbackground="#1a1a1a",
            bd=0,
            relief=tk.FLAT,
            length=420,
            sliderlength=28,
        )
        self.progress_slider.pack(fill=tk.X, padx=10, pady=(0, 6))
        self.progress_slider.bind("<ButtonPress-1>", self.start_seek_drag)
        self.progress_slider.bind("<ButtonRelease-1>", self.flush_seek_change)

        seek_hint = tk.Label(
            progress_frame,
            text="Seek with mouse or Left/Right arrows",
            font=("Courier New", 9),
            bg="#1a1a1a",
            fg="#5cff87",
            padx=10,
            pady=4,
        )
        seek_hint.pack(anchor="w")

        volume_frame = tk.Frame(left_panel, bg="#0a0a0a")
        volume_frame.pack(fill=tk.X, pady=(0, 10))

        volume_label = tk.Label(
            volume_frame,
            text="VOLUME",
            font=("Courier New", 10, "bold"),
            bg="#0a0a0a",
            fg="#00ff41",
        )
        volume_label.pack(side=tk.LEFT, padx=(0, 10))

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
            length=320,
            width=18,
            sliderlength=28,
            sliderrelief=tk.RAISED,
        )
        self.volume_slider.set(self.pending_volume)
        self.volume_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.volume_slider.bind("<ButtonRelease-1>", self.flush_volume_change)

        visualizer_frame = tk.Frame(left_panel, bg="#1a1a1a", bd=2, relief=tk.RIDGE)
        visualizer_frame.pack(fill=tk.BOTH, expand=True)

        visualizer_label = tk.Label(
            visualizer_frame,
            text="SIGNAL VIEW",
            font=("Courier New", 10, "bold"),
            bg="#1a1a1a",
            fg="#00ff41",
            padx=10,
            pady=8,
        )
        visualizer_label.pack(anchor="w")

        self.visualizer_canvas = tk.Canvas(
            visualizer_frame,
            width=520,
            height=180,
            bg="#080808",
            highlightthickness=0,
        )
        self.visualizer_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        playlist_frame = tk.Frame(right_panel, bg="#1a1a1a", bd=2, relief=tk.RIDGE)
        playlist_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        playlist_label = tk.Label(
            playlist_frame,
            text="PLAYLIST",
            font=("Courier New", 12, "bold"),
            bg="#1a1a1a",
            fg="#00ff41",
            padx=10,
            pady=8,
        )
        playlist_label.pack(anchor="w")

        listbox_frame = tk.Frame(playlist_frame, bg="#1a1a1a")
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.playlist_listbox = tk.Listbox(
            listbox_frame,
            bg="#0d0d0d",
            fg="#8cff9a",
            selectbackground="#00ff41",
            selectforeground="#0a0a0a",
            activestyle="none",
            font=("Courier New", 10),
            bd=0,
            highlightthickness=0,
            yscrollcommand=scrollbar.set,
            width=34,
        )
        self.playlist_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.playlist_listbox.bind("<Double-Button-1>", self.on_playlist_activate)
        self.playlist_listbox.bind("<Return>", self.on_playlist_activate)
        scrollbar.config(command=self.playlist_listbox.yview)

        recent_frame = tk.Frame(right_panel, bg="#1a1a1a", bd=2, relief=tk.RIDGE)
        recent_frame.pack(fill=tk.BOTH)

        recent_header = tk.Frame(recent_frame, bg="#1a1a1a")
        recent_header.pack(fill=tk.X, padx=10, pady=(8, 4))

        recent_label = tk.Label(
            recent_header,
            text="RECENT TRACKS",
            font=("Courier New", 11, "bold"),
            bg="#1a1a1a",
            fg="#00ff41",
        )
        recent_label.pack(side=tk.LEFT)

        self.reopen_recent_btn = tk.Button(
            recent_header,
            text="REOPEN",
            command=self.reopen_selected_recent,
            font=("Courier New", 9, "bold"),
            bg="#0a0a0a",
            fg="#00ff41",
            activebackground="#00ff41",
            activeforeground="#0a0a0a",
            bd=1,
            relief=tk.RAISED,
            cursor="hand2",
        )
        self.reopen_recent_btn.pack(side=tk.RIGHT)

        self.recent_listbox = tk.Listbox(
            recent_frame,
            bg="#0d0d0d",
            fg="#8cff9a",
            selectbackground="#00ff41",
            selectforeground="#0a0a0a",
            activestyle="none",
            font=("Courier New", 9),
            bd=0,
            highlightthickness=0,
            height=6,
        )
        self.recent_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.recent_listbox.bind("<Double-Button-1>", self.reopen_selected_recent)

        status_frame = tk.Frame(self.root, bg="#1a1a1a", bd=2, relief=tk.RIDGE)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_label = tk.Label(
            status_frame,
            text=STATUS_READY_TEXT,
            font=("Courier New", 8),
            bg="#1a1a1a",
            fg="#00ff41",
            anchor="w",
            padx=10,
            pady=5,
        )
        self.status_label.pack(fill=tk.X)

        self.draw_visualizer([])

    def bind_shortcuts(self):
        self.root.bind("<space>", lambda _event: self.play_pause())
        self.root.bind("<Control-o>", lambda _event: self.open_file())
        self.root.bind("<Control-O>", lambda _event: self.open_file())
        self.root.bind("<Control-Shift-O>", lambda _event: self.open_folder())
        self.root.bind("<Left>", lambda _event: self.seek_relative(-SEEK_STEP_MS))
        self.root.bind("<Right>", lambda _event: self.seek_relative(SEEK_STEP_MS))
        self.root.bind("<Up>", lambda _event: self.adjust_volume(VOLUME_STEP))
        self.root.bind("<Down>", lambda _event: self.adjust_volume(-VOLUME_STEP))
        self.root.bind("n", lambda _event: self.play_next())
        self.root.bind("p", lambda _event: self.play_previous())

    def enqueue_ui_task(self, callback, *args):
        self._ui_tasks.put((callback, args))

    def drain_ui_tasks(self):
        while True:
            try:
                callback, args = self._ui_tasks.get_nowait()
            except queue.Empty:
                return
            callback(*args)

    def _ensure_player(self):
        """Create VLC objects only when playback-related work is needed."""
        if self.player is not None:
            return self.player

        self.vlc_instance = vlc.Instance()
        self.player = self.vlc_instance.media_player_new()
        self.player.audio_set_volume(getattr(self, "pending_volume", 70))
        return self.player

    @staticmethod
    def format_time(milliseconds):
        if milliseconds is None or milliseconds < 0:
            milliseconds = 0

        total_seconds = int(milliseconds // 1000)
        minutes, seconds = divmod(total_seconds, 60)
        hours, minutes = divmod(minutes, 60)

        if hours:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"

    @staticmethod
    def is_supported_file(path):
        return os.path.splitext(path)[1].lower() in SUPPORTED_EXTENSIONS

    @classmethod
    def metrics_path(cls):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), cls.ANALYTICS_FILE)

    @classmethod
    def state_path(cls):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), cls.STATE_FILE)

    @classmethod
    def track_event(cls, event_name, **properties):
        metrics_path = cls.metrics_path()
        payload = cls._read_json_file(metrics_path, {"events": {}, "last_event": None})

        payload.setdefault("events", {})
        payload["events"][event_name] = payload["events"].get(event_name, 0) + 1
        payload["last_event"] = {
            "name": event_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "properties": properties,
        }
        cls._write_json_file(metrics_path, payload)

    @staticmethod
    def _read_json_file(path, default):
        if not os.path.exists(path):
            return default
        try:
            with open(path, "r", encoding="utf-8") as handle:
                return json.load(handle)
        except (json.JSONDecodeError, OSError):
            return default

    @staticmethod
    def _write_json_file(path, payload):
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)

    def persist_state(self):
        payload = {
            "playlist": [path for path in self.playlist if os.path.exists(path)],
            "current_index": self.current_index,
            "current_file": self.current_file,
            "volume": self.pending_volume,
            "recent_tracks": [
                path for path in self.recent_tracks if isinstance(path, str) and os.path.exists(path)
            ],
        }

        try:
            self._write_json_file(self.state_path(), payload)
        except OSError:
            return

    def restore_state(self):
        payload = self._read_json_file(self.state_path(), None)
        if payload is None:
            return

        saved_playlist = self._filter_supported_paths(payload.get("playlist", []))
        if saved_playlist:
            self.playlist = saved_playlist
            self.refresh_playlist_ui()

        saved_recent_tracks = self._filter_supported_paths(payload.get("recent_tracks", []))
        self.recent_tracks = saved_recent_tracks[:RECENT_TRACK_LIMIT]
        self.refresh_recent_tracks_ui()

        saved_volume = payload.get("volume")
        if isinstance(saved_volume, int):
            self.pending_volume = max(0, min(100, saved_volume))
            self.volume_slider.set(self.pending_volume)

        saved_index = payload.get("current_index")
        if isinstance(saved_index, int) and 0 <= saved_index < len(self.playlist):
            self.current_index = saved_index
            self.current_file = self.playlist[saved_index]
            self.highlight_playlist_index(saved_index)
            self.update_track_labels(self.current_file, prefix="Queued")
            self.add_to_recent_tracks(self.current_file, persist=False)
            self.set_status(f"Restored session with {len(self.playlist)} track(s)")
            self.track_event("recent_reopened", source="startup_restore", track_name=self.get_track_name())
        elif self.playlist:
            self.current_index = 0
            self.current_file = self.playlist[0]
            self.highlight_playlist_index(0)
            self.update_track_labels(self.current_file, prefix="Queued")
            self.add_to_recent_tracks(self.current_file, persist=False)

    def _filter_supported_paths(self, paths):
        return [
            path
            for path in paths
            if isinstance(path, str) and os.path.exists(path) and self.is_supported_file(path)
        ]

    def update_track_labels(self, filename, prefix="Loaded"):
        basename = os.path.basename(filename) if filename else PLAYLIST_EMPTY_TEXT
        if hasattr(self, "file_label"):
            self.file_label.config(text=f"{prefix}: {basename}" if filename else PLAYLIST_EMPTY_TEXT)

    def set_status(self, message):
        if hasattr(self, "status_label"):
            self.status_label.config(text=message)

    def refresh_playlist_ui(self):
        if not hasattr(self, "playlist_listbox"):
            return

        self.playlist_listbox.delete(0, tk.END)
        for index, path in enumerate(self.playlist, start=1):
            self.playlist_listbox.insert(tk.END, f"{index:02d}. {os.path.basename(path)}")

        if self.current_index >= 0:
            self.highlight_playlist_index(self.current_index)

    def highlight_playlist_index(self, index):
        if not hasattr(self, "playlist_listbox"):
            return
        if index < 0 or index >= len(self.playlist):
            return

        self.playlist_listbox.selection_clear(0, tk.END)
        self.playlist_listbox.selection_set(index)
        self.playlist_listbox.activate(index)
        self.playlist_listbox.see(index)

    def format_recent_track(self, path):
        basename = os.path.basename(path)
        track_name, _ = os.path.splitext(basename)
        source_folder = os.path.basename(os.path.dirname(path)) or "~"
        return f"{track_name}  [{source_folder}]"

    def refresh_recent_tracks_ui(self):
        if not hasattr(self, "recent_listbox"):
            return

        self.recent_listbox.delete(0, tk.END)
        if not self.recent_tracks:
            self.recent_listbox.insert(tk.END, RECENT_EMPTY_TEXT)
            return

        for path in self.recent_tracks:
            self.recent_listbox.insert(tk.END, self.format_recent_track(path))

    def add_to_recent_tracks(self, filename, persist=True):
        if not filename:
            return

        self.recent_tracks = [path for path in self.recent_tracks if path != filename]
        self.recent_tracks.insert(0, filename)
        self.recent_tracks = self.recent_tracks[:RECENT_TRACK_LIMIT]
        self.refresh_recent_tracks_ui()

        if persist:
            self.persist_state()

    def dedupe_paths(self, paths):
        existing = list(getattr(self, "playlist", []))
        seen = set(existing)
        unique_paths = []
        for path in paths:
            if path not in seen:
                seen.add(path)
                unique_paths.append(path)
        return unique_paths

    def add_to_playlist(self, paths, replace=False):
        if not hasattr(self, "playlist"):
            self.playlist = []
        if not hasattr(self, "current_index"):
            self.current_index = -1
        if not hasattr(self, "current_file"):
            self.current_file = None

        valid_paths = self._filter_supported_paths(paths)
        if replace:
            self.playlist = []
            self.current_index = -1
            self.current_file = None

        additions = self.dedupe_paths(valid_paths)
        if not additions:
            return 0

        self.playlist.extend(additions)
        if self.current_index == -1:
            self.current_index = 0
            self.current_file = self.playlist[0]

        self.refresh_playlist_ui()
        self.persist_state()
        return len(additions)

    def load_playlist_index(self, index, autoplay=False):
        if index < 0 or index >= len(self.playlist):
            return False

        self.current_index = index
        self.current_file = self.playlist[index]
        self.highlight_playlist_index(index)
        self.queue_track_load(self.current_file, playlist_index=index, autoplay=autoplay)
        self.persist_state()
        return True

    def on_playlist_activate(self, _event=None):
        current_selection = self._get_listbox_selection("playlist_listbox")
        if current_selection is None:
            return

        self.load_playlist_index(current_selection, autoplay=True)

    def reopen_selected_recent(self, _event=None):
        if not self.recent_tracks:
            self.set_status("Select a recent track to reopen.")
            return False

        current_selection = self._get_listbox_selection("recent_listbox")
        if current_selection is None:
            self.set_status("Select a recent track to reopen.")
            return False

        filename = self.recent_tracks[current_selection]
        if filename not in self.playlist:
            self.add_to_playlist([filename], replace=False)

        target_index = self.playlist.index(filename)
        reopened = self.load_playlist_index(target_index, autoplay=False)
        if reopened:
            self.track_event("recent_reopened", source="recent_list", track_name=self.get_track_name())
            self.set_status(f"Reopened recent: {os.path.basename(filename)}")
        return reopened

    def clear_playlist(self):
        self.stop()
        self.playlist = []
        self.current_index = -1
        self.current_file = None
        self.refresh_playlist_ui()
        self.update_track_labels(None)
        self.set_status(STATUS_READY_TEXT)
        if hasattr(self, "current_time_label"):
            self.current_time_label.config(text="00:00")
        if hasattr(self, "duration_label"):
            self.duration_label.config(text="00:00")
        if hasattr(self, "progress_slider"):
            self.progress_slider.set(0)
        self._last_known_length_ms = 0
        self.draw_visualizer([])
        self.persist_state()

    def get_supported_files_in_directory(self, directory):
        if not os.path.isdir(directory):
            return []

        supported = []
        for entry in sorted(os.listdir(directory)):
            path = os.path.join(directory, entry)
            if os.path.isfile(path) and self.is_supported_file(path):
                supported.append(path)
        return supported

    def open_file(self):
        """Open file dialog to select audio files."""
        selected_paths = []
        if hasattr(filedialog, "askopenfilenames"):
            selected_paths = list(
                filedialog.askopenfilenames(
                    title="Select Audio Files",
                    filetypes=AUDIO_FILE_TYPES,
                )
            )
        elif hasattr(filedialog, "askopenfilename"):
            filename = filedialog.askopenfilename(
                title="Select Audio File",
                filetypes=AUDIO_FILE_TYPES,
            )
            if filename:
                selected_paths = [filename]

        if not selected_paths:
            return

        root = getattr(self, "root", None)
        if root is None:
            self.load_file(selected_paths[0])
            return

        added_count = self.add_to_playlist(selected_paths, replace=False)
        if not added_count:
            self.show_error("Error", "No supported audio files were selected.")
            return

        first_new = next((path for path in selected_paths if path in self.playlist), selected_paths[0])
        target_index = self.playlist.index(first_new)
        self.load_playlist_index(target_index, autoplay=False)
        self.track_event("files_added", count=added_count)

    def open_folder(self):
        directory = filedialog.askdirectory(title="Select Music Folder")
        if not directory:
            return

        self.set_status(f"Scanning folder: {os.path.basename(directory) or directory}")
        worker = threading.Thread(
            target=self._scan_folder_worker,
            args=(directory,),
            daemon=True,
        )
        worker.start()

    def _scan_folder_worker(self, directory):
        started_at = time.perf_counter()
        files = self.get_supported_files_in_directory(directory)
        elapsed_ms = int((time.perf_counter() - started_at) * 1000)
        self.enqueue_ui_task(self._finish_folder_scan, directory, files, elapsed_ms)

    def _finish_folder_scan(self, directory, files, elapsed_ms):
        if not files:
            self.show_error("Folder Scan", "No supported audio files were found in that folder.")
            self.set_status("Folder scan finished with no playable files")
            self.track_event("folder_scan_empty", directory=directory)
            return

        added_count = self.add_to_playlist(files, replace=False)
        target_index = self.playlist.index(files[0])
        self.load_playlist_index(target_index, autoplay=False)
        self.set_status(f"Added {added_count} track(s) from folder in {elapsed_ms} ms")
        self.track_event("folder_loaded", count=added_count, elapsed_ms=elapsed_ms)

    def queue_track_load(self, filename, playlist_index=None, autoplay=False):
        basename = os.path.basename(filename)
        self.update_track_labels(filename, prefix="Loading")
        self.set_status(f"Loading file: {basename}")
        self._load_token += 1
        token = self._load_token

        worker = threading.Thread(
            target=self._prepare_track_load,
            args=(token, filename, playlist_index, autoplay),
            daemon=True,
        )
        worker.start()

    def _prepare_track_load(self, token, filename, playlist_index, autoplay):
        started_at = time.perf_counter()
        error_message = None

        extension = os.path.splitext(filename)[1].lower()
        if extension not in SUPPORTED_EXTENSIONS:
            error_message = "Unsupported audio format. Please select an MP3, WAV, or FLAC file."
        elif not os.path.isfile(filename):
            error_message = f"Audio file not found: {filename}"

        elapsed_ms = int((time.perf_counter() - started_at) * 1000)
        self.enqueue_ui_task(
            self._finish_track_load,
            token,
            filename,
            playlist_index,
            autoplay,
            error_message,
            elapsed_ms,
        )

    def _finish_track_load(self, token, filename, playlist_index, autoplay, error_message, elapsed_ms):
        if token != self._load_token:
            return

        if error_message:
            self.show_error("Error", f"Failed to load file: {error_message}")
            self.set_status("Load failed")
            self.track_event("track_load_failed", filename=os.path.basename(filename))
            return

        loaded = self.load_file(
            filename,
            playlist_index=playlist_index,
            autoplay=autoplay,
            prepared_elapsed_ms=elapsed_ms,
        )
        if not loaded:
            self.set_status("Load failed")

    def load_file(self, filename, playlist_index=None, autoplay=False, prepared_elapsed_ms=0):
        """Load audio file into VLC player."""
        started_at = time.perf_counter()
        try:
            extension = os.path.splitext(filename)[1].lower()
            if extension not in SUPPORTED_EXTENSIONS:
                raise ValueError("Unsupported audio format. Please select an MP3, WAV, or FLAC file.")
            if not os.path.isfile(filename):
                raise FileNotFoundError(f"Audio file not found: {filename}")

            player = self._ensure_player()
            media = self.vlc_instance.media_new(filename)
            player.set_media(media)

            self.current_file = filename
            if playlist_index is not None:
                self.current_index = playlist_index
            elif filename in getattr(self, "playlist", []):
                self.current_index = self.playlist.index(filename)

            self.highlight_playlist_index(self.current_index)
            self.add_to_recent_tracks(filename, persist=False)
            self._last_known_length_ms = 0
            self.reset_progress_ui()
            self.update_track_labels(filename, prefix="Loaded")

            basename = os.path.basename(filename)
            self.set_status(f"Ready to play: {basename}")
            self.persist_state()

            total_elapsed_ms = prepared_elapsed_ms + int((time.perf_counter() - started_at) * 1000)
            self.track_event(
                "track_loaded",
                filename=basename,
                elapsed_ms=total_elapsed_ms,
                playlist_size=len(getattr(self, "playlist", [])),
            )

            if autoplay:
                player.play()
                self.set_playback_active(True)
                self.set_status(f"Playing: {basename}")
                self.track_event("playback_started", filename=basename, autoplay=True)

            return True
        except Exception as error:
            self.show_error("Error", self.format_load_error(filename, error))
            self.track_event("track_load_failed", filename=os.path.basename(filename))
            return False

    def format_load_error(self, filename, error):
        basename = os.path.basename(filename)
        if isinstance(error, FileNotFoundError):
            return f"Failed to load file: {basename} no longer exists."
        if isinstance(error, ValueError):
            return f"Failed to load file: {error}"
        return f"Failed to load file: VLC could not prepare {basename}. {error}"

    def play_pause(self):
        """Toggle play/pause."""
        if not self.current_file and self.playlist:
            self.load_playlist_index(max(self.current_index, 0), autoplay=False)
            return

        if not self.current_file:
            self.show_warning("No File", "Please open an audio file first")
            return

        player = self._ensure_player()

        if self.is_playing:
            player.pause()
            self.set_playback_active(False)
            self.set_status("Paused")
            self.track_event("playback_paused", filename=os.path.basename(self.current_file))
        else:
            player.play()
            self.set_playback_active(True)
            basename = os.path.basename(self.current_file)
            self.set_status(f"Playing: {basename}")
            self.track_event("playback_started", filename=basename, autoplay=False)

    def stop(self):
        """Stop playback."""
        if self.player is not None:
            self.player.stop()
        self.set_playback_active(False)
        self.reset_progress_ui(reset_duration=False)
        if self.current_file:
            basename = os.path.basename(self.current_file)
            self.set_status(f"Stopped: {basename}")
            self.track_event("playback_stopped", filename=basename)
        else:
            self.set_status(STATUS_READY_TEXT)

    def play_next(self):
        if not self.playlist:
            return False

        next_index = self.current_index + 1 if self.current_index >= 0 else 0
        if next_index >= len(self.playlist):
            next_index = 0
        return self.load_playlist_index(next_index, autoplay=self.is_playing)

    def play_previous(self):
        if not self.playlist:
            return False

        previous_index = self.current_index - 1 if self.current_index > 0 else len(self.playlist) - 1
        return self.load_playlist_index(previous_index, autoplay=self.is_playing)

    def change_volume(self, value):
        """Change volume level without calling into VLC on every drag event."""
        try:
            volume = int(float(value))
        except (TypeError, ValueError):
            return

        self.pending_volume = max(0, min(100, volume))
        self.persist_state()

        root = getattr(self, "root", None)
        if root is None or not hasattr(root, "after"):
            if self.player is not None:
                self.player.audio_set_volume(self.pending_volume)
            return

        if getattr(self, "_volume_update_job", None) is not None:
            root.after_cancel(self._volume_update_job)

        self._volume_update_job = root.after(VOLUME_DEBOUNCE_MS, self._apply_pending_volume)

    def _apply_pending_volume(self):
        self._volume_update_job = None
        if self.player is None:
            return
        self.player.audio_set_volume(self.pending_volume)

    def flush_volume_change(self, _event=None):
        if getattr(self, "_volume_update_job", None) is not None:
            self.root.after_cancel(self._volume_update_job)
            self._volume_update_job = None
        self._apply_pending_volume()
        self.track_event("volume_changed", volume=self.pending_volume)

    def adjust_volume(self, delta):
        new_volume = max(0, min(100, self.pending_volume + delta))
        if hasattr(self, "volume_slider"):
            self.volume_slider.set(new_volume)
        self.change_volume(new_volume)
        if hasattr(self, "root"):
            self.flush_volume_change()

    def start_seek_drag(self, _event=None):
        self._user_dragging_seek = True

    def on_seek_drag(self, value):
        try:
            ratio = max(0.0, min(1.0, float(value) / SEEK_RANGE))
        except (TypeError, ValueError):
            return

        self.pending_seek_ratio = ratio
        if self._user_dragging_seek and self._last_known_length_ms > 0 and hasattr(self, "current_time_label"):
            preview_ms = int(self._last_known_length_ms * ratio)
            self.current_time_label.config(text=self.format_time(preview_ms))

    def flush_seek_change(self, _event=None):
        self._user_dragging_seek = False
        if self.player is None or self._last_known_length_ms <= 0:
            return

        target_ms = int(self._last_known_length_ms * self.pending_seek_ratio)
        try:
            self.player.set_time(target_ms)
            self.track_event("seek_applied", target_ms=target_ms)
        except Exception:
            return

    def seek_relative(self, delta_ms):
        if self.player is None:
            return

        current_ms = max(0, self.player.get_time())
        target_ms = max(0, current_ms + delta_ms)
        if self._last_known_length_ms > 0:
            target_ms = min(target_ms, self._last_known_length_ms)

        self.player.set_time(target_ms)
        self.track_event("seek_applied", target_ms=target_ms, delta_ms=delta_ms)

    def schedule_progress_poll(self):
        self.drain_ui_tasks()
        self.poll_player_state()
        self._progress_job = self.root.after(PROGRESS_UPDATE_MS, self.schedule_progress_poll)

    def poll_player_state(self):
        if self.player is None:
            self.draw_visualizer([])
            return

        try:
            player_state = self.player.get_state()
        except Exception:
            return

        self._last_player_state = player_state
        self.update_progress_display()

        state_name = str(player_state)
        if "State.Ended" in state_name and self.is_playing:
            self.track_event("track_completed", filename=os.path.basename(self.current_file or ""))
            self.play_next()
        elif "State.Error" in state_name:
            self.set_playback_active(False)
            self.set_status("Playback error: VLC reported a playback failure")
            self.track_event("playback_error", filename=os.path.basename(self.current_file or ""))

    def update_progress_display(self):
        if self.player is None:
            return

        length_ms = self.player.get_length()
        time_ms = self.player.get_time()

        if length_ms and length_ms > 0:
            self._last_known_length_ms = length_ms
            if hasattr(self, "duration_label"):
                self.duration_label.config(text=self.format_time(length_ms))

        if time_ms is None or time_ms < 0:
            time_ms = 0

        if not self._user_dragging_seek:
            if hasattr(self, "current_time_label"):
                self.current_time_label.config(text=self.format_time(time_ms))
            if self._last_known_length_ms > 0 and hasattr(self, "progress_slider"):
                ratio = min(1.0, max(0.0, time_ms / self._last_known_length_ms))
                self.pending_seek_ratio = ratio
                self.progress_slider.set(int(ratio * SEEK_RANGE))

        self.draw_visualizer(self.build_visualizer_levels(time_ms))

    def build_visualizer_levels(self, time_ms):
        bar_count = 20
        if not self.is_playing:
            return [0.08 if i % 3 == 0 else 0.02 for i in range(bar_count)]

        phase = (time_ms / 180.0) if time_ms else self._visualizer_phase
        self._visualizer_phase += 0.25
        volume_gain = max(0.2, self.pending_volume / 100.0)

        levels = []
        for index in range(bar_count):
            wave = abs(math.sin(phase + (index * 0.45)))
            pulse = abs(math.cos((phase * 0.6) + (index * 0.25)))
            levels.append(min(1.0, 0.15 + ((wave * 0.65) + (pulse * 0.2)) * volume_gain))
        return levels

    def draw_visualizer(self, levels):
        if not hasattr(self, "visualizer_canvas"):
            return

        canvas = self.visualizer_canvas
        canvas.delete("all")

        width = int(canvas.winfo_width() or 520)
        height = int(canvas.winfo_height() or 180)
        bar_count = len(levels) or 20
        gap = 6
        bar_width = max(8, int((width - ((bar_count + 1) * gap)) / bar_count))

        for index in range(bar_count):
            level = levels[index] if index < len(levels) else 0.05
            x0 = gap + index * (bar_width + gap)
            x1 = x0 + bar_width
            bar_height = max(8, int((height - 24) * level))
            y0 = height - 12 - bar_height
            y1 = height - 12
            fill = "#00ff41" if level > 0.25 else "#2f6f3a"
            canvas.create_rectangle(x0, y0, x1, y1, fill=fill, outline="")
            canvas.create_rectangle(x0, y0, x1, y1, outline="#8cff9a")

        canvas.create_line(0, height - 8, width, height - 8, fill="#0f4f1b", width=2)

    def get_track_name(self):
        if not self.current_file:
            return None

        basename = os.path.basename(self.current_file)
        track_name, _ = os.path.splitext(basename)
        return track_name or basename

    def build_share_message(self):
        track_name = self.get_track_name()
        if not track_name:
            return None

        return (
            f"Now playing: {track_name} on WinampGera.\n"
            f"Try the neon desktop player: {self.SHARE_URL}"
        )

    def set_share_success_state(self, track_name):
        self.share_btn.config(text="COPIED")
        self.set_status(f"Share copy ready: {track_name}")

        if self._share_reset_job:
            self.root.after_cancel(self._share_reset_job)

        self._share_reset_job = self.root.after(1800, self.reset_share_button)

    def reset_share_button(self):
        self.share_btn.config(text="SHARE")
        self._share_reset_job = None

    def share_current_track(self):
        self.track_event("share_clicked", has_track=bool(self.current_file))

        if not self.current_file:
            self.show_warning("No Track", "Load a track before sharing it")
            return

        share_message = self.build_share_message()
        track_name = self.get_track_name()

        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(share_message)
            self.root.update_idletasks()
        except tk.TclError as error:
            self.show_error("Share failed", f"Couldn't copy share text: {error}")
            return

        self.track_event("share_copied", track_name=track_name)
        self.set_share_success_state(track_name)

    def show_error(self, title, message):
        if messagebox is not None:
            messagebox.showerror(title, message)

    def show_warning(self, title, message):
        if messagebox is not None:
            messagebox.showwarning(title, message)

    def _get_listbox_selection(self, attribute_name):
        listbox = getattr(self, attribute_name, None)
        if listbox is None:
            return None
        current_selection = listbox.curselection()
        if not current_selection:
            return None
        return current_selection[0]

    def set_playback_active(self, is_active):
        self.is_playing = is_active
        if hasattr(self, "play_btn"):
            self.play_btn.config(text="PAUSE" if is_active else "PLAY")

    def reset_progress_ui(self, reset_duration=True):
        if hasattr(self, "progress_slider"):
            self.progress_slider.set(0)
        if hasattr(self, "current_time_label"):
            self.current_time_label.config(text="00:00")
        if reset_duration and hasattr(self, "duration_label"):
            self.duration_label.config(text="00:00")

    def on_closing(self):
        if self._volume_update_job is not None:
            self.root.after_cancel(self._volume_update_job)
            self._volume_update_job = None
        if self._progress_job is not None:
            self.root.after_cancel(self._progress_job)
            self._progress_job = None
        if self.player is not None:
            self.player.stop()
        self.persist_state()
        self.root.destroy()


def main():
    if tk is None:
        raise RuntimeError(
            "tkinter is required to launch WinampGera. Install a Python build with tkinter support."
        )
    if vlc is None:
        raise RuntimeError(
            "python-vlc is required to launch WinampGera. Install dependencies from requirements.txt."
        )

    root = tk.Tk()
    app = WinampGera(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
