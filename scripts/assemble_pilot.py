"""Combina render visual e mix de áudio locais, sem upload."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PIPELINE = json.loads((ROOT / "config/pipeline_fatonauta.json").read_text(encoding="utf-8"))
PILOT = json.loads((ROOT / PIPELINE["default_manifest"]).read_text(encoding="utf-8"))
VIDEO_ID = PILOT["video_id"]
BASE = ROOT / "outputs" / VIDEO_ID
VIDEO = BASE / "video" / "visual_only.mp4"
AUDIO = BASE / "audio" / "mix.wav"
FINAL = BASE / "video" / "pilot_local.mp4"
SRT = ROOT / "work" / "videos" / VIDEO_ID / "captions" / "voice.srt"
ASS = SRT.with_suffix(".ass")


def time_millis(srt_time: str) -> int:
    hours, minutes, rest = srt_time.split(":")
    seconds, millis = rest.split(",")
    return ((int(hours) * 60 + int(minutes)) * 60 + int(seconds)) * 1000 + int(millis)


def ass_millis(value: int) -> str:
    total_seconds, millis = divmod(value, 1000)
    hours, rem = divmod(total_seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{hours}:{minutes:02d}:{seconds:02d}.{millis // 10:02d}"


def write_ass() -> None:
    blocks = re.split(r"\r?\n\s*\r?\n", SRT.read_text(encoding="utf-8").strip())
    header = (
        "[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\n"
        "WrapStyle: 0\nScaledBorderAndShadow: yes\n\n[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
        "Style: FatoNauta,Roboto,62,&H00E2EFF4,&H00E2EFF4,&H002E1707,&H80000000,-1,0,0,0,100,100,0,0,1,4,2,2,100,150,255,1\n\n"
        "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )
    events = []
    for block in blocks:
        lines = block.splitlines()
        if len(lines) < 3 or " --> " not in lines[1]:
            raise ValueError("SRT malformado.")
        start, end = lines[1].split(" --> ")
        spoken = " ".join(lines[2:]).replace("{", "(").replace("}", ")")
        chunks = textwrap.wrap(spoken, width=58, break_long_words=False)
        start_ms, end_ms = time_millis(start), time_millis(end)
        weights = [len(chunk.split()) for chunk in chunks]
        cursor = start_ms
        for index, chunk in enumerate(chunks):
            next_ms = end_ms if index == len(chunks) - 1 else start_ms + round(
                (end_ms - start_ms) * sum(weights[:index + 1]) / sum(weights)
            )
            wrapped = textwrap.wrap(chunk, width=34, break_long_words=False)
            if len(wrapped) > 2:
                raise ValueError(f"Legenda longa demais: {lines[0]}")
            events.append(
                f"Dialogue: 0,{ass_millis(cursor)},{ass_millis(next_ms)},FatoNauta,,0,0,0,,{'\\N'.join(wrapped)}"
            )
            cursor = next_ms
    ASS.write_text(header + "\n".join(events) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    if PILOT.get("publication_enabled") is not False:
        raise SystemExit("Montagem local exige publicação desativada.")
    for path in (VIDEO, AUDIO, SRT):
        if not path.is_file():
            raise SystemExit(f"Entrada ausente: {path}")
    write_ass()
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(VIDEO), "-i", str(AUDIO),
        "-map", "0:v:0", "-map", "1:a:0",
        "-vf", f"ass={ASS.relative_to(ROOT).as_posix()}:fontsdir=assets/fonts/roboto",
        "-c:v", "libx264", "-preset", "fast", "-crf", "19", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-t", str(PILOT["duration_seconds"]), "-movflags", "+faststart", str(FINAL),
    ], check=True, cwd=ROOT)
    report = {
        "video_id": VIDEO_ID,
        "mode": "local_only",
        "visual_input": str(VIDEO.relative_to(ROOT)).replace("\\", "/"),
        "audio_input": str(AUDIO.relative_to(ROOT)).replace("\\", "/"),
        "captions_input": str(SRT.relative_to(ROOT)).replace("\\", "/"),
        "captions_rendered": str(ASS.relative_to(ROOT)).replace("\\", "/"),
        "caption_alignment": "SRT por fala medido; trechos longos subdivididos proporcionalmente ao número de palavras, sujeitos a revisão visual.",
        "output": str(FINAL.relative_to(ROOT)).replace("\\", "/"),
        "sha256": sha256(FINAL),
        "size_bytes": FINAL.stat().st_size,
    }
    report_path = ROOT / "work" / "videos" / VIDEO_ID / "reports" / "assembly.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(FINAL)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
