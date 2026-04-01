#!/usr/bin/env python3
"""Full-component demo for the README GIF.

Shows all 5 components (spinner, message, progress, timer, hint) through
multiple phases with state transitions including success and error.
"""

import time

from rich.console import Console
from rich.live import Live

from thothspinner import ThothSpinner

console = Console()

config = {
    "elements": {
        "spinner": {"style": "claude_stars"},
        "message": {"text": "Analyzing codebase", "shimmer": {"enabled": True, "width": 3}},
        "progress": {"format": {"style": "percentage"}, "total": 100},
        "timer": {"format": {"style": "auto"}},
        "hint": {"text": "(esc to cancel)"},
    },
}

spinner = ThothSpinner(**config)

with Live(spinner, console=console, refresh_per_second=20):
    spinner.start()

    # Phase 1: 0 → 25%
    spinner.set_message(text="Analyzing codebase")
    for i in range(26):
        spinner.update_progress(current=i, total=100)
        time.sleep(0.04)

    # Phase 2: 25 → 55%
    spinner.set_message(text="Building artifacts")
    spinner.set_hint(text="(this may take a moment)")
    for i in range(26, 56):
        spinner.update_progress(current=i, total=100)
        time.sleep(0.04)

    # Phase 3: 55 → 80%
    spinner.set_message(text="Running tests")
    spinner.set_hint(text="(esc to cancel)")
    for i in range(56, 81):
        spinner.update_progress(current=i, total=100)
        time.sleep(0.04)

    # Phase 4: 80 → 100%
    spinner.set_message(text="Deploying")
    spinner.set_hint(text="(almost there!)")
    for i in range(81, 101):
        spinner.update_progress(current=i, total=100)
        time.sleep(0.04)

    spinner.success("Deployed successfully!")
    time.sleep(2.0)

    # Error sequence
    spinner.reset()
    spinner.set_message(text="Connecting to API")
    spinner.set_hint(text="(esc to cancel)")
    for i in range(45):
        spinner.update_progress(current=i, total=100)
        time.sleep(0.02)

    spinner.error("Connection refused")
    time.sleep(1.5)
