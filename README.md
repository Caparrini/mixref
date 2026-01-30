# mixref

CLI Audio Analyzer for Music Producers

> **Status**: Active Development 🚧

A sharp, opinionated audio analysis tool that speaks the language of producers. Focused on electronic music (Drum & Bass, Techno, House) with genre-aware insights.

## Features (In Development)

- 🎚️ **LUFS Metering**: EBU R128 loudness with platform-specific targets
- 🎵 **BPM & Key Detection**: Genre-aware tempo and key analysis with Camelot notation
- 📊 **Spectral Analysis**: Frequency band breakdown for mixing decisions
- 🔄 **A/B Comparison**: Compare your mix against professional references
- 🎯 **Smart Suggestions**: Actionable feedback based on genre best practices

## Installation

```bash
# Coming soon to PyPI
uv pip install mixref
```

## Quick Start

```bash
# Analyze a track
mixref analyze my_track.wav

# Genre-specific analysis
mixref analyze neurofunk.wav --genre dnb

# Compare with reference
mixref compare my_mix.wav reference.wav

# JSON output for automation
mixref analyze track.wav --json
```

## Development

```bash
# Clone and setup
git clone https://github.com/yourusername/mixref.git
cd mixref
uv sync --dev

# Run tests
pytest

# Type check
mypy src/

# Lint
ruff check src/
```

## License

MIT
