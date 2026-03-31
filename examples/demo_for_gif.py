#!/usr/bin/env python3
"""Concise demo for the README GIF — shows ThothSpinner.track() in action."""

import time

from thothspinner import ThothSpinner

with ThothSpinner.track(message="Building project", progress_format="percentage") as spinner:
    for i in range(101):
        spinner.update(i, 100)
        time.sleep(0.025)

time.sleep(1.5)
