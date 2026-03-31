"""Tests for ThothSpinner.track() context manager."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from thothspinner import ThothSpinner
from thothspinner.core.states import ComponentState
from thothspinner.rich.context import _TrackContext


class TestTrackContextManager:
    def test_clean_exit_sets_success_state(self):
        with patch("rich.live.Live.__enter__"), patch("rich.live.Live.__exit__"):
            with ThothSpinner.track(message="Testing") as spinner:
                pass
            assert spinner._spinner._state == ComponentState.SUCCESS

    def test_exception_sets_error_state_and_propagates(self):
        with patch("rich.live.Live.__enter__"), patch("rich.live.Live.__exit__"):
            with pytest.raises(RuntimeError, match="boom"):
                with ThothSpinner.track(message="Testing") as spinner:
                    raise RuntimeError("boom")
            assert spinner._spinner._state == ComponentState.ERROR

    def test_update_sets_progress_current_and_total(self):
        with patch("rich.live.Live.__enter__"), patch("rich.live.Live.__exit__"):
            with ThothSpinner.track(message="Testing") as spinner:
                spinner.update(50, 100)
                progress = spinner._spinner._components["progress"]
                assert progress.current == 50
                assert progress.total == 100

    def test_update_without_total_preserves_existing_total(self):
        with patch("rich.live.Live.__enter__"), patch("rich.live.Live.__exit__"):
            with ThothSpinner.track(message="Testing") as spinner:
                spinner.update(50, 200)
                spinner.update(75)
                progress = spinner._spinner._components["progress"]
                assert progress.current == 75
                assert progress.total == 200

    def test_message_kwarg_sets_message_text(self):
        with patch("rich.live.Live.__enter__"), patch("rich.live.Live.__exit__"):
            with ThothSpinner.track(message="Hello") as spinner:
                msg = spinner._spinner._components["message"]
                assert msg._current_word == "Hello"

    def test_message_text_kwarg_takes_precedence(self):
        with patch("rich.live.Live.__enter__"), patch("rich.live.Live.__exit__"):
            with ThothSpinner.track(message="ignored", message_text="Used") as spinner:
                msg = spinner._spinner._components["message"]
                assert msg._current_word == "Used"

    def test_getattr_forwards_to_spinner(self):
        with patch("rich.live.Live.__enter__"), patch("rich.live.Live.__exit__"):
            with ThothSpinner.track() as spinner:
                # set_message is a ThothSpinner method — should work via __getattr__
                spinner.set_message(text="forwarded")

    def test_error_message_passed_from_exception(self):
        captured = {}

        def fake_error(msg=None):
            captured["msg"] = msg

        with patch("rich.live.Live.__enter__"), patch("rich.live.Live.__exit__"):
            ts = ThothSpinner()
            ts.start()
            ctx = _TrackContext(ts, MagicMock())
            ctx._spinner.error = fake_error  # type: ignore[method-assign]
            try:
                with ctx:
                    raise ValueError("detailed error")
            except ValueError:
                pass
            assert captured["msg"] == "detailed error"

    def test_error_with_no_message_passes_none(self):
        captured = {}

        def fake_error(msg=None):
            captured["msg"] = msg

        with patch("rich.live.Live.__enter__"), patch("rich.live.Live.__exit__"):
            ts = ThothSpinner()
            ts.start()
            ctx = _TrackContext(ts, MagicMock())
            ctx._spinner.error = fake_error  # type: ignore[method-assign]
            try:
                with ctx:
                    raise ValueError
            except ValueError:
                pass
            assert captured["msg"] is None

    def test_existing_live_pattern_still_works(self):
        """Regression: direct ThothSpinner() + Live() usage is unchanged."""

        spinner = ThothSpinner()
        # Just ensure construction doesn't break
        assert isinstance(spinner, ThothSpinner)
        assert callable(spinner.start)
        assert callable(spinner.success)
        assert callable(spinner.error)
