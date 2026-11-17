"""
retention_scorer.py - Algorithmic high-retention moment detector for viral short-form clips.
Analyzes transcript hooks, speech cadence, silence, and audio RMS energy dynamics.
"""

import math
import os
import re
import wave
from typing import Any, Dict, List, Optional
import numpy as np


class RetentionScorer:
    def __init__(
        self,
        min_clip_duration: float = 15.0,
        max_clip_duration: float = 60.0,
        target_clip_duration: float = 30.0
    ):
        self.min_clip_duration = min_clip_duration
        self.max_clip_duration = max_clip_duration
        self.target_clip_duration = target_clip_duration

        # High-retention hook patterns for opening lines
        self.hook_patterns = [
            (r"\b(why|how|what if|did you know|can you|is it possible)\b", 25.0),
            (r"\b(secret|truth|nobody talks about|mistake|stop doing|warning)\b", 25.0),
            (r"\b(insane|crazy|shocking|unbelievable|huge|massive|worst|best)\b", 20.0),
            (r"\b(never|always|actually|literally|the real reason)\b", 15.0),
            (r"\?$", 15.0),  # Questions
            (r"!$", 10.0),  # Exclamations
        ]

    def _compute_audio_energy(self, wav_path: str, start_sec: float, end_sec: float) -> float:
        """
        Compute normalized RMS energy score for an audio segment.
        """
        if not os.path.exists(wav_path):
            return 50.0

        try:
            with wave.open(wav_path, "rb") as wf:
                sample_rate = wf.getframerate()
                n_channels = wf.getnchannels()
                sampwidth = wf.getsampwidth()
                total_frames = wf.getnframes()

                start_frame = int(start_sec * sample_rate)
                end_frame = int(end_sec * sample_rate)

                if start_frame >= total_frames:
                    return 50.0

                end_frame = min(end_frame, total_frames)
                num_frames = end_frame - start_frame
                if num_frames <= 0:
                    return 50.0

                wf.setpos(start_frame)
                raw_bytes = wf.readframes(num_frames)

                if sampwidth == 2:
                    dtype = np.int16
                elif sampwidth == 4:
                    dtype = np.int32
                else:
                    dtype = np.uint8

                samples = np.frombuffer(raw_bytes, dtype=dtype)
                if n_channels > 1:
                    samples = samples[::n_channels]

                if len(samples) == 0:
                    return 50.0

                # Compute RMS
                rms = np.sqrt(np.mean(samples.astype(np.float64) ** 2))
                # Normalize to 0-100 scale (typical 16-bit max is 32767)
                norm_energy = min(100.0, (rms / 8000.0) * 100.0)
                return float(norm_energy)
        except Exception:
            return 50.0

    def _score_hook(self, text: str) -> float:
        """
        Score the opening sentence (first 3-5 seconds) for viral curiosity and attention grabbing.
        """
        text_lower = text.lower()
        score = 20.0  # Baseline
        for pattern, bonus in self.hook_patterns:
            if re.search(pattern, text_lower):
                score += bonus
        return min(100.0, score)

    def _score_pacing(self, words: List[Dict[str, Any]], duration: float) -> float:
        """
        Score pacing based on Words Per Minute (WPM) and pause distribution.
        Ideal short-form WPM: 140 - 180.
        """
        if duration <= 0:
            return 0.0

        wpm = (len(words) / duration) * 60.0

        # WPM scoring curve
        if 130 <= wpm <= 190:
            pacing_score = 95.0
        elif 100 <= wpm < 130 or 190 < wpm <= 220:
            pacing_score = 75.0
        elif 70 <= wpm < 100:
            pacing_score = 50.0
        else:
            pacing_score = 30.0

        # Penalize excessive dead air (pauses > 1.2s between words)
        pause_penalty = 0.0
        for i in range(len(words) - 1):
            gap = words[i + 1]["start"] - words[i]["end"]
            if gap > 1.2:
                pause_penalty += min(15.0, (gap - 1.2) * 10.0)

        final_pacing = max(10.0, pacing_score - pause_penalty)
        return float(final_pacing)

    def extract_clips(
        self,
        transcript: Dict[str, Any],
        audio_path: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Extract top-k candidate viral clips from the transcript and audio metrics.
        """
        segments = transcript.get("segments", [])
        if not segments:
            # Fallback if no segments: create a single clip from available duration
            duration = transcript.get("duration", 30.0)
            return [{
                "rank": 1,
                "start": 0.0,
                "end": min(duration, self.target_clip_duration),
                "duration": min(duration, self.target_clip_duration),
                "retention_score": 75.0,
                "hook_score": 70.0,
                "pacing_score": 75.0,
                "energy_score": 70.0,
                "hook_headline": "🔥 WATCH THIS HIGHLIGHT",
                "text": transcript.get("full_text", "")[:200],
                "words": transcript.get("words", [])
            }]

        candidate_clips = []
        n_segs = len(segments)

        # Sliding window approach over segments to build clips of 15s - 60s
        for i in range(n_segs):
            start_seg = segments[i]
            start_time = start_seg["start"]

            current_text_parts = []
            current_words = []

            for j in range(i, n_segs):
                seg = segments[j]
                end_time = seg["end"]
                duration = end_time - start_time

                current_text_parts.append(seg["text"])
                current_words.extend(seg.get("words", []))

                if duration >= self.min_clip_duration:
                    if duration <= self.max_clip_duration:
                        # Candidate found: calculate scores
                        first_line = start_seg["text"]
                        hook_score = self._score_hook(first_line)
                        pacing_score = self._score_pacing(current_words, duration)

                        # Audio energy
                        energy_score = 50.0
                        if audio_path and os.path.exists(audio_path):
                            energy_score = self._compute_audio_energy(audio_path, start_time, end_time)

                        # Target duration proximity bonus (reward ~30-45s sweet spot)
                        dur_diff = abs(duration - self.target_clip_duration)
                        duration_bonus = max(0.0, 15.0 - (dur_diff * 0.5))

                        # Overall retention composite score
                        composite_score = (
                            (hook_score * 0.35) +
                            (pacing_score * 0.30) +
                            (energy_score * 0.20) +
                            duration_bonus
                        )
                        composite_score = round(min(99.0, max(30.0, composite_score)), 1)

                        # Generate viral hook headline
                        headline = self._generate_headline(first_line)

                        candidate_clips.append({
                            "start": round(start_time, 2),
                            "end": round(end_time, 2),
                            "duration": round(duration, 2),
                            "retention_score": composite_score,
                            "hook_score": round(hook_score, 1),
                            "pacing_score": round(pacing_score, 1),
                            "energy_score": round(energy_score, 1),
                            "hook_headline": headline,
                            "text": " ".join(current_text_parts),
                            "words": current_words.copy()
                        })
                    else:
                        break  # Exceeded max duration

        if not candidate_clips:
            # Create at least one fallback window
            dur = min(segments[-1]["end"], self.max_clip_duration)
            all_words = transcript.get("words", [])
            candidate_clips.append({
                "start": 0.0,
                "end": dur,
                "duration": dur,
                "retention_score": 75.0,
                "hook_score": 70.0,
                "pacing_score": 75.0,
                "energy_score": 65.0,
                "hook_headline": "🔥 MUST WATCH MOMENT",
                "text": " ".join(s["text"] for s in segments),
                "words": all_words
            })

        # Sort candidate clips by retention score descending
        candidate_clips.sort(key=lambda c: c["retention_score"], reverse=True)

        # Non-maximum suppression: prevent overlapping clips with >70% time overlap
        selected_clips = []
        for clip in candidate_clips:
            overlap = False
            for sel in selected_clips:
                intersection = max(0.0, min(clip["end"], sel["end"]) - max(clip["start"], sel["start"]))
                union = max(clip["end"], sel["end"]) - min(clip["start"], sel["start"])
                if union > 0 and (intersection / clip["duration"]) > 0.5:
                    overlap = True
                    break
            if not overlap:
                clip["rank"] = len(selected_clips) + 1
                selected_clips.append(clip)
                if len(selected_clips) >= top_k:
                    break

        return selected_clips

    def _generate_headline(self, first_line: str) -> str:
        """
        Create a punchy viral banner headline from the first spoken sentence.
        """
        clean = first_line.strip().strip('"').strip("'")
        if len(clean) > 40:
            words = clean.split()
            clean = " ".join(words[:6]) + "..."
        clean_upper = clean.upper()
        if not clean_upper.endswith("!") and not clean_upper.endswith("?"):
            clean_upper += " 🤯"
        return f"🚨 {clean_upper}"
