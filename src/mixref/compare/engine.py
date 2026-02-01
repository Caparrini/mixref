"""Comparison engine for A/B analysis.

This module provides tools to compare two audio tracks and identify differences
in loudness, spectral balance, and other characteristics.
"""

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt

from mixref.detective import SpectralResult, analyze_spectrum, detect_bpm, detect_key
from mixref.meters import LoudnessResult, calculate_lufs


@dataclass
class LoudnessComparison:
    """Comparison of loudness metrics between two tracks.

    Attributes:
        track_lufs: Track's integrated LUFS
        reference_lufs: Reference's integrated LUFS
        lufs_difference: Difference in LUFS (positive = track is louder)
        track_peak: Track's true peak in dBTP
        reference_peak: Reference's true peak in dBTP
        peak_difference: Difference in true peak (positive = track has higher peak)
        track_lra: Track's loudness range in LU
        reference_lra: Reference's loudness range in LU
        lra_difference: Difference in LRA (positive = track has wider dynamics)
    """

    track_lufs: float
    reference_lufs: float
    lufs_difference: float
    track_peak: float
    reference_peak: float
    peak_difference: float
    track_lra: float
    reference_lra: float
    lra_difference: float


@dataclass
class BandComparison:
    """Comparison of a single frequency band.

    Attributes:
        band_name: Name of frequency band (Sub, Low, Mid, High, Air)
        track_energy: Track's energy in this band (percentage)
        reference_energy: Reference's energy in this band (percentage)
        difference: Difference in energy (positive = track has more energy)
        is_significant: True if difference is > 3dB (noticeable)
    """

    band_name: str
    track_energy: float
    reference_energy: float
    difference: float
    is_significant: bool


@dataclass
class SpectralComparison:
    """Comparison of spectral balance between two tracks.

    Attributes:
        bands: List of band comparisons (Sub, Low, Mid, High, Air)
    """

    bands: list[BandComparison]


@dataclass
class ComparisonResult:
    """Complete A/B comparison result.

    Attributes:
        track_name: Name of analyzed track
        reference_name: Name of reference track
        loudness: Loudness comparison
        spectral: Spectral balance comparison
        track_bpm: Track's BPM (optional)
        reference_bpm: Reference's BPM (optional)
        bpm_difference: Difference in BPM (optional)
        track_key: Track's musical key (optional)
        reference_key: Reference's musical key (optional)
    """

    track_name: str
    reference_name: str
    loudness: LoudnessComparison
    spectral: SpectralComparison
    track_bpm: float | None = None
    reference_bpm: float | None = None
    bpm_difference: float | None = None
    track_key: str | None = None
    reference_key: str | None = None


def compare_loudness(
    track_result: LoudnessResult,
    reference_result: LoudnessResult,
) -> LoudnessComparison:
    """Compare loudness metrics between two tracks.

    Args:
        track_result: Loudness result for the track being analyzed
        reference_result: Loudness result for the reference track

    Returns:
        LoudnessComparison with differences

    Example:
        >>> from mixref.meters import calculate_lufs
        >>> track_lufs = calculate_lufs(track_audio, 44100)
        >>> ref_lufs = calculate_lufs(ref_audio, 44100)
        >>> comparison = compare_loudness(track_lufs, ref_lufs)
        >>> print(f"LUFS difference: {comparison.lufs_difference:+.1f} dB")
        LUFS difference: -2.1 dB
    """
    lufs_diff = track_result.integrated_lufs - reference_result.integrated_lufs
    peak_diff = track_result.true_peak_db - reference_result.true_peak_db
    lra_diff = track_result.loudness_range_lu - reference_result.loudness_range_lu

    return LoudnessComparison(
        track_lufs=track_result.integrated_lufs,
        reference_lufs=reference_result.integrated_lufs,
        lufs_difference=lufs_diff,
        track_peak=track_result.true_peak_db,
        reference_peak=reference_result.true_peak_db,
        peak_difference=peak_diff,
        track_lra=track_result.loudness_range_lu,
        reference_lra=reference_result.loudness_range_lu,
        lra_difference=lra_diff,
    )


