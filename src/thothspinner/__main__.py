"""CLI entry point for ThothSpinner.

Usage:
    thothspinner preview [STYLE]
    thothspinner browse
"""

from __future__ import annotations

import argparse
import difflib
import sys
import time


def cmd_preview(args: argparse.Namespace) -> int:
    """Show spinner style(s) animating with their names."""
    from rich.console import Console
    from rich.live import Live
    from rich.table import Table
    from rich.text import Text

    from thothspinner.rich.components.spinner import SpinnerComponent
    from thothspinner.rich.spinners.frames import SPINNER_FRAMES

    console = Console()
    style_arg: str | None = args.style

    if style_arg is not None:
        if style_arg not in SPINNER_FRAMES:
            available = sorted(SPINNER_FRAMES.keys())
            suggestions = difflib.get_close_matches(style_arg, available, n=3, cutoff=0.6)
            hint = f" Did you mean {suggestions[0]!r}?" if suggestions else ""
            console.print(f"[red]Unknown spinner style {style_arg!r}.{hint}[/red]")
            console.print(f"Available styles: {', '.join(available)}")
            return 1
        styles_to_show = [style_arg]
        duration = 3.0
    else:
        styles_to_show = sorted(SPINNER_FRAMES.keys())
        duration = 1.2

    for style_name in styles_to_show:
        spinner = SpinnerComponent(style=style_name)
        row = Table.grid(padding=(0, 1))
        row.add_row(spinner, Text(style_name, style="dim"))
        with Live(row, console=console, refresh_per_second=20, transient=True):
            time.sleep(duration)
        console.print(f"  {style_name}")

    return 0


def cmd_browse(args: argparse.Namespace) -> int:
    """Open the interactive Textual TUI style browser."""
    try:
        from thothspinner.__browse__ import BrowseApp
    except ImportError as exc:
        from rich.console import Console

        Console().print(f"[red]browse requires textual: {exc}[/red]")
        return 1
    BrowseApp().run()
    return 0


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="thothspinner",
        description="ThothSpinner CLI tools",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    preview_p = sub.add_parser("preview", help="Preview spinner style(s)")
    preview_p.add_argument(
        "style",
        nargs="?",
        metavar="STYLE",
        default=None,
        help="Style name to preview (default: all styles)",
    )
    preview_p.set_defaults(func=cmd_preview)

    browse_p = sub.add_parser("browse", help="Interactive TUI style browser")
    browse_p.set_defaults(func=cmd_browse)

    args = parser.parse_args(argv)
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
