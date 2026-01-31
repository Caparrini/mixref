"""Tests for spectral analysis."""

import numpy as np
import pytest

from mixref.detective.spectral import (
    FREQUENCY_BANDS,
    BandEnergy,
    FrequencyBand,
    SpectralResult,
    analyze_spectrum,
    compare_spectral_balance,
)


class TestFrequencyBands:
    """Tests for frequency band definitions."""

    def test_frequency_bands_count(self):
        """Test that we have 5 standard bands."""
        assert len(FREQUENCY_BANDS) == 5

    def test_frequency_bands_names(self):
        """Test band names."""
        names = [b.name for b in FREQUENCY_BANDS]
        assert "Sub" in names
        assert "Low" in names
        assert "Mid" in names
        assert "High" in names
        assert "Air" in names

    def test_frequency_bands_ranges(self):
        """Test frequency ranges."""
        sub = FREQUENCY_BANDS[0]
        assert sub.name == "Sub"
        assert sub.min_hz == 20.0
        assert sub.max_hz == 60.0

    def test_frequency_band_dataclass(self):
        """Test FrequencyBand dataclass."""
        band = FrequencyBand("Test", 100.0, 200.0)
        assert band.name == "Test"
        assert band.min_hz == 100.0
        assert band.max_hz == 200.0


class TestAnalyzeSpectrum:
    """Tests for spectral analysis."""

    def test_analyze_spectrum_basic(self):
        """Test basic spectral analysis."""
        sr = 22050
        duration = 3
        # White noise
        audio = np.random.randn(sr * duration) * 0.1

        result = analyze_spectrum(audio, sr)

        assert isinstance(result, SpectralResult)
        assert len(result.bands) == 5
        # Just verify we got a result
        assert isinstance(result.total_energy_db, float)

    def test_analyze_spectrum_bands(self):
        """Test that all bands are analyzed."""
        sr = 22050
        duration = 3
        audio = np.random.randn(sr * duration) * 0.1

        result = analyze_spectrum(audio, sr)

        band_names = [b.band_name for b in result.bands]
        assert "Sub" in band_names
        assert "Low" in band_names
        assert "Mid" in band_names
        assert "High" in band_names
        assert "Air" in band_names

    def test_analyze_spectrum_percentages_sum(self):
        """Test that band percentages sum to ~100."""
        sr = 22050
        duration = 3
        audio = np.random.randn(sr * duration) * 0.1

        result = analyze_spectrum(audio, sr)

        total_percent = sum(b.energy_percent for b in result.bands)
        # Should be close to 100% (allow small floating point error)
        assert 99.0 < total_percent < 101.0

    def test_analyze_spectrum_stereo(self):
        """Test spectral analysis on stereo audio."""
        sr = 22050
        duration = 3
        audio = np.random.randn(2, sr * duration) * 0.1

        result = analyze_spectrum(audio, sr)

        assert len(result.bands) == 5
        assert isinstance(result.total_energy_db, float)

    def test_analyze_spectrum_empty_audio(self):
        """Test that empty audio raises ValueError."""
        audio = np.array([])
        sr = 44100

        with pytest.raises(ValueError, match="Audio array is empty"):
            analyze_spectrum(audio, sr)

    def test_analyze_spectrum_custom_bands(self):
        """Test with custom frequency bands."""
        sr = 22050
        duration = 3
        audio = np.random.randn(sr * duration) * 0.1

        custom_bands = [
            FrequencyBand("Low", 20.0, 500.0),
            FrequencyBand("High", 500.0, 20000.0),
        ]

        result = analyze_spectrum(audio, sr, bands=custom_bands)

        assert len(result.bands) == 2
        assert result.bands[0].band_name == "Low"
        assert result.bands[1].band_name == "High"

    def test_band_energy_dataclass(self):
        """Test BandEnergy dataclass."""
        energy = BandEnergy("Mid", -20.0, 35.5)
        assert energy.band_name == "Mid"
        assert energy.energy_db == -20.0
        assert energy.energy_percent == 35.5

    def test_spectral_result_dataclass(self):
        """Test SpectralResult dataclass."""
        bands = [
            BandEnergy("Sub", -30.0, 10.0),
            BandEnergy("Low", -25.0, 20.0),
        ]
        result = SpectralResult(bands=bands, total_energy_db=-20.0)

        assert len(result.bands) == 2
        assert result.total_energy_db == -20.0


class TestCompareSpectralBalance:
    """Tests for spectral comparison."""

    def test_compare_spectral_balance_basic(self):
        """Test basic spectral comparison."""
        sr = 22050
        duration = 3
        audio1 = np.random.randn(sr * duration) * 0.1
        audio2 = np.random.randn(sr * duration) * 0.1

        result1 = analyze_spectrum(audio1, sr)
        result2 = analyze_spectrum(audio2, sr)
        diff = compare_spectral_balance(result1, result2)

        assert isinstance(diff, dict)
        assert len(diff) == 5  # All 5 bands
        assert "Sub" in diff
        assert "Low" in diff

    def test_compare_spectral_balance_identical(self):
        """Test comparing identical signals."""
        sr = 22050
        duration = 3
        audio = np.random.randn(sr * duration) * 0.1

        result = analyze_spectrum(audio, sr)
        diff = compare_spectral_balance(result, result)

        # All differences should be ~0
        for _band_name, difference in diff.items():
            assert abs(difference) < 0.01

    def test_compare_spectral_balance_different(self):
        """Test comparing different signals."""
        sr = 22050
        duration = 3

        # One signal
        audio1 = np.random.randn(sr * duration) * 0.1

        # Different signal
        audio2 = np.random.randn(sr * duration) * 0.2  # Louder

        result1 = analyze_spectrum(audio1, sr)
        result2 = analyze_spectrum(audio2, sr)
        diff = compare_spectral_balance(result1, result2)

        # Should have some differences
        assert len(diff) == 5
