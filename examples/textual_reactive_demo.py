#!/usr/bin/env python
"""Demo of reactive property patterns in ThothSpinner Textual widgets."""

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Button, Footer, Input, Label

from thothspinner.textual.widgets import HintWidget, ProgressWidget, SpinnerWidget


class ReactiveDemo(App):
    """Demo showing reactive property updates and state CSS classes."""

    BINDINGS = [("ctrl+q", "quit", "Quit")]

    CSS = """
    Container {
        align: center middle;
    }

    Vertical {
        width: 65;
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

    Input {
        margin: 1 0;
    }

    .widget-row {
        height: 3;
        margin: 1 0;
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
                yield Label("Reactive Properties Demo", id="title")

                yield Label("Type a color hex code (e.g., #FF0000):")
                yield Input(placeholder="#RRGGBB", id="color-input")

                yield Label("Spinner (reactive color):")
                yield SpinnerWidget(color="#D97706", id="spinner")

                yield Label("Progress (reactive current/total):")
                yield ProgressWidget(0, 100, format_style="percentage", id="progress")

                yield Label("Hint (reactive text):")
                yield HintWidget("Watch me change!", color="#888888", id="hint")

                yield Button("Apply Color to All", id="apply-color")
                yield Button("Increment Progress (+10)", id="increment")
                yield Button("Success All", id="success")
                yield Button("Error All", id="error")
                yield Button("Reset All", id="reset")
                yield Label("Tab / Shift+Tab to navigate", id="nav-hint")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "apply-color":
            color_input = self.query_one("#color-input", Input)
            color = color_input.value.strip()
            hint = self.query_one("#hint", HintWidget)
            if color and color.startswith("#") and len(color) == 7:
                try:
                    self.query_one("#spinner", SpinnerWidget).color = color
                    self.query_one("#progress", ProgressWidget).color = color
                    hint.color = color
                    hint.text = f"Color set to {color}"
                except ValueError:
                    hint.text = "Invalid color! Use #RRGGBB"
            else:
                hint.text = "Enter a valid #RRGGBB color (e.g. #FF0000)"

        elif event.button.id == "increment":
            progress = self.query_one("#progress", ProgressWidget)
            progress.add(10)
            self.query_one("#hint", HintWidget).text = f"Progress: {progress.current}/{progress.total}"

        elif event.button.id == "success":
            self.query_one("#spinner", SpinnerWidget).success()
            self.query_one("#progress", ProgressWidget).success()
            self.query_one("#hint", HintWidget).success()

        elif event.button.id == "error":
            self.query_one("#spinner", SpinnerWidget).error()
            self.query_one("#progress", ProgressWidget).error()
            self.query_one("#hint", HintWidget).error()

        elif event.button.id == "reset":
            self.query_one("#spinner", SpinnerWidget).reset()
            self.query_one("#progress", ProgressWidget).reset()
            self.query_one("#hint", HintWidget).reset()
            self.query_one("#hint", HintWidget).text = "Watch me change!"


if __name__ == "__main__":
    ReactiveDemo().run()
