#!/usr/bin/env python3
"""Combined Progress and Timer components demonstration."""

import time

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

from thothspinner.rich.components import ProgressComponent, TimerComponent


def demo_download_with_timer():
    """Simulate a download with progress and timer."""
    console = Console()
    console.print("[bold cyan]Download Simulation Demo[/bold cyan]\n")

    # Create components
    progress = ProgressComponent(total=100, format={"style": "percentage"}, color="#00FF00")
    timer = TimerComponent(format={"style": "auto"}, color="#FFFF00")

    # Create layout
    table = Table.grid(padding=1)
    table.add_column(style="cyan", width=15)
    table.add_column(width=10)

    table.add_row("Progress:", progress)
    table.add_row("Elapsed:", timer)

    panel = Panel(table, title="Downloading file.txt")

    # Start download simulation
    timer.start()

    with Live(panel, console=console, refresh_per_second=20):
        for i in range(101):
            progress.set(i)
            # Simulate variable download speed
            if i < 30:
                time.sleep(0.05)  # Slow start
            elif i < 80:
                time.sleep(0.02)  # Fast middle
            else:
                time.sleep(0.03)  # Slow end

    # Mark complete
    progress.success("Complete!")
    timer.success()

    console.print(Panel(table, title="[green]Download Complete![/green]"))
    console.print(f"Total time: {timer}")
    console.print()


def demo_multi_task_processing():
    """Demonstrate multiple tasks with progress and timing."""
    console = Console()
    console.print("[bold cyan]Multi-Task Processing Demo[/bold cyan]\n")

    tasks = [
        ("Analyzing", 50, "#FF6B6B"),
        ("Processing", 75, "#4ECDC4"),
        ("Optimizing", 60, "#45B7D1"),
        ("Finalizing", 40, "#96CEB4"),
    ]

    # Create components for each task
    components = []
    for name, total, color in tasks:
        progress = ProgressComponent(
            total=total, format={"style": "fraction"}, color=color, zero_pad=True
        )
        timer = TimerComponent(format={"style": "mm:ss"}, color=color)
        components.append((name, progress, timer))

    # Create layout table
    table = Table(show_header=True, title="Task Processing")
    table.add_column("Task", style="cyan", width=12)
    table.add_column("Progress", width=10)
    table.add_column("Time", width=8)

    for name, progress, timer in components:
        table.add_row(name, progress, timer)

    # Start all timers
    for _, _, timer in components:
        timer.start()

    # Simulate processing
    with Live(table, console=console, refresh_per_second=10):
        # Process tasks at different rates
        for i in range(100):
            for idx, (_name, progress, _timer) in enumerate(components):
                if not progress.is_complete():
                    # Different speeds for different tasks
                    if i % (idx + 1) == 0:
                        progress.increment()
            time.sleep(0.05)

    # Mark all complete
    for _, progress, timer in components:
        if progress.is_complete():
            progress.success()
            timer.success()
        else:
            progress.error("Incomplete")
            timer.error()

    console.print(table)
    console.print()


def demo_build_process():
    """Simulate a build process with stages."""
    console = Console()
    console.print("[bold cyan]Build Process Demo[/bold cyan]\n")

    stages = [
        ("Dependencies", 20),
        ("Compilation", 40),
        ("Testing", 30),
        ("Packaging", 25),
        ("Deployment", 15),
    ]

    total_timer = TimerComponent(format={"style": "auto"}, color="#FFFFFF")
    total_timer.start()

    for stage_name, stage_steps in stages:
        # Create components for this stage
        progress = ProgressComponent(
            total=stage_steps, format={"style": "percentage"}, color="#00FFFF"
        )
        timer = TimerComponent(format={"style": "seconds_decimal", "precision": 1}, color="#FFFF00")

        # Create stage display
        table = Table.grid(padding=1)
        table.add_column(width=12)
        table.add_column()

        table.add_row("Stage:", f"[bold]{stage_name}[/bold]")
        table.add_row("Progress:", progress)
        table.add_row("Stage Time:", timer)
        table.add_row("Total Time:", total_timer)

        panel = Panel(table, title=f"Building: {stage_name}")

        # Process stage
        timer.start()

        with Live(panel, console=console, refresh_per_second=20):
            for i in range(stage_steps + 1):
                progress.set(i)
                time.sleep(0.05)

        # Complete stage
        progress.success()
        timer.success()

        console.print(f"✓ {stage_name} completed in {timer}")

    total_timer.success()
    console.print(f"\n[bold green]Build completed in {total_timer}[/bold green]")
    console.print()


def demo_performance_benchmark():
    """Demonstrate a performance benchmark with progress and timing."""
    console = Console()
    console.print("[bold cyan]Performance Benchmark Demo[/bold cyan]\n")

    iterations = 1000

    # Create components
    progress = ProgressComponent(
        total=iterations, format={"style": "fraction"}, zero_pad=True, color="#FF00FF"
    )

    timer = TimerComponent(format={"style": "seconds_precise"}, color="#00FFFF")

    ops_per_sec = ProgressComponent(
        current=0, total=1, format={"style": "count_only"}, color="#00FF00"
    )

    # Create display
    table = Table.grid(padding=1)
    table.add_column(style="cyan", width=15)
    table.add_column()

    table.add_row("Iterations:", progress)
    table.add_row("Elapsed:", timer)
    table.add_row("Ops/sec:", ops_per_sec)

    panel = Panel(table, title="Performance Benchmark")

    # Run benchmark
    timer.start()

    with Live(panel, console=console, refresh_per_second=20):
        for i in range(iterations + 1):
            progress.set(i)

            # Calculate operations per second
            elapsed = timer.get_elapsed()
            if elapsed > 0:
                ops = int(i / elapsed)
                ops_per_sec.current = ops

            # Simulate work
            time.sleep(0.001)

    # Complete
    progress.success()
    timer.success()

    final_ops = int(iterations / timer.get_elapsed())
    console.print("\n[green]Benchmark complete![/green]")
    console.print(f"Total iterations: {iterations}")
    console.print(f"Total time: {timer}")
    console.print(f"Average ops/sec: {final_ops}")
    console.print()


if __name__ == "__main__":
    console = Console()

    try:
        console.print("[bold magenta]ThothSpinner Combined Components Demo[/bold magenta]\n")

        demo_download_with_timer()
        demo_multi_task_processing()
        demo_build_process()
        demo_performance_benchmark()

        console.print("[bold green]✓ All demos completed successfully![/bold green]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
