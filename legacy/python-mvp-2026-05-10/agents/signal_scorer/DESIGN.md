# Signal Scorer — Design Document

**Agent:** Signal Scorer
**Capa:** 2 (Content Production)
**Fase:** F3
**Status:** Implementation in progress

---

## 1. Responsabilidad

### Qué hace
- Recibe items pre-filtrados del Source Monitor (lista de `SourceItem`)
- Evalúa cada item contra la **Signal Scoring Rubric** (MASTER_PLAN Anexo B) usando un LLM
- Produce un score 0-100 con breakdown por categoría y justificación en español
- Clasifica items: `strong` (>70), `consider` (50-70), `discard` (<50)
- Entrega una shortlist rankeada al humano (o al Editorial Agent en Fase 4)

### Qué NO hace
- **No genera contenido.** Solo evalúa y rankea.
- **No fetcha fuentes.** Eso es del Source Monitor.
- **No decide publicar.** Eso es del humano + Editorial.
- **No hace fact-checking.** Solo evalúa potencial editorial, no veracidad.

---

## 2. Inputs

- `SourceMonitorResult` JSON (output del Source Monitor en `agents/source_monitor/evidence/{run_id}/`)
- Property config: `projects/<property>/config.yaml`, `brand_voice.md`, `risk_profile.yaml`
- Scoring rubric: `agents/signal_scorer/config.yaml`

## 3. Outputs

### Output principal
```
agents/signal_scorer/evidence/{run_id}/signal_scorer_output.json
```

### ScoredItem schema
```python
class ScoredItem(BaseModel):
    source_item: SourceItem          # Original item from Source Monitor
    signal_score: float              # 0-100, LLM-evaluated
    signal_breakdown: dict           # Per-rubric-category scores
    classification: str              # "strong" | "consider" | "discard"
    justification: str               # 2-3 sentence explanation in Spanish
    suggested_angle: str             # Brief editorial angle suggestion
    risk_flags: list[str]            # Any risk/compliance concerns spotted
```

## 4. Scoring Rubric (from MASTER_PLAN Anexo B)

| Categoría | Peso | Criterio |
|---|---|---|
| Relevancia LATAM | 0-20 | ¿Aplica a la audiencia LATAM? |
| Novedad | 0-15 | ¿Es nuevo o ya circuló ampliamente? |
| Urgencia | 0-10 | ¿Tiene ventana de tiempo? |
| Credibilidad de fuente | 0-15 | ¿Fuente confiable y verificable? |
| Potencial educativo | 0-10 | ¿Enseña algo útil a la audiencia? |
| Potencial viral | 0-10 | ¿Tiene hook fuerte para IG/newsletter? |
| Fit con la marca | 0-10 | ¿Coincide con voz y posicionamiento? |
| Riesgo (penalty) | 0 a -10 | ¿Hay riesgo legal/reputacional? |

- Score >70 = `strong` (candidato fuerte)
- Score 50-70 = `consider` (evaluar manualmente)
- Score <50 = `discard`

## 5. LLM Strategy

- **Model:** Claude Sonnet (fast, cost-effective for scoring)
- **API:** Anthropic API directa (no framework)
- **Batching:** Items scored individually (not batched) for quality
- **Prompt:** System prompt with rubric + brand voice context, user message with item data
- **Cost estimate:** ~$0.01-0.02 per item (Sonnet input+output), ~$0.50-1.00 per full scan of 50 items
- **Fallback:** If API fails, item keeps its preliminary score from Source Monitor

## 6. Frequency

- Runs immediately after Source Monitor, piped or chained
- `autopilot score --property ai-brief-latam` (standalone)
- `autopilot scan --property ai-brief-latam --score` (chained)

## 7. Dependencies

```
anthropic>=0.52          # Claude API client
pydantic>=2.7            # Schemas (shared with source_monitor)
pyyaml>=6.0              # Config
rich>=13.7               # CLI output
```

## 8. Acceptance Tests

### T1 — Score a single item with valid breakdown
```
GIVEN a SourceItem with title, snippet, source info
WHEN signal_scorer.score_item(item) is called
THEN returns ScoredItem with signal_score 0-100
AND signal_breakdown has all 8 rubric categories
AND justification is non-empty Spanish text
AND classification matches score threshold
```

### T2 — Batch scoring produces ranked shortlist
```
GIVEN a list of 5 SourceItems
WHEN signal_scorer.score_batch(items) is called
THEN returns 5 ScoredItems sorted by signal_score descending
AND each has classification assigned
```

### T3 — API failure falls back gracefully
```
GIVEN an API that returns an error
WHEN signal_scorer.score_item(item) is called
THEN item retains its preliminary_score as signal_score
AND error is logged but not raised
```

### T4 — Risk flags are detected
```
GIVEN an item about crypto investment promising returns
WHEN signal_scorer.score_item(item) is called
THEN risk_flags contains relevant warning
AND risk penalty is applied to score
```

### T5 — End-to-end: Source Monitor → Signal Scorer
```
GIVEN a completed Source Monitor run with evidence output
WHEN autopilot score --property ai-brief-latam is called
THEN reads source_monitor_output.json
AND produces signal_scorer_output.json
AND output contains scored items with valid schemas
```
