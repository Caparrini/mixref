# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2026-02-01

### Added

#### 🔄 A/B Comparison Feature
- **New `mixref compare` command** for side-by-side track analysis
  - Compare your mix against professional references
  - Loudness comparison (LUFS, True Peak, LRA)
  - Spectral balance comparison across 5 frequency bands
  - Optional BPM and key comparison with `--bpm` and `--key` flags
  - Smart significance thresholds (3% for spectral differences)
  - Visual diff indicators: 🔺 higher, 🔻 lower, ✅ match, ⚠️ warning
  - Actionable suggestions based on differences
  - JSON output support for scripting
- **Comparison engine** (`src/mixref/compare/`)
  - `compare_loudness()` - LUFS and dynamic range comparison
  - `compare_spectral()` - Frequency band analysis with significance detection
  - `compare_tracks()` - Unified comparison with optional features
  - Comprehensive test coverage (100% for comparison module)

#### 📚 Documentation Improvements
- **Updated README to v0.3.0+ features**
  - Replaced "Coming Soon" with actual implemented features
  - Added real CLI usage examples for all commands
  - Python API examples showcasing all modules
  - Real-world output examples
- **Live terminal demos**
  - SVG animations showing `analyze` and `compare` in action
  - Created with termtosvg for authentic terminal experience
  - Embedded directly in README for better UX
  - Reproducible demo scripts included

### Fixed

#### 🐛 Critical Bug Fixes
- **Fixed stereo-to-mono conversion in BPM and key detection**
  - Issue: `np.mean(audio, axis=0)` with (samples, channels) produced only 2 samples
  - Root cause: Mismatch between `load_audio()` format and detector expectations
  - Solution: Intelligent format detection based on array shape
  - Symptom: BPM was returning 0.0, key detection unreliable
  - Impact: BPM and key detection now work correctly with real audio files
- **Fixed table alignment in CLI output**
  - Issue: Emoji variation selectors caused misaligned pipes
  - Changed ℹ️ (2 chars) to ℹ (1 char) for consistency with 🔴 and ❓
  - Added `min_width` to Value and Status columns
  - All table pipes now perfectly aligned

### Changed
- Analysis output now uses consistent single-character emojis
- Improved warning messages with specific feedback

## [0.3.0] - 2026-01-31

### Added

#### 🎵 BPM Detection (Phase 5)
- **Tempo detection integrated into `mixref analyze`**
  - Automatic BPM detection using librosa beat tracking
  - Confidence scoring based on rhythmic consistency
  - **Genre-aware BPM correction** - automatically detects and fixes half-time issues
    - Doubles BPM if detected below 100 (common issue in electronic music)
    - Validates against genre-specific ranges when `--genre` flag used
  - Visual status indicators in output:
    - 🎵 Normal detection
    - 🔧 BPM was corrected (doubled from half-time)
    - ⚠️ Outside expected genre range
  - Genre BPM ranges:
    - DnB: 160-180 BPM (typical: 174)
    - Techno: 120-140 BPM (typical: 130)
    - House: 118-128 BPM (typical: 124)
    - Dubstep: 135-145 BPM (typical: 140)
    - Trance: 125-145 BPM (typical: 138)
  - Included in JSON output with correction metadata

