#!/usr/bin/env python3
"""Basic ThothSpinner usage example."""

import time

from rich.console import Console
from rich.live import Live

from thothspinner.rich.thothspinner import ThothSpinner

console = Console()


def main():
    """Demonstrate basic ThothSpinner usage."""
    # Simple initialization with defaults
    spinner = ThothSpinner()
    
    with Live(spinner, console=console, refresh_per_second=20):
        spinner.start()
        
        # Simulate work with progress updates
        for i in range(101):
            spinner.update_progress(current=i, total=100)
            time.sleep(0.05)
        
        # Show success state
        spinner.success("Task completed!")
        time.sleep(2)


if __name__ == "__main__":
    main()