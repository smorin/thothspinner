"""Snapshot tests for Textual widgets.

Run with: just test
Update snapshots with: uv run pytest tests/textual/test_snapshots.py --snapshot-update
"""

from __future__ import annotations

from textual.app import App, ComposeResult

from thothspinner.textual.widgets import (
    HintWidget,
    MessageWidget,
    ProgressWidget,
    SpinnerWidget,
    ThothSpinnerWidget,
    TimerWidget,
)

# ---------------------------------------------------------------------------
# Test apps — one per widget type
# ---------------------------------------------------------------------------


class SpinnerApp(App):
    CSS = "Screen { align: left top; }"

    def compose(self) -> ComposeResult:
        yield SpinnerWidget()


class MessageApp(App):
    CSS = "Screen { align: left top; }"

    def compose(self) -> ComposeResult:
        # Single word + very long interval = no rotation during test
        yield MessageWidget(
            action_words=["Loading"],
            interval={"min": 9999, "max": 9999},
            shimmer={"enabled": False},
        )


class ProgressApp(App):
    CSS = "Screen { align: left top; }"

    def compose(self) -> ComposeResult:
        yield ProgressWidget(current=42, total=100)


class TimerApp(App):
    CSS = "Screen { align: left top; }"

    def compose(self) -> ComposeResult:
        yield TimerWidget()


class HintApp(App):
    CSS = "Screen { align: left top; }"

    def compose(self) -> ComposeResult:
        yield HintWidget(text="(esc to cancel)")


class OrchestratorApp(App):
    CSS = "Screen { align: left top; }"

    def compose(self) -> ComposeResult:
        # Disable shimmer + long interval = stable snapshot
        yield ThothSpinnerWidget(
            message_text="Processing",
            message_shimmer=False,
            config={
                "elements": {
                    "message": {
                        "interval": {"min": 9999, "max": 9999},
                    }
                }
            },
        )


# ---------------------------------------------------------------------------
# SpinnerWidget snapshots
# ---------------------------------------------------------------------------


def test_spinner_default(snap_compare):
    """Spinner in default in_progress state (frame 0)."""
    assert snap_compare(SpinnerApp(), terminal_size=(80, 3))


def test_spinner_success(snap_compare):
    """Spinner in success state."""

    async def set_success(pilot):
        pilot.app.query_one(SpinnerWidget).success()

    assert snap_compare(SpinnerApp(), run_before=set_success, terminal_size=(80, 3))


def test_spinner_error(snap_compare):
    """Spinner in error state."""

    async def set_error(pilot):
        pilot.app.query_one(SpinnerWidget).error()

    assert snap_compare(SpinnerApp(), run_before=set_error, terminal_size=(80, 3))


# ---------------------------------------------------------------------------
# MessageWidget snapshots
# ---------------------------------------------------------------------------


def test_message_default(snap_compare):
    """Message widget default state."""
    assert snap_compare(MessageApp(), terminal_size=(80, 3))


def test_message_success(snap_compare):
    """Message widget success state."""

    async def set_success(pilot):
        pilot.app.query_one(MessageWidget).success("Done!")

    assert snap_compare(MessageApp(), run_before=set_success, terminal_size=(80, 3))


def test_message_error(snap_compare):
    """Message widget error state."""

    async def set_error(pilot):
        pilot.app.query_one(MessageWidget).error("Failed!")

    assert snap_compare(MessageApp(), run_before=set_error, terminal_size=(80, 3))


# ---------------------------------------------------------------------------
# ProgressWidget snapshots
# ---------------------------------------------------------------------------


def test_progress_default(snap_compare):
    """Progress widget default state (42/100)."""
    assert snap_compare(ProgressApp(), terminal_size=(80, 3))


def test_progress_success(snap_compare):
    """Progress widget success state."""

    async def set_success(pilot):
        pilot.app.query_one(ProgressWidget).success()

    assert snap_compare(ProgressApp(), run_before=set_success, terminal_size=(80, 3))


def test_progress_error(snap_compare):
    """Progress widget error state."""

    async def set_error(pilot):
        pilot.app.query_one(ProgressWidget).error()

    assert snap_compare(ProgressApp(), run_before=set_error, terminal_size=(80, 3))


# ---------------------------------------------------------------------------
# TimerWidget snapshots
# ---------------------------------------------------------------------------


def test_timer_default(snap_compare):
    """Timer widget default state (not running)."""
    assert snap_compare(TimerApp(), terminal_size=(80, 3))


def test_timer_success(snap_compare):
    """Timer widget success state."""

    async def set_success(pilot):
        pilot.app.query_one(TimerWidget).success()

    assert snap_compare(TimerApp(), run_before=set_success, terminal_size=(80, 3))


def test_timer_error(snap_compare):
    """Timer widget error state."""

    async def set_error(pilot):
        pilot.app.query_one(TimerWidget).error()

    assert snap_compare(TimerApp(), run_before=set_error, terminal_size=(80, 3))


# ---------------------------------------------------------------------------
# HintWidget snapshots
# ---------------------------------------------------------------------------


def test_hint_default(snap_compare):
    """Hint widget default state."""
    assert snap_compare(HintApp(), terminal_size=(80, 3))


# ---------------------------------------------------------------------------
# ThothSpinnerWidget (orchestrator) snapshots
# ---------------------------------------------------------------------------


def test_orchestrator_default(snap_compare):
    """Orchestrator in_progress state with animations frozen at frame 0."""

    async def freeze_animations(pilot):
        # Pause spinner and reset to a known frame
        spinner = pilot.app.query_one(SpinnerWidget)
        if spinner._timer is not None:
            spinner._timer.pause()
        spinner._frame_index = 0
        # Pin message to a stable text (first tick may have rotated it already)
        pilot.app.query_one(ThothSpinnerWidget).set_message_pinned(text="Processing")
        # Pause message animation timer
        msg = pilot.app.query_one(MessageWidget)
        if msg._animation_timer is not None:
            msg._animation_timer.pause()

    assert snap_compare(OrchestratorApp(), run_before=freeze_animations, terminal_size=(80, 3))


def test_orchestrator_success(snap_compare):
    """Orchestrator success state."""

    async def set_success(pilot):
        pilot.app.query_one(ThothSpinnerWidget).success("All done!")

    assert snap_compare(OrchestratorApp(), run_before=set_success, terminal_size=(80, 3))


def test_orchestrator_error(snap_compare):
    """Orchestrator error state."""

    async def set_error(pilot):
        pilot.app.query_one(ThothSpinnerWidget).error("Something went wrong")

    assert snap_compare(OrchestratorApp(), run_before=set_error, terminal_size=(80, 3))
