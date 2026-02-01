"""Analyze command for mixref CLI.

This module provides the analyze command that calculates loudness metrics
for audio files and compares them against platform and genre targets.
"""

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from mixref.audio import load_audio
from mixref.detective import (
    CorrectedBPM,
    KeyResult,
    SpectralResult,
    TempoResult,
    analyze_spectrum,
    correct_bpm,
    detect_bpm,
    detect_key,
)
from mixref.detective import Genre as DetectiveGenre
from mixref.meters import (
    Genre,
    LoudnessResult,
    Platform,
    calculate_lufs,
    compare_to_target,
    get_target,
)

console = Console()


def analyze_command(
    file: Path = typer.Argument(..., help="Path to audio file to analyze"),
    platform: Platform | None = typer.Option(
        None,
        "--platform",
        "-p",
        help="Platform target (e.g., spotify, youtube, club)",
    ),
    genre: Genre | None = typer.Option(
        None,
        "--genre",
        "-g",
        help="Genre target (e.g., dnb, techno, house)",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output results as JSON",
    ),
) -> None:
    """Analyze audio file and calculate loudness metrics.

    Examples:
        # Analyze for Spotify streaming
        $ mixref analyze my_track.wav --platform spotify

        # Analyze for DnB club play
        $ mixref analyze club_banger.wav --genre dnb

        # Get JSON output
        $ mixref analyze track.wav --platform youtube --json

    Args:
        file: Path to audio file
        platform: Platform target for comparison
        genre: Genre target for comparison
        json_output: Output as JSON instead of Rich table

    Raises:
        typer.Exit: If file not found or processing fails
    """
    # Check file exists
    if not file.exists():
        console.print(f"[red]Error: File not found: {file}[/red]")
        raise typer.Exit(code=1)

    try:
        # Load audio (only show progress for table output)
        if not json_output:
            console.print(f"[dim]Loading {file.name}...[/dim]")
        audio, sr = load_audio(file)

        # Transpose for LUFS calculation (load_audio returns (samples, channels))
        # but calculate_lufs expects (channels, samples)
        if audio.ndim == 2:
            audio = audio.T

        # Calculate LUFS (only show progress for table output)
        if not json_output:
            console.print("[dim]Calculating loudness...[/dim]")
        result = calculate_lufs(audio, sr)

        # Detect BPM
        if not json_output:
            console.print("[dim]Detecting tempo...[/dim]")
        # Convert back to (samples, channels) for BPM detection
        bpm_audio = audio.T if audio.ndim == 2 else audio
        tempo_result = detect_bpm(bpm_audio, sr)

        # Apply genre-aware correction if genre specified
        bpm_result: CorrectedBPM | TempoResult = tempo_result
        if genre:
            # Map meters.Genre to detective.Genre
            detective_genre_map = {
                Genre.DNB: DetectiveGenre.DNB,
                Genre.TECHNO: DetectiveGenre.TECHNO,
                Genre.HOUSE: DetectiveGenre.HOUSE,
                Genre.DUBSTEP: DetectiveGenre.DUBSTEP,
                Genre.TRANCE: DetectiveGenre.TRANCE,
            }
            if genre in detective_genre_map:
                bpm_result = correct_bpm(tempo_result.bpm, detective_genre_map[genre])

        # Detect musical key
        if not json_output:
            console.print("[dim]Detecting key...[/dim]")
        key_result = detect_key(bpm_audio, sr)

        # Analyze spectral balance
        if not json_output:
            console.print("[dim]Analyzing frequency balance...[/dim]")
        spectral_result = analyze_spectrum(bpm_audio, sr)

        # Display results
        if json_output:
            _display_json(file, result, bpm_result, key_result, spectral_result, platform, genre)
        else:
            _display_table(file, result, bpm_result, key_result, spectral_result, platform, genre)

    except Exception as e:
        console.print(f"[red]Error analyzing file: {e}[/red]")
        raise typer.Exit(code=1) from None


