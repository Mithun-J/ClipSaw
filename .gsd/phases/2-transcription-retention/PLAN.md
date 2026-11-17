---
phase: 2
plan: 1
wave: 1
gap_closure: false
---

# Plan 2.1: Local Open-Source Transcription & Retention Scoring Engine

## Objective
Implement local, free open-source speech-to-text with word-level timestamps using `faster-whisper`, and build a multi-factor viral retention scoring engine (hook detection, cadence, audio RMS energy, natural pause boundaries) to isolate 15s–60s viral clip candidates.

## Context
- .gsd/SPEC.md
- .gsd/ROADMAP.md
- backend/media_utils.py

## Tasks

<task type="auto">
  <name>Build Local Whisper Transcriber Module</name>
  <files>
    backend/transcriber.py
  </files>
  <action>
    Implement Transcriber class wrapping faster_whisper:
    1. Load model ('tiny', 'base', or 'small') with device detection ('cuda' if available else 'cpu', compute_type='int8' or 'float16').
    2. Transcribe WAV audio with word_timestamps=True and vad_filter=True (voice activity detection).
    3. Return structured transcript: segments list with text, start, end, and word-level timing [{word, start, end, probability}].
    4. Provide fallback transcription mock/heuristic for rapid testing when model weight download is skipped.
  </action>
  <verify>
    python -c "from backend.transcriber import Transcriber; print('Transcriber imported successfully')"
  </verify>
  <done>
    Transcriber generates word-level timestamps without any external API calls.
  </done>
</task>

<task type="auto">
  <name>Build Viral Retention & Hook Scoring Engine</name>
  <files>
    backend/retention_scorer.py
  </files>
  <action>
    Implement RetentionScorer:
    1. Hook analysis: Score opening phrases (interrogative hooks, contrarian statements, emotional superlatives).
    2. Pacing & Cadence: Compute Words-Per-Minute (WPM), penalize excessive dead air / pauses (>1.5s).
    3. Audio RMS energy variance: Read audio samples and detect emotional/vocal emphasis peaks.
    4. Natural sentence boundary snapping: Ensure clips start and end on sentence borders or natural pauses.
    5. Duration enforcement: Filter candidate segments between min_duration (15s) and max_duration (60s).
    6. Aggregate into a normalized Retention Score (0–100%) and rank top candidates.
  </action>
  <verify>
    python -c "from backend.retention_scorer import RetentionScorer; print('RetentionScorer imported successfully')"
  </verify>
  <done>
    RetentionScorer produces ranked list of candidate viral clips with score breakdown.
  </done>
</task>

<task type="auto">
  <name>Verification Suite for Phase 2</name>
  <files>
    tests/test_phase2.py
  </files>
  <action>
    Create test script with realistic speech segments and audio signal:
    1. Test transcription pipeline structure.
    2. Test retention scoring across varying cadences and hook phrases.
    3. Confirm candidate clips meet length limits (15s–60s) and have ranked scores.
  </action>
  <verify>
    python tests/test_phase2.py
  </verify>
  <done>
    test_phase2.py runs and validates word timing and retention ranking with exit code 0.
  </done>
</task>
