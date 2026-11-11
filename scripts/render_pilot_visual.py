"""Renderização 2D determinística do piloto El Niño; não realiza upload.

O desenho usa formas originais em Pillow e a fonte Roboto OFL. Os quadros são
enviados por pipe ao FFmpeg para produzir um vídeo local de 1080 × 1920.
"""

from __future__ import annotations

import hashlib
import json
import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
VIDEO_ID = "cg-el-nino-001"
STORYBOARD = ROOT / "work" / "videos" / VIDEO_ID / "script" / "storyboard.json"
FONT_PATH = ROOT / "assets" / "fonts" / "roboto" / "Roboto.ttf"
FONT_LICENSE = ROOT / "assets" / "fonts" / "roboto" / "OFL.txt"
OUT = ROOT / "outputs" / VIDEO_ID / "video"
REPORT = ROOT / "work" / "videos" / VIDEO_ID / "reports" / "visual.json"
W, H, FPS, SECONDS = 540, 960, 30, 30
NAVY = "#07172e"
MID = "#102843"
CYAN = "#36d5eb"
ORANGE = "#f69b44"
CREAM = "#f4efe2"
MUTED = "#9cb6c8"
WHITE = "#ffffff"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    result = ImageFont.truetype(str(FONT_PATH), size)
    if bold:
        # A ordem de eixos desta versão de Roboto é peso, largura.
        result.set_variation_by_axes([800, 100])
    return result


FONTS = {
    "small": font(17), "label": font(21, True), "body": font(26),
    "body_bold": font(27, True), "title": font(46, True),
    "hero": font(61, True), "number": font(81, True),
}


