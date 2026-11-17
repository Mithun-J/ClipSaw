# ROADMAP.md — Retention Auto-Clipper

> **Current Phase**: Phase 1: Ingestion & Media Pipeline
> **Milestone**: v1.0 MVP
> **Status**: In Progress

## Must-Haves (from SPEC)
- [ ] Universal video ingestion pipeline (local upload & YouTube download via `yt-dlp`)
- [ ] 100% local, free open-source speech transcription with word-level timestamps (`faster-whisper` / `whisper`)
- [ ] Retention scoring algorithm (speech cadence + audio energy peaks + hook detection)
- [ ] 9:16 vertical video re-framing (smart crop / blur background / split-screen) with animated karaoke subtitles
- [ ] Anti-copyright strike protection engine (pitch/tempo shift, background lo-fi music bed, micro-zoom, color grading, metadata scrubbing)
- [ ] Modern dark-mode Web Studio UI (FastAPI + HTML5/Tailwind) with live preview and download

---

## Phases

### Phase 1: Ingestion & Media Pipeline
**Status**: 🟡 In Progress  
**Objective**: Build video downloader and ingestion engine handling local video files and web URLs (`yt-dlp`), extracting metadata, video specs, and audio tracks via FFmpeg.  
**Deliverables**:
- Package setup (`requirements.txt` with `yt-dlp`, `faster-whisper`, etc.)
- Ingestion module `backend/ingestion.py`
- Media inspection & audio extraction `backend/media_utils.py`
- Verification tests with sample media

### Phase 2: Local Open-Source Transcription & Retention Scoring
**Status**: ⬜ Not Started  
**Objective**: Integrate local Whisper model for word-level timestamp transcription, and build the retention analyzer (speech density, audio RMS energy, hook/question detection) to extract ranked 15s–60s clip candidates.  
**Deliverables**:
- `backend/transcriber.py` (local Whisper runner)
- `backend/retention_scorer.py` (high-retention segment detector)
- Verification script testing transcript & segment generation

### Phase 3: 9:16 Vertical Reframing & Dynamic Karaoke Subtitles
**Status**: ⬜ Not Started  
**Objective**: Transform landscape videos into 9:16 vertical format (smart speaker crop via OpenCV, blurred background, split-screen) and render high-engagement animated karaoke subtitles (ASS subtitle generator & FFmpeg burn-in).  
**Deliverables**:
- `backend/subtitle_generator.py` (ASS word-level highlight generator)
- `backend/reframe.py` (OpenCV smart crop / blurred background / split-screen)
- Verification producing a polished 9:16 vertical test clip

### Phase 4: Anti-Copyright Strike & Fair Use Protection Engine
**Status**: ⬜ Not Started  
**Objective**: Implement automated audio/video fingerprint disruption engine (micro-pitch shift, tempo modulation, ducked lo-fi background music bed, micro-zoom/pan breathing, subtle color grading/LUT, metadata scrub).  
**Deliverables**:
- `backend/copyright_shield.py` with presets (Subtle, Balanced, Aggressive)
- Royalty-free background music asset integration
- Verification showing altered audio spectrum & video fingerprint without quality loss

### Phase 5: Modern Web Studio Dashboard & End-to-End Delivery
**Status**: ⬜ Not Started  
**Objective**: Build FastAPI backend and modern dark-mode Web Studio UI with drag-and-drop upload, YouTube URL input, real-time progress, interactive clip previewer, subtitle customizer, protection toggles, and one-click batch export.  
**Deliverables**:
- `backend/app.py` (FastAPI app and API endpoints)
- `frontend/index.html` (Tailwind CSS modern responsive UI)
- End-to-end user verification and startup scripts
