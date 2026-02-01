# mixref

[![Tests](https://github.com/caparrini/mixref/actions/workflows/test.yml/badge.svg)](https://github.com/caparrini/mixref/actions/workflows/test.yml)
[![Documentation](https://github.com/caparrini/mixref/actions/workflows/docs.yml/badge.svg)](https://github.com/caparrini/mixref/actions/workflows/docs.yml)
[![Code Quality](https://github.com/caparrini/mixref/actions/workflows/quality.yml/badge.svg)](https://github.com/caparrini/mixref/actions/workflows/quality.yml)
[![codecov](https://codecov.io/gh/caparrini/mixref/branch/main/graph/badge.svg)](https://codecov.io/gh/caparrini/mixref)
[![PyPI version](https://img.shields.io/pypi/v/mixref)](https://pypi.org/project/mixref/)
[![Python Versions](https://img.shields.io/pypi/pyversions/mixref)](https://pypi.org/project/mixref/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation Status](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://caparrini.github.io/mixref/)

CLI Audio Analyzer for Music Producers

> **Status**: v0.3.0 - Feature Complete! 🎉

A sharp, opinionated audio analysis tool that speaks the language of producers. Not another generic analyzer—built specifically for electronic music (Drum & Bass, Techno, House) with genre-aware insights that matter.

## Features

### 🎚️ Professional Loudness Analysis

- **EBU R128 Metering**: Integrated LUFS, True Peak (dBTP), Loudness Range (LRA)
- **Platform Targets**: Spotify (-14), YouTube (-14), Apple Music (-16), Club (-6 to -8)
- **Genre Awareness**: DnB, Techno, House, Dubstep, Trance profiles
- **Real-time Warnings**: Clipping detection, loudness guidance

### 🎵 Musical Analysis

- **BPM Detection**: Genre-aware tempo detection with half-time correction
- **Key Detection**: Krumhansl-Schmuckler algorithm with Camelot notation (8A, 5B, etc.)
- **Confidence Scores**: Know how reliable the detection is

### 📊 Spectral Analysis

- **5-Band Breakdown**: Sub (20-60Hz), Low (60-250Hz), Mid (250-2kHz), High (2-8kHz), Air (8-20kHz)
- **Visual Bars**: See your frequency balance at a glance
- **Percentage Distribution**: Understand where your energy sits

### 🔄 A/B Comparison

- **Reference Matching**: Compare your mix against professional tracks
- **Side-by-Side Analysis**: Loudness, spectral, BPM, and key comparison
- **Smart Suggestions**: Get actionable feedback on what to adjust
- **Difference Highlighting**: See exactly where you differ (> 3% significance threshold)

### 📤 Flexible Output

- **Rich CLI Tables**: Beautiful terminal output with colors and formatting
- **JSON Export**: Perfect for scripting and automation
- **Multiple Formats**: WAV, FLAC, MP3, OGG, AIFF support

## Installation

```bash
# From PyPI
pip install mixref

# Or with uv
uv pip install mixref
```

### System Requirements

- **Python**: 3.12 or 3.13
- **Platforms**: Linux, macOS, Windows

> **⚠️ Known Issue**: Python 3.13 on Windows is not currently supported due to numpy/librosa compatibility issues. Windows users should use Python 3.12. This limitation does not affect Linux or macOS.

## Quick Start

### Python API

```python
from mixref.audio import load_audio
from mixref.meters import calculate_lufs
from mixref.detective import detect_tempo, detect_key

# Load and analyze
audio, sr = load_audio("your_track.wav")

# Get loudness metrics
result = calculate_lufs(audio, sr)
print(f"LUFS: {result.lufs_integrated}")
print(f"True Peak: {result.true_peak_dbtp}")

# Detect BPM and key
bpm = detect_tempo(audio, sr)
key = detect_key(audio, sr)
print(f"Tempo: {bpm.bpm} BPM")
print(f"Key: {key.key_name} ({key.camelot_code})")
```

### CLI Usage

```bash
# Check version
mixref --version

# Analyze a track
mixref analyze my_track.wav

# With platform target
mixref analyze track.wav --platform spotify

# With genre awareness
mixref analyze dnb_track.wav --genre dnb

# JSON output for scripting
mixref analyze track.wav --json | jq '.lufs.integrated'

# Compare your mix to a reference
mixref compare my_mix.wav professional_reference.wav

# Full comparison with BPM and key
mixref compare my_track.wav reference.wav --bpm --key

# Compare with JSON output
mixref compare track1.wav track2.wav --json
```

## Real-World Example

```bash
$ mixref analyze neurofunk_banger.wav --genre dnb

             Analysis: neurofunk_banger.wav             
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Metric              ┃        Value ┃ Status ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━┩
│ Integrated Loudness │    -6.2 LUFS │   🔴   │
│ True Peak           │    -0.8 dBTP │   ⚠️   │
│ Loudness Range      │       5.2 LU │   ℹ    │
├─────────────────────┼──────────────┼────────┤
│ Tempo               │    174.0 BPM │   ❓   │
│ Key                 │ F minor (4A) │   ❓   │
├─────────────────────┼──────────────┼────────┤
│ Sub                 │   ■■■■■■■□□□ │ 35.2%  │
│ Low                 │   ■■■■■■■■■□ │ 28.4%  │
│ Mid                 │   ■■■■□□□□□□ │ 18.1%  │
│ High                │   ■■■■■■□□□□ │ 14.2%  │
│ Air                 │   ■□□□□□□□□□ │  4.1%  │
└─────────────────────┴──────────────┴────────┘

⚠️  Platform Targets
  • Spotify (-14):      🔴 +7.8 dB too loud
  • YouTube (-14):      🔴 +7.8 dB too loud
  • Club/DJ:            🟢 OK for club play

💡 Genre Insights (DnB)
  • Sub-bass is strong (35%) - typical for neurofunk
  • True peak close to 0dB - consider -1dB headroom
```

## Documentation

Full documentation is available at **[caparrini.github.io/mixref](https://caparrini.github.io/mixref/)**

- 📖 [Installation Guide](https://caparrini.github.io/mixref/installation.html)
- 🚀 [Quick Start](https://caparrini.github.io/mixref/quickstart.html)
- 📚 [API Reference](https://caparrini.github.io/mixref/api/index.html)
- 🎨 [Examples Gallery](https://caparrini.github.io/mixref/auto_examples/index.html)

## Development

```bash
# Clone and setup
git clone https://github.com/caparrini/mixref.git
cd mixref
uv sync --all-extras

# Run tests
uv run pytest

# Type check
uv run mypy src/

# Lint and format
uv run ruff check src/
uv run ruff format src/

# Build docs
cd docs && uv run sphinx-build -b html source build/html
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed development guidelines.

## CI/CD

This project uses GitHub Actions for continuous integration:

- ✅ **Tests**: Python 3.12-3.13 on Ubuntu, macOS, Windows
- 📚 **Docs**: Auto-deployed to [GitHub Pages](https://caparrini.github.io/mixref/)
- 🔍 **Quality**: Linting, type checking, coverage (88%+)
- 📦 **Publish**: Automated PyPI releases
- 📊 **Coverage**: Tracked on [Codecov](https://codecov.io/gh/caparrini/mixref)

See [.github/CICD_SETUP.md](.github/CICD_SETUP.md) for CI/CD configuration details.

## Links

- **PyPI**: https://pypi.org/project/mixref/
- **Documentation**: https://caparrini.github.io/mixref/
- **Source Code**: https://github.com/caparrini/mixref
- **Issue Tracker**: https://github.com/caparrini/mixref/issues
- **Codecov**: https://codecov.io/gh/caparrini/mixref

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.
