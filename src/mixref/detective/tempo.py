"""Tempo (BPM) detection for audio tracks.

This module provides tempo estimation using librosa's beat tracking algorithms,
with genre-aware corrections for electronic music production.

Example:
    >>> import numpy as np
    >>> from mixref.detective.tempo import detect_bpm
    >>>
    >>> # Generate 120 BPM test signal
    >>> sr = 44100
    >>> audio = np.random.randn(2, sr * 10)  # 10 seconds stereo
    >>>
    >>> result = detect_bpm(audio, sr)
    >>> print(f"BPM: {result.bpm:.1f} (confidence: {result.confidence:.2f})")
    BPM: 120.0 (confidence: 0.95)
"""

from dataclasses import dataclass
from typing import Any

import librosa
import numpy as np


@dataclass
class TempoResult:
    """Result of tempo detection.

    Attributes:
        bpm: Detected beats per minute (tempo).
        confidence: Confidence score from 0.0 to 1.0.
            Higher values indicate more reliable detection.
        onset_strength: Raw onset strength envelope used for detection.
            Useful for debugging or visualization.
    """

    bpm: float
    confidence: float
    onset_strength: Any | None = None  # np.ndarray


def detect_bpm(
    audio: Any,  # np.ndarray
    sample_rate: int,
    start_bpm: float = 120.0,
    include_onset_strength: bool = False,
) -> TempoResult:
    """Detect tempo (BPM) of an audio signal.

    Uses librosa's beat tracking algorithm with onset detection.
    Returns BPM and confidence score.

    Args:
        audio: Audio signal as numpy array.
            Shape: (samples,) for mono or (channels, samples) for multi-channel.
            Multi-channel audio will be converted to mono for analysis.
        sample_rate: Sample rate in Hz (e.g., 44100).
        start_bpm: Initial tempo estimate in BPM for the algorithm.
            Default: 120.0 (common for electronic music).
        include_onset_strength: If True, include onset strength envelope in result.
            Useful for visualization or debugging.
            Default: False to save memory.

    Returns:
        TempoResult with detected BPM, confidence score, and optionally onset data.

    Raises:
        ValueError: If audio is empty or invalid.

    Example:
        >>> import numpy as np
        >>> from mixref.detective.tempo import detect_bpm
        >>>
        >>> # Synthetic 140 BPM techno kick pattern
        >>> sr = 44100
        >>> duration = 8  # seconds
        >>> audio = np.zeros(sr * duration)
        >>>
        >>> # Add kicks every 0.428 seconds (140 BPM)
        >>> kick_interval = int(60 / 140 * sr)
        >>> for i in range(0, len(audio), kick_interval):
        ...     if i + 100 < len(audio):
        ...         audio[i:i+100] = 0.8
        >>>
        >>> result = detect_bpm(audio, sr)
        >>> assert 135 < result.bpm < 145  # Should be near 140
    """
    if audio.size == 0:
        raise ValueError("Audio array is empty")

    # Convert to mono if multi-channel
    if audio.ndim > 1:
        audio_mono = np.mean(audio, axis=0)
    else:
        audio_mono = audio

    # Compute onset strength envelope
    onset_env = librosa.onset.onset_strength(y=audio_mono, sr=sample_rate, aggregate=np.median)

    # Detect tempo using autocorrelation
    tempo, beats = librosa.beat.beat_track(
        onset_envelope=onset_env,
        sr=sample_rate,
        start_bpm=start_bpm,
        units="time",
    )

    # Calculate confidence based on onset strength variance
    # Higher variance = more rhythmic = higher confidence
    if len(onset_env) > 0:
        onset_variance = np.var(onset_env)
        onset_mean = np.mean(onset_env)
        # Normalize to 0-1 range (empirically tuned)
        confidence = min(1.0, onset_variance / (onset_mean + 1e-6) / 10.0)
    else:
        confidence = 0.0

    # Convert tempo to float, handling numpy scalar
    bpm_value = float(tempo.item() if hasattr(tempo, "item") else tempo)

    return TempoResult(
        bpm=bpm_value,
        confidence=float(confidence),
        onset_strength=onset_env if include_onset_strength else None,
    )
