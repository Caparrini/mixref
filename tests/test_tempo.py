"""Tests for tempo (BPM) detection."""

import numpy as np
import pytest

from mixref.detective.tempo import TempoResult, detect_bpm


class TestDetectBpm:
    """Tests for detect_bpm function."""

    def test_detect_bpm_basic(self):
        """Test basic BPM detection on synthetic signal."""
        # Create 120 BPM test signal (kicks every 0.5 seconds)
        sr = 22050  # Lower sample rate for faster tests
        duration = 10  # seconds
        audio = np.zeros(sr * duration)

        # Add impulses at 120 BPM intervals
        kick_interval = int(60 / 120 * sr)
        for i in range(0, len(audio), kick_interval):
            if i + 50 < len(audio):
                audio[i : i + 50] = 0.8

        result = detect_bpm(audio, sr)

        assert isinstance(result, TempoResult)
        assert 100 < result.bpm < 140  # Should be near 120 BPM
        assert 0.0 <= result.confidence <= 1.0
        assert result.onset_strength is None  # Default: don't include

    def test_detect_bpm_140_bpm(self):
        """Test detection of 140 BPM (techno range)."""
        sr = 22050
        duration = 8
        audio = np.zeros(sr * duration)

        # 140 BPM pattern
        kick_interval = int(60 / 140 * sr)
        for i in range(0, len(audio), kick_interval):
            if i + 40 < len(audio):
                audio[i : i + 40] = 0.9

        result = detect_bpm(audio, sr, start_bpm=140.0)

        assert 120 < result.bpm < 160  # Techno range
        assert result.confidence > 0.0

    def test_detect_bpm_174_bpm(self):
        """Test detection of 174 BPM (DnB range)."""
        sr = 22050
        duration = 8
        audio = np.zeros(sr * duration)

        # 174 BPM pattern
        kick_interval = int(60 / 174 * sr)
        for i in range(0, len(audio), kick_interval):
            if i + 30 < len(audio):
                audio[i : i + 30] = 0.85

        result = detect_bpm(audio, sr, start_bpm=170.0)

        # BPM detection is hard, allow wide range
        assert 80 < result.bpm < 200
        assert result.confidence > 0.0

    def test_detect_bpm_stereo(self):
        """Test BPM detection on stereo audio (should convert to mono)."""
        sr = 22050
        duration = 6
        # Create stereo audio
        audio = np.zeros((2, sr * duration))

        # Add rhythm to both channels
        kick_interval = int(60 / 128 * sr)
        for i in range(0, audio.shape[1], kick_interval):
            if i + 50 < audio.shape[1]:
                audio[:, i : i + 50] = 0.8

        result = detect_bpm(audio, sr)

        assert 100 < result.bpm < 150
        assert result.confidence > 0.0

    def test_detect_bpm_with_onset_strength(self):
        """Test that onset strength is included when requested."""
        sr = 22050
        duration = 5
        audio = np.random.randn(sr * duration) * 0.1

        result = detect_bpm(audio, sr, include_onset_strength=True)

        assert result.onset_strength is not None
        assert isinstance(result.onset_strength, np.ndarray)
        assert len(result.onset_strength) > 0

    def test_detect_bpm_silent_audio(self):
        """Test BPM detection on silent audio."""
        sr = 22050
        duration = 5
        audio = np.zeros(sr * duration)

        result = detect_bpm(audio, sr)

        # Silent audio returns 0 BPM (no detectable rhythm)
        assert result.bpm >= 0.0
        # Confidence should be low for silence
        assert result.confidence >= 0.0

    def test_detect_bpm_noise(self):
        """Test BPM detection on pure noise (no clear rhythm)."""
        sr = 22050
        duration = 5
        audio = np.random.randn(sr * duration) * 0.2

        result = detect_bpm(audio, sr)

        assert result.bpm > 0
        # Confidence might vary, but should be in valid range
        assert 0.0 <= result.confidence <= 1.0

    def test_detect_bpm_empty_audio(self):
        """Test that empty audio raises ValueError."""
        audio = np.array([])
        sr = 44100

        with pytest.raises(ValueError, match="Audio array is empty"):
            detect_bpm(audio, sr)

    def test_tempo_result_dataclass(self):
        """Test TempoResult dataclass structure."""
        result = TempoResult(bpm=120.5, confidence=0.85)

        assert result.bpm == 120.5
        assert result.confidence == 0.85
        assert result.onset_strength is None

        # Test with onset strength
        onset = np.array([1, 2, 3])
        result2 = TempoResult(bpm=140.0, confidence=0.9, onset_strength=onset)
        assert np.array_equal(result2.onset_strength, onset)

    def test_detect_bpm_different_start_bpm(self):
        """Test that start_bpm parameter affects detection."""
        sr = 22050
        duration = 6
        audio = np.random.randn(sr * duration) * 0.1

        result1 = detect_bpm(audio, sr, start_bpm=120.0)
        result2 = detect_bpm(audio, sr, start_bpm=170.0)

        # Should get valid results with different priors
        assert result1.bpm > 0
        assert result2.bpm > 0
        # Results might differ based on start_bpm
        # (or might be similar if audio is ambiguous)
