"""Finalização única das variantes com o mesmo áudio e conferência técnica."""
import hashlib
import json
import subprocess
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/cg-bunker-v2-001'
subprocess.run(['ffmpeg','-v','error','-y','-i',str(OUT/'css3d-visual.mp4'),'-i',str(OUT/'bunker-v2.mp4'),'-map','0:v:0','-map','1:a:0','-c','copy','-t','30','-movflags','+faststart',str(OUT/'bunker-css3d-v2.mp4')],check=True)
variants=[('threejs_webgl','bunker-v2.mp4'),('css_3d_html','bunker-css3d-v2.mp4'),('blender_workbench','bunker-blender-v2.mp4')]
report={'video_id':'cg-bunker-v2-001','scope':'Três versões completas de 30 segundos; comparação local','variants':[],'voice_restriction':'Faber permanece somente para teste local; nenhum upload autorizado.'}
for engine,filename in variants:
    path=OUT/filename
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)],text=True))
    v=next(s for s in probe['streams'] if s['codec_type']=='video');a=next(s for s in probe['streams'] if s['codec_type']=='audio')
    assert (v['width'],v['height'],v['avg_frame_rate'],int(v['nb_frames']))==(720,1280,'30/1',900)
    assert abs(float(probe['format']['duration'])-30)<.1
    audio_hash=subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-map','0:a:0','-c:a','copy','-f','hash','-'],text=True).strip()
    report['variants'].append({'engine':engine,'file':str(path.relative_to(ROOT)).replace('\\','/'),'duration_seconds':float(probe['format']['duration']),'width':v['width'],'height':v['height'],'fps':v['avg_frame_rate'],'frames':int(v['nb_frames']),'audio_codec':a['codec_name'],'audio_hash':audio_hash,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
assert len({v['audio_hash'] for v in report['variants']})==1,'Áudios diferentes entre as variantes'
header=Image.new('RGB',(1080,48),'#081426');draw=ImageDraw.Draw(header);font=ImageFont.truetype(str(ROOT/'assets/fonts/roboto/Roboto.ttf'),23)
for x,label in [(180,'THREE.JS'),(540,'HTML / CSS 3D'),(900,'BLENDER / STUDIO')]:draw.text((x,24),label,anchor='mm',font=font,fill='#53e1ed')
header.save(OUT/'comparison-header.png')
command=['ffmpeg','-v','error','-y']
for _,filename in variants:command+=['-i',str(OUT/filename)]
command+=['-loop','1','-i',str(OUT/'comparison-header.png'),'-filter_complex','[0:v]scale=360:640[a];[1:v]scale=360:640[b];[2:v]scale=360:640[c];[a][b][c]hstack=inputs=3[body];[3:v][body]vstack=inputs=2:shortest=1[v]','-map','[v]','-map','0:a:0','-t','30','-r','30','-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(OUT/'comparativo-3-modelos.mp4')]
subprocess.run(command,check=True)
report['side_by_side']='outputs/cg-bunker-v2-001/comparativo-3-modelos.mp4'
report['status']='technical_checks_passed_local_only'
(ROOT/'work/videos/cg-bunker-v2-001/comparison.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for v in report['variants']:print(f"{v['engine']}: {v['width']}x{v['height']}, {v['duration_seconds']}s, {v['frames']} quadros, áudio idêntico")
