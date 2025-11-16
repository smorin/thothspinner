#!/usr/bin/env python3
"""Event-triggered updates demo for ThothSpinner."""

import random
import time

from rich.console import Console
from rich.live import Live

from thothspinner.rich.thothspinner import ThothSpinner

console = Console()


def simulate_network_activity(spinner: ThothSpinner):
    """Simulate network activity with shimmer direction changes."""
    console.print("[cyan]Simulating network activity...[/cyan]")

    operations = [
        ("Connecting to server", "left-to-right", 10),
        ("Sending request", "left-to-right", 20),
        ("Waiting for response", "left-to-right", 30),
        ("Receiving data", "right-to-left", 50),
        ("Processing response", "right-to-left", 70),
        ("Parsing data", "left-to-right", 85),
        ("Finalizing", "left-to-right", 100),
    ]

    for message, direction, target in operations:
        spinner.set_message(text=message)
        spinner.set_shimmer_direction(direction=direction)

        current = spinner.get_component("progress").current
        for i in range(current, target + 1):
            spinner.update_progress(current=i, total=100)
            time.sleep(0.02)

        time.sleep(0.3)


def simulate_data_processing(spinner: ThothSpinner):
    """Simulate data processing with dynamic updates."""
    console.print("[cyan]Processing data batches...[/cyan]")

    action_words = [
        "Analyzing",
        "Computing",
        "Transforming",
        "Validating",
        "Optimizing",
        "Aggregating",
    ]

    for batch in range(5):
        # Random action word
        action = random.choice(action_words)
        spinner.set_message(text=f"{action} batch {batch + 1}/5")

        # Change shimmer based on operation
        if "ing" in action:
            spinner.set_shimmer_direction(direction="left-to-right")
        else:
            spinner.set_shimmer_direction(direction="right-to-left")

        # Process batch
        start = batch * 20
        end = (batch + 1) * 20
        for i in range(start, end + 1):
            spinner.update_progress(current=i, total=100)
            time.sleep(0.02)

        time.sleep(0.2)


def simulate_file_operations(spinner: ThothSpinner):
    """Simulate file operations with component updates."""
    console.print("[cyan]Performing file operations...[/cyan]")

    files = ["config.json", "data.csv", "report.pdf", "backup.zip", "cache.db"]

    for idx, filename in enumerate(files):
        # Update multiple components
        spinner.set_message(text=f"Processing {filename}")
        spinner.set_hint(text=f"File {idx + 1}/{len(files)}")

        # Alternate shimmer direction
        direction = "left-to-right" if idx % 2 == 0 else "right-to-left"
        spinner.set_shimmer_direction(direction=direction)

        # Progress for this file
        progress = int((idx + 1) / len(files) * 100)
        spinner.update_progress(current=progress, total=100)

        time.sleep(0.5)


def main():
    """Demonstrate event-triggered updates."""
    console.print("[bold magenta]ThothSpinner Event-Triggered Updates Demo[/bold magenta]\n")

    # Initialize spinner with shimmer enabled
    spinner = ThothSpinner(
        spinner_style="npm_dots",
        message_text="Initializing",
        message_shimmer=True,
        progress_format="percentage",
        timer_format="auto",
        hint_text="Processing...",
    )

    with Live(spinner, console=console, refresh_per_second=20):
        spinner.start()

        # Network activity simulation
        simulate_network_activity(spinner)

        # Reset for next demo
        spinner.reset()
        spinner.update_progress(current=0, total=100)
        time.sleep(0.5)

        # Data processing simulation
        simulate_data_processing(spinner)

        # Reset for final demo
        spinner.reset()
        spinner.update_progress(current=0, total=100)
        time.sleep(0.5)

        # File operations simulation
        simulate_file_operations(spinner)

        # Complete successfully
        spinner.success("All operations completed!")
        time.sleep(2)

    console.print("\n[green]Event-triggered updates demo complete![/green]")


if __name__ == "__main__":
    main()
