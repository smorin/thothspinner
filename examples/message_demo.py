#!/usr/bin/env python3
"""Basic message component demonstration."""

import time

from rich.console import Console
from rich.live import Live

from thothspinner.rich.components import MessageComponent

console = Console()


def main():
    """Run basic message component demo."""
    print("🎯 Basic Message Component Demo\n")

    # Create message component with default settings
    message = MessageComponent(
        action_words=["Processing", "Analyzing", "Computing", "Calculating"],
        interval={"min": 0.5, "max": 2.0},
        color="#D97706",
        suffix="…",
    )

    print("Running message component with rotating words for 10 seconds...")
    print("Words will change randomly every 0.5-2.0 seconds\n")

    with Live(message, console=console, refresh_per_second=20):
        time.sleep(10)

    print("\n✅ Demo complete!")


if __name__ == "__main__":
    main()
