"""
test_phase1.py - Verification for Phase 1 Ingestion and Media Utilities
"""

import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.ingestion import IngestionService
from backend.media_utils import probe_video, extract_audio, extract_frame


def create_synthetic_test_video(path: str, duration: int = 4) -> str:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    # Generate 1280x720 video with a sine wave audio tone
    cmd = [
        "ffmpeg",
        "-y",
        "-f", "lavfi",
        "-i", f"testsrc=duration={duration}:size=1280x720:rate=30",
        "-f", "lavfi",
        "-i", f"sine=frequency=1000:duration={duration}",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "128k",
        path
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return os.path.abspath(path)


def run_verification():
    print("=== Phase 1 Verification Suite ===")
    test_video = os.path.abspath("storage/temp/synthetic_test.mp4")
    print(f"1. Generating synthetic test video: {test_video}")
    create_synthetic_test_video(test_video, duration=4)
    assert os.path.exists(test_video), "Synthetic video creation failed!"

    print("2. Testing media_utils.probe_video...")
    meta = probe_video(test_video)
    print(f"   Resolution: {meta['width']}x{meta['height']}, FPS: {meta['fps']}, Duration: {meta['duration']}s")
    assert meta["width"] == 1280, f"Expected width 1280, got {meta['width']}"
    assert meta["height"] == 720, f"Expected height 720, got {meta['height']}"
    assert meta["has_audio"] is True, "Audio stream not detected"

    print("3. Testing IngestionService...")
    svc = IngestionService(storage_dir="storage")
    item = svc.ingest_local_file(test_video, custom_title="Sample_Viral_Test")
    print(f"   Ingested ID: {item['id']}")
    print(f"   Video Path: {item['video_path']}")
    print(f"   Audio Path: {item['audio_path']}")
    print(f"   Thumb Path: {item['thumb_path']}")

    assert os.path.exists(item["video_path"]), "Ingested video does not exist"
    assert os.path.exists(item["audio_path"]), "Extracted audio does not exist"
    assert os.path.exists(item["thumb_path"]), "Extracted thumbnail does not exist"

    print("4. Testing extracted audio specifications...")
    audio_meta = probe_video(item["audio_path"])
    print(f"   Audio Sample Rate: {audio_meta['audio_sample_rate']}Hz, Codec: {audio_meta['audio_codec']}")
    assert audio_meta["audio_sample_rate"] == 16000, "Audio sample rate must be 16000Hz"

    print("\n✅ PHASE 1 VERIFICATION PASSED: Ingestion & Media Utilities fully operational!")


if __name__ == "__main__":
    run_verification()
