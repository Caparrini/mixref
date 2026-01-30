"""Detective module for audio analysis: BPM, key, and spectral detection."""

from mixref.detective.bpm_correction import (
    BPMRange,
    CorrectedBPM,
    Genre,
    correct_bpm,
    get_genre_range,
    is_in_genre_range,
)
from mixref.detective.tempo import TempoResult, detect_bpm

__all__ = [
    "detect_bpm",
    "TempoResult",
    "correct_bpm",
    "CorrectedBPM",
    "Genre",
    "BPMRange",
    "get_genre_range",
    "is_in_genre_range",
]
