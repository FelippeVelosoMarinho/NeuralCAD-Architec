---
phase: 03-vs-code-like-ui-3d-foundation
kind: ui-design-contract
status: draft
created: 2026-05-03
---

# NeuralCAD Architect — UI-SPEC (Fase 3)

## Product intent

Interface **multimodal** familiar a utilizadores IDE: comando natural no centro, modelo 3D visível ao lado ou em segundo separador, diagnósticos e próximos passos no pé.

## Regions (VS Code analogue)

| Região | Anchoring | Purpose | MVP behaviour |
|--------|-----------|---------|---------------|
| **Activity bar** *(opcional fase*) | Esquerda 48px | Ícones de modo | Pode ser **omitida** em 03-01; usar só sidebar expandida. |
| **Sidebar (primary)** | Esquerda 240–280px resizável | Explorer de topologia (árvore) | Pastas **Root → Corpo → Faces / Arestas / Vértices** alinhadas a dados do job. |
| **Editor group (centre)** | Flex 1 | Monaco + Viewport | **Tabs** “Prompt” \| “3D” com estado conservado ao alternar. |
| **Panel (bottom)** | Dock 120–200px colapsável | Copiloto / lint / progresso texto | Mensagens estáticas + estado job (`pending`/`running`/`success`/`failed`). |
| **Status bar** *(opcional)* | Inferior 22px | Sessão / API target | Mostrar `API: http://…` de `VITE_API_BASE_URL`. |

## Visual language

- **Base:** tema **dark** inspiração VS Code (*not* a pixel-perfect fork).
- **Tipografia UI:** system stack `system-ui, Segoe UI, sans-serif`; **Monaco** só no editor.
- **Cores chave (semântica):** `--bg-app`, `--bg-panel`, `--border`, `--accent`, `--text`, `--text-muted`, `--error`, `--success`.
- **Densidade:** confortável para leitura prolongada; padding mínimo 8px em painéis.

## Keyboard & a11y

- `Ctrl/Cmd+Enter` no Monaco → acionar **submeter prompt** (atalho documentado no tooltip).
- Regiões principais com `aria-label` em inglês ou português conforme `i18n` futuro; foco visível.

## Motion

- Transições de painel **≤ 200ms**; viewport 3D sem animação de câmara obrigatória no MVP.

## Responsive

- Desktop first (≥1280px). Abaixo disso: sidebar pode colapsar para drawer (nice-to-have; não bloqueia fase).

## Out of scope (Fase 3)

- Fluxo realtime WebSocket-only (Phase 4).
- Diff visual entre versões.

---

*Gerado pelo `/gsd-plan-phase 3` para satisfazer o UI safety gate.*
