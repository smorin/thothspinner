#!/usr/bin/env python
"""Demo of the Textual MessageWidget with shimmer effects."""

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Button, Label

from thothspinner.textual.widgets import MessageWidget


class MessageDemo(App):
    """Demo application for MessageWidget."""

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

    MessageWidget {
        text-align: center;
        margin: 1 0;
    }
    """

    def compose(self) -> ComposeResult:
        with Container():
            with Vertical():
                yield Label("MessageWidget Demo", id="title")

                yield MessageWidget(
                    action_words=["Processing", "Analyzing", "Computing", "Loading"],
                    shimmer={"enabled": True, "width": 3, "speed": 1.0},
                    color="#D97706",
                    id="message",
                )

                yield Button("Reverse Shimmer Direction", id="reverse")
                yield Button("Add Custom Words", id="add-words")
                yield Button("Set Custom Text", id="set-text")
                yield Button("Trigger New Word", id="new-word")
                yield Button("Success", id="success")
                yield Button("Error", id="error")
                yield Button("Reset", id="reset")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        message = self.query_one("#message", MessageWidget)

        if event.button.id == "reverse":
            message.reverse_shimmer = not message.reverse_shimmer

        elif event.button.id == "add-words":
            message.extend_action_words(["Optimizing", "Syncing", "Deploying"])

        elif event.button.id == "set-text":
            message.configure(text="Custom message here")

        elif event.button.id == "new-word":
            message.configure(trigger_new=True)

        elif event.button.id == "success":
            message.success("All done!")

        elif event.button.id == "error":
            message.error("Something failed")

        elif event.button.id == "reset":
            message.reset()


if __name__ == "__main__":
    MessageDemo().run()
