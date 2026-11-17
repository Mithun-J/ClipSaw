"""
ingestion.py - Universal ingestion service for local video files and web video URLs (YouTube, etc.).
Includes robust YouTube anti-bot and client fallback mechanisms.
"""

import os
import shutil
import uuid
from typing import Any, Callable, Dict, Optional
from backend.media_utils import extract_audio, extract_frame, probe_video, sanitize_filename


class IngestionService:
    def __init__(self, storage_dir: str = "storage"):
        self.storage_dir = os.path.abspath(storage_dir)
        self.downloads_dir = os.path.join(self.storage_dir, "downloads")
        self.audio_dir = os.path.join(self.storage_dir, "audio")
        self.clips_dir = os.path.join(self.storage_dir, "clips")
        self.temp_dir = os.path.join(self.storage_dir, "temp")

        for d in [self.downloads_dir, self.audio_dir, self.clips_dir, self.temp_dir]:
            os.makedirs(d, exist_ok=True)

    def ingest_local_file(self, file_path: str, custom_title: Optional[str] = None) -> Dict[str, Any]:
        """
        Ingest a local video file, probe its metadata, and extract normalized audio.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Local file not found: {file_path}")

        media_id = str(uuid.uuid4())[:8]
        filename = os.path.basename(file_path)
        base_name, ext = os.path.splitext(filename)
        title = custom_title or base_name

        safe_title = sanitize_filename(title)
        dest_filename = f"{media_id}_{safe_title}{ext}"
        dest_video_path = os.path.join(self.downloads_dir, dest_filename)

        # Copy to storage if not already there
        if os.path.abspath(file_path) != os.path.abspath(dest_video_path):
            shutil.copy2(file_path, dest_video_path)

        # Probe video
        meta = probe_video(dest_video_path)

        # Extract audio track
        audio_filename = f"{media_id}_{safe_title}.wav"
        dest_audio_path = os.path.join(self.audio_dir, audio_filename)
        extract_audio(dest_video_path, dest_audio_path)

        # Extract preview thumbnail at 1s or middle
        thumb_filename = f"{media_id}_{safe_title}_thumb.jpg"
        dest_thumb_path = os.path.join(self.temp_dir, thumb_filename)
        thumb_ts = min(1.0, max(0.0, meta["duration"] / 2))
        extract_frame(dest_video_path, timestamp_sec=thumb_ts, output_img_path=dest_thumb_path)

        return {
            "id": media_id,
            "title": title,
            "source_type": "local",
            "video_path": dest_video_path,
            "audio_path": dest_audio_path,
            "thumb_path": dest_thumb_path,
            "metadata": meta
        }

    def ingest_url(self, url: str, progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None) -> Dict[str, Any]:
        """
        Download remote video URL via yt-dlp with multi-client fallback (android, ios, web),
        probe metadata, and extract normalized audio.
        """
        try:
            import yt_dlp
        except ImportError:
            raise RuntimeError("yt-dlp is not installed. Please install yt-dlp first.")

        media_id = str(uuid.uuid4())[:8]
        temp_template = os.path.join(self.downloads_dir, f"{media_id}_%(title)s.%(ext)s")

        def hook(d):
            if progress_callback and d.get("status") == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                downloaded = d.get("downloaded_bytes", 0)
                pct = (downloaded / total * 100) if total > 0 else 0
                progress_callback({
                    "status": "downloading",
                    "percentage": round(pct, 1),
                    "speed": d.get("speed", 0),
                    "eta": d.get("eta", 0)
                })

        # yt-dlp options configured with player_client fallback to bypass YouTube's
        # bot blocks and "This video is not available" errors.
        ydl_opts = {
            "format": "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
            "outtmpl": temp_template,
            "merge_output_format": "mp4",
            "progress_hooks": [hook],
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "extractor_args": {
                "youtube": {
                    "player_client": ["android", "ios", "web"]
                }
            },
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            downloaded_file = ydl.prepare_filename(info)

        if not os.path.exists(downloaded_file):
            base_no_ext = os.path.splitext(downloaded_file)[0]
            for ext in [".mp4", ".mkv", ".webm"]:
                if os.path.exists(base_no_ext + ext):
                    downloaded_file = base_no_ext + ext
                    break

        if not os.path.exists(downloaded_file):
            prefix = f"{media_id}_"
            candidates = [
                os.path.join(self.downloads_dir, f)
                for f in os.listdir(self.downloads_dir)
                if f.startswith(prefix) and not f.endswith(".part") and not f.endswith(".ytdl")
            ]
            if candidates:
                downloaded_file = candidates[0]
            else:
                raise FileNotFoundError(f"Downloaded file not found for URL: {url}")

        title = info.get("title", f"Video_{media_id}")
        meta = probe_video(downloaded_file)

        safe_title = sanitize_filename(title)
        audio_filename = f"{media_id}_{safe_title}.wav"
        dest_audio_path = os.path.join(self.audio_dir, audio_filename)
        extract_audio(downloaded_file, dest_audio_path)

        thumb_filename = f"{media_id}_{safe_title}_thumb.jpg"
        dest_thumb_path = os.path.join(self.temp_dir, thumb_filename)
        thumb_ts = min(1.0, max(0.0, meta["duration"] / 2))
        extract_frame(downloaded_file, timestamp_sec=thumb_ts, output_img_path=dest_thumb_path)

        return {
            "id": media_id,
            "title": title,
            "source_type": "url",
            "source_url": url,
            "author": info.get("uploader", "Unknown"),
            "video_path": downloaded_file,
            "audio_path": dest_audio_path,
            "thumb_path": dest_thumb_path,
            "metadata": meta
        }
