"""
reframe.py - 9:16 vertical video reframing engine for YouTube Shorts, Reels, and TikTok.
Supports blur_padding (centered with blurred background), smart_crop, and split_screen layouts.
"""

from typing import Dict, Any, Optional


class VideoReframer:
    def __init__(self, target_width: int = 1080, target_height: int = 1920):
        self.target_width = target_width
        self.target_height = target_height

    def build_filter_graph(
        self,
        mode: str = "blur_padding",
        subtitle_ass_path: Optional[str] = None,
        video_shield_filter: Optional[str] = None
    ) -> str:
        """
        Build an FFmpeg complex filter graph string for the specified reframing mode,
        with optional anti-copyright video filters and subtitle burn-in.
        """
        w = self.target_width
        h = self.target_height

        if mode == "smart_crop":
            base_filter = (
                f"[0:v]scale=-2:{h}:force_original_aspect_ratio=increase,"
                f"crop={w}:{h}:(in_w-{w})/2:0[base]"
            )
            current_label = "[base]"

        elif mode == "split_screen":
            half_h = h // 2
            base_filter = (
                f"[0:v]scale={w}:{half_h}:force_original_aspect_ratio=increase,"
                f"crop={w}:{half_h}[top];"
                f"[0:v]scale={w}:{half_h}:force_original_aspect_ratio=increase,"
                f"crop={w}:{half_h},boxblur=15:4[bot];"
                f"[top][bot]vstack[base]"
            )
            current_label = "[base]"

        else:
            # Default: blur_padding
            base_filter = (
                f"[0:v]scale={w}:{h}:force_original_aspect_ratio=increase,"
                f"crop={w}:{h},boxblur=20:5[bg];"
                f"[0:v]scale={w}:-2:force_original_aspect_ratio=decrease[fg];"
                f"[bg][fg]overlay=(W-w)/2:(H-h)/2[base]"
            )
            current_label = "[base]"

        chain_parts = [base_filter]

        # Apply video anti-copyright transformations (color grading, micro-zoom, etc.)
        if video_shield_filter:
            chain_parts.append(f"{current_label}{video_shield_filter}[shielded]")
            current_label = "[shielded]"

        # Burn in subtitles
        if subtitle_ass_path:
            clean_sub_path = subtitle_ass_path.replace("\\", "/").replace(":", "\\:")
            chain_parts.append(f"{current_label}subtitles='{clean_sub_path}'[v]")
        else:
            chain_parts.append(f"{current_label}null[v]")

        return ";".join(chain_parts)
