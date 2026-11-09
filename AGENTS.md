# AI Content Studio — instruções do repositório

## Objetivo atual

Construir e homologar uma fábrica de vídeos curtos com IA, começando por um único piloto de Conhecimentos Gerais: vídeo vertical de 30 segundos sobre como funcionaria um bunker subterrâneo.

## Ordem de homologação

1. Conhecimentos Gerais no YouTube.
2. Conhecimentos Gerais no TikTok.
3. Bíblico no YouTube e depois no TikTok.
4. Kids no YouTube e depois no TikTok.

Não escalar para o próximo canal ou plataforma antes de registrar os critérios de aceite do estágio atual.

## Arquitetura de agentes

As onze funções originais e quatro funções novas são papéis lógicos; não são processos permanentes nem assinaturas:

1. Orquestrador Geral — prioriza trabalhos, aplica gates e controla estados.
2. Gestor Kids — mantém identidade, público e regras do nicho infantil.
3. Gestor Bíblico — mantém identidade, fontes e abordagem do nicho bíblico.
4. Gestor Conhecimentos Gerais — mantém identidade e linha editorial do nicho factual.
5. Pesquisador de Tendências e Fontes — encontra temas, verifica fatos e registra fontes.
6. Roteirista e Storyboard — cria gancho, roteiro cronometrado e plano de cenas.
7. Diretor Visual — escolhe técnica, estilo e consistência visual.
8. Produtor de Mídia — gera ou renderiza cenas e prepara ativos.
9. Diretor de Áudio — cuida de TTS, música, efeitos, mixagem e licenças.
10. SEO e Publicação — prepara metadados por plataforma e publica apenas com autorização.
11. Analista de Qualidade e Métricas — valida o vídeo e aprende com retenção e desempenho.
12. Diretor de Títulos e Thumbnails — cria e testa embalagens coerentes com o vídeo.
13. Gestor de Comunidade — prepara respostas a comentários e identifica dúvidas recorrentes.
14. Planejador Editorial — organiza Shorts, vídeos longos e posts da comunidade em um calendário.
15. Estrategista de Alcance — revisa ganchos, ritmo, compartilhamento e hipóteses de retenção.

Os onze primeiros preservam a arquitetura anterior; os papéis 12 a 15 foram acrescentados em 2026-11-09. Alcance potencial não é garantia de viralização.

## Princípios obrigatórios

- Linguagem principal: Python.
- Trabalho determinístico: Python e FFmpeg; decisões criativas: agentes.
- Blender é opcional para 3D e deve respeitar as limitações da GPU Radeon integrada.
- Supabase será memória operacional, não depósito principal de vídeos pesados no plano gratuito.
- Runway/MCP é opcional; conexão não implica gratuidade e nenhuma geração deve ocorrer sem verificar créditos e autorização.
- Preferir APIs oficiais e integrações autorizadas para publicação e métricas.
- Nunca inventar fatos, fontes, métricas, custos, credenciais, tokens, IDs de conta ou permissões.
- Nunca guardar segredos no repositório. Usar variáveis de ambiente e um arquivo `.env` ignorado.
- Nenhuma publicação, criação de conta, compra, assinatura ou consumo pago é autorizado por uma tarefa de desenvolvimento.
- Conteúdo Kids deve cumprir classificação de público e regras específicas da plataforma.
- Para publicação ou distribuição, vozes, músicas, efeitos, imagens, modelos e fontes precisam de licença comercial e multiplataforma verificável. Testes estritamente locais podem usar ativos com licença pendente se a origem e a restrição estiverem registradas; isso não libera upload, mesmo privado ou não listado.
- Não representar pessoas reais ou clonar vozes sem consentimento e base legal.
- Registrar falhas e incertezas; não marcar etapas como concluídas sem evidência.

## Critério do piloto

O piloto só passa quando houver um MP4 1080 × 1920, 30 s, com roteiro, cenas, narração, trilha/efeitos licenciados, legendas sincronizadas, áudio inteligível, arquivos de origem e relatório de validação. A publicação fica fora do primeiro gate.

## Forma de trabalho

- Fazer mudanças pequenas e testáveis.
- Preservar decisões em `docs/contexto_projeto.json`.
- Manter dados de cada vídeo em um manifesto versionado.
- Usar `channels/<canal>/specifications.md` como fonte de verdade da identidade e das regras do canal.
- Usar `.agents/roles/*.md` como contratos dos quinze papéis; carregar somente os papéis exigidos pela etapa atual.
- Usar `config/visual_styles.json` como catálogo de estilos e registrar a escolha por cena no manifesto antes de produzir mídia.
- Usar `.agents/skills/fatonauta-video-pipeline/SKILL.md` para iniciar ou retomar o fluxo do FatoNauta.
- Usar `config/pipeline_fatonauta.json` como máquina de estados do piloto.
- Em modo de simulação, não chamar serviços externos.
- Validar JSON e testes locais antes de avançar.

## Precedência das fontes

Quando houver conflito, aplicar esta ordem: regras de segurança deste arquivo, especificação do canal, manifesto do vídeo, contrato do papel ativo e sugestões criativas. Uma sugestão nunca pode alterar fatos, licenças, autorização de publicação ou identidade consolidada sem registrar uma decisão.

## Regra de execução dos papéis

Os quinze papéis não ficam ativos ao mesmo tempo. O Orquestrador seleciona o próximo estado, carrega apenas os contratos necessários, exige o artefato de saída e registra o resultado. Uma etapa reprovada retorna ao papel que pode corrigir a causa; não se mascara uma falha em uma etapa posterior. Respostas a comentários, agendamento e publicação externa exigem autorização específica.

Antes de entregar sua demanda, cada papel deve revisar o próprio artefato contra as entradas, seu contrato, o gate da etapa e as regras de segurança. Deve corrigir os erros encontrados e repetir a revisão. A entrega inclui um registro curto do que foi conferido, correções feitas, evidências e pendências. Se houver erro ou pendência que impeça o gate, o papel informa o bloqueio e não marca a etapa como aprovada. Só após a auto-revisão aprovada o Orquestrador verifica o gate e aciona o próximo papel. A auto-revisão não substitui revisão independente prevista no pipeline nem autorização humana para ações externas.

