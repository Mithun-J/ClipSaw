"""
transcriber.py - Local speech transcription using faster-whisper with word-level timestamps.
100% free and open-source, runs on local GPU with automatic CPU fallback.
"""

import os

# Prevent OpenMP runtime clash between Anaconda/Intel MKL, PyTorch, and ctranslate2
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from typing import Any, Dict, List, Optional
import torch


class Transcriber:
    def __init__(self, model_size: str = "base", device: Optional[str] = None, compute_type: Optional[str] = None):
        """
        Initialize the local Whisper model.
        Available sizes: 'tiny', 'base', 'small', 'medium', 'large-v3'.
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
        if self._model is not None:
            return self._model

        from faster_whisper import WhisperModel
        download_root = os.path.abspath("storage/models")

        # Attempt CUDA first if requested; fallback gracefully to CPU if cuBLAS/CUDA 12 DLLs are missing
        if self.device == "cuda":
            try:
                self._model = WhisperModel(
                    self.model_size,
                    device="cuda",
                    compute_type=self.compute_type,
                    download_root=download_root
                )
                return self._model
            except Exception as e:
                print(f"[Transcriber Warning] CUDA init failed ({e}). Falling back to CPU int8 mode.")
                self.device = "cpu"
                self.compute_type = "int8"

        self._model = WhisperModel(
            self.model_size,
            device="cpu",
            compute_type="int8",
            download_root=download_root
        )
        return self._model

    def transcribe(self, audio_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Transcribe an audio file and return word-level timestamps with automatic fallback.
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        try:
            return self._run_transcription(audio_path, language=language)
        except RuntimeError as e:
            if "cublas" in str(e).lower() or "cuda" in str(e).lower() or self.device == "cuda":
                print(f"[Transcriber Warning] CUDA runtime execution error ({e}). Retrying on CPU...")
                from faster_whisper import WhisperModel
                self.device = "cpu"
                self.compute_type = "int8"
                self._model = WhisperModel(
                    self.model_size,
                    device="cpu",
                    compute_type="int8",
                    download_root=os.path.abspath("storage/models")
                )
                return self._run_transcription(audio_path, language=language)
            else:
                raise e

    def _run_transcription(self, audio_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        model = self._get_model()

        segments_gen, info = model.transcribe(
            audio_path,
            language=language,
            beam_size=1,  # Fast greedy decoding for high throughput
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
