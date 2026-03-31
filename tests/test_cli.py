"""Tests for the thothspinner CLI entry point."""

from __future__ import annotations

import subprocess
import sys
from unittest.mock import MagicMock, patch

import pytest

from thothspinner.__main__ import cmd_browse, cmd_preview, main


class TestCLIMain:
    def test_no_subcommand_exits_nonzero(self):
        with pytest.raises(SystemExit) as exc_info:
            main([])
        assert exc_info.value.code != 0

    def test_help_exits_zero(self):
        with pytest.raises(SystemExit) as exc_info:
            main(["--help"])
        assert exc_info.value.code == 0

    def test_preview_help_exits_zero(self):
        with pytest.raises(SystemExit) as exc_info:
            main(["preview", "--help"])
        assert exc_info.value.code == 0

    def test_python_m_thothspinner_help(self):
        result = subprocess.run(
            [sys.executable, "-m", "thothspinner", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "preview" in result.stdout
        assert "browse" in result.stdout


class TestCmdPreview:
    def _make_args(self, style=None):
        args = MagicMock()
        args.style = style
        return args

    def test_valid_single_style_returns_zero(self):
        with (
            patch("time.sleep"),
            patch("rich.live.Live.__enter__"),
            patch("rich.live.Live.__exit__"),
        ):
            result = cmd_preview(self._make_args("npm_dots"))
        assert result == 0

    def test_invalid_style_returns_one(self, capsys):
        result = cmd_preview(self._make_args("npmdots"))
        assert result == 1
        captured = capsys.readouterr()
        assert "Did you mean" in captured.out

    def test_invalid_style_with_no_suggestion_returns_one(self, capsys):
        result = cmd_preview(self._make_args("zzz_totally_invalid_xyz"))
        assert result == 1
        captured = capsys.readouterr()
        assert "Available styles" in captured.out

    def test_all_styles_returns_zero(self):
        with (
            patch("time.sleep"),
            patch("rich.live.Live.__enter__"),
            patch("rich.live.Live.__exit__"),
        ):
            result = cmd_preview(self._make_args(None))
        assert result == 0


class TestCmdBrowse:
    def _make_args(self):
        return MagicMock()

    def test_browse_calls_app_run(self):
        mock_app = MagicMock()
        with patch("thothspinner.__browse__.BrowseApp", return_value=mock_app) as mock_cls:
            result = cmd_browse(self._make_args())
        mock_cls.assert_called_once()
        mock_app.run.assert_called_once()
        assert result == 0
