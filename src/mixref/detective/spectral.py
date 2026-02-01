"""Spectral analysis and frequency band energy measurement.

This module provides frequency band analysis for mixing and mastering,
breaking audio into standard production frequency ranges.
"""

from dataclasses import dataclass
from typing import Any

import librosa
import numpy as np


@dataclass
class FrequencyBand:
    """Definition of a frequency band.

    Attributes:
        name: Band name (e.g., "Sub", "Low").
        min_hz: Minimum frequency in Hz.
        max_hz: Maximum frequency in Hz.

    """

    name: str
    min_hz: float
    max_hz: float


# Standard frequency bands for music production
FREQUENCY_BANDS = [
    FrequencyBand("Sub", 20.0, 60.0),
    FrequencyBand("Low", 60.0, 250.0),
    FrequencyBand("Mid", 250.0, 2000.0),
    FrequencyBand("High", 2000.0, 8000.0),
    FrequencyBand("Air", 8000.0, 20000.0),
]


@dataclass
class BandEnergy:
    """Energy measurement for a frequency band.

    Attributes:
        band_name: Name of the frequency band.
        energy_db: RMS energy in dB.
        energy_percent: Energy as percentage of total (0-100).

    """

    band_name: str
    energy_db: float
    energy_percent: float


@dataclass
class SpectralResult:
    """Result of spectral analysis.

    Attributes:
        bands: List of band energy measurements.
        total_energy_db: Total RMS energy across all frequencies.

    """

    bands: list[BandEnergy]
    total_energy_db: float


def analyze_spectrum(
    audio: Any,  # np.ndarray
    sample_rate: int,
    bands: list[FrequencyBand] | None = None,
) -> SpectralResult:
    """Analyze frequency band energy distribution.

    Args:
        audio: Audio signal as numpy array.
            Shape: (samples,) for mono or (channels, samples) for multi-channel.
        sample_rate: Sample rate in Hz.
        bands: Optional custom frequency bands.
            Defaults to standard production bands.

    Returns:
        SpectralResult with energy per band.

    Example:
        >>> import numpy as np
        >>> from mixref.detective.spectral import analyze_spectrum
        >>>
        >>> # Pink noise (equal energy per octave)
        >>> sr = 44100
        >>> duration = 5
        >>> audio = np.random.randn(sr * duration) * 0.1
        >>>
        >>> result = analyze_spectrum(audio, sr)
        >>> for band in result.bands:
        ...     print(f"{band.band_name}: {band.energy_percent:.1f}%")

    """
    if audio.size == 0:
        raise ValueError("Audio array is empty")

    # Convert to mono if needed
    if audio.ndim > 1:
        audio_mono = np.mean(audio, axis=0)
    else:
        audio_mono = audio

    # Use default bands if not provided
    if bands is None:
        bands = FREQUENCY_BANDS

    # Compute STFT
    stft = librosa.stft(audio_mono)
    magnitude = np.abs(stft)

    # Frequency bins
    freqs = librosa.fft_frequencies(sr=sample_rate)

    # Calculate energy per band
    band_energies = []
    total_energy = 0.0

    for band in bands:
        # Find frequency bins in this band
        band_mask = (freqs >= band.min_hz) & (freqs <= band.max_hz)

        # Calculate RMS energy in this band
        band_magnitude = magnitude[band_mask, :]
        if band_magnitude.size > 0:
            rms = np.sqrt(np.mean(band_magnitude**2))
            total_energy += rms**2
        else:
            rms = 0.0

        # Convert to dB
        energy_db = 20 * np.log10(rms + 1e-10)

        band_energies.append((band.name, energy_db, rms**2))

    # Calculate total RMS
    total_rms = np.sqrt(total_energy)
    total_db = 20 * np.log10(total_rms + 1e-10)

    # Calculate percentages
    results = []
    for name, energy_db, energy_sq in band_energies:
        percent = (energy_sq / (total_energy + 1e-10)) * 100
        results.append(
            BandEnergy(
                band_name=name,
                energy_db=float(energy_db),
                energy_percent=float(percent),
            )
        )

    return SpectralResult(
        bands=results,
        total_energy_db=float(total_db),
    )


def compare_spectral_balance(
    result1: SpectralResult,
    result2: SpectralResult,
) -> dict[str, float]:
    """Compare spectral balance between two tracks.

    Args:
        result1: Spectral analysis of first track.
        result2: Spectral analysis of second track (reference).

    Returns:
        Dict mapping band names to dB difference (track1 - track2).
        Positive = track1 louder in that band.

    Example:
        >>> from mixref.detective.spectral import analyze_spectrum, compare_spectral_balance
        >>> import numpy as np
        >>>
        >>> sr = 44100
        >>> audio1 = np.random.randn(sr * 5) * 0.1
        >>> audio2 = np.random.randn(sr * 5) * 0.1
        >>>
        >>> result1 = analyze_spectrum(audio1, sr)
        >>> result2 = analyze_spectrum(audio2, sr)
        >>> diff = compare_spectral_balance(result1, result2)

    """
    differences = {}

    # Match bands by name
    bands1_dict = {b.band_name: b.energy_db for b in result1.bands}
    bands2_dict = {b.band_name: b.energy_db for b in result2.bands}

    for band_name in bands1_dict:
        if band_name in bands2_dict:
            diff = bands1_dict[band_name] - bands2_dict[band_name]
            differences[band_name] = float(diff)

    return differences
