"""Transcrição local auxiliar para detectar falas ausentes ou muito divergentes."""

from __future__ import annotations

import difflib
import json
import re
import unicodedata
from pathlib import Path

from faster_whisper import WhisperModel


ROOT = Path(__file__).resolve().parents[1]
PIPELINE = json.loads((ROOT / "config/pipeline_fatonauta.json").read_text(encoding="utf-8"))
PILOT = json.loads((ROOT / PIPELINE["default_manifest"]).read_text(encoding="utf-8"))
VIDEO_ID = PILOT["video_id"]
WORK = ROOT / "work" / "videos" / VIDEO_ID
VIDEO = ROOT / "outputs" / VIDEO_ID / "video" / "pilot_local.mp4"
MODEL_NAME = "small"


def normalize(text: str) -> str:
    without_accents = "".join(
        letter for letter in unicodedata.normalize("NFD", text)
        if unicodedata.category(letter) != "Mn"
    )
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", without_accents.lower())).strip()


def main() -> int:
    if not VIDEO.is_file():
        raise SystemExit("MP4 local ausente.")
    model = WhisperModel(
        MODEL_NAME, device="cpu", compute_type="int8",
        download_root=str(ROOT / "outputs" / "models" / "faster-whisper"),
    )
    segments, info = model.transcribe(
        str(VIDEO), language="pt", beam_size=5, word_timestamps=True, vad_filter=False,
    )
    observed = []
    for segment in segments:
        observed.append({
            "start": round(segment.start, 2), "end": round(segment.end, 2),
            "text": segment.text.strip(),
            "words": [{"start": round(word.start, 2), "end": round(word.end, 2), "text": word.word}
                      for word in (segment.words or [])],
        })
    expected_text = (WORK / "script" / "voice.txt").read_text(encoding="utf-8")
    transcript = " ".join(segment["text"] for segment in observed)
    similarity = difflib.SequenceMatcher(None, normalize(expected_text), normalize(transcript), autojunk=False).ratio()
    report = {
        "video_id": VIDEO_ID,
        "mode": "offline_inference_after_model_download",
        "model": f"faster-whisper {MODEL_NAME} CPU int8",
        "model_source": f"https://huggingface.co/Systran/faster-whisper-{MODEL_NAME}",
        "language": info.language,
        "expected": expected_text.strip(),
        "observed": transcript,
        "normalized_similarity": round(similarity, 3),
        "segments": observed,
        "interpretation": "ASR é verificação auxiliar: erros de transcrição não provam falha do áudio e alta similaridade não substitui escuta humana.",
    }
    path = WORK / "reports" / "asr.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Similaridade textual: {similarity:.3f}")
    print(transcript)
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
