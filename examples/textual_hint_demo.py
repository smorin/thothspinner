#!/usr/bin/env python
"""Demo of the Textual HintWidget."""

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Button, Label

from thothspinner.textual.widgets import HintWidget


class HintDemo(App):
    """Demo application for HintWidget."""

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
        margin: 1 0;
    }

    HintWidget {
        text-align: center;
        margin: 1 0;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose the application layout."""
        with Container():
            with Vertical():
                yield Label("🎨 HintWidget Demo", id="title")

                # Basic hint
                yield HintWidget(text="Press ESC to exit", color="#888888", id="basic-hint")

                # Hint with icon
                yield HintWidget(text="Loading data", icon="⚠", color="#FFA500", id="icon-hint")

                # Success hint (initially hidden)
                yield HintWidget(
                    text="Success!", icon="✅", color="#00FF00", visible=False, id="success-hint"
                )

                # Error hint (initially hidden)
                yield HintWidget(
                    text="Error occurred",
                    icon="❌",
                    color="#FF0000",
                    visible=False,
                    id="error-hint",
                )

                yield Button("Toggle Basic Hint", id="toggle-basic")
                yield Button("Change Icon Hint Text", id="change-text")
                yield Button("Show Success", id="show-success")
                yield Button("Show Error", id="show-error")
                yield Button("Fade In/Out Demo", id="fade-demo")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "toggle-basic":
            hint = self.query_one("#basic-hint", HintWidget)
            hint.toggle()

        elif button_id == "change-text":
            hint = self.query_one("#icon-hint", HintWidget)
            # Cycle through different messages
            if hint.text == "Loading data":
                hint.configure(text="Processing...", icon="🔄", color="#00FFFF")
            elif hint.text == "Processing...":
                hint.configure(text="Almost done!", icon="⏳", color="#FFFF00")
            else:
                hint.configure(text="Loading data", icon="⚠", color="#FFA500")

        elif button_id == "show-success":
            # Hide error, show success
            self.query_one("#error-hint", HintWidget).hide()
            success = self.query_one("#success-hint", HintWidget)
            success.show()
            # Auto-hide after 2 seconds
            self.set_timer(2.0, lambda: success.hide())

        elif button_id == "show-error":
            # Hide success, show error
            self.query_one("#success-hint", HintWidget).hide()
            error = self.query_one("#error-hint", HintWidget)
            error.show()
            # Auto-hide after 2 seconds
            self.set_timer(2.0, lambda: error.hide())

        elif button_id == "fade-demo":
            hint = self.query_one("#basic-hint", HintWidget)
            # Fade out then fade in
            hint.fade_out(duration=0.5)
            self.set_timer(0.6, lambda: hint.fade_in(duration=0.5))


if __name__ == "__main__":
    app = HintDemo()
    app.run()
