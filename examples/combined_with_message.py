#!/usr/bin/env python3
"""Combined components with MessageComponent demonstration."""

import time

from rich.console import Console
from rich.live import Live
from rich.table import Table

from thothspinner.rich.components import (
    HintComponent,
    MessageComponent,
    ProgressComponent,
    SpinnerComponent,
    TimerComponent,
)

console = Console()


def main():
    """Run combined components demo."""
    print("🎨 Combined Components with MessageComponent Demo\n")

    # Create all components
    spinner = SpinnerComponent(style="npm_dots", color="#D97706")
    message = MessageComponent(
        action_words=["Downloading", "Processing", "Analyzing", "Optimizing"],
        interval={"min": 0.8, "max": 2.0},
        shimmer={"enabled": True, "width": 3},
    )
    progress = ProgressComponent(total=100, format={"style": "percentage"})
    timer = TimerComponent(format={"style": "auto"})
    hint = HintComponent(text="(press ctrl+c to cancel)", color="#888888")

    print("Demonstrating all components working together:")
    print("- SpinnerComponent: Animated dots")
    print("- MessageComponent: Rotating words with shimmer")
    print("- ProgressComponent: Percentage counter")
    print("- TimerComponent: Elapsed time")
    print("- HintComponent: Helper text\n")

    # Start the timer
    timer.start()

    # Create a table to layout components
    def create_layout():
        table = Table.grid(padding=1)
        table.add_column(style="cyan", justify="center")
        table.add_column(style="white", justify="left")
        table.add_column(style="green", justify="center")
        table.add_column(style="yellow", justify="center")
        table.add_column(style="dim", justify="left")
        table.add_row(spinner, message, progress, timer, hint)
        return table

    with Live(create_layout(), console=console, refresh_per_second=20) as live:
        # Simulate progress
        for i in range(101):
            progress.set(i)

            # Update message at certain points
            if i == 25:
                message.update(text="Optimizing cache")
            elif i == 50:
                message.update(text="Building index")
                message.reverse_shimmer = True
            elif i == 75:
                message.update(trigger_new=True)
                message.reverse_shimmer = False

            # Update live display
            live.update(create_layout())
            time.sleep(0.1)

        # Show success state
        spinner.success()
        message.success("All done!")
        live.update(create_layout())
        time.sleep(2)

    print("\n✅ Combined components demo complete!")


if __name__ == "__main__":
    main()