def _display_table(
    file: Path,
    result: LoudnessResult,
    bpm_result: CorrectedBPM | TempoResult,
    key_result: KeyResult,
    spectral_result: SpectralResult,
    platform: Platform | None,
    genre: Genre | None,
) -> None:
    """Display results as Rich table.

    Args:
        file: Audio file path
        result: LoudnessResult from calculate_lufs
        bpm_result: BPM detection result (TempoResult or CorrectedBPM)
        key_result: Key detection result
        spectral_result: Spectral analysis result
        platform: Platform target (optional)
        genre: Genre target (optional)
    """
    # Main results table
    table = Table(title=f"Analysis: {file.name}", show_header=True, header_style="bold")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right")
    table.add_column("Status", justify="center")

    # Integrated LUFS
    lufs_str = f"{result.integrated_lufs:.1f} LUFS"
    table.add_row("Integrated Loudness", lufs_str, _lufs_status(result.integrated_lufs))

    # True Peak
    peak_str = f"{result.true_peak_db:.1f} dBTP"
    peak_status = _peak_status(result.true_peak_db)
    table.add_row("True Peak", peak_str, peak_status)

    # LRA
    lra_str = f"{result.loudness_range_lu:.1f} LU"
    table.add_row("Loudness Range", lra_str, "ℹ️")

    # Separator
    table.add_section()

    # BPM
    if isinstance(bpm_result, CorrectedBPM):
        bpm_str = f"{bpm_result.corrected_bpm:.1f} BPM"
        bpm_status = "🎵"
        if bpm_result.was_corrected:
            bpm_status = "🔧"  # Was corrected
        if bpm_result.in_genre_range is not None and not bpm_result.in_genre_range:
            bpm_status = "⚠️"  # Outside genre range
    else:
        bpm_str = f"{bpm_result.bpm:.1f} BPM"
        bpm_status = "🎵" if bpm_result.confidence > 0.7 else "❓"

    table.add_row("Tempo", bpm_str, bpm_status)

    # Musical Key
    key_str = f"{key_result.key} ({key_result.camelot})"
    key_status = "🎹" if key_result.confidence > 0.6 else "❓"
    table.add_row("Key", key_str, key_status)

    # Separator for spectral section
    table.add_section()

    # Spectral Balance - Show as visual bars
    for band_energy in spectral_result.bands:
        # Normalize percentage to 10-point scale for visual bars
        bar_length = int(band_energy.energy_percent / 10)
        bar = "■" * bar_length + "□" * (10 - bar_length)

        # Add color based on frequency range
        band_name_upper = band_energy.band_name.upper()
        if band_name_upper == "SUB":
            bar_colored = f"[magenta]{bar}[/magenta]"
        elif band_name_upper == "LOW":
            bar_colored = f"[blue]{bar}[/blue]"
        elif band_name_upper == "MID":
            bar_colored = f"[green]{bar}[/green]"
        elif band_name_upper == "HIGH":
            bar_colored = f"[yellow]{bar}[/yellow]"
        else:  # AIR
            bar_colored = f"[cyan]{bar}[/cyan]"

        band_label = f"{band_energy.band_name}"
        percentage_str = f"{band_energy.energy_percent:.1f}%"
        table.add_row(band_label, bar_colored, percentage_str)

    console.print(table)

    # Platform comparison
    if platform:
        target = get_target(platform=platform)
        is_ok, diff, message = compare_to_target(result.integrated_lufs, target)
        _display_comparison(message, is_ok, "Platform", platform.value)

    # Genre comparison
    if genre:
        target = get_target(genre=genre)
        is_ok, diff, message = compare_to_target(result.integrated_lufs, target)
        _display_comparison(message, is_ok, "Genre", genre.value)


