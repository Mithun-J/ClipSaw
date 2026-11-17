"""
subtitle_generator.py - Generates Advanced SubStation Alpha (.ass) subtitles
with dynamic word-by-word active highlighting (Hormozi / TikTok karaoke style)
and viral hook headline banner.
"""

import os
from typing import Any, Dict, List, Optional


def format_ass_time(seconds: float) -> str:
    """Format seconds into ASS timestamp format: H:MM:SS.cs (centiseconds)."""
    if seconds < 0:
        seconds = 0.0
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int(round((seconds - int(seconds)) * 100))
    if cs >= 100:
        cs = 99
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


class SubtitleGenerator:
    def __init__(
        self,
        font_name: str = "Arial",
        font_size: int = 68,
        active_color: str = "&H002BFF&",    # Vibrant neon yellow/gold in ASS BGR (&H00BBGGRR&)
        inactive_color: str = "&H00FFFFFF&",  # Pure white
        outline_color: str = "&H00000000&",   # Deep black
        words_per_line: int = 4
    ):
        self.font_name = font_name
        self.font_size = font_size
        self.active_color = active_color
        self.inactive_color = inactive_color
        self.outline_color = outline_color
        self.words_per_line = words_per_line

    def generate_ass(
        self,
        words: List[Dict[str, Any]],
        output_ass_path: str,
        time_offset: float = 0.0,
        hook_headline: Optional[str] = None,
        duration: Optional[float] = None
    ) -> str:
        """
        Generate a .ass subtitle file with word-by-word karaoke lighting and hook header.
        - time_offset: subtracted from word start/end to normalize to clip start = 0.0s.
        """
        os.makedirs(os.path.dirname(os.path.abspath(output_ass_path)), exist_ok=True)

        # Normalize word timestamps relative to clip start
        norm_words = []
        for w in words:
            w_start = max(0.0, w.get("start", 0.0) - time_offset)
            w_end = max(w_start + 0.1, w.get("end", 0.0) - time_offset)
            clean_word = w.get("word", "").strip().upper()
            if clean_word:
                norm_words.append({
                    "word": clean_word,
                    "start": w_start,
                    "end": w_end
                })

        # Group words into short visual chunks (3-5 words each)
        chunks = []
        current_chunk = []
        for w in norm_words:
            current_chunk.append(w)
            if len(current_chunk) >= self.words_per_line:
                chunks.append(current_chunk)
                current_chunk = []
        if current_chunk:
            chunks.append(current_chunk)

        lines = [
            "[Script Info]",
            "ScriptType: v4.00+",
            "PlayResX: 1080",
            "PlayResY: 1920",
            "WrapStyle: 0",
            "ScaledBorderAndShadow: yes",
            "",
            "[V4+ Styles]",
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
            # Dialogue Style: centered lower third (Alignment 2, MarginV 480)
            f"Style: Karaoke,{self.font_name},{self.font_size},{self.inactive_color},&H000000FF&,{self.outline_color},&H90000000&,-1,0,0,0,100,100,2,0,1,6,3,2,60,60,480,1",
            # Hook Banner Style: top center (Alignment 8, MarginV 240)
            f"Style: HookBanner,{self.font_name},52,&H0000FFFF&,&H000000FF&,{self.outline_color},&HB0000000&,-1,0,0,0,100,100,1,0,1,5,3,8,40,40,240,1",
            "",
            "[Events]",
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
        ]

        # Add Hook Banner Event if provided
        if hook_headline:
            banner_end = format_ass_time(duration if duration else (norm_words[-1]["end"] if norm_words else 15.0))
            lines.append(f"Dialogue: 1,0:00:00.00,{banner_end},HookBanner,,0,0,0,,{hook_headline}")

        # Build dynamic word highlighting dialogues for each chunk
        for chunk in chunks:
            chunk_start = chunk[0]["start"]
            chunk_end = chunk[-1]["end"]

            for active_idx, active_word in enumerate(chunk):
                w_start = format_ass_time(active_word["start"])
                # Extend active highlight until the next word starts or chunk ends
                next_start = chunk[active_idx + 1]["start"] if active_idx + 1 < len(chunk) else chunk_end
                w_end = format_ass_time(max(active_word["end"], next_start))

                # Assemble chunk text with active word highlighted
                chunk_tokens = []
                for idx, w in enumerate(chunk):
                    if idx == active_idx:
                        # Highlighted active word: bold yellow + scale up slightly
                        token = f"{{\\c{self.active_color}\\fscx112\\fscy112}}{w['word']}{{\\rKaraoke}}"
                    else:
                        token = f"{{\\c{self.inactive_color}}}{w['word']}"
                    chunk_tokens.append(token)

                event_text = " ".join(chunk_tokens)
                lines.append(f"Dialogue: 0,{w_start},{w_end},Karaoke,,0,0,0,,{event_text}")

        with open(output_ass_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

        return os.path.abspath(output_ass_path)
