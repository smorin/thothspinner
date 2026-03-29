#!/usr/bin/env python
"""Demo of the Textual ThothSpinnerWidget orchestrator with full workflow."""

import asyncio

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Button, Footer, Label

from thothspinner.textual import TextualThothSpinner


STYLES = ["npm_dots", "claude_stars", "dots", "arc", "line", "pulse", "vertical_pulse", "pipe", "quarter", "hamburger", "moon", "clock", "earth", "dice", "snowflake", "zodiac", "rune", "matrix", "classic", "circle", "star"]


class OrchestratorDemo(App):
    """Demo application for ThothSpinnerWidget orchestrator."""

    BINDINGS = [("ctrl+q", "quit", "Quit")]

    def __init__(self) -> None:
        super().__init__()
        self._style_index = 0
        self._shimmer_reversed = False

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

    #nav-hint {
        color: #888888;
        text-align: center;
        margin: 1 0 0 0;
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
                yield Label("Tab / Shift+Tab to navigate", id="nav-hint")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        spinner = self.query_one("#spinner", TextualThothSpinner)
        status = self.query_one("#status", Label)

        if event.button.id == "start-sim":
            spinner.start()
            status.update("Status: running simulation...")
            self.run_worker(self._simulate_progress)

        elif event.button.id == "change-style":
            self._style_index = (self._style_index + 1) % len(STYLES)
            style = STYLES[self._style_index]
            spinner.set_spinner_style(style=style)
            status.update(f"Status: spinner style → {style}")

        elif event.button.id == "update-msg":
            spinner.set_message(text="Custom message")
            status.update("Status: message updated")

        elif event.button.id == "shimmer-dir":
            self._shimmer_reversed = not self._shimmer_reversed
            direction = "right-to-left" if self._shimmer_reversed else "left-to-right"
            spinner.set_shimmer_direction(direction=direction)
            status.update(f"Status: shimmer → {direction}")

        elif event.button.id == "error":
            spinner.start()
            spinner.error("Something went wrong!")
            status.update("Status: ERROR")

        elif event.button.id == "reset":
            spinner.reset()
            status.update("Status: reset")

    async def _simulate_progress(self) -> None:
        from thothspinner.core.states import ComponentState

        spinner = self.query_one("#spinner", TextualThothSpinner)
        status = self.query_one("#status", Label)

        for i in range(101):
            if spinner.state != ComponentState.IN_PROGRESS:
                return
            spinner.update_progress(current=i, total=100)
            if i % 25 == 0 and i > 0:
                spinner.set_message(text=f"Phase {i // 25} of 4")
            await asyncio.sleep(0.05)

        if spinner.state == ComponentState.IN_PROGRESS:
            spinner.success("Simulation complete!")
            status.update("Status: SUCCESS")


if __name__ == "__main__":
    OrchestratorDemo().run()