def _display_comparison(message: str, is_ok: bool, target_type: str, target_name: str) -> None:
    """Display target comparison.

    Args:
        message: Message from compare_to_target
        is_ok: Whether within acceptable range
        target_type: "Platform" or "Genre"
        target_name: Name of target (e.g., "spotify", "dnb")
    """
    console.print()
    console.print(f"[bold]{target_type} Target: {target_name.upper()}[/bold]")

    if is_ok and "Perfect" in message:
        console.print(f"[green]{message}[/green]")
    elif "above" in message or "below" in message:
        console.print(f"[yellow]{message}[/yellow]")
    else:
        console.print(f"[cyan]{message}[/cyan]")


def _lufs_status(lufs: float) -> str:
    """Get status emoji for LUFS value.

    Args:
        lufs: Integrated LUFS value

    Returns:
        Status emoji
    """
    if lufs > -6:
        return "🔴"  # Very loud
    elif lufs > -10:
        return "🟡"  # Loud
    elif lufs > -16:
        return "🟢"  # Normal
    else:
        return "🔵"  # Quiet


def _peak_status(peak: float) -> str:
    """Get status emoji for true peak value.

    Args:
        peak: True peak in dBTP

    Returns:
        Status emoji
    """
    if peak > -0.1:
        return "🔴"  # Clipping danger
    elif peak > -1.0:
        return "🟡"  # Close to clipping
    else:
        return "🟢"  # Safe


def _display_json(
    file: Path,
    result: LoudnessResult,
    bpm_result: CorrectedBPM | TempoResult,
    key_result: KeyResult,
    spectral_result: SpectralResult,
    platform: Platform | None,
    genre: Genre | None,
) -> None:
    """Display results as JSON.

    Args:
        file: Audio file path
        result: LoudnessResult from calculate_lufs
        bpm_result: BPM detection result (TempoResult or CorrectedBPM)
        key_result: Key detection result
        spectral_result: Spectral analysis result
        platform: Platform target (optional)
        genre: Genre target (optional)
    """
    import json

    output = {
        "file": str(file),
        "loudness": {
            "integrated_lufs": round(result.integrated_lufs, 2),
            "true_peak_db": round(result.true_peak_db, 2),
            "loudness_range_lu": round(result.loudness_range_lu, 2),
            "short_term_max_lufs": round(result.short_term_max_lufs, 2),
            "short_term_min_lufs": round(result.short_term_min_lufs, 2),
        },
        "tempo": {},
    }

    # Add BPM info
    if isinstance(bpm_result, CorrectedBPM):
        output["tempo"] = {
            "bpm": round(bpm_result.corrected_bpm, 1),
            "original_bpm": round(bpm_result.original_bpm, 1),
            "was_corrected": bpm_result.was_corrected,
            "in_genre_range": bpm_result.in_genre_range,
            "genre": bpm_result.genre.value if bpm_result.genre else None,
        }
    else:
        output["tempo"] = {
            "bpm": round(bpm_result.bpm, 1),
            "confidence": round(bpm_result.confidence, 2),
        }

    # Add key detection
    output["key"] = {
        "key": key_result.key,
        "camelot": key_result.camelot,
        "confidence": round(key_result.confidence, 2),
    }

    # Add spectral analysis
    output["spectral"] = {
        "bands": [
            {
                "name": band.band_name.lower(),
                "energy_db": round(band.energy_db, 2),
                "energy_percent": round(band.energy_percent, 2),
            }
            for band in spectral_result.bands
        ],
        "total_energy_db": round(spectral_result.total_energy_db, 2),
    }

    # Add platform comparison
    if platform:
        target = get_target(platform=platform)
        is_ok, diff, message = compare_to_target(result.integrated_lufs, target)
        output["platform"] = {
            "name": platform.value,
            "target_lufs": target.target_lufs,
            "difference": round(diff, 2),
            "is_acceptable": is_ok,
            "message": message,
        }

    # Add genre comparison
    if genre:
        target = get_target(genre=genre)
        is_ok, diff, message = compare_to_target(result.integrated_lufs, target)
        output["genre"] = {
            "name": genre.value,
            "target_lufs": target.target_lufs,
            "difference": round(diff, 2),
            "is_acceptable": is_ok,
            "message": message,
        }

    console.print_json(json.dumps(output))
