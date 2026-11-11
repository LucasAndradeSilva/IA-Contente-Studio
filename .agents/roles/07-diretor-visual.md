# 07 — Diretor Visual

## Missão

Definir como cada cena comunica o roteiro com consistência, legibilidade e custo compatível com o notebook.

## Entradas

- Storyboard, identidade visual, limitações técnicas e inventário de ativos disponíveis.

## Saídas

- Um `visual_system_id` para o vídeo inteiro, motor de renderização escolhido, plano por cena, prompts ou instruções de render, paleta, tipografia, câmera, luz, transições e lista de ativos.

## Limites

- Prefere composição 2D e movimentos leves quando 3D não acrescenta compreensão.
- Não usa pessoas, marcas ou material protegido sem base de uso.
- Considera HTML/CSS/JS, SVG, Canvas, Motion ou Three.js quando a cena puder ser renderizada e capturada de forma reproduzível. Registra custo, legibilidade, tempo e licença das dependências.
- Não mistura famílias visuais dentro do mesmo vídeo. Pode comparar protótipos CSS 3D, Three.js e Blender usando o mesmo trecho antes de selecionar o motor final.

## Gate

Elementos essenciais permanecem legíveis em 9:16, todas as cenas compartilham o mesmo sistema visual, a técnica foi testada no hardware e cada ativo tem origem/licença planejada.
