---
phase: 5
plan: 1
wave: 1
gap_closure: false
---

# Plan 5.1: Modern Web Studio Dashboard & End-to-End Delivery

## Objective
Build the FastAPI web service and modern responsive dark-mode Web Studio dashboard, bringing together video ingestion (local/URL), local transcription, viral retention scoring, 9:16 vertical formatting, and anti-copyright shield protection in a one-click user studio.

## Context
- .gsd/SPEC.md
- .gsd/ROADMAP.md
- backend/ingestion.py
- backend/transcriber.py
- backend/retention_scorer.py
- backend/video_processor.py
- backend/copyright_shield.py

## Tasks

<task type="auto">
  <name>Build FastAPI Web Server & API Endpoints</name>
  <files>
    backend/app.py
  </files>
  <action>
    Create FastAPI application providing:
    1. Static file serving for frontend UI at '/' and storage media at '/storage'.
    2. Endpoint POST /api/ingest/url (URL download via yt-dlp).
    3. Endpoint POST /api/ingest/upload (multipart file upload).
    4. Endpoint POST /api/analyze/{media_id} (runs local transcription & retention scoring).
    5. Endpoint POST /api/render (renders selected 9:16 clip with chosen anti-copyright shield preset).
    6. Endpoint GET /api/clips (list ready-to-download clips).
    7. Endpoint GET /api/health (health check).
  </action>
  <verify>
    python -c "from backend.app import app; print('FastAPI app imported successfully')"
  </verify>
  <done>
    FastAPI app exposes full workflow as documented REST endpoints.
  </done>
</task>

<task type="auto">
  <name>Build Modern Dark-Mode Web Studio Frontend</name>
  <files>
    frontend/index.html
  </files>
  <action>
    Create sleek, responsive single-page web studio:
    1. Header with branding: "⚡ RETENTION CLIPPER" & "Anti-Copyright Shield: Active".
    2. Ingestion section: YouTube URL input with 'Fetch Video' button and Drag & Drop file zone.
    3. Live Status & Progress tracker with step indicator.
    4. Clips Explorer: Grid of detected viral clips with retention score badges, headline banners, duration, and preview buttons.
    5. Studio Settings Panel:
       - 9:16 Format mode selector (Blur Padding, Smart Center Crop, Split-Screen).
       - Anti-Copyright Shield Preset (Subtle, Balanced, Aggressive, Off).
    6. Preview & Download Studio: Vertical 9:16 video player with download button.
  </action>
  <verify>
    python -c "import os; assert os.path.exists('frontend/index.html'); print('frontend/index.html exists')"
  </verify>
  <done>
    frontend/index.html is ready and serves cleanly at root url.
  </done>
</task>

<task type="auto">
  <name>Verification Suite for Phase 5 & Startup Scripts</name>
  <files>
    tests/test_phase5.py
    run_studio.py
  </files>
  <action>
    1. Implement run_studio.py to start Uvicorn server on port 8000.
    2. Create test_phase5.py using FastAPI TestClient to test health, URL validation, and clip rendering endpoints.
  </action>
  <verify>
    python tests/test_phase5.py
  </verify>
  <done>
    test_phase5.py runs and validates all API routes with exit code 0.
  </done>
</task>
