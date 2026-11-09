# Fluxo de criação — FatoNauta / YouTube Shorts

## Lógica

O fluxo é uma linha de produção com gates. `pipeline_state` indica o último marco aprovado. O papel `owner_role` do próximo estado produz o artefato indicado em `output`; o Orquestrador só registra esse novo estado após verificar o gate e guardar a evidência. Os demais papéis trabalham apenas quando acionados.

Cada papel confere a própria entrega antes de repassá-la: compara com as entradas e o contrato, verifica o gate e a segurança, corrige erros e revisa novamente. O registro de passagem contém verificações, correções, evidências, bloqueios abertos e resultado (`aprovado` ou `bloqueado`). Resultado bloqueado mantém o estado anterior. Quando houver `review_role`, sua revisão vem depois da auto-revisão; o Orquestrador faz a conferência final do gate antes de chamar o próximo papel.

```text
ideia/manifesto
  → briefing
  → pesquisa factual
  → roteiro + storyboard + revisão de alcance
  → escolha visual por cena
  → cenas
  → áudio + legendas
  → montagem
  → qualidade
  → título + thumbnail → metadados
  → autorização humana
  → publicação
  → métricas e aprendizado
```

No MVP do bunker, o fluxo termina em **qualidade**. Metadados podem ser preparados como rascunho, mas não há upload ou publicação automática.

O planejador editorial mantém uma proposta de calendário à parte. Depois que houver comentários, o gestor de comunidade prepara rascunhos de resposta. Agendamento e respostas públicas dependem de autorização específica.

O roteiro consulta `config/visual_styles.json` e sugere um estilo por cena; a direção visual escolhe e justifica técnica, custo, legibilidade e licença. HTML/CSS/JS, Canvas, SVG e Three.js são rotas possíveis para animação reproduzível. As imagens de referência fornecidas pelo usuário mostram categorias de estilo, não prompts completos; o catálogo contém prompts originais.

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

## Primeiro ciclo

1. Aprovar o briefing do bunker.
2. Criar o pacote factual com fontes primárias.
3. Fechar narração e storyboard de 30 segundos.
4. Definir uma solução visual leve para o notebook.
5. Confirmar as ferramentas locais e produzir o primeiro render de teste.
