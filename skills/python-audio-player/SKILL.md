---
name: python-audio-player
description: Build or extend lightweight desktop audio players in Python using tkinter and python-vlc. Use when creating a music player GUI, adding playback controls, loading local MP3/WAV/FLAC files, implementing volume sliders, clipboard share actions, simple local analytics, or tests for Python desktop media apps.
---

# Python Audio Player

## Overview

Build small desktop audio players quickly with `tkinter` for the GUI and `python-vlc` for playback.
Use the patterns in this skill when the request is about shipping a simple local player, not a streaming platform or a DAW.

## Quick Start

1. Run `scripts/check_player_runtime.py` before wiring playback if the environment is unknown.
2. Start from a single-file prototype unless the app already has a structure to preserve.
3. Build the GUI shell first: window, current track label, play/pause/stop buttons, volume slider, and status bar.
4. Initialize VLC lazily so the window can render even when media setup is slow.
5. Validate file extensions before loading media.
6. Add tests with mocks for `tkinter`, dialogs, clipboard, and VLC objects when the environment may be headless.
7. Read [player-patterns.md](/Users/blackmamba/Documents/GitHub/winampGera/skills/python-audio-player/references/player-patterns.md) for implementation details and testable design choices.
8. Start from [simple-player-app.py](/Users/blackmamba/Documents/GitHub/winampGera/skills/python-audio-player/assets/simple-player-app.py) when the user wants a fresh player scaffold.
9. Copy [test_simple_player.py](/Users/blackmamba/Documents/GitHub/winampGera/skills/python-audio-player/assets/test_simple_player.py) when the user wants a starter test suite for CI-safe player behavior.

## Build Workflow

### 1. Confirm runtime assumptions

- Expect local desktop playback, not browser playback.
- Prefer `tkinter` plus `python-vlc` unless the repo already uses another GUI toolkit or audio backend.
- Treat `tkinter` and `vlc` as optional imports in code paths that must still be importable in CI or test environments.

### 2. Build the minimal player loop

- Keep `current_file`, `is_playing`, and `pending_volume` as explicit state.
- Create the player object only when playback work is needed.
- Implement this sequence first:
  - open file dialog
  - validate extension and file existence
  - create VLC media
  - play or pause
  - stop
  - update labels and button text
- Support a small set of formats unless the user asks for more.

### 3. Make the UI responsive enough

- Defer media initialization until after the window is shown.
- Avoid calling `audio_set_volume` on every slider tick; debounce short drag bursts.
- Keep status text explicit: `Ready`, `Loading`, `Playing`, `Paused`, `Stopped`, `Share copied`, or a clear error.

### 4. Add optional convenience features

- Clipboard share actions are a good lightweight add-on. Build the share text from the basename, not the full path.
- Local analytics should stay simple and file-based unless the app already has telemetry infrastructure.
- Keep optional features isolated so the base player still works without them.

### 5. Test without depending on a GUI desktop session

- Mock `filedialog`, `messagebox`, `clipboard`, and VLC objects.
- Test importability when dependencies are missing.
- Test volume clamping, unsupported extensions, and metrics persistence.
- Prefer behavior tests over screenshot or pixel assertions.

## Design Rules

- Preserve the existing toolkit if the repo already uses another GUI framework.
- Keep first versions single-purpose. Do not add playlists, waveform views, or metadata libraries unless requested.
- Prefer local files over library scanners for the initial iteration.
- Avoid hard-coding OS-specific VLC paths unless the repo already needs them.
- Make error dialogs actionable and short.
- Keep path handling private; show user-friendly track names in the UI and shared text.

## Common Requests

- "Build a simple desktop music player in Python."
  - Create a compact `tkinter` app with `python-vlc`, file loading, playback controls, and volume.
- "Add play/pause/stop to this existing GUI."
  - Reuse the app's current widget structure and inject a lazy VLC player wrapper.
- "Support MP3, WAV, and FLAC and show the current track."
  - Add extension validation, basename extraction, and explicit status updates.
- "Make this testable in CI."
  - Split UI state transitions from direct GUI side effects and mock runtime dependencies.
- "Add a share button."
  - Copy a branded message to the clipboard and avoid leaking filesystem paths.

## Resources

### scripts/

- `scripts/check_player_runtime.py`: check whether the local Python environment can import `tkinter` and `vlc`, and report likely setup gaps before editing app code.

### references/

- [player-patterns.md](/Users/blackmamba/Documents/GitHub/winampGera/skills/python-audio-player/references/player-patterns.md): concrete implementation patterns extracted from this repo's player, including lazy VLC setup, slider debouncing, share behavior, and test coverage ideas.

### assets/

- [simple-player-app.py](/Users/blackmamba/Documents/GitHub/winampGera/skills/python-audio-player/assets/simple-player-app.py): minimal reusable desktop player scaffold with lazy VLC initialization, extension validation, playback controls, and a volume slider.
- [test_simple_player.py](/Users/blackmamba/Documents/GitHub/winampGera/skills/python-audio-player/assets/test_simple_player.py): starter unittest module with mocked runtime dependencies for import safety, unsupported format handling, and volume clamping.