def ease(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def center_text(draw: ImageDraw.ImageDraw, xy: tuple[float, float], value: str,
                face: ImageFont.FreeTypeFont, color: str) -> None:
    draw.text(xy, value, font=face, fill=color, anchor="mm", stroke_width=0)


def card(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill: str = MID,
         outline: str = "#31506a", radius: int = 24, width: int = 2) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def badge(draw: ImageDraw.ImageDraw, x: int, y: int, value: str, color: str = CYAN) -> None:
    width = max(100, int(draw.textlength(value, font=FONTS["small"])) + 28)
    card(draw, (x, y, x + width, y + 34), fill="#163952", outline="#27566f", radius=16, width=1)
    draw.text((x + 14, y + 8), value, font=FONTS["small"], fill=color)


def sun(draw: ImageDraw.ImageDraw, x: int, y: int, r: int, color: str = ORANGE) -> None:
    for a in range(0, 360, 45):
        rad = math.radians(a)
        draw.line((x + math.cos(rad) * (r + 8), y + math.sin(rad) * (r + 8),
                   x + math.cos(rad) * (r + 23), y + math.sin(rad) * (r + 23)), fill=color, width=5)
    draw.ellipse((x - r, y - r, x + r, y + r), fill=color)


def cloud(draw: ImageDraw.ImageDraw, x: int, y: int, scale: float = 1.0,
          color: str = CREAM, rain: bool = False) -> None:
    s = scale
    draw.ellipse((x - 53*s, y - 15*s, x + 3*s, y + 32*s), fill=color)
    draw.ellipse((x - 24*s, y - 40*s, x + 48*s, y + 34*s), fill=color)
    draw.ellipse((x + 24*s, y - 15*s, x + 73*s, y + 32*s), fill=color)
    draw.rounded_rectangle((x - 53*s, y + 5*s, x + 73*s, y + 34*s), radius=int(14*s), fill=color)
    if rain:
        for dx in (-30, 8, 45):
            draw.line((x + dx*s, y + 49*s, x + (dx-10)*s, y + 72*s), fill=CYAN, width=max(2, int(5*s)))


def drop(draw: ImageDraw.ImageDraw, x: int, y: int, size: int, color: str = CYAN) -> None:
    draw.polygon([(x, y-size), (x-size*0.65, y+size*0.22), (x-size*0.45, y+size*0.72),
                  (x, y+size), (x+size*0.45, y+size*0.72), (x+size*0.65, y+size*0.22)], fill=color)


def base(draw: ImageDraw.ImageDraw, scene: int, t: float) -> None:
    draw.rectangle((0, 0, W, H), fill=NAVY)
    for x in range(42, W, 42):
        draw.line((x, 0, x, H), fill="#10253b", width=1)
    for y in range(28, H, 42):
        draw.line((0, y, W, y), fill="#10253b", width=1)
    draw.ellipse((-130, -140, 335, 290), outline="#1b3b53", width=3)
    draw.ellipse((390, 440, 820, 870), outline="#163850", width=2)
    draw.text((34, 48), "FATONAUTA", font=FONTS["body_bold"], fill=CREAM)
    draw.text((36, 83), "CIÊNCIA PARA O SEU DIA", font=FONTS["small"], fill=CYAN)
    draw.line((35, 124, 505, 124), fill="#31506a", width=2)
    draw.text((36, 136), f"MISSÃO 001  /  {scene:02d}", font=FONTS["small"], fill=MUTED)
    draw.rounded_rectangle((35, 892, 505, 898), radius=3, fill="#214059")
    draw.rounded_rectangle((35, 892, 35 + int(470*t/SECONDS), 898), radius=3, fill=CYAN)
    draw.text((36, 915), "EL NIÑO  •  PREPARO LOCAL", font=FONTS["small"], fill=MUTED)


def scene_one(draw: ImageDraw.ImageDraw, local: float) -> None:
    center_text(draw, (270, 215), "EL NIÑO", FONTS["hero"], CREAM)
    center_text(draw, (270, 274), "E A SUA CIDADE?", FONTS["body_bold"], CYAN)
    shift = int(14 * ease(local / 1.4))
    sun(draw, 418, 405-shift, 32)
    cloud(draw, 118, 403-shift, 0.68, CREAM, True)
    # Cidade de papel em três camadas, sem geografia específica.
    draw.polygon([(0, 656), (0, 512), (80, 500), (145, 544), (204, 511), (270, 541),
                  (340, 501), (420, 523), (540, 492), (540, 656)], fill="#174362")
    for x, top, width in [(42, 510, 62), (115, 467, 80), (217, 515, 56),
                          (298, 452, 72), (386, 488, 56), (450, 440, 64)]:
        draw.rounded_rectangle((x, top+shift, x+width, 665), radius=8, fill="#2c6380")
        for yy in range(top+shift+20, 630, 28):
            for xx in range(x+13, x+width-6, 23):
                draw.rounded_rectangle((xx, yy, xx+10, yy+12), radius=2, fill="#f5bb79")
    draw.polygon([(0, 642), (110, 615), (240, 653), (360, 616), (540, 635), (540, 722), (0, 722)], fill="#0d344c")


def scene_two(draw: ImageDraw.ImageDraw, local: float) -> None:
    center_text(draw, (270, 210), "ATIVAR ALERTAS", FONTS["title"], CREAM)
    badge(draw, 57, 264, "EXEMPLO DE SMS")
    card(draw, (43, 321, 497, 657), fill="#0d2034", outline="#3b7890", radius=30, width=3)
    draw.ellipse((66, 342, 76, 352), fill=ORANGE)
    draw.ellipse((84, 342, 94, 352), fill=CYAN)
    draw.ellipse((102, 342, 112, 352), fill=CREAM)
    draw.line((65, 369, 475, 369), fill="#24506b", width=2)
    draw.text((70, 395), "ENVIE POR SMS", font=FONTS["label"], fill=MUTED)
    card(draw, (67, 442, 473, 515), fill="#18364c", outline="#41667c", radius=17, width=2)
    draw.text((88, 460), "SEU CEP", font=FONTS["body_bold"], fill=CREAM)
    draw.line((350, 479, 393, 479), fill=CYAN, width=5)
    draw.line((378, 466, 393, 479, 378, 492), fill=CYAN, width=5, joint="curve")
    draw.text((70, 541), "PARA", font=FONTS["label"], fill=MUTED)
    center_text(draw, (300, 580), "40199", FONTS["number"], ORANGE)
    cursor_x = int(145 + 258*ease(local/5.8))
    cursor_y = int(684 - 130*ease(local/5.8))
    draw.polygon([(cursor_x, cursor_y), (cursor_x+16, cursor_y+40),
                  (cursor_x+24, cursor_y+28), (cursor_x+37, cursor_y+23)], fill=CREAM, outline=NAVY)


def scene_three(draw: ImageDraw.ImageDraw, local: float) -> None:
    center_text(draw, (270, 213), "QUAL É O RISCO", FONTS["title"], CREAM)
    center_text(draw, (270, 261), "NA SUA REGIÃO?", FONTS["body_bold"], CYAN)
    active = min(2, int(local / (7/3)))
    items = [("CHUVA", CYAN), ("CALOR", ORANGE), ("SECA", "#d6b77a")]
    for idx, (label, color) in enumerate(items):
        y = 326 + idx*116
        on = idx == active
        card(draw, (52, y, 488, y+94), fill="#1b4058" if on else MID,
             outline=color if on else "#31506a", radius=22, width=4 if on else 2)
        if idx == 0:
            cloud(draw, 115, y+35, 0.36, CREAM, True)
        elif idx == 1:
            sun(draw, 115, y+46, 16, ORANGE)
        else:
            drop(draw, 115, y+48, 21, "#d6b77a")
        draw.text((190, y+31), label, font=FONTS["body_bold"], fill=CREAM if on else MUTED)
        if on:
            draw.ellipse((446, y+37, 461, y+52), fill=color)
    center_text(draw, (270, 687), "CONFIRA O AVISO LOCAL", FONTS["label"], ORANGE)


def scene_four(draw: ImageDraw.ImageDraw, local: float) -> None:
    center_text(draw, (270, 211), "ALERTA DE ENCHENTE?", font(33, True), CREAM)
    badge(draw, 67, 258, "AÇÃO CONDICIONAL", ORANGE)
    # Água genérica, sem rota real de evacuação.
    draw.rounded_rectangle((65, 338, 475, 581), radius=28, fill="#17405a", outline="#397b93", width=3)
    draw.polygon([(66, 489), (125, 472), (190, 491), (254, 467), (323, 492),
                  (393, 474), (474, 490), (474, 580), (66, 580)], fill="#167d9c")
    wave = int(7 * math.sin(local*3))
    draw.arc((75, 480+wave, 215, 535+wave), 190, 350, fill=CYAN, width=5)
    draw.arc((260, 478-wave, 439, 540-wave), 190, 350, fill=CYAN, width=5)
    draw.ellipse((250, 412, 338, 500), outline=ORANGE, width=9)
    draw.line((267, 484, 325, 426), fill=ORANGE, width=9)
    center_text(draw, (270, 624), "EVITE ÁREAS ALAGADAS", FONTS["body_bold"], ORANGE)
    center_text(draw, (270, 668), "CONHEÇA A SAÍDA LOCAL", FONTS["label"], CREAM)


def scene_five(draw: ImageDraw.ImageDraw, local: float) -> None:
    center_text(draw, (270, 208), "O AVISO LOCAL", FONTS["title"], CREAM)
    center_text(draw, (270, 258), "VEM PRIMEIRO", FONTS["body_bold"], CYAN)
    card(draw, (70, 326, 470, 603), fill="#16364c", outline="#3b7890", radius=30, width=3)
    sun(draw, 167, 424, 33)
    drop(draw, 349, 426, 47)
    draw.line((102, 516, 438, 516), fill="#396d83", width=2)
    center_text(draw, (270, 559), "SIGA A DEFESA CIVIL", FONTS["body_bold"], CREAM)
    center_text(draw, (270, 662), "DA SUA REGIÃO", FONTS["label"], ORANGE)


def render_frame(t: float, storyboard: dict) -> Image.Image:
    scene = next((item for item in storyboard["scenes"] if item["start"] <= t < item["end"]),
                 storyboard["scenes"][-1])
    img = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)
    base(draw, scene["scene"], t)
    local = t - scene["start"]
    {1: scene_one, 2: scene_two, 3: scene_three, 4: scene_four, 5: scene_five}[scene["scene"]](draw, local)
    return img


