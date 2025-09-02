#!/usr/bin/env python3
"""Progress component demonstration."""

import time

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

from thothspinner.rich.components import ProgressComponent


def demo_basic_progress():
    """Demonstrate basic progress counter."""
    console = Console()
    console.print("[bold cyan]Basic Progress Counter Demo[/bold cyan]\n")

    progress = ProgressComponent(current=0, total=100, format={"style": "percentage"})

    with Live(progress, console=console, refresh_per_second=10):
        for i in range(101):
            progress.set(i)
            time.sleep(0.02)

    progress.success("Complete!")
    console.print(progress)
    console.print()


def demo_all_formats():
    """Demonstrate all progress formats."""
    console = Console()
    console.print("[bold cyan]All Progress Formats Demo[/bold cyan]\n")

    formats = ["fraction", "percentage", "of_text", "count_only", "ratio"]
    total = 50

    # Create table of progress bars
    table = Table(title="Progress Format Styles", show_header=True)
    table.add_column("Format", style="cyan")
    table.add_column("Display", style="green")

    for format_style in formats:
        progress = ProgressComponent(
            current=35, total=total, format={"style": format_style}, color="#00FF00"
        )
        table.add_row(format_style, progress)

    console.print(table)
    console.print()


def demo_zero_padding():
    """Demonstrate zero padding feature."""
    console = Console()
    console.print("[bold cyan]Zero Padding Demo[/bold cyan]\n")

    # Without padding
    progress1 = ProgressComponent(current=7, total=1000, format={"style": "fraction"})
    console.print("Without padding:", progress1)

    # With padding
    progress2 = ProgressComponent(
        current=7, total=1000, format={"style": "fraction"}, zero_pad=True
    )
    console.print("With padding:   ", progress2)
    console.print()


def demo_animated_progress():
    """Demonstrate animated progress with multiple bars."""
    console = Console()
    console.print("[bold cyan]Multiple Progress Bars Demo[/bold cyan]\n")

    # Create multiple progress bars
    download = ProgressComponent(total=100, format={"style": "percentage"}, color="#00FFFF")
    processing = ProgressComponent(total=100, format={"style": "fraction"}, color="#FFFF00")
    upload = ProgressComponent(total=100, format={"style": "of_text"}, color="#FF00FF")

    # Create layout table
    table = Table.grid(padding=1)
    table.add_column(style="cyan", width=12)
    table.add_column()

    table.add_row("Download:", download)
    table.add_row("Processing:", processing)
    table.add_row("Upload:", upload)

    with Live(table, console=console, refresh_per_second=20):
        # Simulate different speeds
        for i in range(101):
            if i <= 100:
                download.set(i)
            if i >= 10 and i <= 90:
                processing.set(i - 10)
            if i >= 30:
                upload.set(i - 30)
            time.sleep(0.03)

        # Complete remaining
        for i in range(91, 101):
            processing.set(i - 10)
            time.sleep(0.02)

    # Mark all as complete
    download.success()
    processing.success()
    upload.success()

    console.print(Panel(table, title="[green]All Complete![/green]"))
    console.print()


def demo_state_transitions():
    """Demonstrate state transitions."""
    console = Console()
    console.print("[bold cyan]State Transitions Demo[/bold cyan]\n")

    progress = ProgressComponent(total=100, format={"style": "percentage"})

    # Show in-progress state
    console.print("In Progress:")
    with Live(progress, console=console, refresh_per_second=10):
        for i in range(51):
            progress.set(i)
            time.sleep(0.01)

    # Show error state
    progress.error("Connection Failed!")
    console.print("Error State:", progress)

    # Reset and complete
    progress.reset()
    progress.set(100)
    progress.success("Download Complete!")
    console.print("Success State:", progress)
    console.print()


if __name__ == "__main__":
    console = Console()

    try:
        console.print("[bold magenta]ThothSpinner Progress Component Demo[/bold magenta]\n")

        demo_basic_progress()
        demo_all_formats()
        demo_zero_padding()
        demo_animated_progress()
        demo_state_transitions()

        console.print("[bold green]✓ All demos completed successfully![/bold green]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
