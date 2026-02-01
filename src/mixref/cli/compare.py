"""Compare command for mixref CLI.

This module provides the compare command that performs A/B comparison between
a track and a reference, highlighting differences in loudness and spectral balance.
"""

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from mixref.audio import load_audio
from mixref.compare import ComparisonResult, compare_tracks

console = Console()


def compare_command(
    track: Path = typer.Argument(..., help="Path to your track"),
    reference: Path = typer.Argument(..., help="Path to reference track"),
    include_bpm: bool = typer.Option(
        False,
        "--bpm",
        help="Include BPM detection and comparison (slower)",
    ),
    include_key: bool = typer.Option(
        False,
        "--key",
        help="Include musical key detection and comparison (slower)",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output results as JSON",
    ),
) -> None:
    """Compare your track against a professional reference.

    Analyzes both tracks and highlights differences in loudness,
    spectral balance, and optionally BPM/key.

    Examples:
        # Basic comparison
        $ mixref compare my_mix.wav pro_reference.wav

        # Include tempo comparison
        $ mixref compare my_mix.wav pro_reference.wav --bpm

        # Full comparison with JSON output
        $ mixref compare my_mix.wav reference.wav --bpm --key --json

    Args:
        track: Path to your track
        reference: Path to professional reference track
        include_bpm: Detect and compare BPM
        include_key: Detect and compare musical key
        json_output: Output as JSON instead of Rich table

    Raises:
        typer.Exit: If files not found or processing fails
    """
    # Check files exist
    if not track.exists():
        console.print(f"[red]Error: Track file not found: {track}[/red]")
        raise typer.Exit(code=1)

    if not reference.exists():
        console.print(f"[red]Error: Reference file not found: {reference}[/red]")
        raise typer.Exit(code=1)

    try:
        # Load both tracks
        if not json_output:
            console.print("[dim]Loading tracks...[/dim]")

        track_audio, track_sr = load_audio(track)
        ref_audio, ref_sr = load_audio(reference)

        # Ensure same sample rate
        if track_sr != ref_sr:
            if not json_output:
                console.print(f"[yellow]Warning: Resampling reference to {track_sr} Hz[/yellow]")
            ref_audio, ref_sr = load_audio(reference, sample_rate=track_sr)

        # Compare tracks
        if not json_output:
            console.print("[dim]Analyzing and comparing...[/dim]")

        result = compare_tracks(
            track_audio,
            ref_audio,
            track_sr,
            track_name=track.name,
            reference_name=reference.name,
            include_bpm=include_bpm,
            include_key=include_key,
        )

        # Display results
        if json_output:
            _display_json(result)
        else:
            _display_table(result)

    except Exception as e:
        console.print(f"[red]Error comparing tracks: {e}[/red]")
        raise typer.Exit(code=1) from None


def _display_table(result: ComparisonResult) -> None:
    """Display comparison results as Rich table.

    Args:
        result: ComparisonResult from compare_tracks
    """
    # Create main comparison table
    table = Table(
        title=f"🎯 A/B Comparison\n{result.track_name} vs {result.reference_name}",
        show_header=True,
        header_style="bold",
    )
    table.add_column("Metric", style="cyan")
    table.add_column("Your Track", justify="right")
    table.add_column("Reference", justify="right")
    table.add_column("Difference", justify="right")

    # === LOUDNESS SECTION ===
    loudness = result.loudness

    # Integrated LUFS
    diff_str = _format_difference(loudness.lufs_difference, "LUFS")
    table.add_row(
        "Integrated LUFS",
        f"{loudness.track_lufs:.1f}",
        f"{loudness.reference_lufs:.1f}",
        diff_str,
    )

    # True Peak
    diff_str = _format_difference(loudness.peak_difference, "dBTP")
    table.add_row(
        "True Peak",
        f"{loudness.track_peak:.1f}",
        f"{loudness.reference_peak:.1f}",
        diff_str,
    )

    # LRA
    diff_str = _format_difference(loudness.lra_difference, "LU", invert=True)
    table.add_row(
        "Loudness Range",
        f"{loudness.track_lra:.1f}",
        f"{loudness.reference_lra:.1f}",
        diff_str,
    )

    # === SPECTRAL SECTION ===
    table.add_section()

    for band in result.spectral.bands:
        diff_str = _format_spectral_difference(band.difference, band.is_significant)
        table.add_row(
            f"{band.band_name} Band",
            f"{band.track_energy:.1f}%",
            f"{band.reference_energy:.1f}%",
            diff_str,
        )

    # === OPTIONAL: BPM ===
    if result.track_bpm is not None and result.reference_bpm is not None:
        table.add_section()
        diff_str = _format_difference(result.bpm_difference or 0.0, "BPM", threshold=2.0)
        table.add_row(
            "Tempo (BPM)",
            f"{result.track_bpm:.1f}",
            f"{result.reference_bpm:.1f}",
            diff_str,
        )

    # === OPTIONAL: KEY ===
    if result.track_key is not None and result.reference_key is not None:
        table.add_section()
        match_str = "✅ Same" if result.track_key == result.reference_key else "⚠️ Different"
        table.add_row(
            "Musical Key",
            result.track_key,
            result.reference_key,
            match_str,
        )

    console.print(table)

    # Add suggestions
    _print_suggestions(result)


