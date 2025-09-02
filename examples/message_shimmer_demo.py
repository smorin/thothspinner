#!/usr/bin/env python3
"""Message component shimmer direction demonstration."""

import time

from rich.console import Console
from rich.live import Live

from thothspinner.rich.components import MessageComponent

console = Console()


def main():
    """Run shimmer direction demo."""
    print("✨ Message Component Shimmer Direction Demo\n")

    # Create message component with shimmer effect
    message = MessageComponent(
        action_words=["Downloading", "Uploading", "Syncing", "Transferring"],
        interval={"min": 1.0, "max": 2.0},
        color="#D97706",
        shimmer={
            "enabled": True,
            "width": 3,
            "light_color": "#FFA500",
            "speed": 1.0,
            "reverse": False,  # Start with left-to-right
        },
        suffix="…",
    )

    print("Demonstrating shimmer direction changes:")
    print("- First 3 seconds: Left-to-right shimmer")
    print("- Next 3 seconds: Right-to-left shimmer")
    print("- Next 3 seconds: Toggle back to left-to-right")
    print("- Final 3 seconds: Disable shimmer\n")

    with Live(message, console=console, refresh_per_second=20):
        # Left-to-right for 3 seconds
        time.sleep(3)

        # Change to right-to-left
        message.reverse_shimmer = True
        time.sleep(3)

        # Toggle back to left-to-right
        message.reverse_shimmer = False
        time.sleep(3)

        # Disable shimmer
        message.shimmer_enabled = False
        time.sleep(3)

    print("\n✅ Shimmer demo complete!")


if __name__ == "__main__":
    main()
