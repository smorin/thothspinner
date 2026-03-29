#!/usr/bin/env python
"""Demo of the Textual ProgressWidget with all format styles."""

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Button, Footer, Label

from thothspinner.textual.widgets import ProgressWidget


class ProgressDemo(App):
    """Demo application for ProgressWidget."""

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
    """

    def compose(self) -> ComposeResult:
        with Container():
            with Vertical():
                yield Label("ProgressWidget Format Styles", id="title")

                yield Label("fraction:")
                yield ProgressWidget(42, 100, format_style="fraction", color="#55FF55", id="p-fraction")

                yield Label("percentage:")
                yield ProgressWidget(42, 100, format_style="percentage", color="#55FF55", id="p-percentage")

                yield Label("of_text:")
                yield ProgressWidget(42, 100, format_style="of_text", color="#55FF55", id="p-of-text")

                yield Label("count_only:")
                yield ProgressWidget(42, 100, format_style="count_only", color="#55FF55", id="p-count")

                yield Label("ratio:")
                yield ProgressWidget(42, 100, format_style="ratio", color="#55FF55", id="p-ratio")

                yield Button("Increment All (+10)", id="increment")
                yield Button("Reset All", id="reset")
                yield Button("Success All", id="success")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        widgets = self.query(ProgressWidget)

        if event.button.id == "increment":
            for w in widgets:
                w.add(10)

        elif event.button.id == "reset":
            for w in widgets:
                w.reset()
                w.set(42)

        elif event.button.id == "success":
            for w in widgets:
                w.set(100)
                w.success()


if __name__ == "__main__":
    ProgressDemo().run()
