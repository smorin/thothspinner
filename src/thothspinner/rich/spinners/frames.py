"""Built-in spinner frame sets for ThothSpinner.

This module provides various spinner animation frame definitions
compatible with Rich rendering. Each spinner style includes frames
and timing intervals.
"""

from __future__ import annotations

from typing import TypedDict


class SpinnerDefinition(TypedDict):
    """Type definition for spinner configuration."""

    frames: list[str]
    interval: float  # In seconds


SPINNER_FRAMES: dict[str, SpinnerDefinition] = {
    "npm_dots": {
        "frames": ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
        "interval": 0.08,  # 80ms = 12.5 FPS
    },
    "claude_stars": {
        "frames": ["·", "✢", "✳", "✶", "✻", "✽", "✻", "✶", "✳", "✢"],
        "interval": 0.1,  # 100ms = 10 FPS
    },
    "classic": {
        "frames": ["|", "/", "-", "\\"],
        "interval": 0.1,
    },
    "dots": {
        "frames": ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"],
        "interval": 0.08,
    },
    "dots2": {
        "frames": ["⠁", "⠂", "⠄", "⡀", "⢀", "⠠", "⠐", "⠈"],
        "interval": 0.08,
    },
    "dots3": {
        "frames": ["⠋", "⠙", "⠚", "⠞", "⠖", "⠦", "⠴", "⠲", "⠳", "⠓"],
        "interval": 0.08,
    },
    "arrows": {
        "frames": ["←", "↖", "↑", "↗", "→", "↘", "↓", "↙"],
        "interval": 0.1,
    },
    "circle": {
        "frames": ["◐", "◓", "◑", "◒"],
        "interval": 0.12,
    },
    "square": {
        "frames": ["◰", "◳", "◲", "◱"],
        "interval": 0.12,
    },
    "triangle": {
        "frames": ["◢", "◣", "◤", "◥"],
        "interval": 0.12,
    },
    "bounce": {
        "frames": ["⠁", "⠂", "⠄", "⠂"],
        "interval": 0.12,
    },
    "box_bounce": {
        "frames": ["▖", "▘", "▝", "▗"],
        "interval": 0.12,
    },
    "star": {
        "frames": ["✶", "✸", "✹", "✺", "✹", "✸"],
        "interval": 0.08,
    },
    "arc": {
        "frames": ["◜", "◠", "◝", "◞", "◡", "◟"],
        "interval": 0.1,
    },
    "line": {
        "frames": ["-", "—", "─", "━"],
        "interval": 0.12,
    },
    "pulse": {
        "frames": ["▏", "▎", "▍", "▌", "▋", "▊", "▉", "█", "▉", "▊", "▋", "▌", "▍", "▎"],
        "interval": 0.08,
    },
    "pipe": {
        "frames": ["┤", "┘", "┴", "└", "├", "┌", "┬", "┐"],
        "interval": 0.1,
    },
    "vertical_pulse": {
        "frames": ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█", "▇", "▆", "▅", "▄", "▃", "▂"],
        "interval": 0.08,
    },
    "quarter": {
        "frames": ["◴", "◷", "◶", "◵"],
        "interval": 0.12,
    },
    "hamburger": {
        "frames": ["☱", "☲", "☴"],
        "interval": 0.2,
    },
    # Emoji styles — frames are 2 columns wide; may shift adjacent text in
    # horizontal layouts. Work well as standalone spinners.
    "moon": {
        "frames": ["🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"],
        "interval": 0.1,
    },
    "clock": {
        "frames": ["🕛", "🕐", "🕑", "🕒", "🕓", "🕔", "🕕", "🕖", "🕗", "🕘", "🕙", "🕚"],
        "interval": 0.1,
    },
    "earth": {
        "frames": ["🌍", "🌎", "🌏"],
        "interval": 0.18,
    },
    "dice": {
        "frames": ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"],
        "interval": 0.15,
    },
    "snowflake": {
        "frames": ["·", "∗", "✦", "❄", "✦", "∗", "·"],
        "interval": 0.12,
    },
    "zodiac": {
        "frames": ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"],
        "interval": 0.1,
    },
    "rune": {
        "frames": ["ᚠ", "ᚢ", "ᚦ", "ᚨ", "ᚱ", "ᚲ", "ᚷ", "ᚹ", "ᚺ", "ᚾ", "ᛁ", "ᛃ"],
        "interval": 0.12,
    },
    "matrix": {
        "frames": ["ｦ", "ｱ", "ｲ", "ｳ", "ｴ", "ｵ", "ｶ", "ｷ", "ｸ", "ｹ", "ｺ", "ｻ", "ｼ", "ｽ", "ｾ", "ｿ", "ﾀ", "ﾁ", "ﾂ", "ﾃ"],
        "interval": 0.06,
    },
}


def validate_frames(frames: list[str]) -> bool:
    """Validate that frame list is non-empty and contains strings.

    Args:
        frames: List of frame characters to validate

    Returns:
        True if frames are valid, False otherwise
    """
    return (
        isinstance(frames, list)
        and len(frames) > 0
        and all(isinstance(f, str) and len(f) > 0 for f in frames)
    )
