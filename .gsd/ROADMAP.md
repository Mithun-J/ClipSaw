# ROADMAP.md — Retention Auto-Clipper

> **Current Phase**: Complete (v1.0 Milestone Delivered)
> **Milestone**: v1.0 MVP
> **Status**: ✅ All Phases Verified & Committed

## Must-Haves (from SPEC)
- [x] Universal video ingestion pipeline (local upload & YouTube download via `yt-dlp`)
- [x] 100% local, free open-source speech transcription with word-level timestamps (`faster-whisper` on GPU CUDA)
- [x] Retention scoring algorithm (speech cadence + audio energy peaks + hook detection)
- [x] 9:16 vertical video re-framing (smart crop / blur background / split-screen) with animated karaoke subtitles
- [x] Anti-copyright strike protection engine (pitch/tempo shift, background lo-fi music bed, micro-zoom, color grading, metadata scrubbing)
- [x] Modern dark-mode Web Studio UI (FastAPI + HTML5/Tailwind) with live preview and download

---

## Phases

### Phase 1: Ingestion & Media Pipeline
**Status**: 🟢 Complete (Commit `c9caaae`)  
**Deliverable**: `backend/ingestion.py`, `backend/media_utils.py`, `requirements.txt`.

### Phase 2: Local Open-Source Transcription & Retention Scoring
**Status**: 🟢 Complete (Commit `5967096`)  
**Deliverable**: `backend/transcriber.py`, `backend/retention_scorer.py`.

### Phase 3: 9:16 Vertical Reframing & Dynamic Karaoke Subtitles
**Status**: 🟢 Complete (Commit `d186a63`)  
**Deliverable**: `backend/subtitle_generator.py`, `backend/reframe.py`, `backend/video_processor.py`.

### Phase 4: Anti-Copyright Strike & Fair Use Protection Engine
**Status**: 🟢 Complete (Commit `422313b`)  
**Deliverable**: `backend/copyright_shield.py`.

### Phase 5: Modern Web Studio Dashboard & End-to-End Delivery
**Status**: 🟢 Complete (Commit `e399713`)  
**Deliverable**: `backend/app.py`, `frontend/index.html`, `run_studio.py`, `start_studio.bat`, `start_studio.ps1`.
