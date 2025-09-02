#!/usr/bin/env python3
"""Timer component demonstration."""

import time

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

from thothspinner.rich.components import TimerComponent


def demo_basic_timer():
    """Demonstrate basic timer."""
    console = Console()
    console.print("[bold cyan]Basic Timer Demo[/bold cyan]\n")

    timer = TimerComponent(format={"style": "auto"})
    timer.start()

    console.print("Timer running for 3 seconds...")
    with Live(timer, console=console, refresh_per_second=10):
        time.sleep(3)

    timer.stop()
    console.print(f"Final time: {timer}")
    console.print()


def demo_all_formats():
    """Demonstrate all timer formats."""
    console = Console()
    console.print("[bold cyan]All Timer Formats Demo[/bold cyan]\n")

    formats = [
        ("seconds", 5.789),
        ("seconds_decimal", 5.789),
        ("seconds_precise", 5.789),
        ("milliseconds", 1.234),
        ("mm:ss", 83),
        ("hh:mm:ss", 3723),
        ("compact", 3723),
        ("full_ms", 63.456),
        ("auto", 125),
    ]

    table = Table(title="Timer Format Styles", show_header=True)
    table.add_column("Format", style="cyan")
    table.add_column("Example Time", style="yellow")
    table.add_column("Display", style="green")

    for format_style, elapsed in formats:
        timer = TimerComponent(format={"style": format_style})
        display = timer._format_time(elapsed)
        table.add_row(format_style, f"{elapsed}s", display)

    console.print(table)
    console.print()


def demo_auto_format_transitions():
    """Demonstrate auto format transitions."""
    console = Console()
    console.print("[bold cyan]Auto Format Transitions Demo[/bold cyan]\n")
    console.print("Watch the format change as time progresses:\n")

    timer = TimerComponent(format={"style": "auto"}, color="#00FFFF")
    timer.start()

    table = Table.grid(padding=1)
    table.add_column(width=20)
    table.add_column()
    table.add_row("Elapsed Time:", timer)

    with Live(table, console=console, refresh_per_second=10):
        # Show seconds format (< 60s)
        time.sleep(3)

    console.print("Format: seconds (< 60s)")
    console.print()


def demo_timer_controls():
    """Demonstrate timer control methods."""
    console = Console()
    console.print("[bold cyan]Timer Controls Demo[/bold cyan]\n")

    timer = TimerComponent(format={"style": "seconds_decimal", "precision": 1})

    # Start
    console.print("Starting timer...")
    timer.start()
    with Live(timer, console=console, refresh_per_second=10):
        time.sleep(1.5)

    # Stop
    timer.stop()
    console.print(f"Stopped at: {timer}")
    time.sleep(1)

    # Resume
    console.print("Resuming timer...")
    timer.resume()
    with Live(timer, console=console, refresh_per_second=10):
        time.sleep(1.5)

    # Stop again
    timer.stop()
    console.print(f"Final time: {timer}")

    # Reset
    timer.reset()
    console.print(f"After reset: {timer}")
    console.print()


def demo_multiple_timers():
    """Demonstrate multiple timers with different formats."""
    console = Console()
    console.print("[bold cyan]Multiple Timers Demo[/bold cyan]\n")

    # Create timers with different formats
    timer1 = TimerComponent(format={"style": "seconds"}, color="#FF0000")
    timer2 = TimerComponent(format={"style": "mm:ss"}, color="#00FF00")
    timer3 = TimerComponent(format={"style": "full_ms"}, color="#0000FF")

    # Start all timers
    timer1.start()
    timer2.start()
    timer3.start()

    # Create layout
    table = Table.grid(padding=1)
    table.add_column(style="cyan", width=15)
    table.add_column()

    table.add_row("Seconds:", timer1)
    table.add_row("Minutes:", timer2)
    table.add_row("Milliseconds:", timer3)

    console.print("Running multiple timers for 5 seconds...\n")

    with Live(table, console=console, refresh_per_second=20):
        time.sleep(5)

    # Stop all timers
    timer1.success()
    timer2.success()
    timer3.success()

    console.print(Panel(table, title="[green]Timers Complete[/green]"))
    console.print()


def demo_precision_settings():
    """Demonstrate precision settings."""
    console = Console()
    console.print("[bold cyan]Precision Settings Demo[/bold cyan]\n")

    elapsed = 3.456789

    table = Table(title="Decimal Precision", show_header=True)
    table.add_column("Precision", style="cyan")
    table.add_column("Display", style="green")

    for precision in range(4):
        timer = TimerComponent(format={"style": "seconds_decimal", "precision": precision})
        display = timer._format_time(elapsed)
        table.add_row(f"{precision} decimal(s)", display)

    console.print(table)
    console.print()


def demo_state_management():
    """Demonstrate timer state management."""
    console = Console()
    console.print("[bold cyan]Timer State Management Demo[/bold cyan]\n")

    timer = TimerComponent(format={"style": "seconds_decimal", "precision": 1})

    # In progress state
    console.print("Starting timer (in_progress state)...")
    timer.start()

    with Live(timer, console=console, refresh_per_second=10):
        time.sleep(2)

    # Success state (stops timer)
    timer.success()
    console.print(f"Success state (timer stopped): {timer}")

    # Reset and error state
    timer.reset()
    timer.start()
    time.sleep(1)
    timer.error()
    console.print(f"Error state (timer stopped): {timer}")
    console.print()


if __name__ == "__main__":
    console = Console()

    try:
        console.print("[bold magenta]ThothSpinner Timer Component Demo[/bold magenta]\n")

        demo_basic_timer()
        demo_all_formats()
        demo_auto_format_transitions()
        demo_timer_controls()
        demo_multiple_timers()
        demo_precision_settings()
        demo_state_management()

        console.print("[bold green]✓ All demos completed successfully![/bold green]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
