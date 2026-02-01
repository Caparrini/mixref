"""Genre-specific BPM ranges and correction logic.

This module provides genre-aware BPM validation and correction,
helping detect half-time issues common in electronic music.
"""

from dataclasses import dataclass
from enum import Enum


class Genre(str, Enum):
    """Supported music genres for BPM validation."""

    DNB = "dnb"
    TECHNO = "techno"
    HOUSE = "house"
    DUBSTEP = "dubstep"
    TRANCE = "trance"


@dataclass
class BPMRange:
    """BPM range definition for a genre.

    Attributes:
        min_bpm: Minimum typical BPM for the genre.
        max_bpm: Maximum typical BPM for the genre.
        typical: Most common BPM for the genre.

    """

    min_bpm: float
    max_bpm: float
    typical: float


# Genre BPM ranges based on electronic music conventions
GENRE_BPM_RANGES: dict[Genre, BPMRange] = {
    Genre.DNB: BPMRange(min_bpm=160.0, max_bpm=180.0, typical=174.0),
    Genre.TECHNO: BPMRange(min_bpm=120.0, max_bpm=140.0, typical=130.0),
    Genre.HOUSE: BPMRange(min_bpm=118.0, max_bpm=128.0, typical=124.0),
    Genre.DUBSTEP: BPMRange(min_bpm=135.0, max_bpm=145.0, typical=140.0),
    Genre.TRANCE: BPMRange(min_bpm=125.0, max_bpm=145.0, typical=138.0),
}


@dataclass
class CorrectedBPM:
    """Result of BPM correction.

    Attributes:
        original_bpm: The original detected BPM.
        corrected_bpm: The BPM after applying corrections.
        was_corrected: Whether any correction was applied.
        correction_reason: Explanation of why correction was applied.
        in_genre_range: Whether corrected BPM is within genre range.
        genre: The genre used for validation (if any).

    """

    original_bpm: float
    corrected_bpm: float
    was_corrected: bool
    correction_reason: str | None = None
    in_genre_range: bool | None = None
    genre: Genre | None = None


def correct_bpm(
    bpm: float,
    genre: Genre | None = None,
    half_time_threshold: float = 100.0,
) -> CorrectedBPM:
    """Apply genre-aware BPM corrections.

    Common in electronic music production, BPM detection can sometimes
    detect "half-time" (half the actual tempo). This function corrects
    such issues and validates against genre expectations.

    Args:
        bpm: The detected BPM value.
        genre: Optional genre for validation against expected ranges.
        half_time_threshold: BPM below which to consider doubling.
            Default: 100.0 (below this, likely detected half-time).

    Returns:
        CorrectedBPM with original BPM, corrected value, and validation info.

    Example:
        >>> from mixref.detective.bpm_correction import correct_bpm, Genre
        >>>
        >>> # Half-time detection (87 BPM -> 174 BPM for DnB)
        >>> result = correct_bpm(87.0, genre=Genre.DNB)
        >>> print(result.corrected_bpm)
        174.0
        >>> print(result.was_corrected)
        True
        >>>
        >>> # Already in range
        >>> result = correct_bpm(174.0, genre=Genre.DNB)
        >>> print(result.was_corrected)
        False

    """
    original_bpm = bpm
    corrected_bpm = bpm
    was_corrected = False
    correction_reason = None
    in_genre_range = None

    # Check for half-time detection
    if bpm < half_time_threshold:
        corrected_bpm = bpm * 2.0
        was_corrected = True
        correction_reason = f"Detected half-time: {bpm:.1f} BPM doubled to {corrected_bpm:.1f} BPM"

    # Validate against genre range if provided
    if genre is not None:
        genre_range = GENRE_BPM_RANGES[genre]
        in_range = genre_range.min_bpm <= corrected_bpm <= genre_range.max_bpm

        # If not in range after doubling, try other corrections
        if was_corrected and not in_range:
            # Maybe the doubled value isn't right, try halving instead
            halved = original_bpm / 2.0
            if genre_range.min_bpm <= halved <= genre_range.max_bpm:
                corrected_bpm = halved
                correction_reason = (
                    f"Detected double-time: {original_bpm:.1f} BPM "
                    f"halved to {corrected_bpm:.1f} BPM"
                )
            # If still not in range, revert to original
            elif not in_range:
                # Keep the doubled value if it's closer to typical
                if abs(corrected_bpm - genre_range.typical) > abs(
                    original_bpm - genre_range.typical
                ):
                    corrected_bpm = original_bpm
                    was_corrected = False
                    correction_reason = None

        in_genre_range = genre_range.min_bpm <= corrected_bpm <= genre_range.max_bpm

    return CorrectedBPM(
        original_bpm=original_bpm,
        corrected_bpm=corrected_bpm,
        was_corrected=was_corrected,
        correction_reason=correction_reason,
        in_genre_range=in_genre_range,
        genre=genre,
    )


def is_in_genre_range(bpm: float, genre: Genre) -> bool:
    """Check if BPM is within typical range for a genre.

    Args:
        bpm: The BPM value to check.
        genre: The genre to check against.

    Returns:
        True if BPM is within the genre's typical range.

    Example:
        >>> from mixref.detective.bpm_correction import is_in_genre_range, Genre
        >>>
        >>> is_in_genre_range(174.0, Genre.DNB)
        True
        >>> is_in_genre_range(120.0, Genre.DNB)
        False

    """
    genre_range = GENRE_BPM_RANGES[genre]
    return genre_range.min_bpm <= bpm <= genre_range.max_bpm


def get_genre_range(genre: Genre) -> BPMRange:
    """Get the BPM range for a specific genre.

    Args:
        genre: The genre to query.

    Returns:
        BPMRange with min, max, and typical BPM values.

    Example:
        >>> from mixref.detective.bpm_correction import get_genre_range, Genre
        >>>
        >>> range_info = get_genre_range(Genre.TECHNO)
        >>> print(f"{range_info.min_bpm}-{range_info.max_bpm} BPM")
        120.0-140.0 BPM

    """
    return GENRE_BPM_RANGES[genre]
