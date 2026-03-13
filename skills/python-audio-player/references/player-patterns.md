# Player Patterns

Use these patterns when building or extending a small desktop audio player in Python.

## Core architecture

- Keep the first version local-only: open one file, play it, stop it, change volume.
- Store UI state in a small number of fields such as `current_file`, `is_playing`, and `pending_volume`.
- Keep GUI setup separate from playback setup so the module can still import in headless environments.
- Create the VLC instance lazily when playback work starts. This lets the window render before libVLC setup.

## File loading

- Validate extensions before creating media objects.
- Validate that the file exists and fail with a short user-facing message if it does not.
- Show only the basename in labels and share text.
- Start with a tight allowlist such as `.mp3`, `.wav`, `.flac`.

## Playback controls

- Implement `play_pause` as a toggle over explicit state.
- Reset the play button and status text in `stop`.
- Keep button labels and status text synchronized with the actual playback state.
- Guard playback actions when no file is loaded.

## Volume behavior

- Debounce slider updates instead of calling into VLC on every drag event.
- Clamp volume into `0..100`.
- Apply the latest value immediately when dragging ends.
- Keep a `pending_volume` state so changes can be made before the player exists.

## Share and local analytics

- Build share text from the track name without exposing filesystem paths.
- Use clipboard copy as the main action and show a short success state in the UI.
- Keep analytics local and file-based for early validation.
- Persist a simple event counter plus the last event payload if measurement is requested.

## Testing patterns

- Mock `messagebox`, `filedialog`, clipboard calls, and VLC objects.
- Test that the module imports even when `tkinter` or `vlc` are unavailable.
- Test unsupported extensions, missing files, and volume parsing.
- Test helper methods such as track-name extraction and share message generation.
- Test file-based analytics in a temporary directory.

## When to split code

- Stay in one file for the first working prototype.
- Extract helpers only when tests or repeated code make the boundaries obvious.
- If the app grows, separate:
  - UI construction
  - playback adapter
  - analytics helpers
  - test doubles or fixtures
