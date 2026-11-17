"""
subtitle_generator.py - Generates Advanced SubStation Alpha (.ass) subtitles
with dynamic word-by-word active highlighting (Hormozi / TikTok / MrBeast karaoke style)
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
    # ASS colors use &H00BBGGRR& (Alpha, Blue, Green, Red)
    STYLES = {
        "bold": {
            "name": "Hormozi Gold",
            "active_color": "&H0000E6FF&",   # Electric Neon Yellow / Gold
            "inactive_color": "&H00FFFFFF&", # Clean White
            "font_size": 76,
            "outline": 8,
            "scale": 118
        },
        "neon": {
            "name": "Cyber Cyan",
            "active_color": "&H00FFF600&",   # Vibrant Cyan
            "inactive_color": "&H00FFFFFF&",
            "font_size": 76,
            "outline": 8,
            "scale": 118
        },
        "green": {
            "name": "Viral Emerald",
            "active_color": "&H0033FF55&",   # Bright Neon Green
            "inactive_color": "&H00FFFFFF&",
            "font_size": 76,
            "outline": 8,
            "scale": 118
        },
        "minimal": {
            "name": "Minimal White",
            "active_color": "&H0000FFFF&",
            "inactive_color": "&H00F0F0F0&",
            "font_size": 66,
            "outline": 5,
            "scale": 108
        }
    }

    def __init__(
        self,
        font_name: str = "Arial",
        default_style: str = "bold",
        words_per_line: int = 3
    ):
        self.font_name = font_name
        self.default_style = default_style
        self.words_per_line = words_per_line

    def generate_ass(
        self,
        words: List[Dict[str, Any]],
        output_ass_path: str,
        time_offset: float = 0.0,
        hook_headline: Optional[str] = None,
        duration: Optional[float] = None,
        captions_style: str = "bold"
    ) -> str:
        """
        Generate an eye-catching .ass subtitle file with word-by-word karaoke lighting and hook header.
        - time_offset: subtracted from word start/end to normalize to clip start = 0.0s.
        """
        os.makedirs(os.path.dirname(os.path.abspath(output_ass_path)), exist_ok=True)

        cfg = self.STYLES.get(captions_style.lower(), self.STYLES["bold"])
        active_color = cfg["active_color"]
        inactive_color = cfg["inactive_color"]
        font_size = cfg["font_size"]
        outline_size = cfg["outline"]
        scale_pct = cfg["scale"]

        # Normalize word timestamps relative to clip start
        norm_words = []
        for w in words:
            w_start = max(0.0, w.get("start", 0.0) - time_offset)
            w_end = max(w_start + 0.08, w.get("end", 0.0) - time_offset)
            clean_word = w.get("word", "").strip().upper()
            if clean_word:
                norm_words.append({
                    "word": clean_word,
                    "start": w_start,
                    "end": w_end
                })

        # Group words into short punchy visual chunks (2-3 words each for maximum mobile legibility)
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
            # Dialogue Karaoke Style: centered in lower third (Alignment 2, MarginV 520) with heavy black outline
            f"Style: Karaoke,{self.font_name},{font_size},{inactive_color},&H000000FF&,&H00000000&,&H00000000&,-1,0,0,0,100,100,2,0,1,{outline_size},3,2,60,60,520,1",
            # Hook Banner Style: solid background pill box at top center (Alignment 8, MarginV 260, BorderStyle 3 = Opaque Box)
            f"Style: HookBanner,{self.font_name},52,&H0000FFFF&,&H000000FF&,&H00000000&,&HC0000000&,-1,0,0,0,100,100,1,0,3,10,0,8,40,40,260,1",
            "",
            "[Events]",
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
        ]

        # Top Hook Banner Event (persists for full clip)
        if hook_headline:
            banner_end = format_ass_time(duration if duration else (norm_words[-1]["end"] if norm_words else 15.0))
            clean_headline = hook_headline.strip().upper()
            lines.append(f"Dialogue: 1,0:00:00.00,{banner_end},HookBanner,,0,0,0,,{clean_headline}")

        # Dynamic word-level highlighting events
        for chunk in chunks:
            chunk_end = chunk[-1]["end"]

            for active_idx, active_word in enumerate(chunk):
                w_start = format_ass_time(active_word["start"])
                next_start = chunk[active_idx + 1]["start"] if active_idx + 1 < len(chunk) else chunk_end
                w_end = format_ass_time(max(active_word["end"], next_start))

                # Assemble chunk with current active word enlarged and highlighted in vibrant neon
                chunk_tokens = []
                for idx, w in enumerate(chunk):
                    if idx == active_idx:
                        # Eye-catching neon color + scale up
                        token = f"{{\\c{active_color}\\fscx{scale_pct}\\fscy{scale_pct}}}{w['word']}{{\\rKaraoke}}"
                    else:
                        token = f"{{\\c{inactive_color}}}{w['word']}"
                    chunk_tokens.append(token)

                event_text = " ".join(chunk_tokens)
                lines.append(f"Dialogue: 0,{w_start},{w_end},Karaoke,,0,0,0,,{event_text}")

        with open(output_ass_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

        return os.path.abspath(output_ass_path)
