#!/usr/bin/env python
"""Demo of the Textual ThothSpinnerWidget orchestrator with full workflow."""

import asyncio

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Button, Footer, Label

from thothspinner.textual import TextualThothSpinner


class OrchestratorDemo(App):
    """Demo application for ThothSpinnerWidget orchestrator."""

    BINDINGS = [
        ("tab", "focus_next", "Tab"),
        ("shift+tab", "focus_previous", "Shift+Tab"),
        ("ctrl+q", "quit", "Quit"),
    ]

    CSS = """
    Container {
        align: center middle;
    }

    Vertical {
        width: 70;
        height: auto;
        padding: 2;
        border: solid $primary;
    }

    Label {
        text-align: center;
        margin: 1 0;
    }

    Button {
        width: 100%;
        margin: 0 0;
    }

    ThothSpinnerWidget {
        margin: 1 0;
        width: 100%;
    }
    """

    def compose(self) -> ComposeResult:
        with Container():
            with Vertical():
                yield Label("ThothSpinnerWidget Orchestrator Demo", id="title")

                yield TextualThothSpinner(
                    spinner_style="npm_dots",
                    message_text="Ready",
                    progress_format="percentage",
                    timer_format="auto",
                    hint_text="(press Start)",
                    id="spinner",
                )

                yield Label("Status: idle", id="status")
                yield Button("Start Progress Simulation", id="start-sim")
                yield Button("Change Spinner Style", id="change-style")
                yield Button("Update Message", id="update-msg")
                yield Button("Toggle Shimmer Direction", id="shimmer-dir")
                yield Button("Error Demo", id="error")
                yield Button("Reset", id="reset")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        spinner = self.query_one("#spinner", TextualThothSpinner)
        status = self.query_one("#status", Label)

        if event.button.id == "start-sim":
            spinner.start()
            status.update("Status: running simulation...")
            self.run_worker(self._simulate_progress)

        elif event.button.id == "change-style":
            spinner.set_spinner_style(style="claude_stars")
            status.update("Status: changed to claude_stars")

        elif event.button.id == "update-msg":
            spinner.set_message(text="Custom message")
            status.update("Status: message updated")

        elif event.button.id == "shimmer-dir":
            spinner.set_shimmer_direction(direction="right-to-left")
            status.update("Status: shimmer reversed")

        elif event.button.id == "error":
            spinner.start()
            spinner.error("Something went wrong!")
            status.update("Status: ERROR")

        elif event.button.id == "reset":
            spinner.reset()
            status.update("Status: reset")

    async def _simulate_progress(self) -> None:
        spinner = self.query_one("#spinner", TextualThothSpinner)
        status = self.query_one("#status", Label)

        for i in range(101):
            spinner.update_progress(current=i, total=100)
            if i % 25 == 0 and i > 0:
                spinner.set_message(text=f"Phase {i // 25} of 4")
            await asyncio.sleep(0.05)

        spinner.success("Simulation complete!")
        status.update("Status: SUCCESS")


if __name__ == "__main__":
    OrchestratorDemo().run()
