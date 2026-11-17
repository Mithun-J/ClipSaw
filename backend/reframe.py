"""
reframe.py - 9:16 vertical video reframing engine for YouTube Shorts, Reels, and TikTok.
Supports blur_padding (centered with blurred background), smart_crop, and split_screen layouts.
"""

from typing import Dict, Any, Optional


class VideoReframer:
    def __init__(self, target_width: int = 1080, target_height: int = 1920):
        self.target_width = target_width
        self.target_height = target_height

    def build_filter_graph(self, mode: str = "blur_padding", subtitle_ass_path: Optional[str] = None) -> str:
        """
        Build an FFmpeg complex filter graph string for the specified reframing mode,
        with optional subtitle burn-in appended.
        """
        w = self.target_width
        h = self.target_height

        if mode == "smart_crop":
            # Scale video to fit height then crop center width
            base_filter = (
                f"[0:v]scale=-2:{h}:force_original_aspect_ratio=increase,"
                f"crop={w}:{h}:(in_w-{w})/2:0[base]"
            )
            out_label = "[base]"

        elif mode == "split_screen":
            half_h = h // 2
            base_filter = (
                f"[0:v]scale={w}:{half_h}:force_original_aspect_ratio=increase,"
                f"crop={w}:{half_h}[top];"
                f"[0:v]scale={w}:{half_h}:force_original_aspect_ratio=increase,"
                f"crop={w}:{half_h},boxblur=15:4[bot];"
                f"[top][bot]vstack[base]"
            )
            out_label = "[base]"

        else:
            # Default: blur_padding (Universal gold-standard for Shorts/Reels)
            base_filter = (
                f"[0:v]scale={w}:{h}:force_original_aspect_ratio=increase,"
                f"crop={w}:{h},boxblur=20:5[bg];"
                f"[0:v]scale={w}:-2:force_original_aspect_ratio=decrease[fg];"
                f"[bg][fg]overlay=(W-w)/2:(H-h)/2[base]"
            )
            out_label = "[base]"

        if subtitle_ass_path:
            # Escape path for FFmpeg subtitles filter on Windows
            clean_sub_path = subtitle_ass_path.replace("\\", "/").replace(":", "\\:")
            full_filter = f"{base_filter};{out_label}subtitles='{clean_sub_path}'[v]"
            return full_filter
        else:
            full_filter = f"{base_filter};{out_label}null[v]"
            return full_filter
