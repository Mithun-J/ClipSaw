---
phase: 4
plan: 1
wave: 1
gap_closure: false
---

# Plan 4.1: Anti-Copyright Strike & Fair Use Protection Engine

## Objective
Implement multi-layered Content ID and perceptual hash disruption to protect generated clips from automated copyright strikes while preserving natural, high-quality audio and visual clarity for viewers.

## Context
- .gsd/SPEC.md
- .gsd/ROADMAP.md
- backend/video_processor.py
- backend/reframe.py

## Tasks

<task type="auto">
  <name>Build Copyright Shield Engine</name>
  <files>
    backend/copyright_shield.py
  </files>
  <action>
    Implement CopyrightShield providing 3 preset levels (Safe/Subtle, Balanced, Aggressive):
    1. Audio Protections:
       - Micro-pitch shift: ±1.2% to ±2.0% pitch variation.
       - Micro-tempo modulation: 1.02x to 1.05x speed shift.
       - Parametric EQ adjustments: subtle low-end warmth and high-shelf tweak.
       - Ducked background audio bed: generate or overlay ambient royalty-free lofi audio layer.
    2. Video Protections:
       - Subtle color grading / contrast curve (eq=contrast=1.04:saturation=1.06).
       - Micro-zoom modulation (subtle 2% - 3% crop or periodic pan).
       - Optional horizontal flip (mirror mode).
    3. Metadata Scrubbing:
       - Strip all original stream tags, comments, camera metadata (-map_metadata -1).
    4. Provide integrate_shield() method that augments FFmpeg filter graphs and arguments.
  </action>
  <verify>
    python -c "from backend.copyright_shield import CopyrightShield; print('CopyrightShield imported successfully')"
  </verify>
  <done>
    CopyrightShield module cleanly generates transformative filter chains for FFmpeg.
  </done>
</task>

<task type="auto">
  <name>Integrate Shield into VideoProcessor Pipeline</name>
  <files>
    backend/video_processor.py
  </files>
  <action>
    Update VideoProcessor to support protection_level parameter ("off", "subtle", "balanced", "aggressive").
    When enabled, apply CopyrightShield audio filters, video transformations, and metadata stripping.
  </action>
  <verify>
    python -c "from backend.video_processor import VideoProcessor; print('Updated VideoProcessor imported successfully')"
  </verify>
  <done>
    VideoProcessor renders clips with protection filters applied.
  </done>
</task>

<task type="auto">
  <name>Verification Suite for Phase 4</name>
  <files>
    tests/test_phase4.py
  </files>
  <action>
    Create test script comparing unprotected clip vs protected clip:
    1. Probe both clips and compare audio waveform characteristics and metadata.
    2. Verify metadata is sanitized (-map_metadata -1).
    3. Verify audio pitch/tempo transformation is active without audible distortion.
  </action>
  <verify>
    python tests/test_phase4.py
  </verify>
  <done>
    test_phase4.py passes with exit code 0 and verifies fingerprint disruption.
  </done>
</task>
