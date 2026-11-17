"""
app.py - FastAPI application for Retention Auto-Clipper Studio.
"""

import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import json
import shutil
import uuid
from typing import Any, Dict, List, Optional
import torch
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.ingestion import IngestionService
from backend.transcriber import Transcriber
from backend.retention_scorer import RetentionScorer
from backend.video_processor import VideoProcessor
from backend.media_utils import probe_video

app = FastAPI(title="Retention Auto-Clipper API", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize core services
ingestion_service = IngestionService(storage_dir="storage")
retention_scorer = RetentionScorer()
video_processor = VideoProcessor(temp_dir="storage/temp", clips_dir="storage/clips")
transcriber = Transcriber(model_size="base")

# Media sessions cache
MEDIA_REGISTRY: Dict[str, Dict[str, Any]] = {}
ANALYSIS_REGISTRY: Dict[str, Dict[str, Any]] = {}


def get_media_item(media_id: str) -> Optional[Dict[str, Any]]:
    """Look up media item in memory or recover from disk storage."""
    if media_id in MEDIA_REGISTRY:
        return MEDIA_REGISTRY[media_id]

    downloads_dir = os.path.abspath("storage/downloads")
    if os.path.exists(downloads_dir):
        for f in os.listdir(downloads_dir):
            if f.startswith(f"{media_id}_") and f.endswith((".mp4", ".mkv", ".mov", ".webm")):
                video_path = os.path.join(downloads_dir, f)
                base = os.path.splitext(f)[0]
                audio_dir = os.path.abspath("storage/audio")
                audio_path = os.path.join(audio_dir, f"{base}.wav")
                thumb_dir = os.path.abspath("storage/temp")
                thumb_path = os.path.join(thumb_dir, f"{base}_thumb.jpg")
                try:
                    meta = probe_video(video_path)
                except Exception:
                    meta = {"duration": 30.0, "width": 1280, "height": 720}

                item = {
                    "id": media_id,
                    "title": f.split("_", 1)[1] if "_" in f else f,
                    "video_path": video_path,
                    "audio_path": audio_path,
                    "thumb_path": thumb_path,
                    "metadata": meta
                }
                MEDIA_REGISTRY[media_id] = item
                return item
    return None


class URLIngestRequest(BaseModel):
    url: str


class AnalyzeRequest(BaseModel):
    media_id: str
    model_size: Optional[str] = "base"


class RenderClipRequest(BaseModel):
    media_id: str
    start_time: float
    end_time: float
    words: Optional[List[Dict[str, Any]]] = None
    hook_headline: Optional[str] = None
    reframe_mode: Optional[str] = "blur_padding"
    protection_preset: Optional[str] = "subtle"
    captions_style: Optional[str] = "bold"


class RegenerateHeadlineRequest(BaseModel):
    text: str


@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "service": "Retention Auto-Clipper",
        "cuda_available": torch.cuda.is_available(),
        "device": "cuda" if torch.cuda.is_available() else "cpu"
    }


