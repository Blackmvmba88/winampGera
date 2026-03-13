#!/usr/bin/env python3
"""Starter tests for the simple audio player scaffold."""

from __future__ import annotations

import importlib.util
import pathlib
import unittest
from types import SimpleNamespace
from unittest import mock


MODULE_PATH = pathlib.Path(__file__).with_name("simple-player-app.py")


def load_player_module():
    spec = importlib.util.spec_from_file_location("simple_player_app", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class SimplePlayerTemplateTests(unittest.TestCase):
    def setUp(self):
        self.module = load_player_module()

    def test_module_exposes_player_and_main(self):
        self.assertTrue(hasattr(self.module, "SimpleAudioPlayer"))
        self.assertTrue(hasattr(self.module, "main"))

    def test_load_file_rejects_unsupported_format(self):
        app = self.module.SimpleAudioPlayer.__new__(self.module.SimpleAudioPlayer)
        app.vlc_instance = mock.Mock()
        app.player = mock.Mock()
        app.file_label = mock.Mock()
        app.status_label = mock.Mock()
        app.current_file = None

        messagebox = SimpleNamespace(showerror=mock.Mock())
        with mock.patch.object(self.module, "messagebox", messagebox):
            loaded = app.load_file("track.ogg")

        self.assertFalse(loaded)
        self.assertIsNone(app.current_file)
        messagebox.showerror.assert_called_once()
        app.player.set_media.assert_not_called()

    def test_change_volume_clamps_values(self):
        app = self.module.SimpleAudioPlayer.__new__(self.module.SimpleAudioPlayer)
        app.player = mock.Mock()
        app.pending_volume = 70
        app._volume_job = None
        app.root = SimpleNamespace(after=mock.Mock(return_value="job-1"), after_cancel=mock.Mock())

        app.change_volume("150")
        self.assertEqual(app.pending_volume, 100)

        app.change_volume("-10")
        self.assertEqual(app.pending_volume, 0)

        app.change_volume("bad-value")
        self.assertEqual(app.pending_volume, 0)

    def test_play_pause_requires_loaded_track(self):
        app = self.module.SimpleAudioPlayer.__new__(self.module.SimpleAudioPlayer)
        app.current_file = None

        messagebox = SimpleNamespace(showwarning=mock.Mock())
        with mock.patch.object(self.module, "messagebox", messagebox):
            app.play_pause()

        messagebox.showwarning.assert_called_once()


if __name__ == "__main__":
    unittest.main()
