#!/usr/bin/env python
"""Demo of the Textual SpinnerWidget with style switching and speed control."""

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Button, Footer, Label

from thothspinner.textual.widgets import SpinnerWidget


STYLES = ["npm_dots", "claude_stars", "dots", "classic", "circle", "star"]


class SpinnerDemo(App):
    """Demo application for SpinnerWidget."""

    BINDINGS = [("ctrl+q", "quit", "Quit")]

    CSS = """
    Container {
        align: center middle;
    }

    Vertical {
        width: 60;
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

    SpinnerWidget {
        text-align: center;
        margin: 1 0;
    }

    #nav-hint {
        color: #888888;
        text-align: center;
        margin: 1 0 0 0;
    }
    """

    def __init__(self):
        super().__init__()
        self._style_index = 0

    def compose(self) -> ComposeResult:
        with Container():
            with Vertical():
                yield Label("SpinnerWidget Demo", id="title")
                yield SpinnerWidget(style="npm_dots", color="#D97706", id="spinner")
                yield Label("Style: npm_dots | Speed: 1.0x", id="info")
                yield Button("Next Style", id="next-style")
                yield Button("Speed Up (2x)", id="speed-up")
                yield Button("Speed Down (0.5x)", id="speed-down")
                yield Button("Pause / Resume", id="pause")
                yield Button("Success", id="success")
                yield Button("Error", id="error")
                yield Button("Reset", id="reset")
                yield Label("Tab / Shift+Tab to navigate", id="nav-hint")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        spinner = self.query_one("#spinner", SpinnerWidget)
        info = self.query_one("#info", Label)

        if event.button.id == "next-style":
            self._style_index = (self._style_index + 1) % len(STYLES)
            style = STYLES[self._style_index]
            spinner.set_style(style)
            info.update(f"Style: {style} | Speed: {spinner.speed}x")

        elif event.button.id == "speed-up":
            spinner.set_speed(min(spinner.speed * 2, 8.0))
            info.update(f"Style: {STYLES[self._style_index]} | Speed: {spinner.speed}x")

        elif event.button.id == "speed-down":
            spinner.set_speed(max(spinner.speed / 2, 0.25))
            info.update(f"Style: {STYLES[self._style_index]} | Speed: {spinner.speed}x")

        elif event.button.id == "pause":
            spinner.pause()
            status = "Paused" if spinner.paused else "Running"
            info.update(f"Style: {STYLES[self._style_index]} | {status}")

        elif event.button.id == "success":
            spinner.success()
            info.update("State: SUCCESS")

        elif event.button.id == "error":
            spinner.error()
            info.update("State: ERROR")

        elif event.button.id == "reset":
            spinner.reset()
            info.update(f"Style: {STYLES[self._style_index]} | Speed: {spinner.speed}x")


if __name__ == "__main__":
    SpinnerDemo().run()
