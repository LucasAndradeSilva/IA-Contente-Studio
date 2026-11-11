"""Combina o render 3D nativo do Blender com a mesma identidade/legenda do comparativo."""
import argparse
import subprocess
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/cg-bunker-v2-001'
SOURCE=ROOT/'work/render-frames/outputs-cg-bunker-v2-001-visual-mp4'
parser=argparse.ArgumentParser();parser.add_argument('--preview',action='store_true');args=parser.parse_args()
background=Image.open(OUT/'background.png').convert('RGBA')
font=ImageFont.truetype(str(ROOT/'assets/fonts/roboto/Roboto.ttf'),17)
small=ImageFont.truetype(str(ROOT/'assets/fonts/roboto/Roboto.ttf'),15)
labels=['CORTE: ABRIGO CIVIL','CASCA + FECHAMENTOS','ENTRADA / FILTRO / INTERIOR','BELICHES + SANITÁRIOS','ENTRADA BLOQUEADA / ROTA EXTRA','ESTRUTURA + SISTEMAS + MANUTENÇÃO']
def frame(index):
    image=background.copy()
    with Image.open(SOURCE/f'{index:05d}.png') as source:
        image.paste(source.crop((0,0,720,345)),(0,0))
        image.paste(source.crop((0,975,720,1280)),(0,975))
    with Image.open(OUT/'blender/frames'/f'{index+1:05d}.png') as native:
        image.alpha_composite(native.convert('RGBA'),(0,345))
    d=ImageDraw.Draw(image);label=labels[index//150];width=d.textlength(label,font=font)+44
    d.rounded_rectangle(((720-width)/2,875,(720+width)/2,917),radius=22,fill='#081426',outline='#466070')
    d.text((360,896),label,anchor='mm',font=font,fill='#f4efdf')
    d.text((360,947),'ILUSTRAÇÃO DIDÁTICA · SEM ESCALA',anchor='mm',font=small,fill='#94aebc')
    d.text((673,1250),'BLENDER / STUDIO',anchor='rm',font=small,fill='#94aebc')
    return image.convert('RGB')
if args.preview:
    frame(360).save(OUT/'blender-preview.png')
else:
    command=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','720x1280','-r','30','-i','pipe:0','-i',str(OUT/'bunker-v2.mp4'),'-map','0:v:0','-map','1:a:0','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-c:a','copy','-t','30','-movflags','+faststart',str(OUT/'bunker-blender-v2.mp4')]
    p=subprocess.Popen(command,stdin=subprocess.PIPE)
    try:
        for i in range(900):
            p.stdin.write(frame(i).tobytes())
            if i%150==0:print(f'Composição Blender {i}/900',flush=True)
    finally:
        p.stdin.close()
    if p.wait()!=0:raise SystemExit('Falha na composição FFmpeg')
    print(OUT/'bunker-blender-v2.mp4')
