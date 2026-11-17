"""
copyright_shield.py - Anti-Copyright Strike & Fair Use Protection Engine.
Disrupts automated acoustic & perceptual video fingerprinting algorithms (Content ID).
"""

from typing import Any, Dict, List, Optional, Tuple


class CopyrightShield:
    PRESETS = {
        "off": {
            "name": "Off",
            "description": "No transformation applied. Original audio and video untouched.",
            "pitch_shift": 1.0,
            "tempo_shift": 1.0,
            "eq_adjust": False,
            "color_grade": False,
            "micro_zoom": False,
            "mirror_flip": False,
            "strip_metadata": True,
            "ambient_bed": False
        },
        "subtle": {
            "name": "Subtle Protection (Recommended)",
            "description": "Light pitch shift (+1.5%), tempo (1.02x), gentle color pop, cleans metadata.",
            "pitch_shift": 1.015,
            "tempo_shift": 1.02,
            "eq_adjust": True,
            "color_grade": True,
            "micro_zoom": False,
            "mirror_flip": False,
            "strip_metadata": True,
            "ambient_bed": False
        },
        "balanced": {
            "name": "Balanced Shield",
            "description": "Medium pitch shift (+2.5%), tempo (1.035x), 2.5% micro-zoom, saturation boost, EQ contour.",
            "pitch_shift": 1.025,
            "tempo_shift": 1.035,
            "eq_adjust": True,
            "color_grade": True,
            "micro_zoom": True,
            "mirror_flip": False,
            "strip_metadata": True,
            "ambient_bed": False
        },
        "aggressive": {
            "name": "Aggressive Bypass",
            "description": "Strong pitch (-2.5%), tempo (1.05x), micro-zoom (4%), color grading, and ambient music ducking.",
            "pitch_shift": 0.975,
            "tempo_shift": 1.05,
            "eq_adjust": True,
            "color_grade": True,
            "micro_zoom": True,
            "mirror_flip": False,
            "strip_metadata": True,
            "ambient_bed": True
        }
    }

    def __init__(self, preset: str = "subtle", custom_overrides: Optional[Dict[str, Any]] = None):
        self.preset_name = preset.lower() if preset.lower() in self.PRESETS else "subtle"
        self.config = self.PRESETS[self.preset_name].copy()
        if custom_overrides:
            self.config.update(custom_overrides)

    def get_audio_filter_chain(self) -> Optional[str]:
        """
        Build the audio filter string to alter spectral peaks and temporal intervals.
        """
        if self.config.get("pitch_shift", 1.0) == 1.0 and self.config.get("tempo_shift", 1.0) == 1.0 and not self.config.get("eq_adjust"):
            return None

        filters = []
        p = self.config.get("pitch_shift", 1.0)
        t = self.config.get("tempo_shift", 1.0)

        # High-fidelity rubberband pitch & tempo modulation
        if p != 1.0 or t != 1.0:
            filters.append(f"rubberband=pitch={p:.4f}:tempo={t:.4f}")

        # Parametric EQ reshaping (subtle low boost & high-mid control)
        if self.config.get("eq_adjust"):
            filters.append("equalizer=f=120:width_type=o:width=2:g=1.5")
            filters.append("equalizer=f=3800:width_type=o:width=1.5:g=-1.0")

        return ",".join(filters) if filters else None

    def get_video_filter_chain(self) -> Optional[str]:
        """
        Build additional video filters for color grading, micro-zoom, and flip.
        """
        filters = []

        if self.config.get("color_grade"):
            # Subtle color grading to alter perceptual frame hashes
            filters.append("eq=contrast=1.04:brightness=0.01:saturation=1.06:gamma=0.98")

        if self.config.get("micro_zoom"):
            # Subtle 2.5% scale zoom to crop out edge pixels
            filters.append("scale=1.025*iw:1.025*ih,crop=1080:1920:(in_w-1080)/2:(in_h-1920)/2")

        if self.config.get("mirror_flip"):
            filters.append("hflip")

        return ",".join(filters) if filters else None

    def get_ffmpeg_metadata_args(self) -> List[str]:
        """
        Return FFmpeg CLI arguments to wipe all original container and stream metadata.
        """
        if self.config.get("strip_metadata", True):
            return [
                "-map_metadata", "-1",
                "-map_metadata:s:v", "-1",
                "-map_metadata:s:a", "-1"
            ]
        return []
