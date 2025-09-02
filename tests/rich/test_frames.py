"""Unit tests for spinner frame definitions."""

from __future__ import annotations

from thothspinner.rich.spinners.frames import SPINNER_FRAMES, validate_frames


class TestFrames:
    """Test suite for spinner frame definitions."""

    def test_all_builtin_frames_valid(self):
        """Test M02-TS01: All built-in frame sets have valid characters."""
        for name, spinner_def in SPINNER_FRAMES.items():
            frames = spinner_def["frames"]
            assert validate_frames(frames), f"Invalid frames for {name}"
            assert len(frames) > 0, f"Empty frames for {name}"
            assert isinstance(spinner_def["interval"], float), f"Invalid interval for {name}"
            assert spinner_def["interval"] > 0, f"Non-positive interval for {name}"

    def test_npm_dots_frames(self):
        """Test NPM dots spinner has correct frames."""
        npm_dots = SPINNER_FRAMES["npm_dots"]
        assert len(npm_dots["frames"]) == 10
        assert npm_dots["interval"] == 0.08
        # Check it contains braille patterns
        assert all(ord(c) >= 0x2800 and ord(c) <= 0x28FF for c in npm_dots["frames"])

    def test_claude_stars_frames(self):
        """Test Claude stars spinner has correct frames."""
        claude_stars = SPINNER_FRAMES["claude_stars"]
        assert len(claude_stars["frames"]) == 10
        assert claude_stars["interval"] == 0.1
        # Check it contains star-like characters
        assert "✢" in claude_stars["frames"]
        assert "✳" in claude_stars["frames"]

    def test_classic_frames(self):
        """Test classic spinner has simple ASCII frames."""
        classic = SPINNER_FRAMES["classic"]
        assert classic["frames"] == ["|", "/", "-", "\\"]
        assert classic["interval"] == 0.1

    def test_validate_frames_valid_cases(self):
        """Test validate_frames with valid inputs."""
        assert validate_frames(["a", "b", "c"]) is True
        assert validate_frames(["⠋", "⠙", "⠹"]) is True
        assert validate_frames(["1"]) is True

    def test_validate_frames_invalid_cases(self):
        """Test validate_frames with invalid inputs."""
        assert validate_frames([]) is False  # Empty list
        assert validate_frames(["a", "", "c"]) is False  # Empty string
        assert validate_frames(["a", 1, "c"]) is False  # Non-string
        assert validate_frames("abc") is False  # Not a list
        assert validate_frames(None) is False  # None

    def test_all_spinners_have_required_keys(self):
        """Test all spinner definitions have required keys."""
        required_keys = {"frames", "interval"}
        for name, spinner_def in SPINNER_FRAMES.items():
            assert set(spinner_def.keys()) == required_keys, f"Missing keys for {name}"

    def test_frame_uniqueness_within_spinner(self):
        """Test that some spinners have unique frames (not all the same)."""
        for name, spinner_def in SPINNER_FRAMES.items():
            frames = spinner_def["frames"]
            # Most spinners should have different frames
            if name not in ["bounce"]:  # bounce has repeated frames by design
                unique_frames = set(frames)
                assert len(unique_frames) > 1, f"All frames are the same for {name}"

    def test_spinner_styles_available(self):
        """Test that expected spinner styles are available."""
        expected_styles = [
            "npm_dots",
            "claude_stars",
            "classic",
            "dots",
            "dots2",
            "dots3",
            "arrows",
            "circle",
            "square",
            "triangle",
            "bounce",
            "box_bounce",
            "star",
        ]
        for style in expected_styles:
            assert style in SPINNER_FRAMES, f"Missing expected style: {style}"
