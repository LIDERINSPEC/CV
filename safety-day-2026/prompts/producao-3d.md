# Produção da animação 3D — prompts e plano de geração

A edição (legendas, títulos, cartões, logo, tela final e QR code) já está pronta em `pipeline/`.
Esta etapa gera **só a imagem animada e as vozes**. Nenhum texto, logo ou QR é pedido à IA.

Ferramenta: Runway (workspace "Lider", plano Pro).
- Imagens de referência: `nano-banana-pro`, 9:16.
- Vozes: `eleven_v4`, `languageCode: pt`, vozes brasileiras escolhidas via `search_voices`.
- Cenas: `seedance-2.5`, 9:16, 1080p, com `referenceImages` (personagens + fábrica) e `referenceAudio`
  (a fala da cena), para a sincronia labial seguir o áudio real em português.
  Rodar antes um teste em `draft: true` (480p) para medir o custo por segundo e a qualidade.

Entrega dos arquivos: `scenes/s01.mp4 … s08.mp4` e `voices/dialogue.wav` → `python3 pipeline/build.py`.

---

## Bíblia de estilo (vai no início de todos os prompts)

> Cinematic 3D animated feature-film style, appealing stylized adult characters with natural proportions,
> subtle facial acting, soft global illumination, detailed materials (fabric weave, brushed steel,
> matte plastic), shallow depth of field, warm-neutral color grade. Professional, calm, adult tone.
> Vertical 9:16 composition. No text, no letters, no logos, no watermarks, no brand marks anywhere in the image.
> No neon. Smooth, slow camera moves.

## Personagem 1 — Lia (ref-lia)

> Brazilian woman, about 35, warm brown skin, brown eyes, brown hair tied in a low bun tucked fully under the helmet.
> Confident, attentive, kind expression. Navy-blue industrial work uniform (#133969 tone) with a thin gold piping
> detail on the shoulder seam, blank rectangular ID patch on the chest (left empty — the real logo is added in editing),
> work trousers, black safety boots, clear safety glasses, compact over-the-ear hearing protection.
> GREEN hard hat with, on the front, a round white disc containing a solid green cross (prevention symbol) —
> crisp, centered, high-contrast, identical in every shot.
> Character turnaround: front, three-quarter, side. Neutral studio background.

## Personagem 2 — Operador (ref-operador)

> Brazilian man, about 40, friendly face, short dark hair with a few grey strands, light stubble.
> Grey industrial work uniform, clear safety glasses, earplugs on a cord, safety boots, white hard hat.
> Approachable, attentive, humble — a good professional who got momentarily distracted, never a caricature.
> Character turnaround: front, three-quarter, side. Neutral studio background.

## Ambiente (ref-fabrica)

> Clean, organized machining shop. Enclosed CNC machining center with its safety door CLOSED and a viewing window
> showing coolant mist inside. Control panel beside the operator position. Yellow-and-black floor demarcation,
> marked walkways, generic pictogram safety signs (no readable text). A clearly separated "safe phone point":
> a small wall station with a green pictogram sign of a phone, located away from the machines, beside the walkway.
> Soft daylight from high windows mixed with cool industrial light.

---

## Cenas (tempos da linha do tempo final)

Regras em todas as cenas: porta do CNC sempre fechada; nenhum contato com partes móveis; nenhuma proteção aberta;
nenhum acidente; Lia nunca toca no operador; o operador nunca deixa o posto com o ciclo rodando.
Rostos entre y≈760 e y≈1150 do quadro vertical; terço superior e faixa inferior livres para os textos da edição.

| Cena | Tempo | Duração | Áudio de referência | Prompt |
|---|---|---|---|---|
| s01 | 0–8 s | 8 s | Operador: "Enquanto a máquina termina… dá tempo de responder rapidinho." | Slow vertical establishing shot gliding through @fabrica toward @operador standing at his correct position beside the closed CNC machining center. A phone in his hand vibrates; brief close-up of a glowing notification bubble with no readable text and no app icons. He glances down at the phone, his attention visibly leaving the machine. He speaks the line in audio 1 with accurate lip sync. |
| s02 | 8–15 s | 7 s | Lia: "Oi! Posso falar um instante com você?" / Operador: "Claro!" | @lia notices the distraction and walks into @operador's line of sight from the front, stopping at a respectful distance without touching him. Medium two-shot, closed CNC in the background. She speaks audio 1, he answers audio 2 with a friendly nod. Accurate lip sync. |
| s03a | 15–25 s | 10 s | Lia: "Sei que sou visitante aqui. Mas, na Líder… do que a vida. O celular pode tirar sua atenção de um risco." | Two-shot, @lia speaking calmly and warmly to @operador, closed CNC behind them, she keeps an attentive, caring expression. Accurate lip sync to audio 1. |
| s03b | 25–34 s | 9 s | Lia: "Guarda enquanto acompanha a operação? Se for urgente, peça cobertura e use o ponto seguro." | @lia gestures gently toward the safe phone point sign in the distance; @operador nods and puts the phone in his pocket. Accurate lip sync to audio 1. |
| s04 | 34–44 s | 10 s | Operador: "Obrigado pelo toque…" / Lia: "Pra cuidar de alguém…" | Over-the-shoulder on @operador, grateful, then subtle close-up on @lia answering softly; short pause, @operador shows recognition. Lip sync to audio 1 and 2. |
| s05 | 44–50 s | 6 s | Operador: "Mais gente precisava ouvir isso. Segurança é responsabilidade de todo mundo, né?" | Medium shot, @operador reflective, @lia smiles discreetly. Lip sync to audio 1. |
| s06a | 50–60 s | 10 s | Lia: "Exatamente! Vem para o Safety Day 2026… no SENAI Barueri." | Medium shot of @lia, enthusiastic yet calm, open hand gestures, generous headroom (upper third of frame empty factory background). Lip sync to audio 1. |
| s06b | 60–69 s | 9 s | Lia: "Presencial e gratuito! Especialistas, fornecedores e clientes…" | Same framing, gentle push-in, @lia nodding with conviction. Lip sync to audio 1. |
| s07 | 69–78 s | 9 s | Operador: "Vou me inscrever! Mas o celular… só depois, no ponto seguro." / Lia: "Isso aí!" | @operador smiles, pats the pocket where the phone stays put, turns attention back to the CNC control panel; @lia replies with a light approving smile. Light humor. Lip sync to audio 1 and 2. |
| s08 | 78–84 s | 6 s | Lia: "Inscreva-se pelo link ou QR code. É gratuito, mas as vagas são limitadas!" | @lia turns to camera, medium close-up, warm confident direct address. Lip sync to audio 1. Leave the last 0.6 s calm (brand wipe in editing). |

Depois de gerar: cortar cada cena exatamente na janela de tempo, juntar s03a+s03b em `scenes/s03.mp4` e s06a+s06b em
`scenes/s06.mp4`, montar `voices/dialogue.wav` com as falas na posição da linha do tempo, ajustar os tempos das
legendas em `roteiro/cues.json` ao áudio real e rodar `python3 pipeline/build.py`.
