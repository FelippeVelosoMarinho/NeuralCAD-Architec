# NeuralCAD Architect

## Product Vision
Build a production-ready AI-native CAD co-pilot that transforms vague natural-language architectural intent into valid, editable B-rep geometry through an iterative, spec-driven workflow.

The system combines:
- BrepGen as the geometry generation engine
- Claude as the intent-to-geometry orchestrator
- A VS Code-inspired multimodal interface (Monaco + sidebars + 3D viewport)

Goal: reduce manual CAD modeling effort while preserving geometric validity, traceability, and iterative control.

## Core Problem
Architects and CAD users often start with underspecified intent (e.g., "L-bracket with concentric holes, stronger near joints"), but current workflows require expert translation into low-level modeling operations. This causes:
- slow ideation-to-geometry cycles
- high dependency on specialized CAD operators
- frequent topology and validity issues during manual iteration

## Target Users
- Architects and industrial designers needing rapid concept-to-CAD loops
- Mechanical/CAD engineers refining topology-aware solids
- Technical teams building AI-assisted CAD authoring tools

## Product Outcomes
- Convert natural language into structured geometric requirements
- Generate valid B-rep candidates (STEP/STL) quickly
- Support guided refinement by selecting geometric entities (face/edge/vertex)
- Provide geometry lint feedback (watertightness, intersections, instability)
- Keep full version history and visual diffs between iterations

## Non-Goals (MVP)
- Full CAD suite replacement
- Multi-body assembly authoring parity with enterprise CAD suites
- Real-time collaborative multi-user editing
- Custom BrepGen retraining in first release

## Closed Technical Stack (MVP)
- Backend: Python 3.10, FastAPI, Uvicorn, Pydantic v2
- CAD engine: PyTorch 2.2, Diffusers 0.27, BrepGen, pythonocc-core, occwl
- Async: Celery + Redis
- Data: PostgreSQL 16 (metadata), MinIO (artifacts STEP/STL/diffs)
- Frontend: React 18 + TypeScript + Vite
- 3D: Three.js + react-three-fiber
- UX shell: Monaco Editor + VS Code-like layout + vscode-webview-ui-toolkit patterns
- State/data: Zustand + TanStack Query + FastAPI WebSockets
- Quality: pytest, vitest, playwright, ruff, black, eslint, prettier
- Observability: OpenTelemetry + Prometheus + Grafana
- Runtime: Docker Compose + Nginx

## AI Orchestration Contract
Claude acts as **Prompt Architect** and must always:
1. Extract intent, constraints, geometry hints, and quality targets
2. Normalize output to `IntentSchemaV1` JSON
3. Validate ambiguity and ask focused clarifying questions when needed
4. Emit BrepGen-ready generation config
5. Explain trade-offs and predicted geometry risks before generation

## IntentSchemaV1 (Canonical)
```json
{
  "sessionId": "string",
  "promptOriginal": "string",
  "intent": {
    "objectType": "string",
    "style": ["string"],
    "functionalGoal": "string"
  },
  "constraints": {
    "dimensionsMm": {"width": 0, "height": 0, "depth": 0},
    "thicknessMm": 0,
    "symmetry": "none|x|y|z|xy|xz|yz",
    "manufacturingHints": ["string"],
    "materialHints": ["string"]
  },
  "topologyHints": {
    "expectedFacesRange": [0, 0],
    "expectedEdgesRange": [0, 0],
    "holes": [{"type": "concentric|through|blind", "count": 0}]
  },
  "surfaceHints": {
    "curvature": "low|medium|high",
    "freeform": true,
    "continuityPreference": "G0|G1|G2"
  },
  "generationConfig": {
    "mode": "abc|deepcad|furniture",
    "numSurfaces": 0,
    "numEdgesPerSurface": 0,
    "bboxThreshold": 0.0,
    "zThreshold": 0.0
  },
  "qualityTargets": {
    "preferWatertight": true,
    "maxSelfIntersectionRisk": "low|medium|high"
  }
}
```

## UX Blueprint (VS Code-inspired)
- Left Sidebar (Explorer): hierarchical B-rep tree (Face/Edge/Vertex nodes)
- Center Panel: 3D viewport + prompt/code editor tabs
- Bottom Panel (Copilot Console): Claude suggestions and geometric lint diagnostics
- Iteration Diff View: highlight changed regions between versions (source-control style)

## Core Workflows (MVP)
1. Prompt-to-Geometry
   - User writes intent
   - Claude structures + validates
   - Backend generates B-rep
   - UI renders + annotates quality

2. Select-and-Refine
   - User selects face(s)/edge(s)
   - Claude proposes local/global refinement
   - System runs autocompletion/interpolation
   - Visual diff and lint report returned

3. Constraint Completion
   - Claude detects missing specs (thickness, tolerances, radius)
   - Asks minimal questions
   - Regenerates with improved constraints

## Execution Sprints
- Sprint 1: Backend geometric pipeline + unconditional generation via API
- Sprint 2: Prompt Architect + IntentSchemaV1 + validation loop
- Sprint 3: VS Code-like UI shell + 3D viewport foundation
- Sprint 4: Realtime orchestration (chat -> generation -> model update)
- Sprint 5: Edit/refine by selection + interpolation/autocompletion + visual diff

## Success Metrics
- Geometry validity rate (watertight) >= defined baseline
- Prompt-to-first-valid-model latency within acceptable UX threshold
- Iteration success rate (refine request produces meaningful geometric delta)
- Reduction in clarification turns over time
- User-perceived controllability and output relevance

## Risks and Mitigations
- Ambiguous prompts -> strict schema + guided clarifications
- Invalid solids -> geometric lint + threshold fallback + repair attempts
- Local edit breaks global topology -> connectivity checks before commit
- Latency spikes -> async queue, staged preview, caching recent variants

## GSD Bootstrap Prompt (for guided start)
Use this as project brief when running `gsd-new-project`:

"Create a spec-driven AI CAD product called NeuralCAD Architect. The system must transform vague natural-language intent into valid B-rep geometry using Claude as Prompt Architect and BrepGen as generation engine. Build a VS Code-inspired multimodal interface with B-rep hierarchy explorer, Monaco prompt editor, 3D viewport, and copilot console. Enforce IntentSchemaV1 as contract between language and geometry. Include refine-by-selection workflow using autocompletion/interpolation, geometric linter, version history, and visual diffs. Use closed stack: FastAPI, Celery, Redis, Postgres, MinIO, React/TypeScript/Vite, Three.js, Zustand, TanStack Query, WebSockets, Docker Compose. Generate PROJECT.md, REQUIREMENTS.md, ROADMAP.md focused on deliverable MVP in 5 sprints."
