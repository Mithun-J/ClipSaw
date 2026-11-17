"""
video_processor.py - End-to-end rendering pipeline that extracts slices,
applies 9:16 vertical reframing, burns dynamic karaoke subtitles,
and applies multi-layer anti-copyright protection.
"""

import os
import subprocess
import uuid
from typing import Any, Dict, List, Optional
from backend.reframe import VideoReframer
from backend.subtitle_generator import SubtitleGenerator
from backend.copyright_shield import CopyrightShield
from backend.media_utils import probe_video


class VideoProcessor:
    def __init__(self, temp_dir: str = "storage/temp", clips_dir: str = "storage/clips"):
        self.temp_dir = os.path.abspath(temp_dir)
        self.clips_dir = os.path.abspath(clips_dir)
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.clips_dir, exist_ok=True)

        self.subtitle_generator = SubtitleGenerator()
        self.reframer = VideoReframer(target_width=1080, target_height=1920)

    def render_clip(
        self,
        source_video_path: str,
        start_time: float,
        end_time: float,
        words: Optional[List[Dict[str, Any]]] = None,
        hook_headline: Optional[str] = None,
        reframe_mode: str = "blur_padding",
        protection_preset: str = "subtle",
        captions_style: str = "bold",
        custom_protection: Optional[Dict[str, Any]] = None,
        output_clip_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Slice video segment, reframe to 9:16 vertical, burn in karaoke subtitles,
        and apply transformative anti-copyright protection.
        """
        if not os.path.exists(source_video_path):
            raise FileNotFoundError(f"Source video not found: {source_video_path}")

        duration = max(1.0, end_time - start_time)
        clip_id = str(uuid.uuid4())[:8]

        if output_clip_path is None:
            output_clip_path = os.path.join(self.clips_dir, f"clip_{clip_id}.mp4")

        os.makedirs(os.path.dirname(os.path.abspath(output_clip_path)), exist_ok=True)

        # 1. Initialize Anti-Copyright Shield
        shield = CopyrightShield(preset=protection_preset, custom_overrides=custom_protection)
        video_shield_filter = shield.get_video_filter_chain()
        audio_shield_filter = shield.get_audio_filter_chain()
        metadata_args = shield.get_ffmpeg_metadata_args()

        # 2. Generate subtitle .ass file if words or headline provided
        subtitle_ass_path = None
        if words or hook_headline:
            subtitle_ass_path = os.path.join(self.temp_dir, f"sub_{clip_id}.ass")
            self.subtitle_generator.generate_ass(
                words=words or [],
                output_ass_path=subtitle_ass_path,
                time_offset=start_time,
                hook_headline=hook_headline,
                duration=duration,
                captions_style=captions_style
            )

        # 3. Build FFmpeg filter graph
        filter_graph = self.reframer.build_filter_graph(
            mode=reframe_mode,
            subtitle_ass_path=subtitle_ass_path,
            video_shield_filter=video_shield_filter
        )

        # 4. Assemble FFmpeg slicing, filtering, and rendering command
        cmd = [
            "ffmpeg",
            "-y",
            "-ss", f"{start_time:.3f}",
            "-to", f"{end_time:.3f}",
            "-i", source_video_path,
            "-filter_complex", filter_graph,
            "-map", "[v]"
        ]

        if audio_shield_filter:
            cmd.extend(["-af", audio_shield_filter])
        else:
            cmd.extend(["-map", "0:a?"])

        # Metadata stripping arguments
        cmd.extend(metadata_args)

        # Video/Audio encoding options
        cmd.extend([
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "22",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-movflags", "+faststart",
            output_clip_path
        ])

        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg render clip failed: {result.stderr}")

        meta = probe_video(output_clip_path)

        return {
            "clip_id": clip_id,
            "clip_path": os.path.abspath(output_clip_path),
            "start_time": start_time,
            "end_time": end_time,
            "duration": meta["duration"],
            "width": meta["width"],
            "height": meta["height"],
            "is_vertical": meta["is_vertical"],
            "protection_preset": protection_preset,
            "subtitle_path": subtitle_ass_path
        }