def _format_difference(diff: float, unit: str, threshold: float = 1.0, invert: bool = False) -> str:
    """Format a difference value with color and status icons.

    Args:
        diff: Difference value (track - reference)
        unit: Unit string (e.g., "LUFS", "dBTP")
        threshold: Threshold for "significant" difference
        invert: If True, higher values are worse (e.g., for LRA)

    Returns:
        Formatted string with emoji and color
    """
    if abs(diff) < 0.1:
        return "[green]✅ Match[/green]"

    sign = "+" if diff > 0 else ""
    abs_diff = abs(diff)

    # Determine if significant
    is_significant = abs_diff >= threshold

    # For inverted metrics (higher is worse), swap the logic
    if invert:
        if diff > 0:  # Track has more (e.g., wider LRA = more dynamic)
            icon = "🔻" if is_significant else "↓"
            color = "yellow" if is_significant else "white"
        else:
            icon = "🔺" if is_significant else "↑"
            color = "yellow" if is_significant else "white"
    else:
        # Normal: track is louder/higher
        if diff > 0:
            icon = "🔺" if is_significant else "↑"
            color = "yellow" if is_significant else "white"
        else:
            icon = "🔻" if is_significant else "↓"
            color = "yellow" if is_significant else "white"

    return f"[{color}]{icon} {sign}{diff:.1f} {unit}[/{color}]"


def _format_spectral_difference(diff: float, is_significant: bool) -> str:
    """Format spectral band difference.

    Args:
        diff: Percentage point difference
        is_significant: True if difference is > 3%

    Returns:
        Formatted string with color
    """
    if abs(diff) < 0.5:
        return "[green]✅ Match[/green]"

    sign = "+" if diff > 0 else ""
    color = "yellow" if is_significant else "white"
    icon = "⚠️" if is_significant else ""

    return f"[{color}]{icon} {sign}{diff:.1f}%[/{color}]"


def _print_suggestions(result: ComparisonResult) -> None:
    """Print actionable suggestions based on comparison.

    Args:
        result: ComparisonResult
    """
    suggestions = []

    # Check LUFS difference
    lufs_diff = result.loudness.lufs_difference
    if lufs_diff < -2.0:
        suggestions.append(
            f"💡 Your track is {abs(lufs_diff):.1f} dB quieter. Consider increasing gain or limiting."
        )
    elif lufs_diff > 2.0:
        suggestions.append(
            f"💡 Your track is {lufs_diff:.1f} dB louder. May cause clipping or fatigue."
        )

    # Check significant spectral differences
    for band in result.spectral.bands:
        if band.is_significant:
            if band.difference < 0:
                suggestions.append(
                    f"💡 {band.band_name} band is {abs(band.difference):.1f}% lower. "
                    f"Boost around {_get_band_freq_hint(band.band_name)}."
                )
            else:
                suggestions.append(
                    f"💡 {band.band_name} band is {band.difference:.1f}% higher. "
                    f"Consider cutting around {_get_band_freq_hint(band.band_name)}."
                )

    # Check true peak
    if result.loudness.track_peak > -0.5:
        suggestions.append(
            f"⚠️ True peak is {result.loudness.track_peak:.1f} dBTP (very close to 0dB). "
            "Risk of clipping on some systems."
        )

    if suggestions:
        console.print("\n[bold]💡 Suggestions:[/bold]")
        for suggestion in suggestions[:5]:  # Limit to top 5
            console.print(f"  {suggestion}")


def _get_band_freq_hint(band_name: str) -> str:
    """Get frequency hint for a band name.

    Args:
        band_name: Name of band (Sub, Low, Mid, High, Air)

    Returns:
        Frequency range hint
    """
    hints = {
        "Sub": "20-60 Hz",
        "Low": "60-250 Hz",
        "Mid": "250-2000 Hz",
        "High": "2-8 kHz",
        "Air": "8-20 kHz",
    }
    return hints.get(band_name, "unknown")


def _display_json(result: ComparisonResult) -> None:
    """Display comparison results as JSON.

    Args:
        result: ComparisonResult from compare_tracks
    """
    output = {
        "track": result.track_name,
        "reference": result.reference_name,
        "loudness": {
            "track_lufs": result.loudness.track_lufs,
            "reference_lufs": result.loudness.reference_lufs,
            "lufs_difference": result.loudness.lufs_difference,
            "track_peak": result.loudness.track_peak,
            "reference_peak": result.loudness.reference_peak,
            "peak_difference": result.loudness.peak_difference,
            "track_lra": result.loudness.track_lra,
            "reference_lra": result.loudness.reference_lra,
            "lra_difference": result.loudness.lra_difference,
        },
        "spectral": {
            "bands": [
                {
                    "name": band.band_name,
                    "track_energy": band.track_energy,
                    "reference_energy": band.reference_energy,
                    "difference": band.difference,
                    "is_significant": band.is_significant,
                }
                for band in result.spectral.bands
            ]
        },
    }

    if result.track_bpm is not None:
        output["bpm"] = {
            "track": result.track_bpm,
            "reference": result.reference_bpm,
            "difference": result.bpm_difference,
        }

    if result.track_key is not None:
        output["key"] = {
            "track": result.track_key,
            "reference": result.reference_key,
        }

    console.print(json.dumps(output, indent=2))
