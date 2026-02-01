"""Tests for A/B comparison engine."""

import numpy as np
import pytest
from synthetic_audio import generate_pink_noise, generate_sine_wave

from mixref.compare import compare_loudness, compare_spectral, compare_tracks
from mixref.detective import BandEnergy, SpectralResult, analyze_spectrum
from mixref.meters import calculate_lufs


def test_compare_loudness_identical_tracks():
    """Test comparing identical tracks returns zero differences."""
    # Generate identical audio
    audio, sr = generate_sine_wave(duration=2.0)

    # Transpose for LUFS (expects channels first)
    result = calculate_lufs(audio, sr)

    # Compare with itself
    comparison = compare_loudness(result, result)

    assert comparison.lufs_difference == 0.0
    assert comparison.peak_difference == 0.0
    assert comparison.lra_difference == 0.0


def test_compare_loudness_louder_track():
    """Test comparing tracks where one is louder."""
    # Generate quiet and loud signals
    quiet, sr = generate_sine_wave(amplitude=0.1, duration=2.0)
    loud, _ = generate_sine_wave(amplitude=0.5, duration=2.0)

    quiet_result = calculate_lufs(quiet, sr)
    loud_result = calculate_lufs(loud, sr)

    comparison = compare_loudness(loud_result, quiet_result)

    # Loud should be louder (positive difference)
    assert comparison.lufs_difference > 0
    assert comparison.track_lufs == loud_result.integrated_lufs
    assert comparison.reference_lufs == quiet_result.integrated_lufs


def test_compare_spectral_identical_tracks():
    """Test spectral comparison of identical tracks."""
    audio, sr = generate_pink_noise(duration=2.0)

    spectral = analyze_spectrum(audio, sr)
    comparison = compare_spectral(spectral, spectral)

    # All differences should be zero
    for band in comparison.bands:
        assert band.difference == 0.0
        assert not band.is_significant


def test_compare_spectral_significance_threshold():
    """Test spectral comparison significance threshold."""
    # Create mock spectral results with known differences
    track_bands = [
        BandEnergy("Sub", -20.0, 10.0),  # 10% energy
        BandEnergy("Low", -10.0, 20.0),  # 20% energy
        BandEnergy("Mid", -5.0, 30.0),  # 30% energy
        BandEnergy("High", -8.0, 25.0),  # 25% energy
        BandEnergy("Air", -15.0, 15.0),  # 15% energy
    ]

    ref_bands = [
        BandEnergy("Sub", -15.0, 15.0),  # 15% (+5% difference - significant)
        BandEnergy("Low", -10.5, 21.0),  # 21% (+1% difference - not significant)
        BandEnergy("Mid", -5.0, 30.0),  # 30% (0% difference)
        BandEnergy("High", -10.0, 20.0),  # 20% (-5% difference - significant)
        BandEnergy("Air", -15.5, 14.0),  # 14% (-1% difference - not significant)
    ]

    track_spectral = SpectralResult(bands=track_bands, total_energy_db=-10.0)
    ref_spectral = SpectralResult(bands=ref_bands, total_energy_db=-10.0)

    comparison = compare_spectral(track_spectral, ref_spectral, significance_threshold=3.0)

    # Check differences
    assert comparison.bands[0].difference == pytest.approx(-5.0)  # Sub: track has less
    assert comparison.bands[0].is_significant  # -5% is > 3% threshold

    assert comparison.bands[1].difference == pytest.approx(-1.0)  # Low
    assert not comparison.bands[1].is_significant  # -1% is < 3%

    assert comparison.bands[2].difference == pytest.approx(0.0)  # Mid
    assert not comparison.bands[2].is_significant

    assert comparison.bands[3].difference == pytest.approx(5.0)  # High: track has more
    assert comparison.bands[3].is_significant  # 5% is > 3%


def test_compare_tracks_basic():
    """Test complete track comparison."""
    # Generate two different tracks
    track1, sr = generate_sine_wave(frequency=440.0, amplitude=0.3, duration=2.0)
    track2, _ = generate_sine_wave(frequency=880.0, amplitude=0.5, duration=2.0)

    result = compare_tracks(
        track1,
        track2,
        sr,
        track_name="Track A",
        reference_name="Track B",
        include_bpm=False,
        include_key=False,
    )

    # Check structure
    assert result.track_name == "Track A"
    assert result.reference_name == "Track B"
    assert result.loudness is not None
    assert result.spectral is not None
    assert result.track_bpm is None  # Not requested
    assert result.track_key is None  # Not requested


def test_compare_tracks_with_bpm():
    """Test track comparison including BPM detection."""
    audio1, sr = generate_pink_noise(duration=5.0)  # Longer for BPM detection
    audio2, _ = generate_pink_noise(duration=5.0)

    result = compare_tracks(
        audio1,
        audio2,
        sr,
        include_bpm=True,
        include_key=False,
    )

    # BPM should be detected (values may vary for noise)
    assert result.track_bpm is not None
    assert result.reference_bpm is not None
    assert result.bpm_difference is not None
    assert isinstance(result.bpm_difference, float)


def test_compare_tracks_with_key():
    """Test track comparison including key detection."""
    audio1, sr = generate_sine_wave(duration=10.0)  # Longer for key detection
    audio2, _ = generate_sine_wave(duration=10.0)

    result = compare_tracks(
        audio1,
        audio2,
        sr,
        include_bpm=False,
        include_key=True,
    )

    # Key should be detected
    assert result.track_key is not None
    assert result.reference_key is not None
    assert isinstance(result.track_key, str)
    assert isinstance(result.reference_key, str)


def test_compare_tracks_stereo():
    """Test track comparison with stereo audio."""
    # Generate stereo audio (samples, 2)
    mono, sr = generate_pink_noise(duration=2.0)
    stereo = np.stack([mono, mono], axis=1)  # (samples, 2)

    result = compare_tracks(stereo, stereo, sr)

    # Should work with stereo
    assert result.loudness is not None
    assert result.spectral is not None


def test_compare_tracks_invalid_sample_rate():
    """Test that invalid sample rate raises error."""
    audio, _ = generate_sine_wave()

    with pytest.raises(ValueError, match="Sample rate must be positive"):
        compare_tracks(audio, audio, sample_rate=-1)

    with pytest.raises(ValueError, match="Sample rate must be positive"):
        compare_tracks(audio, audio, sample_rate=0)


def test_loudness_comparison_attributes():
    """Test LoudnessComparison has all expected attributes."""
    audio, sr = generate_sine_wave(duration=2.0)
    result = calculate_lufs(audio, sr)
    comparison = compare_loudness(result, result)

    # Check all attributes exist
    assert hasattr(comparison, "track_lufs")
    assert hasattr(comparison, "reference_lufs")
    assert hasattr(comparison, "lufs_difference")
    assert hasattr(comparison, "track_peak")
    assert hasattr(comparison, "reference_peak")
    assert hasattr(comparison, "peak_difference")
    assert hasattr(comparison, "track_lra")
    assert hasattr(comparison, "reference_lra")
    assert hasattr(comparison, "lra_difference")


def test_spectral_comparison_band_order():
    """Test that spectral comparison preserves band order."""
    audio, sr = generate_pink_noise(duration=2.0)
    spectral = analyze_spectrum(audio, sr)
    comparison = compare_spectral(spectral, spectral)

    expected_order = ["Sub", "Low", "Mid", "High", "Air"]
    actual_order = [band.band_name for band in comparison.bands]

    assert actual_order == expected_order
