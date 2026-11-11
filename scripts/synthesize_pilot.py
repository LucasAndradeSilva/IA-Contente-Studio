"""Renderiza localmente a narração de cada cena do manifesto ativo com Piper."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import wave
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PIPELINE = json.loads((ROOT / "config/pipeline_fatonauta.json").read_text(encoding="utf-8"))
PILOT = json.loads((ROOT / PIPELINE["default_manifest"]).read_text(encoding="utf-8"))
VIDEO_ID = PILOT["video_id"]
STORYBOARD = ROOT / "work" / "videos" / VIDEO_ID / "script" / "storyboard.json"
MODEL = ROOT / "assets" / "voices" / "piper" / "pt_BR-faber-medium" / "pt_BR-faber-medium.onnx"
OUTPUT = ROOT / "outputs" / VIDEO_ID / "audio"


def main() -> int:
    if not MODEL.is_file():
        raise SystemExit(f"Modelo local ausente: {MODEL}")
    storyboard = json.loads(STORYBOARD.read_text(encoding="utf-8"))
    if storyboard["video_id"] != VIDEO_ID:
        raise SystemExit("Storyboard e manifesto apontam para vídeos diferentes.")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    report = {"video_id": VIDEO_ID, "engine": "Piper 1.8.0", "mode": "local_only", "scenes": []}
    for scene in storyboard["scenes"]:
        scene_id = scene["scene"]
        text_path = OUTPUT / f"scene_{scene_id:02d}.txt"
        wav_path = OUTPUT / f"scene_{scene_id:02d}.wav"
        text_path.write_text(scene["voice"] + "\n", encoding="utf-8")
        subprocess.run(
            [sys.executable, "-m", "piper", "-m", str(MODEL), "-i", str(text_path), "-f", str(wav_path)],
            check=True,
            cwd=ROOT,
        )
        with wave.open(str(wav_path), "rb") as wav:
            duration = wav.getnframes() / wav.getframerate()
        slot = scene["end"] - scene["start"]
        report["scenes"].append({
            "scene": scene_id,
            "duration_seconds": round(duration, 3),
            "slot_seconds": slot,
            "fits_slot": duration <= slot,
            "file": str(wav_path.relative_to(ROOT)).replace("\\", "/"),
            "sha256": hashlib.sha256(wav_path.read_bytes()).hexdigest(),
        })
    report_path = ROOT / "work" / "videos" / VIDEO_ID / "reports" / "audio_timing.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for scene in report["scenes"]:
        print(f"Cena {scene['scene']}: {scene['duration_seconds']} s / {scene['slot_seconds']} s — {'OK' if scene['fits_slot'] else 'LONGA'}")
    print(report_path)
    return 0 if all(scene["fits_slot"] for scene in report["scenes"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