@app.post("/api/ingest/url")
def ingest_url(req: URLIngestRequest):
    if not req.url or not req.url.startswith("http"):
        raise HTTPException(status_code=400, detail="Invalid video URL")
    try:
        item = ingestion_service.ingest_url(req.url)
        MEDIA_REGISTRY[item["id"]] = item
        return {
            "success": True,
            "media": {
                "id": item["id"],
                "title": item["title"],
                "author": item.get("author", "Unknown"),
                "duration": item["metadata"]["duration"],
                "resolution": f"{item['metadata']['width']}x{item['metadata']['height']}",
                "thumb_url": f"/storage/temp/{os.path.basename(item['thumb_path'])}"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to ingest URL: {str(e)}")


@app.post("/api/ingest/upload")
async def ingest_upload(file: UploadFile = File(...)):
    filename = file.filename or "upload.mp4"
    temp_upload_path = os.path.join("storage", "temp", f"upload_{uuid.uuid4().hex[:8]}_{filename}")
    os.makedirs(os.path.dirname(temp_upload_path), exist_ok=True)

    with open(temp_upload_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        item = ingestion_service.ingest_local_file(temp_upload_path, custom_title=os.path.splitext(filename)[0])
        MEDIA_REGISTRY[item["id"]] = item
        return {
            "success": True,
            "media": {
                "id": item["id"],
                "title": item["title"],
                "duration": item["metadata"]["duration"],
                "resolution": f"{item['metadata']['width']}x{item['metadata']['height']}",
                "thumb_url": f"/storage/temp/{os.path.basename(item['thumb_path'])}"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process uploaded file: {str(e)}")


@app.post("/api/analyze")
def analyze_video(req: AnalyzeRequest):
    media = get_media_item(req.media_id)
    if not media:
        raise HTTPException(status_code=404, detail="Media not found. Ingest video first.")

    audio_path = media["audio_path"]
    if not os.path.exists(audio_path):
        raise HTTPException(status_code=400, detail="Extracted audio missing for media.")

    try:
        # Run local transcription with word-level timestamps
        transcript = transcriber.transcribe(audio_path)
        # Run viral retention scoring with dynamic clickbait headlines
        clips = retention_scorer.extract_clips(transcript, audio_path=audio_path, top_k=8)

        ANALYSIS_REGISTRY[req.media_id] = {
            "transcript": transcript,
            "clips": clips
        }

        return {
            "success": True,
            "media_id": req.media_id,
            "duration": transcript["duration"],
            "language": transcript["language"],
            "total_clips_found": len(clips),
            "clips": clips
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription & retention analysis failed: {str(e)}")


@app.post("/api/render")
def render_clip(req: RenderClipRequest):
    media = get_media_item(req.media_id)
    if not media:
        raise HTTPException(status_code=404, detail=f"Media {req.media_id} not found.")

    source_video_path = media["video_path"]
    if not os.path.exists(source_video_path):
        raise HTTPException(status_code=404, detail="Source video file not found on disk.")

    try:
        render_result = video_processor.render_clip(
            source_video_path=source_video_path,
            start_time=req.start_time,
            end_time=req.end_time,
            words=req.words,
            hook_headline=req.hook_headline,
            reframe_mode=req.reframe_mode or "blur_padding",
            protection_preset=req.protection_preset or "subtle",
            captions_style=req.captions_style or "bold"
        )

        filename = os.path.basename(render_result["clip_path"])
        return {
            "success": True,
            "clip_id": render_result["clip_id"],
            "download_url": f"/storage/clips/{filename}",
            "duration": render_result["duration"],
            "resolution": f"{render_result['width']}x{render_result['height']}",
            "protection_preset": render_result["protection_preset"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rendering clip failed: {str(e)}")


@app.post("/api/headline/regenerate")
def regenerate_headline(req: RegenerateHeadlineRequest):
    """Regenerate a fresh clickbait hook title for a clip."""
    headline = retention_scorer._generate_headline(req.text, req.text.split(".")[0])
    return {"headline": headline}


@app.get("/api/clips")
def list_clips():
    clips_dir = os.path.abspath("storage/clips")
    if not os.path.exists(clips_dir):
        return {"clips": []}

    clips = []
    for f in os.listdir(clips_dir):
        if f.endswith(".mp4"):
            full_path = os.path.join(clips_dir, f)
            try:
                meta = probe_video(full_path)
                clips.append({
                    "filename": f,
                    "url": f"/storage/clips/{f}",
                    "size_mb": round(os.path.getsize(full_path) / (1024 * 1024), 2),
                    "duration": meta["duration"],
                    "resolution": f"{meta['width']}x{meta['height']}",
                    "is_vertical": meta["is_vertical"]
                })
            except Exception:
                pass
    return {"clips": clips}


# Mount storage files for video preview & download
os.makedirs("storage/temp", exist_ok=True)
os.makedirs("storage/clips", exist_ok=True)
app.mount("/storage", StaticFiles(directory="storage"), name="storage")


# Serve frontend index
@app.get("/")
def serve_index():
    index_file = os.path.abspath("frontend/index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Frontend not found"}
