"""
BPM Detection
=============

This example demonstrates tempo (BPM) detection on synthetic audio signals.

Tempo detection is crucial for electronic music production, helping you
understand the rhythmic structure of your tracks and ensuring they match
genre expectations.
"""

import matplotlib.pyplot as plt
import numpy as np

from mixref.detective.tempo import detect_bpm

# %%
# Generate 130 BPM House Kick Pattern
# ------------------------------------
# House music typically ranges from 118-128 BPM, but let's use 130
# to show the detector working at the upper end.

sr = 22050  # Sample rate
duration = 8  # seconds
audio = np.zeros(sr * duration)

# Add kicks every 0.46 seconds (130 BPM = 60/130 seconds per beat)
kick_interval = int(60 / 130 * sr)
kick_samples = 50

for i in range(0, len(audio), kick_interval):
    if i + kick_samples < len(audio):
        # Create kick envelope (exponential decay)
        envelope = np.exp(-np.linspace(0, 5, kick_samples))
        audio[i : i + kick_samples] = 0.7 * envelope

# %%
# Detect BPM
# ----------
# Run the detector with default settings

result = detect_bpm(audio, sr, start_bpm=120.0)

print(f"Detected BPM: {result.bpm:.1f}")
print(f"Confidence: {result.confidence:.2f}")

# %%
# Visualize the Audio Pattern
# ----------------------------
# Show the kick pattern we created

time = np.linspace(0, duration, len(audio))

plt.figure(figsize=(12, 4))
plt.plot(time, audio, linewidth=0.5)
plt.xlabel("Time (seconds)")
plt.ylabel("Amplitude")
plt.title(f"Synthetic {130} BPM House Pattern (Detected: {result.bpm:.1f} BPM)")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# %%
# Compare Different Tempos
# -------------------------
# Let's test the detector on multiple common BPM ranges

test_bpms = [120, 128, 140, 174]  # House, Techno, DnB
results = []

for target_bpm in test_bpms:
    # Generate pattern
    test_audio = np.zeros(sr * 6)
    interval = int(60 / target_bpm * sr)

    for i in range(0, len(test_audio), interval):
        if i + 40 < len(test_audio):
            test_audio[i : i + 40] = 0.8

    # Detect
    detection = detect_bpm(test_audio, sr, start_bpm=target_bpm)
    results.append((target_bpm, detection.bpm, detection.confidence))

# Plot comparison
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

targets = [r[0] for r in results]
detected = [r[1] for r in results]
confidences = [r[2] for r in results]

# BPM comparison
ax1.bar(range(len(targets)), detected, color="steelblue", alpha=0.7, label="Detected")
ax1.plot(range(len(targets)), targets, "ro-", label="Target", markersize=8)
ax1.set_xticks(range(len(targets)))
ax1.set_xticklabels([f"{t} BPM" for t in targets])
ax1.set_ylabel("BPM")
ax1.set_title("BPM Detection Accuracy")
ax1.legend()
ax1.grid(True, alpha=0.3)

# Confidence scores
ax2.bar(range(len(targets)), confidences, color="green", alpha=0.7)
ax2.set_xticks(range(len(targets)))
ax2.set_xticklabels([f"{t} BPM" for t in targets])
ax2.set_ylabel("Confidence")
ax2.set_ylim([0, 1])
ax2.set_title("Detection Confidence")
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

print("\nDetection Results:")
print("-" * 50)
for target, det, conf in results:
    error = abs(det - target)
    print(f"Target: {target:3.0f} BPM | Detected: {det:6.1f} BPM | "
          f"Error: {error:5.1f} | Confidence: {conf:.2f}")
