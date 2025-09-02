#!/usr/bin/env python3
"""Configuration-based ThothSpinner setup example."""

import time

from rich.console import Console
from rich.live import Live

from thothspinner.rich.thothspinner import ThothSpinner

console = Console()


def main():
    """Demonstrate configuration-based ThothSpinner setup."""
    # Configuration dictionary
    config = {
        "defaults": {
            "color": "#D97706",
            "visible": True
        },
        "elements": {
            "spinner": {
                "style": "npm_dots",
                "success_icon": "✓",
                "error_icon": "✗"
            },
            "message": {
                "text": "Processing",
                "shimmer": {
                    "enabled": True,
                    "width": 3
                }
            },
            "progress": {
                "format": {
                    "style": "percentage"
                },
                "total": 100
            },
            "timer": {
                "format": {
                    "style": "auto"
                }
            },
            "hint": {
                "text": "(esc to cancel)",
                "color": "#888888"
            }
        },
        "render_order": ["spinner", "message", "progress", "timer", "hint"],
        "fade_away": {
            "enabled": True,
            "direction": "left-to-right",
            "interval": 0.05
        }
    }
    
    # Create from configuration
    spinner = ThothSpinner(**config)
    
    with Live(spinner, console=console, refresh_per_second=20):
        spinner.start()
        
        # Simulate different phases of work
        phases = [
            ("Initializing", 25),
            ("Loading data", 50),
            ("Processing", 75),
            ("Finalizing", 100)
        ]
        
        for phase, target in phases:
            spinner.set_message(text=phase)
            
            current = spinner.get_component("progress").current
            for i in range(current, target + 1):
                spinner.update_progress(current=i, total=100)
                time.sleep(0.03)
            
            time.sleep(0.5)
        
        # Success with fade-away
        spinner.success("Configuration example completed!")
        time.sleep(3)


if __name__ == "__main__":
    main()