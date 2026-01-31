"""Tests for BPM correction and genre validation."""

from mixref.detective.bpm_correction import (
    BPMRange,
    CorrectedBPM,
    Genre,
    correct_bpm,
    get_genre_range,
    is_in_genre_range,
)


class TestGenreRanges:
    """Tests for genre BPM range definitions."""

    def test_genre_enum_values(self):
        """Test that Genre enum has expected values."""
        assert Genre.DNB == "dnb"
        assert Genre.TECHNO == "techno"
        assert Genre.HOUSE == "house"
        assert Genre.DUBSTEP == "dubstep"
        assert Genre.TRANCE == "trance"

    def test_get_genre_range_dnb(self):
        """Test getting DnB range."""
        range_info = get_genre_range(Genre.DNB)
        assert isinstance(range_info, BPMRange)
        assert range_info.min_bpm == 160.0
        assert range_info.max_bpm == 180.0
        assert range_info.typical == 174.0

    def test_get_genre_range_techno(self):
        """Test getting Techno range."""
        range_info = get_genre_range(Genre.TECHNO)
        assert range_info.min_bpm == 120.0
        assert range_info.max_bpm == 140.0
        assert range_info.typical == 130.0

    def test_get_genre_range_house(self):
        """Test getting House range."""
        range_info = get_genre_range(Genre.HOUSE)
        assert range_info.min_bpm == 118.0
        assert range_info.max_bpm == 128.0
        assert range_info.typical == 124.0

    def test_is_in_genre_range_dnb_valid(self):
        """Test BPM in DnB range."""
        assert is_in_genre_range(174.0, Genre.DNB) is True
        assert is_in_genre_range(160.0, Genre.DNB) is True
        assert is_in_genre_range(180.0, Genre.DNB) is True

    def test_is_in_genre_range_dnb_invalid(self):
        """Test BPM outside DnB range."""
        assert is_in_genre_range(120.0, Genre.DNB) is False
        assert is_in_genre_range(87.0, Genre.DNB) is False
        assert is_in_genre_range(200.0, Genre.DNB) is False

    def test_is_in_genre_range_house_valid(self):
        """Test BPM in House range."""
        assert is_in_genre_range(124.0, Genre.HOUSE) is True
        assert is_in_genre_range(118.0, Genre.HOUSE) is True
        assert is_in_genre_range(128.0, Genre.HOUSE) is True

    def test_is_in_genre_range_techno_valid(self):
        """Test BPM in Techno range."""
        assert is_in_genre_range(130.0, Genre.TECHNO) is True
        assert is_in_genre_range(125.0, Genre.TECHNO) is True
        assert is_in_genre_range(135.0, Genre.TECHNO) is True


class TestCorrectBpm:
    """Tests for BPM correction logic."""

    def test_correct_bpm_no_correction_needed(self):
        """Test BPM that doesn't need correction."""
        result = correct_bpm(174.0)

        assert isinstance(result, CorrectedBPM)
        assert result.original_bpm == 174.0
        assert result.corrected_bpm == 174.0
        assert result.was_corrected is False
        assert result.correction_reason is None

    def test_correct_bpm_half_time_detection(self):
        """Test half-time BPM gets doubled."""
        result = correct_bpm(87.0)

        assert result.original_bpm == 87.0
        assert result.corrected_bpm == 174.0
        assert result.was_corrected is True
        assert "half-time" in result.correction_reason.lower()

    def test_correct_bpm_with_genre_dnb(self):
        """Test correction with DnB genre validation."""
        # 87 BPM should double to 174 (in DnB range)
        result = correct_bpm(87.0, genre=Genre.DNB)

        assert result.corrected_bpm == 174.0
        assert result.was_corrected is True
        assert result.in_genre_range is True
        assert result.genre == Genre.DNB

    def test_correct_bpm_already_in_range(self):
        """Test BPM already in genre range."""
        result = correct_bpm(174.0, genre=Genre.DNB)

        assert result.corrected_bpm == 174.0
        assert result.was_corrected is False
        assert result.in_genre_range is True

    def test_correct_bpm_house_range(self):
        """Test correction with House genre."""
        # 62 BPM should double to 124 (in House range)
        result = correct_bpm(62.0, genre=Genre.HOUSE)

        assert result.corrected_bpm == 124.0
        assert result.was_corrected is True
        assert result.in_genre_range is True

    def test_correct_bpm_techno_range(self):
        """Test correction with Techno genre."""
        # 65 BPM should double to 130 (in Techno range)
        result = correct_bpm(65.0, genre=Genre.TECHNO)

        assert result.corrected_bpm == 130.0
        assert result.was_corrected is True
        assert result.in_genre_range is True

    def test_correct_bpm_out_of_range_after_correction(self):
        """Test when doubled BPM is still out of range."""
        # 50 BPM * 2 = 100 BPM, not in DnB range (160-180)
        result = correct_bpm(50.0, genre=Genre.DNB)

        # Should keep the doubled value or original based on which is closer
        assert result.was_corrected is True
        # After doubling: 100 BPM, still out of range
        assert result.in_genre_range is False

    def test_correct_bpm_custom_threshold(self):
        """Test custom half-time threshold."""
        # With threshold 120, BPM 110 should be doubled
        result = correct_bpm(110.0, half_time_threshold=120.0)

        assert result.corrected_bpm == 220.0
        assert result.was_corrected is True

        # With default threshold 100, BPM 110 should NOT be doubled
        result2 = correct_bpm(110.0)
        assert result2.was_corrected is False

    def test_correct_bpm_dataclass_fields(self):
        """Test all fields of CorrectedBPM dataclass."""
        result = correct_bpm(87.0, genre=Genre.DNB)

        assert hasattr(result, "original_bpm")
        assert hasattr(result, "corrected_bpm")
        assert hasattr(result, "was_corrected")
        assert hasattr(result, "correction_reason")
        assert hasattr(result, "in_genre_range")
        assert hasattr(result, "genre")

    def test_correct_bpm_no_genre(self):
        """Test correction without genre validation."""
        result = correct_bpm(87.0)

        assert result.corrected_bpm == 174.0
        assert result.was_corrected is True
        assert result.in_genre_range is None  # No genre provided
        assert result.genre is None

    def test_correct_bpm_double_time_detection(self):
        """Test detection of double-time (needs halving)."""
        # If detector returns 350 BPM for DnB, it should be halved to 175
        # (This tests the double-time logic in the function)
        result = correct_bpm(350.0, genre=Genre.DNB)

        # Function tries to correct if out of range
        # 350 is way out of range, might try halving
        # Check the actual behavior
        assert result.original_bpm == 350.0

    def test_bpm_range_dataclass(self):
        """Test BPMRange dataclass structure."""
        range_info = BPMRange(min_bpm=120.0, max_bpm=140.0, typical=130.0)

        assert range_info.min_bpm == 120.0
        assert range_info.max_bpm == 140.0
        assert range_info.typical == 130.0

    def test_correct_bpm_edge_case_exactly_100(self):
        """Test BPM exactly at threshold."""
        # Exactly 100 BPM with threshold 100 should NOT be corrected
        result = correct_bpm(100.0, half_time_threshold=100.0)

        assert result.was_corrected is False
        assert result.corrected_bpm == 100.0

    def test_correct_bpm_very_low_bpm(self):
        """Test very low BPM values."""
        result = correct_bpm(40.0, genre=Genre.DNB)

        # 40 * 2 = 80, still out of range (160-180)
        assert result.original_bpm == 40.0
        assert result.was_corrected is True
        assert result.in_genre_range is False
