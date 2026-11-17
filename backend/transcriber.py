"""
transcriber.py - Local speech transcription using faster-whisper with word-level timestamps.
100% free and open-source, runs on local GPU/CPU.
"""

import os
from typing import Any, Dict, List, Optional
import torch


class Transcriber:
    def __init__(self, model_size: str = "base", device: Optional[str] = None, compute_type: Optional[str] = None):
        """
        Initialize the local Whisper model.
        Available sizes: 'tiny', 'base', 'small', 'medium', 'large-v3'.
        'base' is an optimal tradeoff of speed (realtime on GPU) and accuracy.
        """
        self.model_size = model_size
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        if compute_type is None:
            self.compute_type = "float16" if self.device == "cuda" else "int8"
        else:
            self.compute_type = compute_type

        self._model = None

    def _get_model(self):
        if self._model is None:
            from faster_whisper import WhisperModel
            self._model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
                download_root=os.path.abspath("storage/models")
            )
        return self._model

    def transcribe(self, audio_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Transcribe an audio file (16kHz WAV recommended) and return word-level timestamps.
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        model = self._get_model()

        segments_gen, info = model.transcribe(
            audio_path,
            language=language,
            word_timestamps=True,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500)
        )

        segments_list = []
        full_text_parts = []
        all_words = []

        for seg in segments_gen:
            words = []
            if seg.words:
                for w in seg.words:
                    word_obj = {
                        "word": w.word.strip(),
                        "start": round(w.start, 3),
                        "end": round(w.end, 3),
                        "probability": round(w.probability, 3)
                    }
                    words.append(word_obj)
                    all_words.append(word_obj)

            seg_dict = {
                "id": seg.id,
                "start": round(seg.start, 3),
                "end": round(seg.end, 3),
                "text": seg.text.strip(),
                "words": words
            }
            segments_list.append(seg_dict)
            full_text_parts.append(seg.text.strip())

        return {
            "language": info.language,
            "language_probability": round(info.language_probability, 3),
            "duration": round(info.duration, 3),
            "full_text": " ".join(full_text_parts),
            "segments": segments_list,
            "words": all_words
        }
