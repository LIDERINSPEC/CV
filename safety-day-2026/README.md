# Safety Day 2026 — Reels animado (Líder)

Reels vertical de 90 s (1080 × 1920, 30 fps) que divulga o Safety Day 2026. Estilo de animação 3D cinematográfica, com Lia (Inspetora da Líder) e o Operador.

## Situação

| Parte | Status |
|---|---|
| Roteiro com tempos, legendas PT-BR (`roteiro/cues.json`, `roteiro/legendas.srt`) | pronto |
| Títulos, identificação "Lia \| Inspetora da Líder", cartões do convite, transição diagonal | pronto |
| Tela final 84–90 s (azul #133969, filetes ouro, logo original, QR code testado) | pronto |
| Trilha instrumental, ambiente de usinagem e notificação (sintetizados, com ducking) | pronto |
| Animação 3D das cenas + vozes com sincronia labial | **aguardando autorização de créditos** (ver `prompts/producao-3d.md`) |

Sem as cenas animadas, o pipeline monta uma **prévia (animatic)** com a descrição de cada plano no lugar da animação. Com isso dá para aprovar o ritmo, os textos e a tela final.

## Como montar

```bash
pip install numpy scipy pillow qrcode opencv-python-headless
python3 pipeline/build.py           # → output/safety-day-2026-reels-1080x1920.mp4
python3 pipeline/build.py --stills  # só quadros-chave para conferir
```

Quando as cenas forem geradas, coloque `scenes/s01.mp4 … s08.mp4` e `voices/dialogue.wav`, ajuste os tempos das legendas ao áudio real em `roteiro/cues.json` e rode o comando de novo. O vídeo final sai com exatamente 90,0 s.

## Verificações feitas na prévia

- Duração 90,000 s, 2700 quadros, H.264 High + AAC 48 kHz, `+faststart`.
- QR code lido no quadro exportado (86,5 s): `https://liderinspecoes.com.br/safetyday2026/`.
- Tela final idêntica de 84,0 s a 90,0 s.
- Loudness integrado em torno de −15 LUFS (alvo de redes sociais).
- Textos dentro da zona segura do Reels (x 80–960, y 220–1540). Legendas com no máximo 2 linhas.

## Identidade visual

Usa as cores e fontes pedidas no briefing: #133969, #d29d18, #f9faf8, #858e9a, Saira Semi Condensed e Inter. O logo é o arquivo original (`assets/logo-lider-original.jpg`), só recortado e aplicado sobre a placa clara, sem redesenho.

> Atenção: o Design System Líder publicado (Brandbook V1) marca #133969, #D29D18, Saira e Inter como **obsoletos** e indica #25437A / #BF9000 / Roboto. Esta peça seguiu o briefing. Para trocar, basta alterar as constantes no início de `pipeline/graphics.py`.
