"""Interactive TUI style browser for ThothSpinner (thothspinner browse)."""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Footer, Header, Label, ListItem, ListView

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


class PreviewPanel(Widget):
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
    SUB_TITLE = "↑↓ to browse styles  •  Q to quit"
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("up", "cursor_up", "Previous"),
        Binding("down", "cursor_down", "Next"),
    ]

    DEFAULT_CSS = """
    #content {
        height: 1fr;
    }
    #style-list {
        width: 1fr;
        border: solid $primary;
    }
    #preview-panel {
        width: 2fr;
        border: solid $accent;
        padding: 1 2;
        layout: vertical;
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
        with Horizontal(id="content"):
            yield ListView(
                *[StyleListItem(name) for name in SORTED_STYLES],
                id="style-list",
            )
            yield PreviewPanel(id="preview-panel")
        yield Footer()

    def action_cursor_up(self) -> None:
        self.query_one(ListView).action_cursor_up()

    def action_cursor_down(self) -> None:
        self.query_one(ListView).action_cursor_down()

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if isinstance(event.item, StyleListItem):
            self.query_one(PreviewPanel).style_name = event.item.style_name

    def on_mount(self) -> None:
        self.query_one(ListView).focus()
