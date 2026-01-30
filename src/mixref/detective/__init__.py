"""Detective module for audio analysis: BPM, key, and spectral detection."""

from mixref.detective.tempo import TempoResult, detect_bpm

__all__ = ["detect_bpm", "TempoResult"]
