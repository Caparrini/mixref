"""Tests for musical key detection."""

import numpy as np
import pytest

from mixref.detective.key import (
    CAMELOT_WHEEL,
    KeyResult,
    detect_key,
    get_compatible_keys,
)


class TestCamelotWheel:
    """Tests for Camelot wheel mapping."""

    def test_camelot_wheel_completeness(self):
        """Test that all 24 keys are mapped."""
        assert len(CAMELOT_WHEEL) == 24

    def test_camelot_wheel_c_major(self):
        """Test C major mapping."""
        assert CAMELOT_WHEEL["C major"] == "8B"

    def test_camelot_wheel_a_minor(self):
        """Test A minor mapping (relative to C major)."""
        assert CAMELOT_WHEEL["A minor"] == "8A"

    def test_camelot_wheel_uses_flats(self):
        """Test that flat notation is used."""
        assert "Eb major" in CAMELOT_WHEEL
        assert "Eb minor" in CAMELOT_WHEEL
        assert "D# major" not in CAMELOT_WHEEL


class TestDetectKey:
    """Tests for key detection."""

    def test_detect_key_basic(self):
        """Test basic key detection on synthetic signal."""
        sr = 22050
        duration = 5
        # Simple sine wave (not really in a key, but should return something)
        audio = np.sin(2 * np.pi * 440 * np.arange(sr * duration) / sr)

        result = detect_key(audio, sr)

        assert isinstance(result, KeyResult)
        assert result.key in CAMELOT_WHEEL
        assert result.camelot in CAMELOT_WHEEL.values()
        assert 0.0 <= result.confidence <= 1.0

    def test_detect_key_stereo(self):
        """Test key detection on stereo audio."""
        sr = 22050
        duration = 5
        audio = np.random.randn(2, sr * duration) * 0.1

        result = detect_key(audio, sr)

        assert isinstance(result, KeyResult)
        assert result.key in CAMELOT_WHEEL

    def test_detect_key_empty_audio(self):
        """Test that empty audio raises ValueError."""
        audio = np.array([])
        sr = 44100

        with pytest.raises(ValueError, match="Audio array is empty"):
            detect_key(audio, sr)

    def test_key_result_dataclass(self):
        """Test KeyResult dataclass structure."""
        result = KeyResult(
            key="C major",
            camelot="8B",
            confidence=0.85,
        )

        assert result.key == "C major"
        assert result.camelot == "8B"
        assert result.confidence == 0.85

    def test_detect_key_noise(self):
        """Test key detection on random noise."""
        sr = 22050
        duration = 5
        audio = np.random.randn(sr * duration) * 0.2

        result = detect_key(audio, sr)

        # Should still return a valid key, even if confidence is low
        assert result.key in CAMELOT_WHEEL
        assert 0.0 <= result.confidence <= 1.0


class TestCompatibleKeys:
    """Tests for compatible key finding."""

    def test_get_compatible_keys_c_major(self):
        """Test compatible keys for C major (8B)."""
        compatible = get_compatible_keys("C major")

        assert "8A" in compatible  # Relative minor (A minor)
        assert "7B" in compatible  # One step down
        assert "9B" in compatible  # One step up
        assert len(compatible) == 3

    def test_get_compatible_keys_camelot_notation(self):
        """Test with Camelot notation directly."""
        compatible = get_compatible_keys("5A")

        assert "5B" in compatible  # Relative major
        assert "4A" in compatible  # Adjacent
        assert "6A" in compatible  # Adjacent
        assert len(compatible) == 3

    def test_get_compatible_keys_wraparound(self):
        """Test wraparound at 1 and 12."""
        # 1B should wrap to 12B and 2B
        compatible = get_compatible_keys("1B")
        assert "12B" in compatible
        assert "2B" in compatible
        assert "1A" in compatible

        # 12A should wrap to 11A and 1A
        compatible = get_compatible_keys("12A")
        assert "11A" in compatible
        assert "1A" in compatible
        assert "12B" in compatible

    def test_get_compatible_keys_invalid_input(self):
        """Test with invalid input."""
        compatible = get_compatible_keys("invalid")
        assert compatible == []

        compatible = get_compatible_keys("")
        assert compatible == []

    def test_get_compatible_keys_all_majors(self):
        """Test that all major keys have 3 compatible keys."""
        for key_name, camelot in CAMELOT_WHEEL.items():
            if "major" in key_name:
                compatible = get_compatible_keys(camelot)
                assert len(compatible) == 3, f"{key_name} should have 3 compatible keys"
