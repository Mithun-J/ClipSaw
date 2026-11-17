"""
test_phase4.py - Verification for Phase 4 Anti-Copyright Strike Engine
"""

import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.copyright_shield import CopyrightShield
from backend.video_processor import VideoProcessor
from backend.media_utils import probe_video


def run_verification():
    print("=== Phase 4 Verification Suite ===")

    print("1. Testing CopyrightShield presets...")
    shield_subtle = CopyrightShield(preset="subtle")
    af_subtle = shield_subtle.get_audio_filter_chain()
    vf_subtle = shield_subtle.get_video_filter_chain()
    meta_subtle = shield_subtle.get_ffmpeg_metadata_args()

    print(f"   Subtle Audio Filters: {af_subtle}")
    print(f"   Subtle Video Filters: {vf_subtle}")
    print(f"   Metadata Args: {meta_subtle}")

    assert "rubberband=pitch=1.0150" in af_subtle, "Missing pitch shift in subtle preset"
    assert "tempo=1.0200" in af_subtle, "Missing tempo shift in subtle preset"
    assert "eq=contrast=1.04" in vf_subtle, "Missing color grade in subtle preset"
    assert "-map_metadata" in meta_subtle, "Missing metadata stripping"

    print("2. Testing Balanced and Aggressive presets...")
    shield_balanced = CopyrightShield(preset="balanced")
    vf_balanced = shield_balanced.get_video_filter_chain()
    assert "scale=1.025" in vf_balanced, "Missing micro-zoom in balanced preset"

    shield_aggressive = CopyrightShield(preset="aggressive")
    af_aggressive = shield_aggressive.get_audio_filter_chain()
    assert "pitch=0.9750" in af_aggressive, "Missing downward pitch shift in aggressive preset"

    print("3. Testing VideoProcessor rendering with Balanced Anti-Copyright Shield...")
    source_video = os.path.abspath("storage/temp/synthetic_test.mp4")
    out_protected_clip = os.path.abspath("storage/clips/test_protected_clip.mp4")

    processor = VideoProcessor()
    test_words = [
        {"word": "Protected", "start": 0.0, "end": 0.8},
        {"word": "From", "start": 0.8, "end": 1.4},
        {"word": "Strikes", "start": 1.4, "end": 2.2}
    ]

    result = processor.render_clip(
        source_video_path=source_video,
        start_time=0.0,
        end_time=3.0,
        words=test_words,
        hook_headline="🛡️ ANTI-COPYRIGHT ACTIVE 🛡️",
        reframe_mode="blur_padding",
        protection_preset="balanced",
        output_clip_path=out_protected_clip
    )

    print(f"   Rendered Protected Clip: {result['clip_path']}")
    print(f"   Dimensions: {result['width']}x{result['height']}")
    print(f"   Duration: {result['duration']}s")
    print(f"   Protection Preset: {result['protection_preset']}")

    assert os.path.exists(result["clip_path"]), "Protected clip was not rendered"
    assert result["width"] == 1080, "Expected width 1080"
    assert result["height"] == 1920, "Expected height 1920"

    print("\n✅ PHASE 4 VERIFICATION PASSED: Anti-Copyright Strike Engine fully operational!")


if __name__ == "__main__":
    run_verification()
