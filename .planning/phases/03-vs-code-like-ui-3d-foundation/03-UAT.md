---
status: testing
phase: 03-vs-code-like-ui-3d-foundation
source:
  - 03-01-SUMMARY.md
  - 03-02-SUMMARY.md
  - 03-03-SUMMARY.md
started: 2026-05-03T12:00:00Z
updated: 2026-05-03T15:30:00Z
---

## Current Test

number: 1
name: Cold Start Smoke Test
expected: |
  Com o stack backend parado (ou após garantir estado limpo), segues o README para subir `docker compose up --build` (ou `-d`). Postgres e Redis ficam healthy; sem erros fatais de arranque nos serviços críticos. Num pedido rápido à API na porta configurada (`HOST_API_PORT` ou 8000), `GET /health` responde com sucesso. Em seguida, na pasta services/web, depois de `npm install`, `npm run dev` corre sem crash imediato; o URL do Vite (ex.: 5173) abre a app no browser.
awaiting: user response

## Tests

### 1. Cold Start Smoke Test

expected: |
  Com o stack backend parado (ou após garantir estado limpo), segues o README para subir `docker compose up --build` (ou `-d`). Postgres e Redis ficam healthy; sem erros fatais de arranque nos serviços críticos. Num pedido rápido à API na porta configurada (`HOST_API_PORT` ou 8000), `GET /health` responde com sucesso. Em seguida, na pasta services/web, depois de `npm install`, `npm run dev` corre sem crash imediato; o URL do Vite (ex.: 5173) abre a app no browser.
result: [pending]

### 2. Shell VS Code-like e estado persistente

expected: |
  Na app web, ves regiões de layout coherentes com um shell tipo IDE (barra lateral, área central, painel inferior se aplicável). Consegues usar os controlos definidos pelo produto para abrir/fechar sidebar e painel inferior; alternar estado (ex.: abas centrais) não “parte” navegação de forma óbvia (ex.: regressão não recuperável só com refresh).

result: [pending]

### 3. Monaco e disparo por teclado (Ctrl+Enter)

expected: |
  O editor Monaco está visível e utilizável para editar texto. Prima Ctrl+Enter (ou equivalente documentado pela app) para enviar/especificar intent: a UI não fica silent — mostra pelo menos estado de rede/carga ou resposta textual (elicitação, mensagem ou feedback de erro conhecível por ti).

result: [pending]

### 4. Polling do job até estado terminal

expected: |
  Após iniciar um job a partir da UI (ou mesmo fluxo de demo/fallback prévisto no cliente), ves progressão de estado até um terminal claro (`success`, `failure` ou erro apresentado) sem teres de contar apenas com refresh manual forçado ao browser como único recurso durante o período habitual de espera (~ minutos MVP).

result: [pending]

### 5. Viewport 3D com mesh STL

expected: |
  Para um job concluído com sucesso e com STL disponível no backend (rota `/api/v1/jobs/{id}/artifacts/stl`), o viewport Three/R3F mostra geometria perceptível como malha/sólido (sem canvas vazio “para sempre”; performance aceitável para um asset MVP de teste).

result: [pending]

### 6. Explorer de topologia alinhado ao artefacto

expected: |
  O painel de explorer de topologia apresenta uma hierarquia/árvore que faz sentido em relação ao artefacto de teste gerado pelo worker — nomeadamente existe correspondência suficientemente clara entre nós seleccionáveis e o que esperas para esse caso (pelo menos no nível MVP documentado pela phase).

result: [pending]

## Summary

total: 6
passed: 0
issues: 0
pending: 6
skipped: 0
blocked: 0

## Gaps

