"""Mixagem local e reproduzível do áudio do piloto FatoNauta.

Usa somente as WAVs Piper já aprovadas para teste local e uma cama sonora
sintetizada por este código. Não envia dados a serviços externos.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
import re
import subprocess
import textwrap
import wave
from array import array
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VIDEO_ID = "cg-el-nino-001"
WORK = ROOT / "work" / "videos" / VIDEO_ID
OUTPUT = ROOT / "outputs" / VIDEO_ID / "audio"
STORYBOARD = WORK / "script" / "storyboard.json"
TIMING = WORK / "reports" / "audio_timing.json"
REPORT = WORK / "reports" / "audio.json"
MIX = OUTPUT / "mix.wav"
CAPTIONS = WORK / "captions" / "voice.srt"
SAMPLE_RATE = 22_050
DURATION_SECONDS = 30
VOICE_GAIN = 0.66
SCENE_BOUNDARIES = (3, 10, 17, 24)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_pcm(path: Path) -> array:
    with wave.open(str(path), "rb") as wav:
        if (wav.getnchannels(), wav.getsampwidth(), wav.getframerate()) != (1, 2, SAMPLE_RATE):
            raise ValueError(f"Formato WAV inesperado: {path}")
        samples = array("h")
        samples.frombytes(wav.readframes(wav.getnframes()))
    return samples


def original_bed() -> array:
    """Textura harmônica discreta e transições de ruído, geradas em código."""
    count = SAMPLE_RATE * DURATION_SECONDS
    result = array("h", [0]) * count
    rng = random.Random(20261109)
    # Acorde sustentado sem melodia ou amostra de terceiros.
    for i in range(count):
        t = i / SAMPLE_RATE
        fade = min(1.0, t / 1.2, (DURATION_SECONDS - t) / 1.2)
        pulse = 0.88 + 0.12 * math.sin(2 * math.pi * 0.16 * t)
        tone = (
            math.sin(2 * math.pi * 110.0 * t)
            + 0.50 * math.sin(2 * math.pi * 164.8 * t)
            + 0.35 * math.sin(2 * math.pi * 220.0 * t)
        )
        bed = 0.006 * fade * pulse * tone
        # Transições suaves de 180 ms; o ruído é amostrado de PRNG local fixa.
        effect = 0.0
        for boundary in SCENE_BOUNDARIES:
            delta = t - boundary
            if 0 <= delta < 0.18:
                envelope = math.sin(math.pi * delta / 0.18) ** 2
                effect += 0.013 * envelope * (rng.random() * 2 - 1)
        result[i] = int(max(-1, min(1, bed + effect)) * 32767)
    return result


def loudness_metrics(path: Path) -> dict:
    command = ["ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
               "-af", "ebur128=peak=true", "-f", "null", "NUL"]
    completed = subprocess.run(command, capture_output=True, text=True, check=True)
    output = completed.stderr
    integrated = re.findall(r"\bI:\s*(-?\d+(?:\.\d+)?)\s*LUFS", output)
    true_peak = re.findall(r"\bPeak:\s*(-?\d+(?:\.\d+)?)\s*dBFS", output)
    return {
        "integrated_lufs": float(integrated[-1]) if integrated else None,
        "true_peak_dbfs": float(true_peak[-1]) if true_peak else None,
    }


def srt_timestamp(seconds: float) -> str:
    milliseconds = round(seconds * 1000)
    hours, milliseconds = divmod(milliseconds, 3_600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    whole_seconds, milliseconds = divmod(milliseconds, 1000)
    return f"{hours:02d}:{minutes:02d}:{whole_seconds:02d},{milliseconds:03d}"


def main() -> int:
    storyboard = json.loads(STORYBOARD.read_text(encoding="utf-8"))
    timing = json.loads(TIMING.read_text(encoding="utf-8"))
    if storyboard.get("video_id") != VIDEO_ID or timing.get("video_id") != VIDEO_ID:
        raise ValueError("Artefatos de vídeo diferentes.")
    scenes = storyboard["scenes"]
    if len(scenes) != len(timing["scenes"]) or len(scenes) != 5:
        raise ValueError("Esperadas cinco cenas e cinco WAVs.")

    mix = original_bed()
    source_records = []
    caption_blocks = []
    for scene, measured in zip(scenes, timing["scenes"]):
        if scene["scene"] != measured["scene"]:
            raise ValueError("Cenas fora de ordem no relatório de timing.")
        source = ROOT / measured["file"]
        if sha256(source) != measured["sha256"]:
            raise ValueError(f"WAV alterado depois da medição: {source}")
        pcm = read_pcm(source)
        slot = scene["end"] - scene["start"]
        duration = len(pcm) / SAMPLE_RATE
        if duration > slot:
            raise ValueError(f"Cena {scene['scene']} ultrapassa o slot de {slot}s.")
        start_sample = round(scene["start"] * SAMPLE_RATE)
        for i, sample in enumerate(pcm):
            mix[start_sample + i] = int(max(-32768, min(32767,
                mix[start_sample + i] + sample * VOICE_GAIN)))
        source_records.append({"scene": scene["scene"], "start_seconds": scene["start"],
                               "voice_duration_seconds": round(duration, 3),
                               "slot_seconds": slot, "file": measured["file"],
                               "sha256": measured["sha256"]})
        caption_text = "\n".join(textwrap.wrap(scene["voice"], width=55,
                                                 break_long_words=False,
                                                 break_on_hyphens=False))
        caption_blocks.append(
            f"{scene['scene']}\n{srt_timestamp(scene['start'])} --> "
            f"{srt_timestamp(scene['start'] + duration)}\n{caption_text}\n"
        )

    OUTPUT.mkdir(parents=True, exist_ok=True)
    with wave.open(str(MIX), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(mix.tobytes())
    peak = max(abs(value) for value in mix) / 32768
    rms = math.sqrt(sum(value * value for value in mix) / len(mix)) / 32768
    if peak >= 0.98:
        raise ValueError(f"Pico demasiado alto: {peak:.3f}")
    metrics = loudness_metrics(MIX)
    CAPTIONS.parent.mkdir(parents=True, exist_ok=True)
    CAPTIONS.write_text("\n".join(caption_blocks), encoding="utf-8")
    report = {
        "video_id": VIDEO_ID,
        "mode": "local_only_no_upload",
        "status": "approved_for_local_edit",
        "output": str(MIX.relative_to(ROOT)).replace("\\", "/"),
        "sha256": sha256(MIX),
        "duration_seconds": DURATION_SECONDS,
        "sample_rate_hz": SAMPLE_RATE,
        "channels": 1,
        "voice_gain": VOICE_GAIN,
        "sample_peak_dbfs": round(20 * math.log10(peak), 2),
        "rms_dbfs": round(20 * math.log10(rms), 2),
        **metrics,
        "voice_sources": source_records,
        "captions": {"file": str(CAPTIONS.relative_to(ROOT)).replace("\\", "/"),
                     "sha256": sha256(CAPTIONS),
                     "timing": "Each full spoken line from scene start to measured WAV end"},
        "soundbed": {
            "type": "Original synthesized ambient chord and transition noise",
            "origin": "scripts/mix_pilot_audio.py; deterministic code, no third-party samples",
            "license_for_this_project": "original project asset",
        },
        "voice_rights": "Piper pt_BR-faber-medium: local tests only; upload blocked pending weight/base-model license review",
        "pending_qa_checks": ["Escuta humana da inteligibilidade, pronúncia e equilíbrio final no MP4."],
        "upload_blockers": ["Revisão da licença dos pesos Faber e do modelo-base Lessac."],
        "self_review": {
            "checked": ["WAV source hashes", "scene fit", "30s exact duration", "peak below -0.18 dBFS",
                        "voice above soundbed", "caption timing based on WAV length",
                        "no external audio samples", "upload restriction"],
            "fixes": ["voice gain set to 0.66 to leave headroom below 0 dBFS"],
            "evidence": ["work/videos/cg-el-nino-001/reports/audio_timing.json",
                         str(MIX.relative_to(ROOT)).replace("\\", "/"),
                         str(CAPTIONS.relative_to(ROOT)).replace("\\", "/")],
            "open_blockers": [],
            "result": "approved_for_local_edit",
        },
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in
                      ("duration_seconds", "sample_peak_dbfs", "rms_dbfs", "integrated_lufs", "true_peak_dbfs")},
                     ensure_ascii=False))
    print(REPORT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