#### 🎹 Musical Key Detection (Phase 6)
- **Key detection integrated into `mixref analyze`**
  - Chroma-based key detection using Krumhansl-Schmuckler profiles
  - **Camelot wheel notation for DJs** - Shows both traditional (e.g., "Eb minor") and Camelot code (e.g., "8A")
  - Compatible key suggestions for harmonic mixing
  - Prefers flat notation (Eb not D#) per electronic music conventions
  - Confidence scoring for key detection quality
  - Visual status indicators:
    - 🎹 High confidence detection (>60%)
    - ❓ Low confidence - key may be ambiguous
  - Included in JSON output with confidence scores

#### 📊 Spectral Analysis (Phase 7)
- **Frequency band analysis integrated into `mixref analyze`**
  - 5 production-focused frequency bands analyzed:
    - **Sub** (20-60Hz) - Magenta bars 🟣
    - **Low** (60-250Hz) - Blue bars 🔵
    - **Mid** (250-2kHz) - Green bars 🟢
    - **High** (2-8kHz) - Yellow bars 🟡
    - **Air** (8-20kHz) - Cyan bars 🔷
  - **Visual energy bars** in Rich table output showing relative energy per band
  - Energy displayed as both dB and percentage of total
  - STFT-based analysis for accurate frequency measurement
  - Spectral comparison function for A/B reference comparison (foundation for Phase 8)
  - Included in JSON output with per-band energy data

#### 📈 Enhanced Analyze Command
- **Complete production analysis in one command**:
  ```bash
  mixref analyze track.wav --platform spotify --genre dnb
  ```
  Now shows:
  - ✅ Loudness (LUFS, True Peak, LRA)
  - ✅ **Tempo (BPM with genre validation)**
  - ✅ **Musical Key (with Camelot code)**
  - ✅ **5 Frequency Bands (visual bars)**
  - ✅ Platform comparison
  - ✅ Genre comparison

- **JSON output includes all detective data**:
  - `tempo` object with BPM, confidence, correction info
  - `key` object with musical key, Camelot code, confidence
  - `spectral` object with 5 band energies and percentages

### Testing
- **136 total tests** (up from 75 in v0.2.0)
  - +10 tempo detection tests
  - +22 BPM correction tests  
  - +14 key detection tests
  - +15 spectral analysis tests
  - 12 CLI integration tests (updated for new features)
- **All tests passing** with comprehensive coverage
- Synthetic audio generation for all detective module tests

### Technical Improvements
- Genre enum mapping between `meters.Genre` and `detective.Genre`
- Audio shape handling for different analysis functions
- Efficient STFT-based spectral analysis
- Krumhansl-Schmuckler key profiles implementation
- Onset strength-based BPM confidence scoring

### Documentation
- Sphinx-Gallery example for BPM detection
- Complete API documentation for all detective modules
- Updated analyze command examples showing new features

## [0.2.0] - 2026-01-30

### Added

#### 🎉 Analyze Command
- **`mixref analyze` CLI command** - First usable command for producers!
  - Analyze audio files and get loudness metrics (LUFS, true peak, LRA)
  - Beautiful Rich table output with color-coded status indicators (🟢🟡🔴)
  - `--platform` option to compare against streaming targets (Spotify, YouTube, Apple Music, Tidal, SoundCloud, Club, Broadcast)
  - `--genre` option to compare against genre-specific targets (DnB, Techno, House, Dubstep, Trance)
  - `--json` flag for machine-readable output (automation-friendly)
  - Short options: `-p` for platform, `-g` for genre
  - Comprehensive error handling with helpful messages

#### 🎚️ LUFS Metering & Targets
- **EBU R128 loudness measurement** (`calculate_lufs`)
  - Integrated LUFS (whole-track loudness)
  - True peak detection (dBTP) for clipping prevention
  - Loudness range (LRA) for dynamic range measurement
  - Short-term max/min LUFS values
  - Supports both mono and stereo audio
- **Platform-specific targets** (`Platform` enum, `get_target`)
  - Spotify: -14 LUFS | YouTube: -14 LUFS | Apple Music: -16 LUFS
  - Tidal: -14 LUFS | SoundCloud: -10 LUFS
  - Club/DJ: -8 LUFS | Broadcast: -23 LUFS
- **Genre-specific targets** (`Genre` enum)
  - Drum & Bass: -8 LUFS (club-ready)
  - Techno: -9 LUFS | House: -10 LUFS
  - Dubstep: -7 LUFS (most aggressive) | Trance: -9 LUFS
- **Target comparison** (`compare_to_target`)
  - Returns is_acceptable flag, difference in dB, and human-readable message
  - Genre-aware feedback (e.g., "5.9 dB below Drum & Bass target")

#### ✅ Audio Validation
- **Audio file validation** (`validate_duration`, `validate_sample_rate`)
  - Check duration constraints (min/max)
  - Verify sample rates with tolerance
  - Detailed error messages
- **Audio metadata** (`get_audio_info`)
  - Extract duration, sample rate, channels, format, subtype
  - Returns structured `AudioInfo` namedtuple

#### 📚 Documentation
- **Sphinx-Gallery examples**
  - `plot_analyze_command.py` - Complete workflow demonstration
  - `plot_lufs_and_targets.py` - LUFS metering and target comparison
  - `plot_audio_validation.py` - Audio file validation
  - `plot_loading_audio_files.py` - Audio loading examples
  - `plot_error_handling.py` - Error handling patterns
- **API documentation** - Complete Sphinx documentation for all modules
- **README updates** - Installation instructions, platform support matrix

#### 🧪 Testing
- **75 total tests** (up from 25 in v0.1.0)
  - 12 CLI integration tests
  - 17 loudness target tests
  - 10 LUFS metering tests
  - 11 audio validation tests
  - 14 audio loading tests
- **91% code coverage** (exceeds 85% requirement)
- **Synthetic audio generation** - Test fixtures for reproducible testing

#### 🚀 CI/CD Improvements
- **GitHub Actions workflows**
  - Test matrix: Ubuntu, macOS, Windows × Python 3.12, 3.13
  - Code quality checks: ruff, mypy, interrogate
  - Documentation builds with warnings-as-errors
  - Automated PyPI publishing on release tags
  - Codecov integration
- **Platform support** - Python 3.13 on Windows excluded (known numpy issue)

### Fixed
- Audio shape handling: `load_audio` returns `(samples, channels)` but `calculate_lufs` expects `(channels, samples)` - analyze command handles transpose automatically
- Sphinx documentation warnings (duplicate object descriptions resolved)
- Type annotations for all CLI functions

### Developer Experience
- **Pre-commit checklist** - Mandatory quality checks before committing
- **Release process documentation** - Step-by-step release guide
- **CI fixes summary** - Troubleshooting reference

### Technical Details
- Uses `pyloudnorm` for EBU R128 compliance
- Rich library for beautiful terminal output
- Typer for CLI with automatic help generation
- All code follows strict type checking (mypy)
- 100% formatted with ruff

## [0.1.0] - 2026-01-29

### Added
- Initial release with basic audio loading functionality
- `load_audio()` function supporting WAV, FLAC, MP3 formats
- Automatic mono/stereo handling
- Sample rate validation and resampling
- Comprehensive error handling
- CLI skeleton with `--version` flag
- Full test suite with 25 tests
- Sphinx documentation
- GitHub Actions CI/CD
- PyPI and TestPyPI publishing
