"""
retention_scorer.py - Algorithmic high-retention moment detector for viral short-form clips.
Analyzes transcript hooks, speech cadence, silence, and audio RMS energy dynamics.
Generates dynamic, topic-tailored clickbait titles for each clip.
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
                # Normalize to 0-100 scale
                norm_energy = min(100.0, (rms / 8000.0) * 100.0)
                return float(norm_energy)
        except Exception:
            return 50.0

    def _score_hook(self, text: str) -> float:
        """
        Score the opening sentence (first 3-5 seconds) for viral curiosity and attention grabbing.
        """
        text_lower = text.lower()
        score = 20.0
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
        top_k: int = 8
    ) -> List[Dict[str, Any]]:
        """
        Extract top-k candidate viral clips with unique IDs, topic-tailored clickbait titles,
        and full metadata.
        """
        segments = transcript.get("segments", [])
        if not segments:
            duration = transcript.get("duration", 30.0)
            return [{
                "id": "clip_1_0",
                "rank": 1,
                "start": 0.0,
                "end": min(duration, self.target_clip_duration),
                "duration": min(duration, self.target_clip_duration),
                "retention_score": 75.0,
                "hook_score": 70.0,
                "pacing_score": 75.0,
                "energy_score": 70.0,
                "hook_headline": "🔥 MUST WATCH HIGHLIGHT 🤯",
                "text": transcript.get("full_text", "")[:200],
                "words": transcript.get("words", [])
            }]

        candidate_clips = []
        n_segs = len(segments)

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
                        first_line = start_seg["text"]
                        full_clip_text = " ".join(current_text_parts)
                        hook_score = self._score_hook(first_line)
                        pacing_score = self._score_pacing(current_words, duration)

                        # Audio energy
                        energy_score = 50.0
                        if audio_path and os.path.exists(audio_path):
                            energy_score = self._compute_audio_energy(audio_path, start_time, end_time)

                        # Duration sweet spot bonus (~25s to 45s)
                        dur_diff = abs(duration - self.target_clip_duration)
                        duration_bonus = max(0.0, 15.0 - (dur_diff * 0.5))

                        composite_score = (
                            (hook_score * 0.35) +
                            (pacing_score * 0.30) +
                            (energy_score * 0.20) +
                            duration_bonus
                        )
                        composite_score = round(min(99.0, max(30.0, composite_score)), 1)

                        # Dynamic, topic-tailored clickbait headline
                        headline = self._generate_headline(full_clip_text, first_line)

                        candidate_clips.append({
                            "start": round(start_time, 2),
                            "end": round(end_time, 2),
                            "duration": round(duration, 2),
                            "retention_score": composite_score,
                            "hook_score": round(hook_score, 1),
                            "pacing_score": round(pacing_score, 1),
                            "energy_score": round(energy_score, 1),
                            "hook_headline": headline,
                            "text": full_clip_text,
                            "words": current_words.copy()
                        })
                    else:
                        break

        if not candidate_clips:
            dur = min(segments[-1]["end"], self.max_clip_duration)
            all_words = transcript.get("words", [])
            clip_text = " ".join(s["text"] for s in segments)
            candidate_clips.append({
                "start": 0.0,
                "end": dur,
                "duration": dur,
                "retention_score": 75.0,
                "hook_score": 70.0,
                "pacing_score": 75.0,
                "energy_score": 65.0,
                "hook_headline": self._generate_headline(clip_text, segments[0]["text"]),
                "text": clip_text,
                "words": all_words
            })

        # Sort candidate clips by retention score descending
        candidate_clips.sort(key=lambda c: c["retention_score"], reverse=True)

        # Non-maximum suppression: prevent heavy overlapping clips (>50% time overlap)
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
                idx = len(selected_clips) + 1
                clip["id"] = f"clip_{idx}_{int(clip['start'])}"
                clip["rank"] = idx
                selected_clips.append(clip)
                if len(selected_clips) >= top_k:
                    break

        return selected_clips

    def _generate_headline(self, full_text: str, first_line: str) -> str:
        """
        Create a high-CTR, punchy clickbait banner headline matching the clip topic and mood.
        """
        text_lower = full_text.lower()
        seed = abs(hash(full_text))

        # 1. Mistakes, warnings & warnings
        if re.search(r"\b(mistake|wrong|fail|error|destroy|ruin|stop|never|avoid|warning)\b", text_lower):
            templates = [
                "🚨 STOP MAKING THIS HUGE MISTAKE 🛑",
                "⚠️ THE FATAL ERROR YOU MUST AVOID 💥",
                "🛑 NEVER DO THIS AGAIN 😱",
                "⚠️ WHY 99% OF PEOPLE GET THIS WRONG ❌",
                "🚨 WATCH THIS BEFORE YOU MAKE A MISTAKE 🛑"
            ]
            return templates[seed % len(templates)]

        # 2. Secrets, truth & untold stories
        elif re.search(r"\b(secret|nobody|truth|hidden|lie|actually|reveal|exposed)\b", text_lower):
            templates = [
                "🤫 THE UNTOLD TRUTH NOBODY TALKS ABOUT 💥",
                "🔓 THE SECRET THEY DON'T WANT YOU TO KNOW 😱",
                "🚨 THE BRUTAL REALITY EXPOSED 🤯",
                "🤫 WHAT HAPPENS BEHIND CLOSED DOORS ⚠️",
                "🔥 THIS IS THE UNFILTERED TRUTH 💥"
            ]
            return templates[seed % len(templates)]

        # 3. High action, race, fast moments
        elif re.search(r"\b(race|kart|speed|fast|win|crazy|insane|wild|catch|run|danger|epic)\b", text_lower):
            templates = [
                "🏁 THE CRAZIEST MOMENT EVER RECORDED 🏎️",
                "🤯 WAIT TILL THE VERY END 😱",
                "🔥 DO NOT BLINK OR YOU'LL MISS IT ⚡",
                "🚨 YOU WON'T BELIEVE WHAT HAPPENED 🤯",
                "😱 NOBODY EXPECTED THIS FINISH 🏁"
            ]
            return templates[seed % len(templates)]

        # 4. How-to, routines, tips & hacks
        elif re.search(r"\b(how to|simple|trick|hack|routine|easy|tip|advice|cadence|habit)\b", text_lower):
            templates = [
                "💡 THIS ONE SIMPLE TRICK CHANGED EVERYTHING 📈",
                "🚀 THE ULTIMATE SHORTCUT YOU NEED TODAY 🎯",
                "⚡ DO THIS SIMPLE ROUTINE EVERY DAY 🔥",
                "💡 TRY THIS HACK AND THANK ME LATER 🤯",
                "📈 THE EXACT METHOD THAT DOUBLED RESULTS 🚀"
            ]
            return templates[seed % len(templates)]

        # 5. Money, business & growth
        elif re.search(r"\b(money|rich|million|wealth|business|earn|scale|income|dollar)\b", text_lower):
            templates = [
                "💰 THE 1% WEALTH RULE NO ONE SHARES 📈",
                "💵 HOW TO SCALE FASTER THAN EVER 🚀",
                "💸 STOP LOSING MONEY ON THIS 🛑",
                "📈 THE MILLION-DOLLAR LESSON 💥"
            ]
            return templates[seed % len(templates)]

        # 6. Questions
        elif re.search(r"\b(why|what if|is it|can you|did you)\b", text_lower) or "?" in first_line:
            clean_q = first_line.split("?")[0].strip()
            words = clean_q.split()
            if 3 <= len(words) <= 7:
                return f"❓ {clean_q.upper()}? 🤯"
            else:
                templates = [
                    "❓ WHY DOES NOBODY UNDERSTAND THIS? 🤯",
                    "😱 THE QUESTION EVERYONE IS ASKING ❓",
                    "🤯 COULD THIS REALLY BE POSSIBLE? 💥"
                ]
                return templates[seed % len(templates)]

        # Default fallback extracting first punchy sentence
        clean = first_line.strip().split(".")[0].strip()
        words = clean.split()
        if len(words) > 7:
            clean = " ".join(words[:6]) + "..."
        clean_upper = clean.upper()
        if not clean_upper.endswith("!") and not clean_upper.endswith("?"):
            clean_upper += " 🤯"
        return f"🚨 {clean_upper}"
