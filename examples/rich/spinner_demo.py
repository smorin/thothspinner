"""Demonstration of SpinnerComponent capabilities."""

from __future__ import annotations

import signal
import sys
import time

from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.text import Text

from thothspinner.rich.components import SpinnerComponent


def styles_demo(console: Console) -> None:
    """Demo different spinner styles."""
    console.print("[bold cyan]Spinner Styles Demo[/bold cyan]\n")

    styles = ["npm_dots", "claude_stars", "classic", "dots", "arrows", "circle", "star"]
    for style in styles:
        spinner = SpinnerComponent(style=style)
        # Create table to show label and spinner side by side
        table = Table.grid(padding=1)
        table.add_row(Text(f"{style:15}"), spinner)

        with Live(table, console=console, refresh_per_second=20, transient=True):
            time.sleep(2)


def state_transitions_demo(console: Console) -> None:
    """Demo state transitions with proper Live usage."""
    console.print("\n[bold cyan]State Transitions Demo[/bold cyan]\n")

    spinner = SpinnerComponent()
    status_text = Text("Processing...")

    # Combine spinner and text in a table
    display = Table.grid(padding=1)
    display.add_row(spinner, status_text)

    with Live(display, console=console, refresh_per_second=20):
        # Processing state
        time.sleep(2)

        # Success state
        spinner.success()
        status_text.plain = "Done!"
        time.sleep(1)

        # Reset and retry
        spinner.reset()
        status_text.plain = "Retrying..."
        time.sleep(2)

        # Error state
        spinner.error()
        status_text.plain = "Failed!"
        time.sleep(1)


def custom_frames_demo(console: Console) -> None:
    """Demo custom frames and speed control."""
    console.print("\n[bold cyan]Custom Frames Demo[/bold cyan]\n")

    # Earth rotation spinner
    earth_spinner = SpinnerComponent(frames=["🌍", "🌎", "🌏"], interval=0.3)

    # Moon phases spinner
    moon_spinner = SpinnerComponent(
        frames=["🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"], interval=0.2
    )

    # Clock spinner
    clock_spinner = SpinnerComponent(
        frames=["🕐", "🕑", "🕒", "🕓", "🕔", "🕕", "🕖", "🕗", "🕘", "🕙", "🕚", "🕛"],
        interval=0.1,
    )

    # Create table for side-by-side display
    table = Table.grid(padding=2)
    table.add_row(
        Text("Earth:"),
        earth_spinner,
        Text("   Moon:"),
        moon_spinner,
        Text("   Clock:"),
        clock_spinner,
    )

    with Live(table, console=console, refresh_per_second=20):
        time.sleep(5)


def speed_demo(console: Console) -> None:
    """Demo speed multiplier effect."""
    console.print("\n[bold cyan]Speed Multiplier Demo[/bold cyan]\n")

    # Create spinners with different speeds
    slow_spinner = SpinnerComponent(style="npm_dots", speed=0.5)
    normal_spinner = SpinnerComponent(style="npm_dots", speed=1.0)
    fast_spinner = SpinnerComponent(style="npm_dots", speed=2.0)

    table = Table.grid(padding=2)
    table.add_row(
        Text("0.5x speed:"),
        slow_spinner,
        Text("   1.0x speed:"),
        normal_spinner,
        Text("   2.0x speed:"),
        fast_spinner,
    )

    with Live(table, console=console, refresh_per_second=20):
        time.sleep(5)


def interrupt_demo(console: Console) -> None:
    """Demo interrupt handling in user code."""
    console.print("\n[bold cyan]Interrupt Demo (Press Ctrl+C)[/bold cyan]\n")

    spinner = SpinnerComponent(style="npm_dots", color="#FFA500")
    status = Text("Running... Press Ctrl+C to stop")

    table = Table.grid(padding=1)
    table.add_row(spinner, status)

    def signal_handler(signum, frame):
        """Handle interrupt gracefully."""
        spinner.error()
        status.plain = "Interrupted by user"
        console.print("\n[yellow]Process interrupted![/yellow]")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    with Live(table, console=console, refresh_per_second=20):
        try:
            time.sleep(10)
            spinner.success()
            status.plain = "Completed successfully!"
            time.sleep(1)
        except KeyboardInterrupt:
            pass  # Handled by signal handler


def colors_demo(console: Console) -> None:
    """Demo different color configurations."""
    console.print("\n[bold cyan]Colors Demo[/bold cyan]\n")

    colors = [
        ("#FF0000", "Red"),
        ("#00FF00", "Green"),
        ("#0000FF", "Blue"),
        ("#FFA500", "Orange"),
        ("#FF00FF", "Magenta"),
        ("#00FFFF", "Cyan"),
        ("#D97706", "Claude Orange"),
    ]

    for color, name in colors:
        spinner = SpinnerComponent(style="star", color=color)
        table = Table.grid(padding=1)
        table.add_row(Text(f"{name:15}"), spinner)

        with Live(table, console=console, refresh_per_second=20, transient=True):
            time.sleep(1)


def claude_stars_demo(console: Console) -> None:
    """Featured demo of the claude_stars spinner."""
    console.print("\n[bold cyan]Featured: Claude Stars Spinner[/bold cyan]\n")

    # Show claude_stars with different colors
    spinner1 = SpinnerComponent(style="claude_stars", color="#D97706")  # Claude orange
    spinner2 = SpinnerComponent(style="claude_stars", color="#FFA500")  # Light orange
    spinner3 = SpinnerComponent(style="claude_stars", color="#00FFFF")  # Cyan

    table = Table.grid(padding=2)
    table.add_row(
        Text("Claude Orange:"),
        spinner1,
        Text("   Light Orange:"),
        spinner2,
        Text("   Cyan:"),
        spinner3,
    )

    with Live(table, console=console, refresh_per_second=20):
        time.sleep(3)

    # Show claude_stars with state transitions
    console.print("\n[dim]Claude Stars with state transitions:[/dim]")
    spinner = SpinnerComponent(style="claude_stars", color="#D97706")
    status = Text("Processing with Claude Stars...")

    display = Table.grid(padding=1)
    display.add_row(spinner, status)

    with Live(display, console=console, refresh_per_second=20):
        time.sleep(2)
        spinner.success()
        status.plain = "Claude Stars complete!"
        time.sleep(1)


def main() -> None:
    """Run all spinner demos."""
    console = Console()

    console.print("\n[bold magenta]═══ ThothSpinner Component Demo ═══[/bold magenta]\n")

    # Feature claude_stars first
    claude_stars_demo(console)

    # Run other demos
    styles_demo(console)
    state_transitions_demo(console)
    custom_frames_demo(console)
    speed_demo(console)
    colors_demo(console)
    interrupt_demo(console)

    console.print("\n[bold green]✓ All demos completed![/bold green]")


if __name__ == "__main__":
    main()
