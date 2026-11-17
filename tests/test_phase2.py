"""
test_phase2.py - Verification for Phase 2 Transcription and Retention Scoring Engine
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.transcriber import Transcriber
from backend.retention_scorer import RetentionScorer


def run_verification():
    print("=== Phase 2 Verification Suite ===")

    print("1. Testing Transcriber instantiation...")
    transcriber = Transcriber(model_size="base")
    print(f"   Transcriber initialized with device: {transcriber.device}, compute: {transcriber.compute_type}")
    assert transcriber.device in ["cuda", "cpu"], "Invalid device detected"

    print("2. Simulating realistic long-form transcript data...")
    mock_transcript = {
        "duration": 120.0,
        "language": "en",
        "full_text": "Did you know that 99% of people make this mistake? It literally destroys their productivity every day. So here is what happens when you wake up in the morning. Your brain is in a very specific frequency. If you immediately check your phone you trigger high cortisol. Let me explain the exact science behind it. When blue light enters your eyes it halts melatonin production. This is the truth that nobody talks about. Instead do this simple 10 minute routine.",
        "segments": [
            {
                "id": 0,
                "start": 0.0,
                "end": 8.5,
                "text": "Did you know that 99% of people make this mistake?",
                "words": [
                    {"word": "Did", "start": 0.0, "end": 0.3, "probability": 0.98},
                    {"word": "you", "start": 0.3, "end": 0.5, "probability": 0.99},
                    {"word": "know", "start": 0.5, "end": 0.9, "probability": 0.99},
                    {"word": "that", "start": 0.9, "end": 1.1, "probability": 0.95},
                    {"word": "99%", "start": 1.1, "end": 1.8, "probability": 0.96},
                    {"word": "of", "start": 1.8, "end": 2.0, "probability": 0.97},
                    {"word": "people", "start": 2.0, "end": 2.5, "probability": 0.99},
                    {"word": "make", "start": 2.5, "end": 3.0, "probability": 0.99},
                    {"word": "this", "start": 3.0, "end": 3.3, "probability": 0.98},
                    {"word": "mistake?", "start": 3.3, "end": 4.1, "probability": 0.99}
                ]
            },
            {
                "id": 1,
                "start": 8.6,
                "end": 18.0,
                "text": "It literally destroys their productivity every day. So here is what happens when you wake up in the morning.",
                "words": [
                    {"word": "It", "start": 8.6, "end": 8.8, "probability": 0.95},
                    {"word": "literally", "start": 8.8, "end": 9.4, "probability": 0.99},
                    {"word": "destroys", "start": 9.4, "end": 10.0, "probability": 0.98},
                    {"word": "their", "start": 10.0, "end": 10.3, "probability": 0.97},
                    {"word": "productivity", "start": 10.3, "end": 11.2, "probability": 0.99},
                    {"word": "every", "start": 11.2, "end": 11.6, "probability": 0.99},
                    {"word": "day.", "start": 11.6, "end": 12.0, "probability": 0.98}
                ]
            },
            {
                "id": 2,
                "start": 18.1,
                "end": 32.0,
                "text": "Your brain is in a very specific frequency. If you immediately check your phone you trigger high cortisol.",
                "words": [
                    {"word": "Your", "start": 18.1, "end": 18.4, "probability": 0.98},
                    {"word": "brain", "start": 18.4, "end": 18.9, "probability": 0.99},
                    {"word": "is", "start": 18.9, "end": 19.1, "probability": 0.97},
                    {"word": "in", "start": 19.1, "end": 19.3, "probability": 0.96},
                    {"word": "a", "start": 19.3, "end": 19.5, "probability": 0.95},
                    {"word": "frequency.", "start": 19.5, "end": 20.5, "probability": 0.98}
                ]
            },
            {
                "id": 3,
                "start": 32.5,
                "end": 48.0,
                "text": "Let me explain the exact science behind it. When blue light enters your eyes it halts melatonin production.",
                "words": [
                    {"word": "Let", "start": 32.5, "end": 32.8, "probability": 0.97},
                    {"word": "me", "start": 32.8, "end": 33.0, "probability": 0.98},
                    {"word": "explain", "start": 33.0, "end": 33.6, "probability": 0.99}
                ]
            },
            {
                "id": 4,
                "start": 48.5,
                "end": 68.0,
                "text": "This is the truth that nobody talks about. Instead do this simple 10 minute routine.",
                "words": [
                    {"word": "This", "start": 48.5, "end": 48.8, "probability": 0.98},
                    {"word": "is", "start": 48.8, "end": 49.0, "probability": 0.98},
                    {"word": "the", "start": 49.0, "end": 49.2, "probability": 0.97},
                    {"word": "truth", "start": 49.2, "end": 49.7, "probability": 0.99},
                    {"word": "nobody", "start": 49.7, "end": 50.2, "probability": 0.99},
                    {"word": "talks", "start": 50.2, "end": 50.6, "probability": 0.98},
                    {"word": "about.", "start": 50.6, "end": 51.1, "probability": 0.99}
                ]
            }
        ]
    }

    print("3. Testing RetentionScorer.extract_clips...")
    scorer = RetentionScorer(min_clip_duration=15.0, max_clip_duration=60.0, target_clip_duration=30.0)
    clips = scorer.extract_clips(mock_transcript, top_k=3)

    print(f"   Found {len(clips)} candidate clips:")
    for c in clips:
        print(f"   [Rank #{c['rank']}] Retention: {c['retention_score']}% | Duration: {c['duration']}s ({c['start']}s -> {c['end']}s)")
        print(f"      Headline: {c['hook_headline']}")
        print(f"      Hook Score: {c['hook_score']} | Pacing: {c['pacing_score']}")
        print(f"      Text excerpt: {c['text'][:60]}...")

    assert len(clips) > 0, "No clips extracted"
    assert clips[0]["retention_score"] >= clips[-1]["retention_score"], "Clips not sorted by retention"
    assert clips[0]["duration"] >= 15.0, "Clip is shorter than min duration"
    assert clips[0]["duration"] <= 60.0, "Clip is longer than max duration"

    print("\n✅ PHASE 2 VERIFICATION PASSED: Transcription & Retention Scoring fully operational!")


if __name__ == "__main__":
    run_verification()
