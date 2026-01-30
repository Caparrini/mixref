# Changelog

All notable changes to mixref will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Audio validation utilities (duration, sample rate checks)
- LUFS metering functionality
- BPM and key detection
- Spectral analysis
- A/B comparison engine

## [0.1.0] - 2026-01-30

### Added
- Initial project structure with uv package manager
- Audio file loading with format handling (WAV, FLAC, MP3, OGG, AIFF)
- Custom exception hierarchy for audio errors:
  - AudioFileNotFoundError
  - UnsupportedFormatError
  - CorruptFileError
  - InvalidAudioDataError
- Mono/stereo conversion with configurable modes
- Optional resampling to target sample rate
- Basic CLI with --help and --version
- Comprehensive test suite (25 tests, 88%+ coverage)
- Sphinx documentation with gallery examples
- GitHub Actions CI/CD pipeline
- Automated PyPI publishing on release
- Synthetic audio generators for testing

### Infrastructure
- Test matrix: Python 3.12-3.13 on Ubuntu, macOS, Windows
- Automated documentation deployment to GitHub Pages
- Code quality checks (ruff, mypy, docstrings)
- Coverage tracking with Codecov
- PyPI and TestPyPI publishing workflows

### Documentation
- Complete API reference
- Installation guide
- Quick start guide
- Two Sphinx-Gallery examples (audio loading, error handling)
- CI/CD setup documentation
- Contributing guidelines

### Published
- ✅ PyPI: https://pypi.org/project/mixref/
- ✅ TestPyPI: https://test.pypi.org/project/mixref/
- ✅ Codecov configured and tracking coverage