def compare_spectral(
    track_result: SpectralResult,
    reference_result: SpectralResult,
    significance_threshold: float = 3.0,
) -> SpectralComparison:
    """Compare spectral balance between two tracks.

    Args:
        track_result: Spectral result for the track being analyzed
        reference_result: Spectral result for the reference track
        significance_threshold: Minimum difference (in percentage points) to be
            considered significant. Default: 3.0 (roughly 3dB difference)

    Returns:
        SpectralComparison with band-by-band differences

    Example:
        >>> from mixref.detective import analyze_spectrum
        >>> track_spec = analyze_spectrum(track_audio, 44100)
        >>> ref_spec = analyze_spectrum(ref_audio, 44100)
        >>> comparison = compare_spectral(track_spec, ref_spec)
        >>> for band in comparison.bands:
        ...     if band.is_significant:
        ...         print(f"{band.band_name}: {band.difference:+.1f}%")
        Sub: -3.2%
        High: +4.1%
    """
    # Create a dict for quick lookup by band name
    ref_bands = {band.band_name: band for band in reference_result.bands}

    comparisons: list[BandComparison] = []
    for track_band in track_result.bands:
        ref_band = ref_bands[track_band.band_name]

        diff = track_band.energy_percent - ref_band.energy_percent
        is_significant = abs(diff) >= significance_threshold

        comparisons.append(
            BandComparison(
                band_name=track_band.band_name,
                track_energy=track_band.energy_percent,
                reference_energy=ref_band.energy_percent,
                difference=diff,
                is_significant=is_significant,
            )
        )

    return SpectralComparison(bands=comparisons)


def compare_tracks(
    track_audio: npt.NDArray[np.float32],
    reference_audio: npt.NDArray[np.float32],
    sample_rate: int,
    track_name: str = "Track",
    reference_name: str = "Reference",
    include_bpm: bool = False,
    include_key: bool = False,
) -> ComparisonResult:
    """Compare two audio tracks comprehensively.

    Analyzes both tracks and compares loudness, spectral balance, BPM, and key.

    Args:
        track_audio: Audio data for track being analyzed.
            Shape: (samples,) for mono or (samples, channels) for stereo
        reference_audio: Audio data for reference track.
            Shape: (samples,) for mono or (samples, channels) for stereo
        sample_rate: Sample rate in Hz (must be same for both tracks)
        track_name: Human-readable name for the track (e.g., filename)
        reference_name: Human-readable name for the reference
        include_bpm: If True, detect and compare BPM (slower)
        include_key: If True, detect and compare musical key (slower)

    Returns:
        ComparisonResult with all metrics

    Raises:
        ValueError: If audio arrays have incompatible shapes or invalid sample rate

    Example:
        >>> from mixref.audio import load_audio
        >>> track, sr = load_audio("my_mix.wav")
        >>> reference, _ = load_audio("pro_reference.wav", sample_rate=sr)
        >>> result = compare_tracks(track, reference, sr, include_bpm=True)
        >>> print(f"LUFS diff: {result.loudness.lufs_difference:+.1f} dB")
        LUFS diff: -2.3 dB
    """
    # Validate inputs
    if sample_rate <= 0:
        raise ValueError(f"Sample rate must be positive, got {sample_rate}")

    # Transpose audio for LUFS calculation if stereo (samples, channels) -> (channels, samples)
    track_for_lufs = track_audio.T if track_audio.ndim == 2 else track_audio
    ref_for_lufs = reference_audio.T if reference_audio.ndim == 2 else reference_audio

    # Calculate loudness metrics
    track_loudness = calculate_lufs(track_for_lufs, sample_rate)
    ref_loudness = calculate_lufs(ref_for_lufs, sample_rate)
    loudness_comparison = compare_loudness(track_loudness, ref_loudness)

    # Analyze spectral balance
    track_spectral = analyze_spectrum(track_audio, sample_rate)
    ref_spectral = analyze_spectrum(reference_audio, sample_rate)
    spectral_comparison = compare_spectral(track_spectral, ref_spectral)

    # Optional: BPM comparison
    track_bpm_val = None
    ref_bpm_val = None
    bpm_diff = None
    if include_bpm:
        track_bpm = detect_bpm(track_audio, sample_rate)
        ref_bpm = detect_bpm(reference_audio, sample_rate)
        track_bpm_val = track_bpm.bpm
        ref_bpm_val = ref_bpm.bpm
        bpm_diff = track_bpm_val - ref_bpm_val

    # Optional: Key comparison
    track_key_val = None
    ref_key_val = None
    if include_key:
        track_key_result = detect_key(track_audio, sample_rate)
        ref_key_result = detect_key(reference_audio, sample_rate)
        track_key_val = f"{track_key_result.key} ({track_key_result.camelot})"
        ref_key_val = f"{ref_key_result.key} ({ref_key_result.camelot})"

    return ComparisonResult(
        track_name=track_name,
        reference_name=reference_name,
        loudness=loudness_comparison,
        spectral=spectral_comparison,
        track_bpm=track_bpm_val,
        reference_bpm=ref_bpm_val,
        bpm_difference=bpm_diff,
        track_key=track_key_val,
        reference_key=ref_key_val,
    )
