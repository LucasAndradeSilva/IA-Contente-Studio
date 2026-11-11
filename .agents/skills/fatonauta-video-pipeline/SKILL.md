---
name: fatonauta-video-pipeline
description: Planejar, produzir, validar ou retomar um Short do canal FatoNauta, do briefing ao pacote de publicação, usando os gates e artefatos do AI Content Studio.
---

# Pipeline FatoNauta

Use esta skill quando o pedido tratar da criação de um vídeo do FatoNauta ou da continuidade de uma etapa do pipeline.

## Fontes obrigatórias

Antes de agir, leia:

1. `channels/fatonauta-youtube/specifications.md` para identidade e regras editoriais.
2. O manifesto do vídeo em `config/` para o objetivo e o estado do trabalho.
3. `config/pipeline_fatonauta.json` para descobrir a etapa atual, a próxima transição e o papel responsável.
4. Somente os contratos em `.agents/roles/` exigidos pela etapa atual.
5. `config/visual_styles.json` quando selecionar ou produzir um estilo visual.

## Execução

- O estado registrado é o último marco aprovado. Leia o campo `next`, acione o `owner_role` desse próximo estado e não refaça artefatos aprovados sem motivo documentado.
- Produza o `output` do próximo estado e registre fontes, licenças, incertezas e bloqueios aplicáveis.
- Evite relatórios de auto-revisão e confirmações entre papéis. Entregue o artefato e avance; se houver falha concreta, retorne diretamente ao papel capaz de corrigi-la.
- Faça apenas duas conferências obrigatórias: fontes antes do roteiro e propriedades técnicas do MP4 no final. Isso não substitui autorização humana para upload, publicação ou gasto.
- O roteiro sugere intenções visuais; o Diretor Visual escolhe uma única família de estilo para todas as cenas e um motor de renderização. Protótipos curtos podem comparar motores antes da escolha.
- Mantenha fatos separados de hipóteses e dramatizações.
- Não invente pesquisa, licença, métrica, custo, credencial ou evidência de validação.
- No MVP, pare em `qa_passed`. Upload e publicação são fases separadas e exigem autorização explícita no momento da ação.
- Serviços pagos e geração externa permanecem desativados até decisão registrada.

## Roteamento dos papéis

- Controle de estado e exceções: `.agents/roles/01-orquestrador-geral.md`.
- Identidade do FatoNauta: `.agents/roles/04-gestor-conhecimentos-gerais.md`.
- Pesquisa: `.agents/roles/05-pesquisador-tendencias-fontes.md`.
- Roteiro e storyboard: `.agents/roles/06-roteirista-storyboard.md`.
- Direção visual: `.agents/roles/07-diretor-visual.md`.
- Hipóteses de alcance e revisão do gancho: `.agents/roles/15-estrategista-alcance.md`.
- Produção das cenas: `.agents/roles/08-produtor-midia.md`.
- Narração e mixagem: `.agents/roles/09-diretor-audio.md`.
- Metadados: `.agents/roles/10-seo-publicacao.md`.
- Título e thumbnail: `.agents/roles/12-titulos-thumbnails.md`.
- Validação e aprendizado: `.agents/roles/11-qualidade-metricas.md`.
- Calendário de conteúdo: `.agents/roles/14-planejador-editorial.md`.
- Comentários após publicação: `.agents/roles/13-gestor-comunidade.md`.

Os gestores Kids e Bíblico não participam do piloto FatoNauta; seus contratos existem para a expansão futura.
