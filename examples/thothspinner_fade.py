#!/usr/bin/env python3
"""Fade-away animation demo for ThothSpinner."""

import time

from rich.console import Console
from rich.live import Live

from thothspinner.rich.thothspinner import ThothSpinner

console = Console()


def demo_left_to_right_fade():
    """Demonstrate left-to-right fade animation."""
    config = {
        "fade_away": {
            "enabled": True,
            "direction": "left-to-right",
            "interval": 0.1  # 100ms between each element
        }
    }
    
    spinner = ThothSpinner(
        message_text="Left to right fade",
        **config
    )
    
    console.print("\n[cyan]Left-to-right fade animation:[/cyan]")
    
    with Live(spinner, console=console, refresh_per_second=20):
        spinner.start()
        
        for i in range(101):
            spinner.update_progress(current=i, total=100)
            time.sleep(0.01)
        
        # Success triggers fade-away
        spinner.success("Fading out left to right...")
        time.sleep(2)  # Watch the fade animation


def demo_right_to_left_fade():
    """Demonstrate right-to-left fade animation."""
    config = {
        "fade_away": {
            "enabled": True,
            "direction": "right-to-left",
            "interval": 0.1
        }
    }
    
    spinner = ThothSpinner(
        message_text="Right to left fade",
        **config
    )
    
    console.print("\n[cyan]Right-to-left fade animation:[/cyan]")
    
    with Live(spinner, console=console, refresh_per_second=20):
        spinner.start()
        
        for i in range(101):
            spinner.update_progress(current=i, total=100)
            time.sleep(0.01)
        
        # Error also triggers fade-away
        spinner.error("Fading out right to left...")
        time.sleep(2)


def demo_instant_disappear():
    """Demonstrate instant disappear (no fade)."""
    config = {
        "fade_away": {
            "enabled": False  # Instant disappear
        }
    }
    
    spinner = ThothSpinner(
        message_text="Instant disappear",
        **config
    )
    
    console.print("\n[cyan]Instant disappear (no fade):[/cyan]")
    
    with Live(spinner, console=console, refresh_per_second=20):
        spinner.start()
        
        for i in range(101):
            spinner.update_progress(current=i, total=100)
            time.sleep(0.01)
        
        # Success with instant disappear
        spinner.success("Disappearing instantly!")
        time.sleep(0.5)
        spinner.clear()


def demo_fast_fade():
    """Demonstrate fast fade animation."""
    config = {
        "fade_away": {
            "enabled": True,
            "direction": "left-to-right",
            "interval": 0.02  # Very fast fade (20ms)
        }
    }
    
    spinner = ThothSpinner(
        message_text="Fast fade animation",
        **config
    )
    
    console.print("\n[cyan]Fast fade animation (20ms interval):[/cyan]")
    
    with Live(spinner, console=console, refresh_per_second=20):
        spinner.start()
        
        for i in range(101):
            spinner.update_progress(current=i, total=100)
            time.sleep(0.01)
        
        spinner.success("Rapid fade-away!")
        time.sleep(1)


def main():
    """Run all fade animation demos."""
    console.print("[bold magenta]ThothSpinner Fade-Away Animation Demo[/bold magenta]")
    
    demo_left_to_right_fade()
    time.sleep(1)
    
    demo_right_to_left_fade()
    time.sleep(1)
    
    demo_instant_disappear()
    time.sleep(1)
    
    demo_fast_fade()
    
    console.print("\n[green]Fade animation demo complete![/green]")


if __name__ == "__main__":
    main()