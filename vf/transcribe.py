"""Phiên âm từng từ.
- Mac Apple Silicon: mlx-whisper (chạy trên GPU của chip M), lùi faster-whisper CPU int8 nếu chưa cài.
- Windows/Linux: faster-whisper (CUDA nếu có GPU NVIDIA, không thì CPU).
Chọn tay: VF_TRANSCRIBER = auto (mặc định) | mlx | faster. Model: VF_WHISPER_MODEL (mặc định large-v3)."""
from __future__ import annotations

import os
import platform
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from vf.ffutil import ffprobe_json

DEFAULT_MODEL = os.environ.get("VF_WHISPER_MODEL", "large-v3")
# tên model faster-whisper → repo MLX tương ứng trên Hugging Face
MLX_MODELS = {
    "large-v3": "mlx-community/whisper-large-v3-mlx",
    "large-v3-turbo": "mlx-community/whisper-large-v3-turbo",
    "medium": "mlx-community/whisper-medium-mlx",
    "small": "mlx-community/whisper-small-mlx",
}


@dataclass(frozen=True)
class Word:
    text: str
    start: float
    end: float


def is_apple_silicon() -> bool:
    return sys.platform == "darwin" and platform.machine() == "arm64"


def mlx_available() -> bool:
    try:
        import mlx_whisper  # noqa: F401
    except ImportError:
        return False
    return True


def backend() -> str:
    """'mlx' hoặc 'faster' — bộ phiên âm sẽ dùng."""
    choice = os.environ.get("VF_TRANSCRIBER", "auto").lower()
    if choice in ("mlx", "faster"):
        return choice
    return "mlx" if is_apple_silicon() and mlx_available() else "faster"


def mlx_repo(model: str) -> str:
    return model if "/" in model else MLX_MODELS.get(model, f"mlx-community/whisper-{model}-mlx")


def _add_cuda_dlls() -> None:
    """Windows: cho ctranslate2 thấy cuBLAS/cuDNN cài bằng pip (nvidia-*-cu12)."""
    if os.name != "nt":
        return
    try:
        import nvidia
    except ImportError:
        return
    for base in nvidia.__path__:
        for bin_dir in Path(base).glob("*/bin"):
            os.add_dll_directory(str(bin_dir))
            os.environ["PATH"] = str(bin_dir) + os.pathsep + os.environ.get("PATH", "")


@lru_cache(maxsize=2)
def _model(name: str):
    _add_cuda_dlls()
    from faster_whisper import WhisperModel

    if sys.platform == "darwin":  # ctranslate2 không chạy GPU Mac: CPU int8 là nhanh nhất
        return WhisperModel(name, device="cpu", compute_type="int8")
    return WhisperModel(name, device="auto", compute_type="auto")


def _transcribe_mlx(path: Path, lang: str, model: str) -> list[Word]:
    import mlx_whisper

    result = mlx_whisper.transcribe(str(path), path_or_hf_repo=mlx_repo(model), language=lang,
                                    word_timestamps=True, verbose=None)
    words: list[Word] = []
    for seg in result.get("segments", []):
        for w in seg.get("words", []) or []:
            text = str(w.get("word", "")).strip()
            if text:
                words.append(Word(text, round(float(w["start"]), 3), round(float(w["end"]), 3)))
    return words


def transcribe(path: Path, lang: str = "vi", model: str = DEFAULT_MODEL) -> list[Word]:
    """Trả [] nếu file không có tiếng (video chỉ có cảnh sản phẩm)."""
    data = ffprobe_json(path)
    if not any(s["codec_type"] == "audio" for s in data["streams"]):
        return []
    if backend() == "mlx":
        return _transcribe_mlx(path, lang, model)
    segments, _ = _model(model).transcribe(str(path), language=lang, word_timestamps=True)
    words: list[Word] = []
    for seg in segments:
        for w in seg.words or []:
            text = w.word.strip()
            if text:
                words.append(Word(text, round(w.start, 3), round(w.end, 3)))
    return words
