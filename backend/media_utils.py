"""
media_utils.py - FFmpeg & FFprobe utilities for video metadata, audio extraction, and frame snapshots.
"""

import json
import os
import re
import subprocess
from typing import Any, Dict, Optional


def sanitize_filename(name: str, max_length: int = 100) -> str:
    """Sanitize title/filename to remove characters illegal in Windows/Unix paths."""
    clean = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", name)
    clean = clean.strip().replace(" ", "_")
    if not clean:
        clean = "clip"
    return clean[:max_length]


def probe_video(video_path: str) -> Dict[str, Any]:
    """
    Probe a video file using ffprobe and return structured metadata.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        video_path
    ]

    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        data = json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"ffprobe failed: {e.stderr}")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse ffprobe JSON output: {e}")

    format_info = data.get("format", {})
    streams = data.get("streams", [])

    video_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)

    width = int(video_stream.get("width", 0)) if video_stream else 0
    height = int(video_stream.get("height", 0)) if video_stream else 0

    fps = 30.0
    if video_stream and "r_frame_rate" in video_stream:
        r_fps = video_stream["r_frame_rate"]
        if "/" in r_fps:
            num, den = r_fps.split("/")
            if float(den) > 0:
                fps = round(float(num) / float(den), 2)
        else:
            try:
                fps = float(r_fps)
            except ValueError:
                pass

    duration = float(format_info.get("duration", 0.0))
    if duration == 0.0 and video_stream:
        duration = float(video_stream.get("duration", 0.0))

    bitrate = int(format_info.get("bit_rate", 0))

    return {
        "file_path": os.path.abspath(video_path),
        "file_size": os.path.getsize(video_path),
        "duration": duration,
        "width": width,
        "height": height,
        "fps": fps,
        "aspect_ratio": f"{width}:{height}" if height > 0 else "unknown",
        "is_vertical": height > width,
        "video_codec": video_stream.get("codec_name") if video_stream else None,
        "audio_codec": audio_stream.get("codec_name") if audio_stream else None,
        "has_audio": audio_stream is not None,
        "audio_sample_rate": int(audio_stream.get("sample_rate", 0)) if audio_stream else 0
    }


def extract_audio(video_path: str, output_wav_path: Optional[str] = None, sample_rate: int = 16000) -> str:
    """
    Extract a normalized 16kHz mono 16-bit PCM WAV from a video, optimized for Whisper speech recognition.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    if output_wav_path is None:
        base, _ = os.path.splitext(video_path)
        output_wav_path = f"{base}_audio.wav"

    os.makedirs(os.path.dirname(os.path.abspath(output_wav_path)), exist_ok=True)

    cmd = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", str(sample_rate),
        "-ac", "1",
        output_wav_path
    ]

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg audio extraction failed: {result.stderr}")

    return os.path.abspath(output_wav_path)


def extract_frame(video_path: str, timestamp_sec: float = 1.0, output_img_path: Optional[str] = None) -> str:
    """
    Extract a single representative frame from video for preview/thumbnail.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    if output_img_path is None:
        base, _ = os.path.splitext(video_path)
        output_img_path = f"{base}_thumb.jpg"

    os.makedirs(os.path.dirname(os.path.abspath(output_img_path)), exist_ok=True)

    cmd = [
        "ffmpeg",
        "-y",
        "-ss", str(max(0.0, timestamp_sec)),
        "-i", video_path,
        "-vframes", "1",
        "-q:v", "2",
        output_img_path
    ]

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg thumbnail extraction failed: {result.stderr}")

    return os.path.abspath(output_img_path)
