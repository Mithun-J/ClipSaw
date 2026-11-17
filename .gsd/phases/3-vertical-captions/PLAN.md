---
phase: 3
plan: 1
wave: 1
gap_closure: false
---

# Plan 3.1: 9:16 Vertical Reframing & Dynamic Karaoke Subtitles

## Objective
Implement vertical video reframing (1080x1920 9:16 aspect ratio) for YouTube Shorts, Instagram Reels, and TikTok, paired with high-engagement animated karaoke subtitles (word-level active highlighting and hook header banner) burned in via FFmpeg.

## Context
- .gsd/SPEC.md
- .gsd/ROADMAP.md
- backend/media_utils.py
- backend/transcriber.py

## Tasks

<task type="auto">
  <name>Build Dynamic Karaoke Subtitle Generator (ASS format)</name>
  <files>
    backend/subtitle_generator.py
  </files>
  <action>
    Implement SubtitleGenerator producing Advanced SubStation Alpha (.ass) files:
    1. Define modern short-form style: bold sans-serif font (Arial/Impact/Montserrat), large size, high contrast (bright yellow/green active word, crisp white text, heavy black outline, drop shadow).
    2. Group word timestamps into short, readable 3-6 word phrases.
    3. Generate dynamic word highlighting: active spoken word turns bright yellow (#00FFFF / &H00FFFF&) while surrounding phrase words stay white.
    4. Optional top hook headline box styling at 15% screen height.
  </action>
  <verify>
    python -c "from backend.subtitle_generator import SubtitleGenerator; print('SubtitleGenerator imported successfully')"
  </verify>
  <done>
    SubtitleGenerator produces valid .ass subtitle file with word-by-word karaoke highlights.
  </done>
</task>

<task type="auto">
  <name>Build 9:16 Vertical Video Reframing Engine</name>
  <files>
    backend/reframe.py
  </files>
  <action>
    Implement VideoReframer using FFmpeg complex filter graphs:
    1. Mode 'blur_padding': Background scaled to 1080x1920 and blurred (boxblur or gblur), foreground original video scaled to 1080 width and centered vertically at y=(1920-h)/2.
    2. Mode 'smart_crop': 1080x1920 center/face-tracking crop from landscape source.
    3. Mode 'split_screen': Top half speaker/source, bottom half blurred/b-roll background.
  </action>
  <verify>
    python -c "from backend.reframe import VideoReframer; print('VideoReframer imported successfully')"
  </verify>
  <done>
    VideoReframer generates the required 9:16 FFmpeg filter graphs for all layout modes.
  </done>
</task>

<task type="auto">
  <name>Build Video Clip Renderer Pipeline</name>
  <files>
    backend/video_processor.py
  </files>
  <action>
    Implement VideoProcessor coordinating:
    1. Extracting clip slice (start_time to end_time) from master video.
    2. Generating .ass subtitle file relative to clip start time (offset timestamps to 0.0s).
    3. Running FFmpeg with reframe filter + subtitles burn-in (`subtitles=...:force_style=...`).
    4. Exporting optimized H.264 vertical MP4 clip.
  </action>
  <verify>
    python -c "from backend.video_processor import VideoProcessor; print('VideoProcessor imported successfully')"
  </verify>
  <done>
    VideoProcessor produces ready-to-watch 9:16 vertical MP4 video with embedded subtitles.
  </done>
</task>

<task type="auto">
  <name>Verification Suite for Phase 3</name>
  <files>
    tests/test_phase3.py
  </files>
  <action>
    Create a test script that:
    1. Takes a synthetic 16:9 test video and mock timed words.
    2. Generates an .ass subtitle file.
    3. Processes the video into 1080x1920 vertical format with burned-in subtitles.
    4. Verifies the output file exists, has resolution 1080x1920, and correct duration.
  </action>
  <verify>
    python tests/test_phase3.py
  </verify>
  <done>
    test_phase3.py passes with exit code 0 and verifies 1080x1920 vertical MP4 generation.
  </done>
</task>
