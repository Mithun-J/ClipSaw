---
phase: 1
plan: 1
wave: 1
gap_closure: false
---

# Plan 1.1: Core Ingestion & Media Utilities Engine

## Objective
Establish the project environment, directory layout, and robust media processing foundation for ingesting both local video files and web video URLs (YouTube, etc.), extracting technical metadata and normalized audio tracks for downstream processing.

## Context
- .gsd/SPEC.md
- .gsd/ROADMAP.md

## Tasks

<task type="auto">
  <name>Setup Dependencies & Project Directory Structure</name>
  <files>
    requirements.txt
    storage/.gitkeep
  </files>
  <action>
    Create requirements.txt specifying required open-source libraries:
    - yt-dlp
    - faster-whisper
    - fastapi
    - uvicorn
    - python-multipart
    - aiofiles
    - pydantic
    - numpy
    - opencv-python
    Create storage folders: storage/downloads, storage/clips, storage/temp, storage/audio.
    Ensure .gitignore excludes video/audio files from git.
  </action>
  <verify>
    python -c "import os; os.makedirs('storage/downloads', exist_ok=True); print('Storage ready')"
  </verify>
  <done>
    Directory structure created and requirements.txt ready.
  </done>
</task>

<task type="auto">
  <name>Build Media Utilities Engine (FFmpeg Wrapper)</name>
  <files>
    backend/media_utils.py
  </files>
  <action>
    Implement FFmpeg wrapper functions:
    1. probe_video(path): Extract width, height, duration, fps, bitrate, audio codec using ffprobe/ffmpeg.
    2. extract_audio(video_path, output_audio_path): Extract 16kHz mono 16-bit PCM WAV optimized for Whisper.
    3. extract_frame(video_path, timestamp_sec, output_img_path): Generate preview thumbnail.
    4. sanitize_filename(name): Safe filename generation.
    Ensure robust error handling for missing files, corrupted streams, or FFmpeg subprocess failures.
  </action>
  <verify>
    python -c "from backend.media_utils import probe_video; print('media_utils imported successfully')"
  </verify>
  <done>
    media_utils.py provides clean helper functions for all media probing and audio extraction.
  </done>
</task>

<task type="auto">
  <name>Build Universal Video Ingestion Module</name>
  <files>
    backend/ingestion.py
  </files>
  <action>
    Implement video ingestion handling both:
    1. Local video file ingestion (validate formats: mp4, mkv, mov, webm; copy/move to storage/downloads).
    2. Remote URL ingestion via yt-dlp: Download video + audio in highest MP4 quality up to 1080p, extract title, duration, author, thumbnail.
    3. Return unified VideoInfo object with path, audio_path, duration, resolution, title.
  </action>
  <verify>
    python -c "from backend.ingestion import IngestionService; print('IngestionService imported successfully')"
  </verify>
  <done>
    IngestionService can accept local files or URLs and return normalized media metadata.
  </done>
</task>

<task type="auto">
  <name>Verification Suite for Phase 1</name>
  <files>
    tests/test_phase1.py
  </files>
  <action>
    Create a verification script that:
    1. Generates a synthetic test video with audio using FFmpeg.
    2. Ingests it via IngestionService.
    3. Probes the video metadata and extracts 16kHz mono audio.
    4. Confirms audio and thumbnail files exist with correct attributes.
  </action>
  <verify>
    python tests/test_phase1.py
  </verify>
  <done>
    tests/test_phase1.py passes with exit code 0 and verifies metadata & audio extraction.
  </done>
</task>
