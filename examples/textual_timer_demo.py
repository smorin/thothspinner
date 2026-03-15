#!/usr/bin/env python
"""Demo of the Textual TimerWidget with controls and format styles."""

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Button, Label

from thothspinner.textual.widgets import TimerWidget


class TimerDemo(App):
    """Demo application for TimerWidget."""

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

    TimerWidget {
        text-align: center;
        margin: 1 0;
    }
    """

    def compose(self) -> ComposeResult:
        with Container():
            with Vertical():
                yield Label("TimerWidget Demo", id="title")

                yield Label("auto format:")
                yield TimerWidget(format_style="auto", color="#FFFF55", id="timer-auto")

                yield Label("hh:mm:ss format:")
                yield TimerWidget(format_style="hh:mm:ss", color="#55FFFF", id="timer-hms")

                yield Label("milliseconds format:")
                yield TimerWidget(format_style="milliseconds", color="#FF55FF", id="timer-ms")

                yield Button("Start All", id="start")
                yield Button("Stop All", id="stop")
                yield Button("Pause / Resume All", id="pause")
                yield Button("Reset All", id="reset")
                yield Button("Success", id="success")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        timers = list(self.query(TimerWidget))

        if event.button.id == "start":
            for t in timers:
                t.start()

        elif event.button.id == "stop":
            for t in timers:
                t.stop()

        elif event.button.id == "pause":
            for t in timers:
                t.pause()

        elif event.button.id == "reset":
            for t in timers:
                t.reset()

        elif event.button.id == "success":
            for t in timers:
                t.success()


if __name__ == "__main__":
    TimerDemo().run()
