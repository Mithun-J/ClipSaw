"""
test_phase3.py - Verification for Phase 3 9:16 Vertical Reframing and Subtitles
"""

import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.subtitle_generator import SubtitleGenerator
from backend.reframe import VideoReframer
from backend.video_processor import VideoProcessor
from backend.media_utils import probe_video


def ensure_synthetic_video(path: str) -> str:
    if os.path.exists(path):
        return path
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "testsrc=duration=5:size=1280x720:rate=30",
        "-f", "lavfi", "-i", "sine=frequency=1000:duration=5",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        path
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return path


def run_verification():
    print("=== Phase 3 Verification Suite ===")
    source_video = os.path.abspath("storage/temp/synthetic_test.mp4")
    ensure_synthetic_video(source_video)

    print("1. Testing SubtitleGenerator...")
    sub_gen = SubtitleGenerator()
    test_words = [
        {"word": "Did", "start": 0.0, "end": 0.4},
        {"word": "you", "start": 0.4, "end": 0.7},
        {"word": "know", "start": 0.7, "end": 1.2},
        {"word": "this", "start": 1.2, "end": 1.5},
        {"word": "secret?", "start": 1.5, "end": 2.2}
    ]
    ass_path = os.path.abspath("storage/temp/test_sub.ass")
    sub_gen.generate_ass(
        words=test_words,
        output_ass_path=ass_path,
        time_offset=0.0,
        hook_headline="🚨 WATCH THIS SECRET 🤯",
        duration=3.0
    )
    assert os.path.exists(ass_path), "Subtitle .ass was not created"
    with open(ass_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "PlayResX: 1080" in content, "Missing 1080 resolution in ASS header"
    assert "WATCH THIS SECRET" in content, "Missing hook headline in ASS"
    print("   ASS file generated and verified.")

    print("2. Testing VideoReframer filter graphs...")
    reframer = VideoReframer(1080, 1920)
    fg_blur = reframer.build_filter_graph("blur_padding", ass_path)
    assert "boxblur" in fg_blur, "Missing boxblur in blur_padding filter graph"
    assert "subtitles" in fg_blur, "Missing subtitles filter in filter graph"
    print("   Filter graphs generated successfully.")

    print("3. Testing VideoProcessor render_clip (9:16 vertical render)...")
    processor = VideoProcessor()
    out_clip = os.path.abspath("storage/clips/test_rendered_9_16.mp4")
    result = processor.render_clip(
        source_video_path=source_video,
        start_time=0.5,
        end_time=3.5,
        words=test_words,
        hook_headline="🚨 SECRET VIRAL TRICK 🤯",
        reframe_mode="blur_padding",
        output_clip_path=out_clip
    )

    print(f"   Rendered clip: {result['clip_path']}")
    print(f"   Dimensions: {result['width']}x{result['height']}")
    print(f"   Duration: {result['duration']}s")
    print(f"   Is Vertical: {result['is_vertical']}")

    assert os.path.exists(result["clip_path"]), "Rendered clip file not found"
    assert result["width"] == 1080, f"Expected width 1080, got {result['width']}"
    assert result["height"] == 1920, f"Expected height 1920, got {result['height']}"
    assert result["is_vertical"] is True, "Output video is not vertical (9:16)"

    print("\n✅ PHASE 3 VERIFICATION PASSED: 9:16 Vertical Reframing & Subtitles operational!")


if __name__ == "__main__":
    run_verification()