def probe(path: Path) -> dict:
    command = ["ffprobe", "-v", "error", "-select_streams", "v:0",
               "-show_entries", "stream=width,height,r_frame_rate,nb_frames,duration",
               "-of", "json", str(path)]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    return json.loads(result.stdout)["streams"][0]


def main() -> int:
    if not FONT_PATH.is_file() or not FONT_LICENSE.is_file():
        raise SystemExit("Roboto ou licença OFL ausentes.")
    storyboard = json.loads(STORYBOARD.read_text(encoding="utf-8"))
    if storyboard["video_id"] != VIDEO_ID:
        raise SystemExit("Storyboard de outro vídeo.")
    OUT.mkdir(parents=True, exist_ok=True)
    samples = []
    for scene in storyboard["scenes"]:
        t = (scene["start"] + scene["end"]) / 2
        sample = OUT / f"sample_scene_{scene['scene']:02d}.png"
        render_frame(t, storyboard).resize((1080, 1920), Image.Resampling.LANCZOS).save(sample)
        samples.append(str(sample.relative_to(ROOT)).replace("\\", "/"))
    video = OUT / "visual_only.mp4"
    stderr_path = OUT / "ffmpeg_visual.log"
    command = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
               "-s", f"{W}x{H}", "-r", str(FPS), "-i", "pipe:0", "-an",
               "-vf", "scale=1080:1920:flags=lanczos", "-c:v", "libx264",
               "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
               "-movflags", "+faststart", str(video)]
    with stderr_path.open("wb") as stderr:
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=stderr, cwd=ROOT)
        assert process.stdin is not None
        try:
            for index in range(FPS * SECONDS):
                process.stdin.write(render_frame(index / FPS, storyboard).tobytes())
        except Exception:
            process.kill()
            raise
        finally:
            process.stdin.close()
        if process.wait() != 0:
            raise RuntimeError(f"FFmpeg falhou; veja {stderr_path}")
    stream = probe(video)
    if (stream.get("width"), stream.get("height"), stream.get("r_frame_rate")) != (1080, 1920, "30/1"):
        raise RuntimeError(f"Formato inesperado: {stream}")
    report = {
        "video_id": VIDEO_ID, "status": "rendered_awaiting_visual_inspection",
        "output": str(video.relative_to(ROOT)).replace("\\", "/"),
        "sha256": hashlib.sha256(video.read_bytes()).hexdigest(),
        "ffprobe": stream, "frames_expected": FPS * SECONDS,
        "sample_frames": samples,
        "font": {"path": str(FONT_PATH.relative_to(ROOT)).replace("\\", "/"),
                 "license": "OFL-1.1", "license_file": str(FONT_LICENSE.relative_to(ROOT)).replace("\\", "/")},
        "assets": "Formas e ícones originais desenhados em código; sem fotos, logos oficiais ou CEP real.",
        "captions": "Não embutidas no vídeo visual; área y=1450–1650 reservada para voice.srt na montagem final.",
        "external_services": False,
        "self_review": {
            "checked": ["storyboard", "5 cenas", "1080x1920", "30fps", "área livre para legendas", "licença da fonte", "fontes de ativos"],
            "fixes": [], "evidence": samples + [str(video.relative_to(ROOT)).replace("\\", "/")],
            "open_blockers": ["inspeção visual dos quadros de amostra"], "result": "pending_inspection"
        }
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(video), "ffprobe": stream, "samples": samples}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
