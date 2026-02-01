# mixref Developer Companion

**Project**: mixref – CLI Audio Analyzer for Music Producers  
**Focus**: Electronic Music, Drum & Bass, Techno, House  
**Status**: v0.3.0 Active Development  
**Last Updated**: 2026-02-01

---

## ⚠️ CRITICAL: PRE-COMMIT REQUIREMENTS

**BEFORE MAKING ANY CODE CHANGES**, understand this:

### Why GitHub Actions Fail When Local Tests Pass

GitHub Actions runs with **strict formatting checks** that may not be enforced in your local environment:

1. **Formatting is MANDATORY**: All code must pass `ruff format --check`
2. **Local testing might not catch this**: Your local environment may have different ruff settings or you might only run `ruff check` (which doesn't verify formatting)
3. **CI/CD fails on unformatted code**: Even if tests pass locally

### The Fix: ALWAYS Run These Commands Before Committing

```bash
# 1. Format ALL code (not just check - actually format it)
uv run ruff format src/ tests/

# 2. Verify formatting is correct
uv run ruff format --check src/ tests/

# 3. Run linting
uv run ruff check src/ tests/

# 4. Run type checking
uv run mypy src/

# 5. Run tests
uv run pytest
```

### All-in-One Pre-Commit Command

```bash
uv run ruff format src/ tests/ && \
uv run ruff format --check src/ tests/ && \
uv run ruff check src/ tests/ && \
uv run mypy src/ && \
uv run pytest
```

**If ANY of these fail, DO NOT COMMIT.** Fix the issues first.

### Common Formatting Issues

1. **String quotes**: Ruff prefers double quotes `"` over single quotes `'`
2. **Line length**: Keep lines under 88 characters (ruff default)
3. **Function calls**: Ruff may condense multi-line calls that fit on one line
4. **Import order**: Ruff automatically sorts imports

### Why This Matters

- ❌ **Without formatting**: GitHub Actions will fail with `action_required` status
- ✅ **With formatting**: All workflows pass cleanly
- 🎯 **Result**: Faster PR merges, no wasted CI/CD time

---

## 🎯 PROJECT VISION
A sharp, opinionated audio tool that speaks the language of producers. Not another generic analyzer—something that understands that a DnB track should hit differently than a deep house tune.

---

## 🛠️ BUILD, TEST, LINT

### Essential Commands
```bash
# Setup
uv sync --all-extras              # Install all dependencies (dev + docs)

# Testing
uv run pytest                      # Run all tests
uv run pytest tests/test_tempo.py  # Run single test file
uv run pytest -k test_bpm_detection # Run tests matching pattern
uv run pytest --cov=src/mixref --cov-report=term-missing  # With coverage

# Type Checking
uv run mypy src/                   # Type check source code

# Linting & Formatting
uv run ruff check src/ tests/      # Lint code
uv run ruff format src/ tests/     # Format code
uv run ruff format --check src/    # Check formatting without changes

# Documentation
cd docs && uv run sphinx-build -W -b html source build/html

# Run the CLI locally
uv run mixref --help
uv run mixref analyze path/to/audio.wav
```

### Quality Requirements
- **Coverage**: 85%+ (enforced in CI)
- **Type checking**: Strict mode, all functions typed
- **Formatting**: Ruff (line length: 100)
- **Python**: 3.12+ (3.13 on Windows has numpy issues)

---

## 🏗️ ARCHITECTURE

### Module Organization
```
src/mixref/
├── audio/          # Audio I/O layer
│   ├── loader.py       # File loading (WAV/FLAC/MP3/OGG/AIFF)
│   ├── validation.py   # Format/integrity checks
│   └── exceptions.py   # Custom audio errors
│
├── detective/      # Feature extraction
│   ├── tempo.py           # BPM detection (librosa beat tracking)
│   ├── bpm_correction.py  # Genre-aware BPM validation
│   ├── key.py             # Musical key + Camelot codes
│   └── spectral.py        # Frequency band analysis
│
├── meters/         # Loudness metering
│   ├── loudness.py   # EBU R128 LUFS (pyloudnorm)
│   └── targets.py    # Platform targets (Spotify/YouTube/Club)
│
├── compare/        # A/B comparison
│   └── engine.py   # Track comparison logic
│
└── cli/            # User interface
    ├── main.py      # Typer app entry point
    ├── analyze.py   # analyze command
    └── compare.py   # compare command
```

### Data Flow Pattern
1. **Load**: `audio.loader.load_audio()` → numpy array + sample rate
2. **Detect**: `detective.*` modules extract features (BPM, key, spectral)
3. **Measure**: `meters.*` calculate loudness metrics
4. **Compare**: `compare.*` performs A/B analysis (optional)
5. **Present**: `cli.*` formats output with Rich tables

### Key Design Decisions
- **Mono conversion for analysis**: Multi-channel audio converted to mono for tempo/key detection (keeps stereo for loudness)
- **Lazy imports**: Heavy dependencies (librosa) only loaded when needed
- **Dataclasses for results**: Type-safe, immutable analysis results
- **Rich for output**: Terminal-first UX with colors and tables

---

## 📝 CODE CONVENTIONS

### Type Hints (Required)
```python
# ✅ Good
def detect_tempo(audio: NDArray[np.float32], sample_rate: int) -> TempoResult:
    """Detect tempo with confidence score."""
    ...

# ❌ Bad - no types
def detect_tempo(audio, sample_rate):
    ...
```

### Docstrings (Google Style)
```python
def calculate_lufs(audio: NDArray[np.float32], sample_rate: int) -> LoudnessResult:
    """Calculate EBU R128 loudness metrics.

    Args:
        audio: Audio signal (mono or stereo, float32)
        sample_rate: Sample rate in Hz

    Returns:
        LoudnessResult with LUFS, true peak, and LRA

    Raises:
        ValueError: If audio is empty or sample_rate invalid

    Example:
        >>> audio, sr = load_audio("track.wav")
        >>> result = calculate_lufs(audio, sr)
        >>> print(f"LUFS: {result.lufs_integrated}")
    """
```

### Naming Conventions
- **Functions**: `snake_case` - `calculate_lufs()`, `detect_tempo()`
- **Classes**: `PascalCase` - `LoudnessResult`, `TempoResult`
- **Constants**: `UPPER_SNAKE` - `DEFAULT_SAMPLE_RATE`, `MIN_BPM`
- **Private**: Leading `_` - `_convert_to_mono()`, `_validate_audio()`

### Error Handling
```python
# ✅ Good - specific exceptions with helpful messages
if not audio_path.exists():
    raise AudioFileNotFoundError(f"File not found: {audio_path}")

# ❌ Bad - generic exception
if not audio_path.exists():
    raise Exception("File not found")
```

---

## 🧪 TESTING PATTERNS

### Test File Organization
```
tests/
├── test_audio.py           # Audio loading tests
├── test_loudness.py        # LUFS calculation tests
├── test_tempo.py           # BPM detection tests
├── test_key.py             # Key detection tests
├── test_spectral.py        # Spectral analysis tests
├── test_compare.py         # Comparison engine tests
├── test_cli_*.py           # CLI command tests
├── synthetic_audio.py      # Shared test fixtures
└── conftest.py             # pytest configuration
```

### Synthetic Audio Only
```python
# ✅ Good - generate test signals
from tests.synthetic_audio import generate_sine_wave

def test_lufs_calculation():
    audio = generate_sine_wave(duration=1.0, frequency=440, sample_rate=44100)
    result = calculate_lufs(audio, 44100)
    assert result.lufs_integrated < 0

# ❌ Bad - NEVER commit real audio files
def test_lufs_calculation():
    audio, sr = load_audio("data/real_track.wav")  # NO!
```

### Available Test Signals
- `generate_sine_wave()` - Pure tones (A4 = 440Hz)
- `generate_pink_noise()` - Full spectrum noise
- `generate_silence()` - Silent buffer (edge case testing)
- `generate_clipped_signal()` - Distorted/clipping audio
- `generate_stereo_signal()` - Multi-channel audio

### Coverage Requirements
- **Minimum**: 85% overall coverage
- **Target**: 90%+ for new features
- **Critical paths**: 100% (audio loading, LUFS calculation)

---

## 🔄 DEVELOPMENT WORKFLOW

### Starting New Feature
```bash
# 1. Create feature branch (optional)
git checkout -b feature/batch-analysis

# 2. Install dependencies if needed
uv add librosa  # Example

# 3. Run tests baseline
uv run pytest

# 4. Make changes...
```

### Before Every Commit
```bash
# Run the full quality check
uv run ruff format src/ tests/ && \
uv run ruff format --check src/ tests/ && \
uv run ruff check src/ tests/ && \
uv run mypy src/ && \
uv run pytest
```

### Commit Message Format
```bash
# Format: <type>: <description>

# Types:
feat:     # New feature
fix:      # Bug fix
docs:     # Documentation only
refactor: # Code restructuring
test:     # Test changes
chore:    # Build/tooling changes

# Examples:
git commit -m "feat: add A/B comparison engine"
git commit -m "fix: correct stereo-to-mono conversion in BPM detection"
git commit -m "docs: update README with compare command examples"
```

---

## 🎧 AUDIO PHILOSOPHY

### Loudness Targets
- **Streaming**: -14 LUFS (Spotify, YouTube, Apple Music)
- **Club/DnB**: -8 to -6 LUFS (maximum impact)
- **True Peak**: Never clip above -1.0 dBTP
- **LRA (Loudness Range)**:
  - < 8 LU: Heavily compressed (EDM, DnB)
  - > 12 LU: Dynamic (acoustic, jazz)

### BPM Detection Philosophy
Electronic music cheat codes:
- If detected BPM < 100 → probably half-time → double it
- **DnB range**: 160-180 BPM (typical: 174)
- **Techno range**: 120-140 BPM (typical: 130)
- **House range**: 118-128 BPM (typical: 124)
- **Dubstep range**: 135-145 BPM (typical: 140)

### Key Detection
- **Prefer flats**: Eb minor, not D# minor (producer convention)
- **Camelot codes**: 8A, 5B, etc. (DJ-friendly)
- **Confidence thresholds**: > 0.6 = reliable, < 0.4 = ambiguous

### Spectral Bands (Production-Focused)
- **Sub (20-60Hz)**: Kick fundamental, sub-bass
- **Low (60-250Hz)**: Bass, kick body
- **Mid (250-2kHz)**: Vocals, snares, most instruments
- **High (2-8kHz)**: Hi-hats, cymbals, vocal presence
- **Air (8-20kHz)**: Sparkle, ambience

---

## 🚀 QUICK REFERENCE

### Most Common Tasks

**Run single test file:**
```bash
uv run pytest tests/test_tempo.py -v
```

**Check what changed:**
```bash
git status
git diff
```

**Format and commit:**
```bash
uv run ruff format src/ tests/
git add .
git commit -m "feat: your message here"
```

**Test specific function:**
```bash
uv run pytest -k test_detect_bpm
```

**Run with coverage:**
```bash
uv run pytest --cov=src/mixref --cov-report=html
```

---

## 💡 TIPS FOR COPILOT SESSIONS

1. **Provide context**: Include file paths, function names, error messages
2. **Show actual output**: Paste command results, stack traces, test failures
3. **Be specific**: "Fix BPM detection for half-time tracks" > "Make BPM work better"
4. **Spanish OK**: Comments in Spanish are fine for personal notes
5. **Ask why**: Understanding beats memorizing

### Example Good Prompts
```
"Create a function to compare two tracks' spectral balance.
Should return percentage difference per band with 3% significance threshold.
Include tests with synthetic audio."

"The BPM detection returns 0.0 for data/example.wav. Error shows:
'UserWarning: n_fft=2048 is too large for input signal of length=2'
What's wrong with the mono conversion?"

"Add a --json flag to the compare command that outputs comparison
results in JSON format instead of Rich tables."
```

---

## 📦 DEPENDENCIES

### Core (Runtime)
- **librosa**: Audio analysis (BPM, key, spectral)
- **pyloudnorm**: EBU R128 loudness metering
- **soundfile**: Audio file I/O
- **typer**: CLI framework
- **rich**: Terminal formatting

### Development
- **pytest**: Testing framework
- **pytest-cov**: Coverage reporting
- **mypy**: Type checking
- **ruff**: Linting and formatting

### Documentation
- **sphinx**: Documentation generator
- **sphinx-gallery**: Example gallery
- **sphinx-rtd-theme**: ReadTheDocs theme

---

## 🎯 PROJECT STATUS (v0.3.0)

### ✅ Completed
- [x] Audio loading (WAV, FLAC, MP3, OGG, AIFF)
- [x] LUFS metering (EBU R128)
- [x] Platform targets (Spotify, YouTube, Club)
- [x] Genre targets (DnB, Techno, House)
- [x] BPM detection with half-time correction
- [x] Musical key detection with Camelot codes
- [x] Spectral analysis (5-band breakdown)
- [x] `mixref analyze` command with Rich output
- [x] JSON export for automation
- [x] A/B comparison (`mixref compare`)
- [x] Live terminal demos in README

### 🚧 In Progress
- [ ] Batch analysis (`mixref batch`)
- [ ] Smart suggestions engine
- [ ] Genre-specific feedback improvements

### 📋 Planned
- [ ] Audio preview/playback
- [ ] Export comparison reports (PDF/HTML)
- [ ] Integration with DAWs (Ableton, FL Studio)
- [ ] Web UI (optional)

---

**Remember**: Quality over speed. Tests and types prevent bugs. Format before commit. 🎯
