"""
test_phase5.py - End-to-end verification for Phase 5 Web Studio API
"""

import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import (
    app,
    health_check,
    list_clips,
    render_clip,
    ingestion_service,
    MEDIA_REGISTRY,
    RenderClipRequest
)


def ensure_synthetic_video(path: str) -> str:
    if os.path.exists(path):
        return path
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "testsrc=duration=4:size=1280x720:rate=30",
        "-f", "lavfi", "-i", "sine=frequency=1000:duration=4",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        path
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return path


def run_verification():
    print("=== Phase 5 Verification Suite ===")

    print("1. Testing GET /api/health handler...")
    health = health_check()
    print(f"   Health check: {health}")
    assert health["status"] == "online", "Health check status not online"

    print("2. Verifying frontend/index.html (CLIPSAW)...")
    frontend_path = os.path.abspath("frontend/index.html")
    assert os.path.exists(frontend_path), "frontend/index.html missing"
    with open(frontend_path, "r", encoding="utf-8") as f:
        html = f.read()
    assert "CLIPSAW" in html, "Missing CLIPSAW header title in frontend"
    assert "ANTI-COPYRIGHT" in html, "Missing Anti-Copyright badge in frontend"
    assert "9:16 Shorts" in html, "Missing 9:16 layout section in frontend"
    print("   Frontend UI validated.")

    print("3. Ingesting synthetic test video into MEDIA_REGISTRY...")
    test_video = os.path.abspath("storage/temp/synthetic_test.mp4")
    ensure_synthetic_video(test_video)
    assert os.path.exists(test_video), "Synthetic test video missing"
    media_item = ingestion_service.ingest_local_file(test_video, custom_title="E2E_Test_Video")
    MEDIA_REGISTRY[media_item["id"]] = media_item
    print(f"   Registered media ID: {media_item['id']}, Title: {media_item['title']}")

    print("4. Testing POST /api/render handler with Anti-Copyright Shield...")
    req = RenderClipRequest(
        media_id=media_item["id"],
        start_time=0.5,
        end_time=3.5,
        words=[
            {"word": "VIRAL", "start": 0.5, "end": 1.2},
            {"word": "REEL", "start": 1.2, "end": 2.0},
            {"word": "STUDIO", "start": 2.0, "end": 3.0}
        ],
        hook_headline="🔥 END TO END VERIFICATION 🚀",
        reframe_mode="blur_padding",
        protection_preset="subtle"
    )

    result = render_clip(req)
    print(f"   Rendered Clip Result: {result}")
    assert result["success"] is True, "Clip rendering did not return success"
    assert result["resolution"] == "1080x1920", f"Expected 1080x1920, got {result['resolution']}"
    assert result["protection_preset"] == "subtle", "Protection preset mismatch"

    print("5. Testing GET /api/clips handler...")
    clips_res = list_clips()
    print(f"   Total Rendered Clips in Storage: {len(clips_res['clips'])}")
    assert len(clips_res["clips"]) >= 1, "Expected at least 1 rendered clip"
    latest_clip = clips_res["clips"][0]
    assert latest_clip["is_vertical"] is True, "Latest clip is not marked vertical"

    print("\n✅ PHASE 5 VERIFICATION PASSED: CLIPSAW Web Studio & End-to-End API operational!")


if __name__ == "__main__":
    run_verification()
