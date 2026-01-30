# mixref

[![Tests](https://github.com/yourusername/mixref/actions/workflows/test.yml/badge.svg)](https://github.com/yourusername/mixref/actions/workflows/test.yml)
[![Documentation](https://github.com/yourusername/mixref/actions/workflows/docs.yml/badge.svg)](https://github.com/yourusername/mixref/actions/workflows/docs.yml)
[![Code Quality](https://github.com/yourusername/mixref/actions/workflows/quality.yml/badge.svg)](https://github.com/yourusername/mixref/actions/workflows/quality.yml)
[![PyPI](https://img.shields.io/pypi/v/mixref)](https://pypi.org/project/mixref/)
[![Python Versions](https://img.shields.io/pypi/pyversions/mixref)](https://pypi.org/project/mixref/)
[![License](https://img.shields.io/github/license/yourusername/mixref)](LICENSE)

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

# Build docs
cd docs && make html
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed development guidelines.

## CI/CD

This project uses GitHub Actions for continuous integration:

- ✅ **Tests**: Python 3.12-3.13 on Ubuntu, macOS, Windows
- 📚 **Docs**: Auto-deployed to GitHub Pages
- 🔍 **Quality**: Linting, type checking, coverage (85%+)
- 📦 **Publish**: Automated PyPI releases

See [.github/CICD_SETUP.md](.github/CICD_SETUP.md) for CI/CD configuration details.

## License

MIT
