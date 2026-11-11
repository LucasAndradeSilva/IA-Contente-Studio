# Fluxo de criação — FatoNauta / YouTube Shorts

## Lógica

O fluxo é uma linha de produção com gates. `pipeline_state` indica o último marco aprovado. O papel `owner_role` do próximo estado produz o artefato indicado em `output`; o Orquestrador só registra esse novo estado após verificar o gate e guardar a evidência. Os demais papéis trabalham apenas quando acionados.

Cada papel entrega diretamente seu artefato. A V2 remove relatórios repetitivos de auto-revisão e ciclos genéricos de aprovação. As duas conferências obrigatórias são fontes antes do roteiro e propriedades técnicas do MP4 final. Falhas concretas voltam ao responsável.

```text
ideia/manifesto
  → briefing
  → pesquisa factual
  → roteiro + storyboard + revisão de alcance
  → sistema visual único + plano de cenas
  → cenas
  → áudio + legendas
  → montagem
  → qualidade
  → título + thumbnail → metadados
  → autorização humana
  → publicação
  → métricas e aprendizado
```

No MVP atual do bunker V2, o fluxo termina na conferência técnica local. Metadados podem ser preparados como rascunho, mas não há upload ou publicação automática.

O planejador editorial mantém uma proposta de calendário à parte. Depois que houver comentários, o gestor de comunidade prepara rascunhos de resposta. Agendamento e respostas públicas dependem de autorização específica.

O roteiro consulta `config/visual_styles.json` e sugere famílias para o vídeo inteiro. A direção visual escolhe um sistema único e define foco e movimento por cena. HTML/CSS/JS, Canvas, SVG, Three.js e Blender são rotas possíveis. GPT-6 Astra executa os papéis criativos; o motor selecionado renderiza a mídia.

## Artefatos por vídeo

Quando a produção começar, cada vídeo deverá manter uma pasta própria com:

```text
work/videos/<video_id>/
  manifest.json
  research/sources.json
  script/voice.txt
  script/storyboard.json
  visual/plan.json
  media/
  audio/
  captions/
  renders/
  reports/qa.json
  publish/metadata.json
```

Os arquivos pesados podem permanecer fora do versionamento, mas seus nomes, hashes, origem e licenças devem constar no manifesto ou nos relatórios.

## Retornos por falha

| Falha | Retorno |
|---|---|
| Afirmação sem fonte ou exagerada | Pesquisa |
| Narração longa ou confusa | Roteiro |
| Cena ilegível ou incoerente | Direção visual |
| Ativo ausente, corrompido ou sem licença | Produção de mídia |
| Voz mascarada, corte ou legenda fora de sincronia | Áudio |
| Duração, resolução ou quadro preto | Montagem/produção de mídia |
| Título não entregue pelo vídeo | SEO |
| Métrica ausente | Aguardar dado oficial; não estimar como real |

## Estado do primeiro ciclo

1. Briefing e pesquisa factual do El Niño registrados.
2. Roteiro e storyboard auto-revisados e aprovados pelo Estrategista de Alcance.
3. Animação 2D e áudio local renderizados; MP4 com legendas montado.
4. QA técnico passou; escuta e sincronismo fino das legendas ainda impedem `qa_passed`.
