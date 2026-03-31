"""Tests for the interactive TUI style browser (thothspinner browse)."""

from __future__ import annotations

import pytest

from thothspinner.__browse__ import BrowseApp, PreviewPanel, StyleListItem
from thothspinner.rich.spinners.frames import SPINNER_FRAMES


class TestBrowseApp:
    @pytest.mark.asyncio
    async def test_app_mounts_with_all_styles(self):
        async with BrowseApp().run_test() as pilot:
            items = pilot.app.query(StyleListItem)
            assert len(items) == len(SPINNER_FRAMES)

    @pytest.mark.asyncio
    async def test_first_style_is_selected_on_mount(self):
        async with BrowseApp().run_test() as pilot:
            panel = pilot.app.query_one(PreviewPanel)
            # Initial style should be the first alphabetically
            from thothspinner.__browse__ import SORTED_STYLES

            assert panel.style_name == SORTED_STYLES[0]

    @pytest.mark.asyncio
    async def test_pressing_down_changes_preview_style(self):
        async with BrowseApp().run_test() as pilot:
            panel = pilot.app.query_one(PreviewPanel)
            await pilot.press("down")
            await pilot.pause()
            # After pressing down, style should change to next in list
            from thothspinner.__browse__ import SORTED_STYLES

            expected = SORTED_STYLES[1]
            assert panel.style_name == expected

    @pytest.mark.asyncio
    async def test_pressing_q_exits_app(self):
        async with BrowseApp().run_test() as pilot:
            await pilot.press("q")
            # App should have exited cleanly (no exception)


class TestPreviewPanel:
    def test_sorted_styles_covers_all_frames(self):
        from thothspinner.__browse__ import SORTED_STYLES

        assert set(SORTED_STYLES) == set(SPINNER_FRAMES.keys())
        assert len(SORTED_STYLES) == len(SPINNER_FRAMES)
