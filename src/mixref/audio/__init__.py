"""Audio file loading and handling.

This module provides utilities for loading and processing audio files.
"""

from mixref.audio.exceptions import (
    AudioError,
    AudioFileNotFoundError,
    CorruptFileError,
    InvalidAudioDataError,
    UnsupportedFormatError,
)
from mixref.audio.loader import load_audio

__all__ = [
    "load_audio",
    "AudioError",
    "AudioFileNotFoundError",
    "CorruptFileError",
    "InvalidAudioDataError",
    "UnsupportedFormatError",
]
