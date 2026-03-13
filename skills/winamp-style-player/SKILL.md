---
name: winamp-style-player
description: Build or extend retro Winamp-inspired desktop audio players with bold skins, neon or high-contrast themes, geometric UI details, local file playback, share interactions, and lightweight metrics. Use when the request is about recreating a Winamp-like vibe, modernizing a nostalgic desktop player, or styling a Python media player with strong retro-futuristic personality.
---

# Winamp Style Player

## Overview

Build desktop audio players that feel intentionally nostalgic instead of generic.
Use this skill when the player should have a strong visual identity, especially a Winamp-like mix of compact controls, loud accent color, dark chrome, and playful status feedback.

## Quick Start

1. Start from [winamp_player_app.py](/Users/blackmamba/Documents/GitHub/winampGera/skills/winamp-style-player/assets/winamp_player_app.py) when the user wants a fresh retro player.
2. Read [style-guide.md](/Users/blackmamba/Documents/GitHub/winampGera/skills/winamp-style-player/references/style-guide.md) before changing colors, spacing, copy, or decorative motifs.
3. Keep the first pass focused on the shell, core controls, and theme before adding extra features.
4. Reuse the `python-vlc` playback pattern from the player scaffold instead of inventing a new audio backend unless the repo already uses something else.
5. Add themed tests only for behavior; do not over-invest in pixel-perfect automation for a first iteration.

## Workflow

### 1. Lock the aesthetic direction

- Use a dark base, one strong accent color, and a monospace or machine-like display font.
- Make the theme specific. Avoid bland “media app” styling.
- Prefer geometric trims, segmented panels, and hard edges over soft consumer-app cards.

### 2. Keep the layout compact and legible

- Put current track information in a dedicated display strip.
- Group transport controls so the user can read them at a glance.
- Reserve one area for decorative elements so the interface feels authored, not noisy.
- Use status text intentionally; short system-like phrases work well.

### 3. Layer personality onto solid playback behavior

- Get open, load, play, pause, stop, and volume working before adding cosmetic extras.
- Make share actions or status flashes feel part of the skin.
- Keep filenames private; show the track name instead.
- Lightweight local metrics are acceptable if the feature set includes share or engagement actions.

### 4. Extend carefully

- Add playlist support only if the user asks.
- Add cover art only if assets are available or the repo already supports metadata extraction.
- If animations are used, keep them small and intentional.

## Design Rules

- Favor contrast and strong framing over minimalist whitespace.
- Use one accent color consistently.
- Avoid modern app clichés that fight the retro concept.
- Preserve usability; the aesthetic should not hide the current state.
- Keep nostalgic references suggestive rather than direct copies of proprietary skins.

## Common Requests

- "Make this player feel like Winamp."
  - Restyle the shell with darker panels, bold accent color, compact controls, and a more expressive title/status area.
- "Build a retro desktop player in Python."
  - Start from the retro scaffold and wire in local file playback with `python-vlc`.
- "Add a share button that fits the theme."
  - Treat the action like a console event: short copy, clear success state, branded message.
- "Modernize the UI but keep the nostalgia."
  - Clean up spacing and labels without flattening the visual personality.

## Resources

### assets/

- [winamp_player_app.py](/Users/blackmamba/Documents/GitHub/winampGera/skills/winamp-style-player/assets/winamp_player_app.py): retro-styled `tkinter` + `python-vlc` player scaffold inspired by the visual direction in this repo.

### references/

- [style-guide.md](/Users/blackmamba/Documents/GitHub/winampGera/skills/winamp-style-player/references/style-guide.md): theme guidance for color, typography, panel treatment, motion restraint, and Winamp-adjacent visual language.
