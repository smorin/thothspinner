#!/usr/bin/env python3
"""Message component state transitions demonstration."""

import time

from rich.console import Console
from rich.live import Live

from thothspinner.rich.components import MessageComponent

console = Console()


def main():
    """Run state transitions demo."""
    print("🚦 Message Component State Transitions Demo\n")

    # Create message component
    message = MessageComponent(
        action_words=["Processing", "Working", "Computing", "Analyzing"],
        interval={"min": 0.5, "max": 1.5},
        shimmer={"enabled": True, "width": 3},
    )

    print("Demonstrating state transitions:")
    print("- in_progress: Animated words with shimmer")
    print("- success: Static success message")
    print("- error: Static error message")
    print("- reset: Return to in_progress\n")

    with Live(message, console=console, refresh_per_second=20):
        print(f"1️⃣ Initial state: {message.state}")
        print("   Showing animated words with shimmer for 5 seconds...")
        time.sleep(5)

        print("\n2️⃣ Transitioning to success state")
        message.success("✅ Operation completed successfully!")
        print(f"   Current state: {message.state}")
        print("   Showing static success message for 3 seconds...")
        time.sleep(3)

        print("\n3️⃣ Resetting to in_progress")
        message.reset()
        print(f"   Current state: {message.state}")
        print("   Back to animated words for 3 seconds...")
        time.sleep(3)

        print("\n4️⃣ Transitioning to error state")
        message.error("❌ Operation failed!")
        print(f"   Current state: {message.state}")
        print("   Showing static error message for 3 seconds...")
        time.sleep(3)

        print("\n5️⃣ Resetting again")
        message.reset()
        print(f"   Current state: {message.state}")
        print("   Back to animated words for 3 seconds...")
        time.sleep(3)

        print("\n6️⃣ Success with custom message")
        message.success("🎉 All tasks completed!")
        print(f"   Current state: {message.state}")
        time.sleep(3)

    print("\n✅ State transitions demo complete!")


if __name__ == "__main__":
    main()
