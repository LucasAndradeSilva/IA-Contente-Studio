"""Confere propriedades técnicas do MP4 local do piloto."""

from __future__ import annotations

import json
import hashlib
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PIPELINE = json.loads((ROOT / "config/pipeline_fatonauta.json").read_text(encoding="utf-8"))
PILOT = json.loads((ROOT / PIPELINE["default_manifest"]).read_text(encoding="utf-8"))
VIDEO_ID = PILOT["video_id"]
VIDEO = ROOT / "outputs" / VIDEO_ID / "video" / "pilot_local.mp4"


def main() -> int:
    if not VIDEO.is_file():
        raise SystemExit(f"MP4 local ausente: {VIDEO}")
    probe = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration:stream=codec_type,width,height,avg_frame_rate,sample_rate,channels",
        "-of", "json", str(VIDEO),
    ], text=True, encoding="utf-8"))
    streams = probe.get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video"), {})
    audio = next((s for s in streams if s.get("codec_type") == "audio"), {})
    duration = float(probe.get("format", {}).get("duration", 0))
    expected = PILOT["duration_seconds"]
    fps = video.get("avg_frame_rate", "0/1")
    numerator, denominator = (int(part) for part in fps.split("/"))
    actual_fps = numerator / denominator if denominator else 0
    checks = {
        "mp4_exists": VIDEO.stat().st_size > 0,
        "resolution": (video.get("width"), video.get("height")) == (1080, 1920),
        "duration": abs(duration - expected) <= PILOT["acceptance"]["duration_tolerance_seconds"],
        "fps": abs(actual_fps - PILOT["canvas"]["fps"]) < 0.01,
        "audio_stream": bool(audio),
        "publication_disabled": PILOT.get("publication_enabled") is False,
        "sources_recorded": (ROOT / PILOT["research"]).is_file(),
        "storyboard_recorded": (ROOT / PILOT["script"]["storyboard"]).is_file(),
    }
    digest = hashlib.sha256()
    with VIDEO.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    video_sha256 = digest.hexdigest()
    report_path = ROOT / "work" / "videos" / VIDEO_ID / "reports" / "qa.json"
    previous = json.loads(report_path.read_text(encoding="utf-8")) if report_path.exists() else {}
    same_video = previous.get("video_sha256") == video_sha256
    report = {
        "video_id": VIDEO_ID,
        "file": str(VIDEO.relative_to(ROOT)).replace("\\", "/"),
        "video_sha256": video_sha256,
        "duration_seconds": duration,
        "resolution": [video.get("width"), video.get("height")],
        "fps": actual_fps,
        "audio": {"sample_rate": audio.get("sample_rate"), "channels": audio.get("channels")},
        "checks": checks,
        "technical_pass": all(checks.values()),
        "editorial_and_caption_review": previous.get("editorial_and_caption_review", "pending_manual_preview") if same_video else "pending_manual_preview",
        "qa_gate_passed": previous.get("qa_gate_passed", False) if same_video else False,
        "publication_status": "blocked",
    }
    if same_video:
        for key in ("review_findings", "asr_auxiliary_review"):
            if key in previous:
                report[key] = previous[key]
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, passed in checks.items():
        print(f"{name}: {'OK' if passed else 'FALHOU'}")
    print(report_path)
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
