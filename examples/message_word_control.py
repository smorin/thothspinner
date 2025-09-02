#!/usr/bin/env python3
"""Message component word control demonstration."""

import time

from rich.console import Console
from rich.live import Live

from thothspinner.rich.components import MessageComponent

console = Console()


def main():
    """Run word control demo."""
    print("🎮 Message Component Word Control Demo\n")

    # Create message component
    message = MessageComponent(
        action_words=["Analyzing", "Processing", "Computing", "Calculating", "Thinking"],
        interval={"min": 1.0, "max": 2.0},
        shimmer={"enabled": True, "width": 3},
    )

    print("Demonstrating word control methods:")
    print("- update(text='Custom') - Set custom text")
    print("- update(trigger_new=True) - Force new random word")
    print("- update(reverse_shimmer=True) - Change shimmer direction\n")

    with Live(message, console=console, refresh_per_second=20):
        print("1️⃣ Default rotation for 3 seconds...")
        time.sleep(3)

        print("2️⃣ Setting custom text: 'Thinking deeply'")
        message.update(text="Thinking deeply")
        time.sleep(3)

        print("3️⃣ Forcing new random word selection")
        message.update(trigger_new=True)
        time.sleep(2)

        print("4️⃣ Another forced word change")
        message.update(trigger_new=True)
        time.sleep(2)

        print("5️⃣ Custom text with shimmer direction change")
        message.update(text="Reversing", reverse_shimmer=True)
        time.sleep(3)

        print("6️⃣ Multiple updates at once")
        message.update(text="Multi-update", reverse_shimmer=False)
        time.sleep(2)

        print("7️⃣ Back to random rotation")
        message.update(trigger_new=True)
        time.sleep(3)

    print("\n✅ Word control demo complete!")


if __name__ == "__main__":
    main()
