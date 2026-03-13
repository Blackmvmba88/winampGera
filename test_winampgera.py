#!/usr/bin/env python3
"""
Tests for WinampGera imports and lightweight player behavior.
"""
import importlib
import json
import os
import tempfile
import unittest
from unittest import mock


class WinampGeraTests(unittest.TestCase):
    def setUp(self):
        self.module = importlib.import_module("winampgera")

    def test_module_imports(self):
        self.assertTrue(hasattr(self.module, "WinampGera"))
        self.assertTrue(hasattr(self.module, "main"))

    def test_class_structure(self):
        from winampgera import WinampGera

        required_methods = [
            "setup_ui",
            "open_file",
            "load_file",
            "play_pause",
            "stop",
            "change_volume",
            "build_share_message",
            "share_current_track",
            "add_to_recent_tracks",
            "reopen_selected_recent",
        ]

        for method in required_methods:
            self.assertTrue(hasattr(WinampGera, method), f"Method '{method}' is missing")

    def test_main_requires_runtime_dependencies(self):
        module = self.module

        if module.tk is not None and module.vlc is not None:
            self.skipTest("Runtime dependencies are available in this environment")

        with self.assertRaisesRegex(RuntimeError, "is required"):
            module.main()

    def test_build_share_message_uses_track_name_without_path(self):
        app = self.module.WinampGera.__new__(self.module.WinampGera)
        app.current_file = "/tmp/Daft Punk - Voyager.flac"

        message = app.build_share_message()

        self.assertIn("Now playing: Daft Punk - Voyager on WinampGera.", message)
        self.assertIn(self.module.WinampGera.SHARE_URL, message)
        self.assertNotIn("/tmp", message)

    def test_track_event_persists_counts(self):
        original_metrics_file = self.module.WinampGera.ANALYTICS_FILE

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                self.module.WinampGera.ANALYTICS_FILE = os.path.join(tmpdir, "metrics-test.json")

                self.module.WinampGera.track_event("share_clicked", has_track=True)
                self.module.WinampGera.track_event("share_clicked", has_track=False)

                with open(self.module.WinampGera.metrics_path(), "r", encoding="utf-8") as handle:
                    payload = json.load(handle)

                self.assertEqual(payload["events"]["share_clicked"], 2)
                self.assertEqual(payload["last_event"]["name"], "share_clicked")
                self.assertFalse(payload["last_event"]["properties"]["has_track"])
        finally:
            self.module.WinampGera.ANALYTICS_FILE = original_metrics_file

    def test_add_to_recent_tracks_dedupes_and_limits(self):
        app = self.module.WinampGera.__new__(self.module.WinampGera)
        app.recent_tracks = ["/music/one.mp3", "/music/two.mp3", "/music/three.mp3"]
        app.refresh_recent_tracks_ui = mock.Mock()
        app.persist_state = mock.Mock()

        app.add_to_recent_tracks("/music/two.mp3")
        app.add_to_recent_tracks("/music/four.mp3")
        app.add_to_recent_tracks("/music/five.mp3")
        app.add_to_recent_tracks("/music/six.mp3")

        self.assertEqual(
            app.recent_tracks,
            ["/music/six.mp3", "/music/five.mp3", "/music/four.mp3", "/music/two.mp3", "/music/one.mp3"],
        )

    def test_persist_state_includes_recent_tracks(self):
        original_state_file = self.module.WinampGera.STATE_FILE

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                track_path = os.path.join(tmpdir, "song.mp3")
                with open(track_path, "w", encoding="utf-8") as handle:
                    handle.write("fake")

                self.module.WinampGera.STATE_FILE = os.path.join(tmpdir, "state-test.json")
                app = self.module.WinampGera.__new__(self.module.WinampGera)
                app.playlist = [track_path]
                app.current_index = 0
                app.current_file = track_path
                app.pending_volume = 70
                app.recent_tracks = [track_path]

                app.persist_state()

                with open(self.module.WinampGera.state_path(), "r", encoding="utf-8") as handle:
                    payload = json.load(handle)

                self.assertEqual(payload["recent_tracks"], [track_path])
                self.assertEqual(payload["current_file"], track_path)
        finally:
            self.module.WinampGera.STATE_FILE = original_state_file

    def test_restore_state_rehydrates_recent_tracks(self):
        original_state_file = self.module.WinampGera.STATE_FILE

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                track_path = os.path.join(tmpdir, "song.mp3")
                with open(track_path, "w", encoding="utf-8") as handle:
                    handle.write("fake")

                state_path = os.path.join(tmpdir, "state-test.json")
                with open(state_path, "w", encoding="utf-8") as handle:
                    json.dump(
                        {
                            "playlist": [track_path],
                            "current_index": 0,
                            "current_file": track_path,
                            "volume": 55,
                            "recent_tracks": [track_path],
                        },
                        handle,
                    )

                self.module.WinampGera.STATE_FILE = state_path
                app = self.module.WinampGera.__new__(self.module.WinampGera)
                app.playlist = []
                app.recent_tracks = []
                app.current_index = -1
                app.current_file = None
                app.pending_volume = 70
                app.volume_slider = mock.Mock()
                app.refresh_playlist_ui = mock.Mock()
                app.refresh_recent_tracks_ui = mock.Mock()
                app.highlight_playlist_index = mock.Mock()
                app.update_track_labels = mock.Mock()
                app.set_status = mock.Mock()
                app.add_to_recent_tracks = mock.Mock()
                app.track_event = mock.Mock()

                app.restore_state()

                self.assertEqual(app.playlist, [track_path])
                self.assertEqual(app.recent_tracks, [track_path])
                self.assertEqual(app.current_file, track_path)
                app.track_event.assert_called_once_with(
                    "recent_reopened",
                    source="startup_restore",
                    track_name="song",
                )
        finally:
            self.module.WinampGera.STATE_FILE = original_state_file

    def test_reopen_selected_recent_tracks_event(self):
        app = self.module.WinampGera.__new__(self.module.WinampGera)
        app.recent_tracks = ["/music/one.mp3"]
        app.playlist = ["/music/one.mp3"]
        app.recent_listbox = mock.Mock()
        app.recent_listbox.curselection.return_value = (0,)
        app.load_playlist_index = mock.Mock(return_value=True)
        app.track_event = mock.Mock()
        app.get_track_name = mock.Mock(return_value="one")
        app.set_status = mock.Mock()

        reopened = app.reopen_selected_recent()

        self.assertTrue(reopened)
        app.load_playlist_index.assert_called_once_with(0, autoplay=False)
        app.track_event.assert_called_once_with(
            "recent_reopened",
            source="recent_list",
            track_name="one",
        )


if __name__ == "__main__":
    unittest.main()
