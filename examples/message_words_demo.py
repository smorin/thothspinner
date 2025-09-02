#!/usr/bin/env python3
"""Message component custom word list demonstration."""

import time

from rich.console import Console
from rich.live import Live

from thothspinner.rich.components import MessageComponent

console = Console()


def main():
    """Run custom word list demo."""
    print("📝 Message Component Word List Management Demo\n")

    # Demo 1: Replace mode
    print("1️⃣ Replace mode - using only custom words:")
    message = MessageComponent(
        action_words={
            "mode": "replace",
            "words": ["Compiling", "Building", "Linking", "Optimizing"],
        },
        interval={"min": 0.5, "max": 1.0},
        shimmer={"enabled": True},
    )

    with Live(message, console=console, refresh_per_second=20):
        time.sleep(5)

    print("\n2️⃣ Add mode - appending to default 87 words:")
    message2 = MessageComponent(
        action_words={"mode": "add", "words": ["Deploying", "Migrating", "Scaling"]},
        interval={"min": 0.5, "max": 1.0},
        shimmer={"enabled": True},
    )

    print(f"Total words available: {len(message2.action_words)}")
    with Live(message2, console=console, refresh_per_second=20):
        time.sleep(5)

    print("\n3️⃣ Runtime word list modification:")
    message3 = MessageComponent(
        action_words=["Starting", "Initializing"], interval={"min": 0.5, "max": 1.0}
    )

    with Live(message3, console=console, refresh_per_second=20):
        print("Initial words: Starting, Initializing")
        time.sleep(3)

        # Replace entire word list
        message3.action_words = ["Replaced1", "Replaced2", "Replaced3"]
        print("Replaced word list with: Replaced1, Replaced2, Replaced3")
        time.sleep(3)

        # Extend with more words
        message3.extend_action_words(["Extended1", "Extended2"])
        print("Extended with: Extended1, Extended2")
        time.sleep(3)

    print("\n✅ Word list management demo complete!")


if __name__ == "__main__":
    main()
