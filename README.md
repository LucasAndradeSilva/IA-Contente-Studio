# AI Content Studio

Base inicial do projeto de automação de seis perfis de conteúdo: Kids, Bíblico e Conhecimentos Gerais, cada um no YouTube e no TikTok.

O objetivo atual é comparar três versões completas do bunker V2: HTML/CSS 3D, Three.js e Blender, com 30 segundos e 720 × 1280, usando GPT-6 Astra na criação. El Niño V1 e café permanecem como histórico.

## Bunker V2

Manifesto: `config/pilot_bunker_v2.json`. Instruções, fontes e comandos das três versões: `work/videos/cg-bunker-v2-001/production.md`. Saídas locais: `bunker-v2.mp4` (Three.js), `bunker-css3d-v2.mp4` e `bunker-blender-v2.mp4`, em `outputs/cg-bunker-v2-001/`.

```powershell
npm ci
.\.venv\Scripts\python.exe scripts/prepare_bunker_v2_audio.py
node scripts/render_browser_template.mjs templates/video-models/bunker-v2/index.html outputs/cg-bunker-v2-001/visual.mp4 30 30
.\.venv\Scripts\python.exe scripts/finish_bunker_v2.py
```

Requer a voz local e o modelo Whisper small já baixados, dependências de `requirements-qa.txt`, FFmpeg e Brave, Edge ou Chrome. As cenas compartilham um estilo único; o fluxo tem pesquisa factual e uma conferência técnica final, sem relatórios repetitivos entre papéis.

## Histórico da base e do El Niño V1

- Contexto e decisões registrados.
- Quinze papéis de agentes definidos, com onze originais e quatro novos.
- Contratos individuais dos quinze papéis criados.
- Skill do pipeline FatoNauta e máquina de estados criadas.
- Canal FatoNauta publicado com identidade inicial.
- Piloto El Niño com briefing, fontes oficiais, roteiro, storyboard e plano visual registrados.
- Candidato MP4 local produzido: 30 s, 1080 × 1920, 30 fps, narração, trilha original e legendas.
- QA técnico aprovado; escuta do MP4 e alinhamento fino das legendas ainda pendentes. Nenhum upload autorizado.
- Verificador de ambiente disponível.
- Python 3.13.17, FFmpeg 9.0.2, Blender 5.2.3 LTS e Piper TTS 1.8.0 instalados e validados.
- Voz `pt_BR-faber-medium` baixada e validada para testes locais do MVP.
- Liberação da voz para upload, Supabase, Runway e publicação ainda não configurados.

## Começar

No PowerShell:

```powershell
.\scripts\check_environment.ps1
python .\scripts\validate_project.py
python -m unittest discover -s tests
```

Requer Python 3.11 ou superior no PATH. O verificador apenas diagnostica o ambiente. Para preparar um novo clone para testes locais de voz:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m piper.download_voices --download-dir assets/voices/piper/pt_BR-faber-medium pt_BR-faber-medium
```

O modelo de voz (`.onnx`), o ambiente virtual e os arquivos em `outputs/` são locais e não entram no Git. Os arquivos de origem e as evidências de licença ficam versionados. O download da voz não libera nenhum upload, inclusive privado ou não listado; veja `assets/voices/piper/pt_BR-faber-medium/LICENSE_EVIDENCE.md`.

O MP4 histórico fica em `outputs/cg-el-nino-001/video/pilot_local.mp4` e não entra no Git. Os scripts antigos permanecem preservados; alguns dependem do manifesto ativo, portanto use a receita acima para a V2.

Em `config/pipeline_fatonauta.json`, o manifesto ativo define o estado atual. Os papéis entregam seus artefatos diretamente e somente a conferência técnica final libera o marco local.

A checagem opcional de fala roda localmente depois do primeiro download de um modelo de reconhecimento, guardado em `outputs/`. Ela compara a transcrição com o roteiro, mas não substitui a escuta:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-qa.txt
.\.venv\Scripts\python.exe scripts\check_speech_local.py
```

## Estrutura

- `AGENTS.md`: regras permanentes e arquitetura operacional.
- `.agents/roles/`: contratos de entrada, saída, limites e gates dos quinze papéis.
- `.agents/skills/fatonauta-video-pipeline/`: fluxo reutilizável carregado sob demanda pelo Codex.
- `docs/contexto_projeto.json`: decisões, sugestões, limites e pendências.
- `config/pipeline_fatonauta.json`: estados e transições do fluxo de criação.
- `config/visual_styles.json`: estilos, técnicas e prompt base para o vídeo inteiro.
- `config/pilot_bunker_v2.json`: manifesto ativo; os manifestos anteriores preservam o histórico.
- `work/videos/cg-el-nino-001/`: briefing, fontes e artefatos verificáveis do piloto.
- `workflows/fatonauta-youtube-shorts.md`: visão humana do fluxo e dos artefatos.
- `scripts/check_environment.ps1`: diagnóstico somente leitura.
- `scripts/validate_project.py`: valida o manifesto e a linha do tempo.
- `tests/`: testes determinísticos do contrato do piloto.

## Próximo gate

Concluir o QA editorial e de áudio do MP4 local. A Faber segue restrita a testes locais; qualquer upload depende da revisão da licença dos pesos e da autorização específica do proprietário.

