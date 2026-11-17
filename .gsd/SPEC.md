# SPEC.md — Retention Auto-Clipper with Anti-Copyright Shield

> **Status**: `FINALIZED`
>
> ⚠️ **Planning Lock**: UNLOCKED. Requirements agreed and finalized.

## Vision
An automated, high-retention video clipping studio and processing engine built entirely with free, open-source local technologies. The tool ingests long-form video files or video URLs (YouTube, etc.), automatically transcribes speech locally using open-source models, analyzes dialogue cadence, energy peaks, and viral hooks to extract high-retention 15s–60s segments, reframes them into 9:16 vertical video (Shorts/Reels/TikTok) with animated karaoke subtitles, and applies multi-layered transformative anti-copyright protection (pitch/tempo shift, background music bed, micro-zoom, color grade, metadata stripping) to defeat automated Content ID fingerprint strikes without external API costs.

---

## Goals
1. **Universal Video Ingestion**: Support both drag-and-drop local video file uploads (MP4, MKV, MOV, WebM) and direct video URL fetching (YouTube, etc., via `yt-dlp`).
2. **100% Free & Local AI Analysis**:
   - Transcribe audio locally using open-source Whisper / faster-whisper models with word-level timestamps (offline, zero API costs).
   - Identify viral clips through speech density, energy spikes, silence elimination, and hook/punchline detection.
3. **9:16 Vertical Video Reframing (Reels / Shorts / TikTok)**:
   - Dynamic vertical crop with smart speaker centering (OpenCV face/motion detection), blurred background padding mode, or split-screen mode.
4. **Animated Word-by-Word Subtitles**:
   - Render eye-catching, animated karaoke subtitles (Hormozi / MrBeast style) with dynamic word highlighting.
5. **Multi-Tier Anti-Copyright Strike Shield (Content ID Disruption)**:
   - **Audio Layer**: Micro-pitch adjustment (±1.5%), micro-tempo modulation (1.02x–1.05x), audio frequency reshaping, and ducked royalty-free background lo-fi music bed mix.
   - **Visual Layer**: Dynamic micro-zoom/pan breathing, subtle color grading/LUT tone shift, optional horizontal flip, and visual noise disruption.
   - **Container Layer**: Comprehensive metadata stripping and re-encoding to destroy original stream fingerprints.
   - **Presets**: Configurable levels (`Subtle`, `Balanced`, `Aggressive`, `Custom`).
6. **Modern Dark-Mode Web Studio UI**:
   - FastAPI + HTML5/Tailwind/Alpine dashboard with real-time video preview player, clip timeline cards, retention score badges, protection level controls, and batch export/download.

---

## Non-Goals (Out of Scope)
- Cloud/paid API dependencies (e.g. OpenAI / Gemini paid keys required) — must run completely on free/open-source local stack.
- Multi-track timeline non-linear video editing (NLE) — focus is automated viral clipping and conversion.
- Direct account publishing / bot auto-posting in v1 (v1 focuses on high quality export ready for manual or scheduled upload).

---

## Users
- Content creators, podcasters, streamers, and theme page curators wanting fast, automated short-form video generation that bypasses algorithmic duplicate/copyright detection.

---

## Constraints
- **Host OS**: Windows 11 / PowerShell environment.
- **Hardware Acceleration**: NVIDIA GPU / CUDA support available (`torch 2.7.1+cu118`), with CPU fallback.
- **Tools**: Python 3.13, FFmpeg 8.0, OpenCV, FastAPI, Uvicorn.
- **GSD Rules**: Atomic commits per task, empirical verification for every step, no shell operator chaining (`&&` / `||`).

---

## Success Criteria
- [ ] Users can enter a YouTube URL or upload a local video and start processing.
- [ ] Local open-source transcription generates word-level timestamps without any external API keys.
- [ ] Retention detection identifies top 3–5 engaging clips with calculated retention scores.
- [ ] Clips are exported in vertical 9:16 format with high-visibility animated karaoke subtitles.
- [ ] Anti-copyright shield successfully alters audio/video fingerprints while preserving crisp viewer experience.
- [ ] Web Studio is fully interactive, running locally at `http://localhost:8000` with clean UI and download capabilities.

---

## Technical Stack
| Domain | Open-Source Technology | Purpose |
|--------|------------------------|---------|
| **Backend & API** | Python 3.13 + FastAPI + Uvicorn | Orchestration, video pipeline, REST endpoints |
| **Video Engine** | FFmpeg 8.0.1 + OpenCV | Video reformatting, audio filtering, subtitles, transforms |
| **Ingestion** | `yt-dlp` | Remote video/audio stream downloading |
| **Transcription** | `faster-whisper` / `whisper` | Fast local speech-to-text with word-level timestamps |
| **Retention Detector** | Audio RMS energy + speech cadence NLP | Algorithmic viral moment isolation |
| **Anti-Copyright** | FFmpeg rubberband/atempo, eq, curves, zoompan | Content ID fingerprint disruption |
| **Frontend** | Modern HTML5 + Tailwind CSS + Vanilla JS | Responsive, reactive, dark-themed Web Studio UI |

---

*Status: FINALIZED — Approved by User*
