"""Musical key detection for audio tracks.

This module provides key estimation using chroma features and pattern matching,
with Camelot wheel notation support for DJs.
"""

from dataclasses import dataclass
from typing import Any

import librosa
import numpy as np


# Camelot wheel mapping: key -> Camelot code
CAMELOT_WHEEL = {
    "C major": "8B",
    "C minor": "5A",
    "C# major": "3B",
    "C# minor": "12A",
    "D major": "10B",
    "D minor": "7A",
    "Eb major": "5B",
    "Eb minor": "2A",
    "E major": "12B",
    "E minor": "9A",
    "F major": "7B",
    "F minor": "4A",
    "F# major": "2B",
    "F# minor": "11A",
    "G major": "9B",
    "G minor": "6A",
    "Ab major": "4B",
    "Ab minor": "1A",
    "A major": "11B",
    "A minor": "8A",
    "Bb major": "6B",
    "Bb minor": "3A",
    "B major": "1B",
    "B minor": "10A",
}


@dataclass
class KeyResult:
    """Result of key detection.

    Attributes:
        key: Detected musical key (e.g., "C major", "Eb minor").
        camelot: Camelot wheel notation (e.g., "8B", "5A").
        confidence: Confidence score from 0.0 to 1.0.
    """

    key: str
    camelot: str
    confidence: float


def detect_key(
    audio: Any,  # np.ndarray
    sample_rate: int,
) -> KeyResult:
    """Detect musical key of an audio signal.

    Uses chroma features to estimate the most likely musical key.
    Prefers flat notation (Eb instead of D#) as per mixref conventions.

    Args:
        audio: Audio signal as numpy array.
            Shape: (samples,) for mono or (channels, samples) for multi-channel.
        sample_rate: Sample rate in Hz.

    Returns:
        KeyResult with key name, Camelot code, and confidence.

    Example:
        >>> import numpy as np
        >>> from mixref.detective.key import detect_key
        >>> 
        >>> # Generate C major-ish signal
        >>> sr = 22050
        >>> duration = 10
        >>> audio = np.sin(2 * np.pi * 261.63 * np.arange(sr * duration) / sr)
        >>> 
        >>> result = detect_key(audio, sr)
        >>> print(result.key)
        C major
    """
    if audio.size == 0:
        raise ValueError("Audio array is empty")

    # Convert to mono if needed
    if audio.ndim > 1:
        audio_mono = np.mean(audio, axis=0)
    else:
        audio_mono = audio

    # Extract chroma features
    chroma = librosa.feature.chroma_cqt(y=audio_mono, sr=sample_rate)

    # Average chroma over time
    chroma_avg = np.mean(chroma, axis=1)

    # Normalize
    chroma_avg = chroma_avg / (np.sum(chroma_avg) + 1e-6)

    # Key profiles (major and minor templates)
    # Krumhansl-Schmuckler key profiles
    major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 
                               2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
    minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53,
                               2.54, 4.75, 3.98, 2.69, 3.34, 3.17])

    # Normalize profiles
    major_profile = major_profile / np.sum(major_profile)
    minor_profile = minor_profile / np.sum(minor_profile)

    # Test all 24 keys (12 major, 12 minor)
    keys = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
    scores = []

    for i, root in enumerate(keys):
        # Roll chroma to match key
        rolled_chroma = np.roll(chroma_avg, -i)

        # Correlation with major and minor profiles
        major_corr = np.corrcoef(rolled_chroma, major_profile)[0, 1]
        minor_corr = np.corrcoef(rolled_chroma, minor_profile)[0, 1]

        scores.append((root + " major", major_corr))
        scores.append((root + " minor", minor_corr))

    # Find best match
    best_key, best_score = max(scores, key=lambda x: x[1])

    # Confidence based on how much better the best key is vs others
    sorted_scores = sorted([s[1] for s in scores], reverse=True)
    if len(sorted_scores) > 1 and sorted_scores[0] > sorted_scores[1]:
        confidence = (sorted_scores[0] - sorted_scores[1]) / sorted_scores[0]
    else:
        confidence = 0.5

    # Clamp confidence to valid range
    confidence = max(0.0, min(1.0, confidence))

    # Get Camelot code
    camelot = CAMELOT_WHEEL.get(best_key, "?")

    return KeyResult(
        key=best_key,
        camelot=camelot,
        confidence=float(confidence),
    )


def get_compatible_keys(key: str) -> list[str]:
    """Get harmonically compatible keys for mixing.

    Returns keys that are adjacent on the Camelot wheel
    (same number ±1, or same letter).

    Args:
        key: Musical key (e.g., "C major", "8B").

    Returns:
        List of compatible keys in Camelot notation.

    Example:
        >>> from mixref.detective.key import get_compatible_keys
        >>> 
        >>> compatible = get_compatible_keys("8B")
        >>> print(compatible)
        ['7B', '9B', '8A']
    """
    # If given musical key, convert to Camelot
    if key in CAMELOT_WHEEL:
        camelot = CAMELOT_WHEEL[key]
    else:
        camelot = key

    if not camelot or len(camelot) < 2:
        return []

    try:
        number = int(camelot[:-1])
        letter = camelot[-1]
    except (ValueError, IndexError):
        return []

    compatible = []

    # Same number, different letter (relative major/minor)
    other_letter = "A" if letter == "B" else "B"
    compatible.append(f"{number}{other_letter}")

    # Adjacent numbers, same letter
    prev_num = 12 if number == 1 else number - 1
    next_num = 1 if number == 12 else number + 1
    compatible.append(f"{prev_num}{letter}")
    compatible.append(f"{next_num}{letter}")

    return compatible
