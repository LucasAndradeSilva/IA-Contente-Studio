"""Narração Faber, cama sonora original e timestamps locais para a V2."""
import json
import difflib
import re
import unicodedata
import math
import random
import subprocess
import wave
from array import array
from pathlib import Path

from piper import PiperVoice
from piper.config import SynthesisConfig
from faster_whisper import WhisperModel

ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT / 'config/pilot_bunker_v2.json').read_text(encoding='utf-8'))
out = ROOT / 'outputs' / manifest['video_id']
out.mkdir(parents=True, exist_ok=True)
sr = 22050
voice = PiperVoice.load(str(ROOT / 'assets/voices/piper/pt_BR-faber-medium/pt_BR-faber-medium.onnx'))
mix = array('h', [0]) * (sr * 30)
records = []
for scene in manifest['timeline']:
    target = out / f"voice-{scene['scene']}.wav"
    with wave.open(str(target), 'wb') as f:
        voice.synthesize_wav(scene['voice'], f, SynthesisConfig(length_scale=1.03))
    with wave.open(str(target), 'rb') as f:
        duration = f.getnframes()/f.getframerate()
    # A pequena folga preserva o fim da fala antes da próxima cena.
    speed = max(1.0, duration/4.65)
    fitted = out / f"voice-{scene['scene']}-fit.wav"
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(target),'-af',f'atempo={speed}',str(fitted)],check=True)
    with wave.open(str(fitted),'rb') as f:
        pcm=array('h');pcm.frombytes(f.readframes(f.getnframes()))
    start=round((scene['start']+.12)*sr)
    for i, sample in enumerate(pcm):
        mix[start+i]=int(sample*.76)
    records.append({'scene':scene['scene'],'start':scene['start']+.12,'duration':len(pcm)/sr,'speed':speed})
raw=out/'voice.wav'
def save(path, pcm):
    with wave.open(str(path),'wb') as f:
        f.setnchannels(1);f.setsampwidth(2);f.setframerate(sr);f.writeframes(pcm.tobytes())
save(raw,mix)
rng=random.Random(37)
for i in range(len(mix)):
    t=i/sr;fade=min(1,t/.6,(30-t)/.8)
    bed=.005*(math.sin(2*math.pi*110*t)+.35*math.sin(2*math.pi*165*t))*fade
    d=t%5
    fx=.018*math.exp(-d*20)*math.sin(2*math.pi*(220-70*d)*t) if d<.3 else 0
    mix[i]=int(max(-32760,min(32760,mix[i]+32767*(bed+fx))))
save(out/'mix-raw.wav',mix)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(out/'mix-raw.wav'),'-af','loudnorm=I=-16:TP=-1.5:LRA=9','-ar','48000',str(out/'mix.wav')],check=True)
model=WhisperModel('small',device='cpu',compute_type='int8',cpu_threads=6,download_root=str(ROOT/'outputs/models/faster-whisper'),local_files_only=True)
segments,_=model.transcribe(str(raw),language='pt',beam_size=3,word_timestamps=True,vad_filter=False,initial_prompt='Bunker, abrigo suíço, concreto armado, beliches, sanitários secos, ventilação.')
observed=[{'text':w.word.strip(),'start':round(w.start,3),'end':round(w.end,3)} for s in segments for w in (s.words or [])]
def norm(t):
    return re.sub(r'[^a-z0-9]', '', unicodedata.normalize('NFKD',t.lower()).encode('ascii','ignore').decode())
words=[]
for sc, timing in zip(manifest['timeline'],records):
    expected=sc['voice'].split()
    spoken=[w for w in observed if sc['start'] <= (w['start']+w['end'])/2 < sc['end']]
    matcher=difflib.SequenceMatcher(a=[norm(w) for w in expected],b=[norm(w['text']) for w in spoken],autojunk=False)
    for op,a,b,c,d in matcher.get_opcodes():
        if op=='equal':
            words.extend({**spoken[c+i], 'text':expected[a+i], 'alignment':'asr'} for i in range(b-a))
        elif b>a:
            left=spoken[c]['start'] if c<len(spoken) else timing['start']+timing['duration']-.2
            right=spoken[d-1]['end'] if d>c else min(timing['start']+timing['duration'], left+.2*(b-a))
            for i in range(b-a):
                words.append({'text':expected[a+i],'start':round(left+(right-left)*i/(b-a),3),'end':round(left+(right-left)*(i+1)/(b-a),3),'alignment':'interpolated_mismatch'})
(out/'captions.json').write_text(json.dumps({'words':words,'observed':observed,'scenes':records,'method':'Texto do roteiro alinhado com timestamps ASR; divergências interpoladas e marcadas.'},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(records,ensure_ascii=False));print(' '.join(w['text'] for w in words))
