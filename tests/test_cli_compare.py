"""Tests for compare CLI command."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from mixref.cli.main import app
from synthetic_audio import generate_pink_noise, generate_sine_wave

runner = CliRunner()


@pytest.fixture
def temp_audio_files(tmp_path: Path) -> tuple[Path, Path]:
    """Create temporary audio files for testing.

    Args:
        tmp_path: Pytest temporary directory fixture

    Returns:
        Tuple of (track_path, reference_path)
    """
    import soundfile as sf

    # Generate two different tracks
    track_audio, sr = generate_sine_wave(frequency=440.0, amplitude=0.3, duration=2.0)
    ref_audio, _ = generate_sine_wave(frequency=880.0, amplitude=0.5, duration=2.0)

    track_path = tmp_path / "track.wav"
    ref_path = tmp_path / "reference.wav"

    sf.write(track_path, track_audio, sr)
    sf.write(ref_path, ref_audio, sr)

    return track_path, ref_path


def test_compare_basic(temp_audio_files: tuple[Path, Path]) -> None:
    """Test basic compare command."""
    track, reference = temp_audio_files

    result = runner.invoke(app, ["compare", str(track), str(reference)])

    assert result.exit_code == 0
    assert "A/B Comparison" in result.stdout
    assert "Integrated LUFS" in result.stdout
    assert "True Peak" in result.stdout
    assert "Spectral" in result.stdout or "Band" in result.stdout


def test_compare_with_bpm(temp_audio_files: tuple[Path, Path]) -> None:
    """Test compare command with BPM detection."""
    track, reference = temp_audio_files

    result = runner.invoke(app, ["compare", str(track), str(reference), "--bpm"])

    assert result.exit_code == 0
    assert "Tempo (BPM)" in result.stdout or "BPM" in result.stdout


def test_compare_with_key(temp_audio_files: tuple[Path, Path]) -> None:
    """Test compare command with key detection."""
    track, reference = temp_audio_files

    result = runner.invoke(app, ["compare", str(track), str(reference), "--key"])

    assert result.exit_code == 0
    assert "Musical Key" in result.stdout or "Key" in result.stdout


def test_compare_json_output(temp_audio_files: tuple[Path, Path]) -> None:
    """Test compare command with JSON output."""
    import json

    track, reference = temp_audio_files

    result = runner.invoke(app, ["compare", str(track), str(reference), "--json"])

    assert result.exit_code == 0

    # Should be valid JSON
    output = json.loads(result.stdout)
    assert "track" in output
    assert "reference" in output
    assert "loudness" in output
    assert "spectral" in output


def test_compare_track_not_found() -> None:
    """Test compare with non-existent track file."""
    result = runner.invoke(app, ["compare", "nonexistent.wav", "also_nonexistent.wav"])

    assert result.exit_code == 1
    assert "not found" in result.stdout.lower()


def test_compare_reference_not_found(temp_audio_files: tuple[Path, Path]) -> None:
    """Test compare with non-existent reference file."""
    track, _ = temp_audio_files

    result = runner.invoke(app, ["compare", str(track), "nonexistent.wav"])

    assert result.exit_code == 1
    assert "not found" in result.stdout.lower()


def test_compare_help() -> None:
    """Test compare command help."""
    result = runner.invoke(app, ["compare", "--help"])

    assert result.exit_code == 0
    assert "Compare your track" in result.stdout
    assert "TRACK" in result.stdout
    assert "REFERENCE" in result.stdout
    assert "--bpm" in result.stdout
    assert "--key" in result.stdout
    assert "--json" in result.stdout
