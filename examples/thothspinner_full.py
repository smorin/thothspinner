#!/usr/bin/env python3
"""Full-featured ThothSpinner demo."""

import time

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from thothspinner.rich.thothspinner import ThothSpinner

console = Console()


def demo_all_features():
    """Demonstrate all ThothSpinner features."""
    # Comprehensive configuration
    config = {
        "defaults": {
            "color": "#D97706",
            "visible": True,
            "success": {"color": "#00FF00", "behavior": "indicator"},
            "error": {"color": "#FF0000", "behavior": "indicator"},
        },
        "elements": {
            "spinner": {"style": "claude_stars", "success_icon": "✅", "error_icon": "❌"},
            "message": {"text": "Initializing system", "shimmer": {"enabled": True, "width": 3}},
            "progress": {"format": {"style": "percentage"}, "total": 100, "color": "#55FF55"},
            "timer": {"format": {"style": "auto", "precision": 1}, "color": "#FFFF55"},
            "hint": {"text": "(esc to cancel)", "color": "#888888"},
        },
        "render_order": ["spinner", "message", "progress", "timer", "hint"],
        "fade_away": {"enabled": True, "direction": "left-to-right", "interval": 0.08},
    }

    spinner = ThothSpinner(success_duration=3.0, error_duration=2.0, **config)

    with Live(spinner, console=console, refresh_per_second=20):
        spinner.start()

        # Phase 1: Initialization
        phases = [
            ("🚀 Starting application", 5),
            ("📦 Loading dependencies", 10),
            ("🔧 Configuring environment", 15),
            ("📊 Initializing database", 25),
            ("🌐 Establishing connections", 35),
            ("📝 Loading configuration", 40),
            ("🔐 Verifying credentials", 45),
            ("📈 Preparing analytics", 55),
            ("🎨 Loading UI components", 65),
            ("✨ Optimizing performance", 75),
            ("🔍 Running diagnostics", 85),
            ("✅ Finalizing setup", 95),
            ("🎉 Ready to go!", 100),
        ]

        for message, target in phases:
            spinner.set_message(text=message)

            # Change shimmer direction occasionally
            if target % 20 == 0:
                direction = "right-to-left" if target % 40 == 0 else "left-to-right"
                spinner.set_shimmer_direction(direction=direction)

            # Update progress
            current = spinner.get_component("progress").current
            for i in range(current, target + 1):
                spinner.update_progress(current=i, total=100)
                time.sleep(0.02)

            # Change spinner style mid-operation
            if target == 50:
                spinner.set_spinner_style(style="npm_dots")

            # Update hint at certain points
            if target == 25:
                spinner.set_hint(text="(this may take a moment)")
            elif target == 75:
                spinner.set_hint(text="(almost there!)")
            elif target == 95:
                spinner.set_hint(text="(completing...)")

            time.sleep(0.1)

        # Success state with fade-away
        spinner.success("System initialized successfully!")
        time.sleep(3.5)

        # Reset and demonstrate error handling
        console.print("\n[yellow]Simulating error scenario...[/yellow]")
        spinner.reset()
        spinner.set_message(text="Attempting risky operation")
        spinner.set_hint(text="(cross your fingers)")

        for i in range(51):
            spinner.update_progress(current=i, total=100)
            time.sleep(0.01)

        # Trigger error
        spinner.error("Operation failed - retrying...")
        time.sleep(2.5)

        # Reset and retry successfully
        console.print("[green]Retrying operation...[/green]")
        spinner.reset()
        spinner.set_message(text="Retrying with fallback method")

        for i in range(101):
            spinner.update_progress(current=i, total=100)
            time.sleep(0.01)

        spinner.success("Recovery successful!")
        time.sleep(2)


def demo_component_access():
    """Demonstrate direct component access."""
    console.print("\n[cyan]Direct component access demo:[/cyan]")

    spinner = ThothSpinner()

    with Live(spinner, console=console, refresh_per_second=20):
        spinner.start()

        # Direct component manipulation
        try:
            progress = spinner.get_component("progress")
            progress.set(50)
            progress.total = 200

            timer = spinner.get_component("timer")
            if hasattr(timer, "start"):
                timer.start()

            message = spinner.get_component("message")
            if hasattr(message, "update"):
                message.update(text="Direct component control")

            time.sleep(2)

            # Generic update method
            spinner.update_component("hint", text="Updated via generic method")
            spinner.update_component("progress", current=150)

            time.sleep(2)

        except KeyError as e:
            console.print(f"[red]Component not found: {e}[/red]")

        spinner.success("Component access demo complete!")
        time.sleep(1)


def demo_configuration_methods():
    """Demonstrate configuration methods."""
    console.print("\n[cyan]Configuration methods demo:[/cyan]")

    # From dictionary
    config_dict = {
        "elements": {
            "spinner": {"style": "claude_stars"},
            "message": {"text": "From config dict"},
            "progress": {"format": {"style": "fraction"}},
        }
    }

    spinner = ThothSpinner.from_dict(config_dict)

    with Live(spinner, console=console, refresh_per_second=20):
        spinner.start()

        for i in range(101):
            spinner.update_progress(current=i, total=100)
            time.sleep(0.01)

        spinner.success("Configuration demo complete!")
        time.sleep(1)


def main():
    """Run the full-featured demo."""
    title = Text("ThothSpinner Full-Featured Demo", style="bold magenta")
    panel = Panel(title, expand=False, border_style="magenta")
    console.print(panel)
    console.print()

    # All features demo
    demo_all_features()

    # Component access demo
    demo_component_access()

    # Configuration methods demo
    demo_configuration_methods()

    console.print("\n[bold green]✨ Full demo complete! ✨[/bold green]")
    console.print("[dim]All ThothSpinner features have been demonstrated.[/dim]")


if __name__ == "__main__":
    main()
