# AI Content Studio

Base inicial do projeto de automação de seis perfis de conteúdo: Kids, Bíblico e Conhecimentos Gerais, cada um no YouTube e no TikTok.

O primeiro objetivo é deliberadamente menor: produzir e validar localmente um vídeo vertical de 30 segundos sobre bunker, sem publicar e sem consumir serviços pagos.

## Estado atual

- Contexto e decisões registrados.
- Quinze papéis de agentes definidos, com onze originais e quatro novos.
- Contratos individuais dos quinze papéis criados.
- Skill do pipeline FatoNauta e máquina de estados criadas.
- Canal FatoNauta publicado com identidade inicial.
- Manifesto do piloto criado e validável.
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

Este repositório ainda contém a estrutura e os contratos do processo. O MP4 do piloto, os scripts de renderização e a integração de publicação ainda não foram produzidos. Em `config/pipeline_fatonauta.json`, cada estado significa o último marco aprovado; o próximo estado só é registrado após seu artefato e gate serem verificados.

## Estrutura

- `AGENTS.md`: regras permanentes e arquitetura operacional.
- `.agents/roles/`: contratos de entrada, saída, limites e gates dos quinze papéis.
- `.agents/skills/fatonauta-video-pipeline/`: fluxo reutilizável carregado sob demanda pelo Codex.
- `docs/contexto_projeto.json`: decisões, sugestões, limites e pendências.
- `config/pipeline_fatonauta.json`: estados e transições do fluxo de criação.
- `config/visual_styles.json`: estilos, técnicas e prompt base para decisão por cena.
- `config/pilot_bunker.json`: contrato do primeiro vídeo.
- `workflows/fatonauta-youtube-shorts.md`: visão humana do fluxo e dos artefatos.
- `scripts/check_environment.ps1`: diagnóstico somente leitura.
- `scripts/validate_project.py`: valida o manifesto e a linha do tempo.
- `tests/`: testes determinísticos do contrato do piloto.

## Próximo gate

Executar as três primeiras etapas do piloto: briefing, pesquisa factual e roteiro/storyboard. Usar a Faber apenas em testes locais e manter o gate de upload pendente até a revisão final da licença dos pesos. Depois, implementar o renderizador local e medir tempo, qualidade e custo.

