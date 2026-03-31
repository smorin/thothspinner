"""Tests for error messages on invalid spinner/progress/timer config."""

from __future__ import annotations

import pytest

from thothspinner.rich.components.progress import ProgressComponent
from thothspinner.rich.components.spinner import SpinnerComponent
from thothspinner.rich.components.timer import TimerComponent
from thothspinner.rich.thothspinner import ThothSpinner


class TestSpinnerStyleValidation:
    def test_invalid_style_close_match_raises_with_suggestion(self):
        with pytest.raises(ValueError, match="Did you mean 'npm_dots'"):
            SpinnerComponent(style="npmdots")

    def test_invalid_style_no_match_raises_without_suggestion(self):
        with pytest.raises(ValueError, match="Unknown spinner style 'xyzzy_totally_invalid'"):
            SpinnerComponent(style="xyzzy_totally_invalid")

    def test_invalid_style_lists_available_styles(self):
        with pytest.raises(ValueError, match="Available styles:"):
            SpinnerComponent(style="badstyle")

    def test_valid_style_does_not_raise(self):
        SpinnerComponent(style="npm_dots")
        SpinnerComponent(style="claude_stars")
        SpinnerComponent(style="moon")

    def test_custom_frames_bypasses_style_validation(self):
        # Custom frames don't go through style lookup
        s = SpinnerComponent(frames=["|", "/", "-", "\\"])
        assert s.frames == ["|", "/", "-", "\\"]


class TestSetSpinnerStyleValidation:
    def test_invalid_style_raises_with_suggestion(self):
        spinner = ThothSpinner(spinner_style="npm_dots")
        with pytest.raises(ValueError, match="Did you mean 'npm_dots'"):
            spinner.set_spinner_style(style="npmdots")

    def test_invalid_style_no_match_raises(self):
        spinner = ThothSpinner(spinner_style="npm_dots")
        with pytest.raises(ValueError, match="Unknown spinner style"):
            spinner.set_spinner_style(style="totally_made_up_style")

    def test_valid_style_does_not_raise(self):
        spinner = ThothSpinner(spinner_style="npm_dots")
        spinner.set_spinner_style(style="moon")


class TestProgressFormatValidation:
    def test_invalid_format_style_raises_with_suggestion(self):
        with pytest.raises(ValueError, match="Did you mean 'percentage'"):
            ProgressComponent(format={"style": "percetage"})  # codespell:ignore

    def test_invalid_format_style_no_match_raises(self):
        with pytest.raises(ValueError, match="Unknown progress format style"):
            ProgressComponent(format={"style": "totally_invalid"})

    def test_invalid_format_lists_available(self):
        with pytest.raises(ValueError, match="Available styles:"):
            ProgressComponent(format={"style": "bad"})

    def test_valid_format_styles_do_not_raise(self):
        for style in ("fraction", "percentage", "of_text", "count_only", "ratio"):
            ProgressComponent(format={"style": style})


class TestTimerFormatValidation:
    def test_invalid_format_style_raises_with_suggestion(self):
        with pytest.raises(ValueError, match="Did you mean"):
            TimerComponent(format={"style": "mm_ss"})

    def test_invalid_format_style_no_match_raises(self):
        with pytest.raises(ValueError, match="Unknown timer format style"):
            TimerComponent(format={"style": "totally_invalid"})

    def test_invalid_format_lists_available(self):
        with pytest.raises(ValueError, match="Available styles:"):
            TimerComponent(format={"style": "bad"})

    def test_valid_format_styles_do_not_raise(self):
        for style in (
            "seconds",
            "seconds_decimal",
            "seconds_precise",
            "milliseconds",
            "mm:ss",
            "hh:mm:ss",
            "compact",
            "full_ms",
            "auto",
            "auto_ms",
        ):
            TimerComponent(format={"style": style})
