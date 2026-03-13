# WinampGera Music Player

A modern Python-based music player with a neon-green geometric tech theme, inspired by the classic Winamp interface.

![WinampGera](assets/icon.svg)

## Features

- 🎵 **Multi-format Support**: Play MP3, WAV, and FLAC audio files
- ▶️ **Playback Controls**: Play, Pause, and Stop functionality
- 🔊 **Volume Control**: Adjustable volume slider (0-100%)
- 📋 **One-Tap Share**: Copy a branded "Now Playing" message with the WinampGera link
- 🕘 **Recent Tracks**: Reopen the last songs you played from a built-in recent list
- 💾 **Session Restore**: Bring back the last opened track automatically on app launch
- 🎨 **Modern Theme**: Neon-green (#00ff41) geometric tech design on dark background
- 🖥️ **Simple Interface**: Clean, intuitive GUI built with tkinter
- 🚀 **VLC Backend**: Powered by python-vlc for robust audio playback

## Roadmap Priorities

These are the highest-value improvements suggested by the current repository state.

### Near-Term Priorities

- **Modularize the app**: Split `winampgera.py` into focused modules for UI, playback, analytics, and app state.
- **Improve runtime reliability**: Harden VLC detection, playback state handling, and user-facing error messages.
- **Expand test coverage**: Add integration-style tests for file loading, playback controls, share flow, and shutdown behavior.
- **Prepare packaging and CI**: Add a repeatable test workflow plus first-pass desktop packaging for beta distribution.
- **Add a queue or playlist**: Move beyond single-track playback so the app is useful for repeated listening sessions.

### Product Improvements Backlog

- **Track metadata**: Show artist, title, and duration when metadata is available.
- **Keyboard shortcuts**: Support quick actions for open, play/pause, and stop.
- **Progress and seek UI**: Show playback progress and allow seeking within a track.
- **Richer share UX**: Improve now-playing copy and success/error feedback after clipboard actions.

### Constraints and Risks

- **VLC dependency**: Installation and packaging differ by operating system and remain the biggest release risk.
- **Fixed window size**: The current `920x720` Tkinter layout may become cramped as playlist and metadata features are added.
- **Single-file architecture**: Continuing to add features in one file will increase regression risk and slow future changes.
- **Test limitations**: Current tests pass, but they do not yet cover real GUI, clipboard, or packaging scenarios.

### Full Roadmap Document

The repo roadmap lives in [ROADMAP.md](/Users/blackmamba/Documents/GitHub/winampGera/ROADMAP.md), and the generated 6-week planning document is available at [output/doc/winampgera-6-week-roadmap.docx](/Users/blackmamba/Documents/GitHub/winampGera/output/doc/winampgera-6-week-roadmap.docx).

## Requirements

- Python 3.7 or higher
- VLC media player installed on your system
- tkinter (usually included with Python)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Blackmvmba88/winampGera.git
cd winampGera
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Make sure VLC media player is installed on your system:
   - **Windows**: Download from [videolan.org](https://www.videolan.org/vlc/)
   - **macOS**: `brew install vlc` or download from videolan.org
   - **Linux**: `sudo apt-get install vlc` (Ubuntu/Debian) or `sudo dnf install vlc` (Fedora)

## Usage

Run the application:
```bash
python winampgera.py
```

Or make it executable (Linux/macOS):
```bash
chmod +x winampgera.py
./winampgera.py
```

### Controls

- **OPEN**: Click to browse and select an audio file (MP3, WAV, or FLAC)
- **PLAY**: Start playback or resume if paused (becomes PAUSE when playing)
- **STOP**: Stop playback completely
- **SHARE**: Copy the current track and app link to your clipboard for posting anywhere
- **VOLUME**: Use the slider to adjust volume from 0% to 100%
- **RECENT TRACKS**: Double click or use `REOPEN` to jump back into a recent song

### Measurement

WinampGera writes lightweight local adoption metrics to `winampgera_metrics.json` and playback state to `winampgera_state.json` in the project folder.

- `share_clicked`: Fired when someone taps the `SHARE` button
- `share_copied`: Fired when the clipboard copy succeeds
- `recent_reopened`: Fired when the last track is restored on startup or reopened from the recent list

## Project Structure

```
winampGera/
├── winampgera.py       # Main application file
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── ROADMAP.md         # Product and engineering roadmap
├── output/doc/        # Generated planning documents
├── winampgera_state.json # Saved playlist, volume, and recent track state
└── assets/
    └── icon.svg       # Application icon
```

## Design Theme

WinampGera features a distinctive neon-green geometric tech aesthetic:
- **Primary Color**: Neon Green (#00ff41)
- **Background**: Dark (#0a0a0a)
- **Accents**: Geometric shapes and borders
- **Font**: Courier New (monospace)
- **Style**: High-tech, minimalist, retro-futuristic

## Dependencies

- `python-vlc==3.0.18121` - Python bindings for VLC media player
- `Pillow==10.1.0` - Python Imaging Library (for potential future enhancements)

## Troubleshooting

### VLC not found
If you get an error about VLC not being found:
- Ensure VLC is properly installed on your system
- On Windows, make sure VLC is in your PATH or installed in the default location
- On Linux, install the libvlc-dev package: `sudo apt-get install libvlc-dev`

### Audio file won't play
- Verify the file format is MP3, WAV, or FLAC
- Check that the file is not corrupted
- Ensure VLC can play the file independently

## License

This project is open source and available for educational and personal use.

## Author

Created by Blackmvmba88

## Acknowledgments

- Inspired by the classic Winamp media player
- Built with Python, tkinter, and VLC
