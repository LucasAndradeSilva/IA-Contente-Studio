"""Monta o MP4 e registra somente a conferência técnica final."""
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
folder=ROOT/'outputs/cg-bunker-v2-001'
final=folder/'bunker-v2.mp4'
subprocess.run(['ffmpeg','-v','error','-y','-i',str(folder/'visual.mp4'),'-i',str(folder/'mix.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-t','30','-movflags','+faststart',str(final)],check=True)
data=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(final)],text=True))
v=next(s for s in data['streams'] if s['codec_type']=='video')
a=next(s for s in data['streams'] if s['codec_type']=='audio')
assert (v['width'],v['height'])==(720,1280)
assert abs(float(data['format']['duration'])-30)<.1
assert v['avg_frame_rate']=='30/1'
assert int(v['nb_frames'])==900
report={'video_id':'cg-bunker-v2-001','status':'technical_checks_passed_local_only','output':str(final.relative_to(ROOT)).replace('\\','/'),'width':v['width'],'height':v['height'],'duration_seconds':float(data['format']['duration']),'frames':int(v['nb_frames']),'fps':v['avg_frame_rate'],'video_codec':v['codec_name'],'audio_codec':a['codec_name'],'audio_sample_rate':a['sample_rate'],'file_bytes':int(data['format']['size']),'sources':'config/pilot_bunker_v2.json','captions':'outputs/cg-bunker-v2-001/captions.json','visual_preview':'outputs/cg-bunker-v2-001/preview.png','limitations':['Não houve escuta humana integral registrada.','Timestamps corrigidos por interpolação quando o ASR diverge do roteiro.','Faber autorizada apenas para teste local; upload pendente de licença.','Comparação adicional CSS 3D e Blender não produzida nesta versão.']}
path=ROOT/'work/videos/cg-bunker-v2-001/technical.json'
path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
captions=json.loads((folder/'captions.json').read_text(encoding='utf-8'))
def stamp(t):
    ms=round(t*1000);s,ms=divmod(ms,1000);m,s=divmod(s,60);h,m=divmod(m,60)
    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'
blocks=[]
for scene in range(6):
    words=[w for w in captions['words'] if scene*5 <= (w['start']+w['end'])/2 < (scene+1)*5]
    for i in range(0,len(words),5):
        chunk=words[i:i+5]
        blocks.append(f"{len(blocks)+1}\n{stamp(chunk[0]['start'])} --> {stamp(chunk[-1]['end'])}\n"+' '.join(w['text'] for w in chunk)+'\n')
(folder/'legendas.srt').write_text('\n'.join(blocks),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
