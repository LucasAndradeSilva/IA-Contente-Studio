# Bunker V2 — produção local

Pedido: retomar o bunker usando GPT-6 Astra para executar os papéis criativos e entregar três versões completas. O termo “ATRAS” foi esclarecido pelo proprietário nesta conversa. Os motores de mídia são HTML/CSS 3D, Three.js e Blender.

Briefing, roteiro de seis cenas, direção visual, fontes e licenças estão no manifesto `config/pilot_bunker_v2.json`. Cada versão usa 720 × 1280, 30 segundos e 900 quadros nativos. O relatório `comparison.json` registra os arquivos finais e confirma a mesma faixa de áudio nas três versões.

Fonte factual: [Federal Office for Civil Protection, Shelters for the population](https://www.babs.admin.ch/en/shelters-for-the-population), consultada em 2026-11-09. Escopo: abrigos civis suíços. Estrutura, ventilação, equipamentos, saída de emergência e manutenção são sustentados pelas seções Structure of a shelter, Supplies e Maintenance obligation. Não generalizar a todos os bunkers.

Sistema visual: maquete low-poly em corte, uma família de materiais e paleta marinho/ciano/laranja/creme; seis focos sucessivos no mesmo ambiente. A geometria é uma ilustração original, sem escala ou pretensão de planta construtiva.

Áudio: Piper Faber local; texto do manifesto, uma fala por cena. Textura e efeitos sintetizados pelo script, sem amostras externas. Legendas usam o texto correto do roteiro alinhado aos tempos de palavras do Whisper local; divergências de reconhecimento são interpoladas e identificadas no JSON.

Reprodução:

1. `.venv/Scripts/python.exe scripts/prepare_bunker_v2_audio.py`
2. `node scripts/render_browser_template.mjs templates/video-models/bunker-v2/index.html outputs/cg-bunker-v2-001/visual.mp4 30 30`
3. FFmpeg combina `visual.mp4` e `mix.wav` em `bunker-v2.mp4`, copiando vídeo e codificando áudio AAC.

Direitos: geometria e trilha originais; Roboto sob OFL, Three.js MIT. Voz Faber liberada somente para teste local, com a pendência dos pesos registrada em `assets/voices/piper/pt_BR-faber-medium/LICENSE_EVIDENCE.md`. Nenhum upload autorizado.

## Variantes completas

- Three.js: `outputs/cg-bunker-v2-001/bunker-v2.mp4`; geometria WebGL e HTML.
- HTML/CSS 3D: `outputs/cg-bunker-v2-001/bunker-css3d-v2.mp4`; geometria feita com elementos DOM e transformações CSS, sem Three.js.
- Blender: `outputs/cg-bunker-v2-001/bunker-blender-v2.mp4`; maquete criada e animada no Blender, render nativo Workbench com iluminação de estúdio, sombras e oclusão. Não usa imagens Three.js na região da maquete. Compartilha os overlays de texto/legenda para manter a comparação consistente.

Reprodução das duas variantes adicionais, após gerar a primeira versão e preservar seus quadros:

```powershell
blender --background --python scripts/render_blender_bunker_v2.py
node scripts/render_browser_template.mjs templates/video-models/bunker-background/index.html outputs/cg-bunker-v2-001/background.png 30 30 0
node scripts/render_browser_template.mjs templates/video-models/bunker-css3d/index.html outputs/cg-bunker-v2-001/css3d-visual.mp4 30 30
.\.venv\Scripts\python.exe scripts/compose_blender_bunker_v2.py
.\.venv\Scripts\python.exe scripts/finish_bunker_comparison.py
```

O projeto editável do Blender está em `outputs/cg-bunker-v2-001/blender/bunker-v2.blend`; o script gerador fica versionado. A região 3D contém 900 renders nativos, sem repetição de um único quadro estático.
