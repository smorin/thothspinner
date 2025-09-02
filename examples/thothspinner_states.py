#!/usr/bin/env python3
"""State transitions demo for ThothSpinner."""

import time

from rich.console import Console
from rich.live import Live

from thothspinner.rich.thothspinner import ThothSpinner

console = Console()


def main():
    """Demonstrate state transitions in ThothSpinner."""
    # Initialize with auto-clear durations
    spinner = ThothSpinner(
        spinner_style="claude_stars",
        message_text="Working on task",
        progress_format="fraction",
        timer_format="mm:ss",
        success_duration=2.0,  # Auto-clear after 2 seconds
        error_duration=3.0     # Auto-clear after 3 seconds
    )
    
    with Live(spinner, console=console, refresh_per_second=20):
        # Start in in_progress state
        console.print("[blue]Starting in IN_PROGRESS state[/blue]")
        spinner.start()
        
        # Simulate work
        for i in range(51):
            spinner.update_progress(current=i, total=100)
            time.sleep(0.02)
        
        # Transition to success
        console.print("[green]Transitioning to SUCCESS state[/green]")
        spinner.success("First task completed!", duration=2.0)
        time.sleep(2.5)  # Will auto-clear after 2 seconds
        
        # Reset to in_progress
        console.print("[yellow]Resetting to IN_PROGRESS state[/yellow]")
        spinner.reset()
        spinner.set_message(text="Working on second task")
        
        # Simulate more work
        for i in range(51, 76):
            spinner.update_progress(current=i, total=100)
            time.sleep(0.02)
        
        # Transition to error
        console.print("[red]Transitioning to ERROR state[/red]")
        spinner.error("Connection failed", duration=3.0)
        time.sleep(3.5)  # Will auto-clear after 3 seconds
        
        # Reset and try again
        console.print("[cyan]Resetting and trying again[/cyan]")
        spinner.reset()
        spinner.set_message(text="Retrying operation")
        
        # Complete successfully
        for i in range(76, 101):
            spinner.update_progress(current=i, total=100)
            time.sleep(0.02)
        
        spinner.success("All tasks completed successfully!")
        time.sleep(2)
        
        # Manual stop
        console.print("[dim]Stopping spinner[/dim]")
        spinner.stop()  # Using stop() alias


if __name__ == "__main__":
    main()