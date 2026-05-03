# Feature Research

**Domain:** AI copilot for CAD / B-rep iteration
**Researched:** 2026-05-03
**Confidence:** HIGH para escopo MVP (derivado do `IDEA.md`)

## Feature Landscape

### Table Stakes (Users Expect These)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| NL → geometria candidata | Promessa central do produto | HIGH | Depende BrepGen + schema |
| Export/visualização STEP/STL | Integração com ferramentas existentes | MEDIUM | MinIO + viewer |
| Feedback de validade (watertight, interseções) | Confiança em IA para CAD | MEDIUM | Lint pipeline OCC |
| Histórico de versões / iterações | Iteração sem perda de trabalho | MEDIUM | Metadados + artefatos |
| Modo assíncrono com status | Jobs longos | MEDIUM | Celery + WS |

### Differentiators (Competitive Advantage)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| IntentSchemaV1 rígido | Auditabilidade NL↔geom | MEDIUM | Reduz ambiguidade |
| Refino por seleção topológica | Controle fino sem reescrever prompt | HIGH | Face/edge/vertex |
| Diff visual entre B-reps | “Source control” geométrico | HIGH | Comparar tesselações/metanós |
| Console copiloto + lint | Transparência das decisões da IA | MEDIUM | UX VS Code |

### Anti-Features (Deliberately Not Building in MVP)

| Feature | Why Problematic | Alternative |
|---------|-----------------|-------------|
| Paridade montagem enterprise | Anos de escopo | Escopo explícito “Out of Scope” |
| Multiplayer realtime | Infra e OT complexos | Assíncrono single-user primeiro |
| Retreino BrepGen | Ciência + dados | Config frozen + eval offline depois |

## Feature Dependencies

```
IntentSchemaV1 + API
    └── requires ──> Job queue + storage (MinIO)
            └── requires ──> Worker com BrepGen/OCC

UI shell
    └── requires ──> API + (fase posterior) WS

Refine-by-selection
    └── requires ──> Picking 3D + IDs estáveis + backend interpolação
```

---
*Categorias alinhadas ao brief NeuralCAD Architect.*
