#!/usr/bin/env python3
"""Demonstration of the HintComponent.

Shows various use cases for the HintComponent including:
- Default configuration
- Custom colors and text
- Visibility toggling
- Configuration from dictionary
- Error handling with invalid colors
"""

import time

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from thothspinner.rich.components import HintComponent


def main():
    """Run the hint component demonstration."""
    console = Console()

    console.print("\n[bold cyan]═══ ThothSpinner HintComponent Demo ═══[/bold cyan]\n")

    # Basic usage
    console.print("[bold]1. Basic Usage[/bold]")
    console.print("Default hint component:")
    hint = HintComponent()
    console.print(Panel(hint, expand=False))
    console.print()

    # Custom text and colors
    console.print("[bold]2. Custom Text and Colors[/bold]")
    hints = [
        HintComponent("Press ENTER to continue", color="#00FF00"),
        HintComponent("Press Q to quit", color="#FF0000"),
        HintComponent("Press SPACE to pause", color="#FFFF00"),
        HintComponent("Press R to restart", color="#00FFFF"),
    ]

    for hint in hints:
        console.print("  • ", hint)
        time.sleep(0.3)
    console.print()

    # Configuration from dictionary
    console.print("[bold]3. Configuration from Dictionary[/bold]")
    config = {"text": "Configured from dict", "color": "#FF00FF", "visible": True}
    configured_hint = HintComponent.from_config(config)
    console.print("Config:", config)
    console.print("Result:", configured_hint)
    console.print()

    # Visibility toggle with Live display
    console.print("[bold]4. Visibility Toggle (Live Update)[/bold]")
    hint = HintComponent("This hint will toggle on/off", color="#FF00FF")
    console.print("Watch the hint toggle visibility:")

    with Live(Panel(hint, expand=False), console=console, refresh_per_second=2) as live:
        for _i in range(6):
            time.sleep(0.5)
            hint.visible = not hint.visible
            status = "[green]visible[/green]" if hint.visible else "[red]hidden[/red]"
            live.update(Panel(hint, title=f"Status: {status}", expand=False))
    console.print()

    # Integration with Progress
    console.print("[bold]5. Integration with Rich Progress[/bold]")
    hint = HintComponent("Press Ctrl+C to cancel download", color="#FFA500")

    console.print(hint)
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Downloading...", total=100)
        for _i in range(100):
            progress.update(task, advance=1)
            time.sleep(0.02)
    console.print("[green]✓[/green] Download complete!")
    console.print()

    # Dynamic updates
    console.print("[bold]6. Dynamic Property Updates[/bold]")
    hint = HintComponent("Initial text", color="#888888")
    console.print("Initial state:", hint)

    # Update properties
    hint.update(text="Updated text", color="#00FF00")
    console.print("After update: ", hint)

    # Update individual properties
    hint.text = "Final text"
    hint.color = "#FF00FF"
    console.print("Final state:  ", hint)
    console.print()

    # Error handling demonstration
    console.print("[bold]7. Error Handling[/bold]")
    console.print("Attempting to create hints with invalid colors:")

    invalid_colors = ["red", "#FFF", "123456", "#GGGGGG"]
    for bad_color in invalid_colors:
        try:
            HintComponent(text="Test", color=bad_color)
            console.print(f"  [red]✗[/red] {bad_color!r} - Should have failed!")
        except ValueError as e:
            console.print(f"  [green]✓[/green] {bad_color!r} - Correctly rejected: {e}")

    console.print("\n[bold green]Demo completed successfully![/bold green]")
    console.print("[dim]HintComponent is ready for use in your Rich applications.[/dim]\n")


if __name__ == "__main__":
    main()
