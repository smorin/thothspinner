"""Interactive TUI style browser for ThothSpinner (thothspinner browse)."""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.reactive import reactive
from textual.widgets import Footer, Header, Label, ListItem, ListView, Static

from thothspinner.rich.spinners.frames import SPINNER_FRAMES
from thothspinner.textual import ThothSpinnerWidget

SORTED_STYLES: list[str] = sorted(SPINNER_FRAMES.keys())


class StyleListItem(ListItem):
    """A list item representing a single spinner style name."""

    def __init__(self, style_name: str) -> None:
        super().__init__()
        self.style_name = style_name

    def compose(self) -> ComposeResult:
        yield Label(self.style_name)


class PreviewPanel(Static):
    """Right panel: live spinner preview + metadata."""

    style_name: reactive[str] = reactive("npm_dots", recompose=True)

    def compose(self) -> ComposeResult:
        frames = SPINNER_FRAMES[self.style_name]["frames"]
        interval = SPINNER_FRAMES[self.style_name]["interval"]
        yield Label(f"[bold]{self.style_name}[/bold]", id="preview-title")
        yield ThothSpinnerWidget(
            spinner_style=self.style_name,
            message_text=f"Previewing {self.style_name}",
            id="preview-spinner",
        )
        yield Label(
            f"Frames: {len(frames)}  •  Interval: {interval * 1000:.0f}ms",
            id="preview-meta",
        )
        frame_preview = "  ".join(frames[:10]) + ("…" if len(frames) > 10 else "")
        yield Label(frame_preview, id="preview-frames")

    def on_mount(self) -> None:
        spinner = self.query_one("#preview-spinner", ThothSpinnerWidget)
        spinner.start()


class BrowseApp(App):
    """Interactive style browser TUI for ThothSpinner."""

    TITLE = "ThothSpinner Style Browser"
    BINDINGS = [
        Binding("q", "quit", "Quit"),
    ]

    DEFAULT_CSS = """
    Screen {
        layout: grid;
        grid-size: 2;
        grid-columns: 1fr 2fr;
    }
    #style-list {
        border: solid $primary;
        height: 100%;
    }
    #preview-panel {
        border: solid $accent;
        height: 100%;
        padding: 1 2;
    }
    #preview-title {
        text-style: bold;
        margin-bottom: 1;
    }
    #preview-meta {
        color: $text-muted;
        margin-top: 1;
    }
    #preview-frames {
        color: $text-muted;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield ListView(
            *[StyleListItem(name) for name in SORTED_STYLES],
            id="style-list",
        )
        yield PreviewPanel(id="preview-panel")
        yield Footer()

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if isinstance(event.item, StyleListItem):
            self.query_one(PreviewPanel).style_name = event.item.style_name

    def on_mount(self) -> None:
        self.query_one(ListView).focus()
