# Source Monitor — Design Document

**Agent:** Source Monitor
**Capa:** 2 (Content Production)
**Fase:** F3
**Status:** Design complete, implementation pending

---

## 1. Responsabilidad

### Qué hace
- Lee fuentes configuradas por property (RSS feeds, Inoreader API, scraping selectivo)
- Extrae items nuevos desde la última ejecución
- Deduplica contra historial de items ya procesados
- Normaliza cada item a un schema uniforme (`SourceItem`)
- Asigna un score de relevancia preliminar (0-100) basado en heurísticas rápidas (no LLM)
- Entrega una lista rankeada de items al siguiente agente (Signal Scorer) o directamente al humano

### Qué NO hace
- **No genera contenido.** Solo descubre y rankea fuentes.
- **No decide qué publicar.** Eso es responsabilidad del Signal Scorer + Editorial + Human Approval.
- **No hace fact-checking.** Solo reporta lo que las fuentes dicen.
- **No scrapea agresivamente.** Respeta rate limits, robots.txt, y ToS de cada plataforma.
- **No almacena contenido completo de artículos.** Solo metadata + snippet.
- **No usa LLM para el scoring preliminar.** El scoring pesado con LLM es del Signal Scorer.

---

## 2. Inputs

### Fuentes primarias
1. **Inoreader API** (fuente principal)
   - Manuel ya tiene cuenta configurada con 244+ items
   - Folder "AI Brief LATAM" con feeds curados
   - API permite: listar items no leídos, marcar como leídos, filtrar por folder/tag
   - Rate limit: 100 requests/hour (free tier), 1000/hour (pro)

2. **RSS feeds directos** (fallback si Inoreader no tiene el feed)
   - Para fuentes que no están en Inoreader
   - Parsing con `feedparser`

3. **Scraping selectivo** (solo para fuentes sin RSS)
   - Anthropic Blog (no tiene RSS estable)
   - Se implementa caso por caso, con parsers específicos
   - Nunca scraping genérico o masivo

### Configuración
- `projects/<property>/sources.yaml` — lista de fuentes con URLs, tipo, peso
- `agents/source_monitor/config.yaml` — parámetros del agente (frecuencia, thresholds, dedup window)

---

## 3. Outputs

### Output principal
Lista ordenada de `SourceItem` objects, serializada como JSON/YAML en:
```
evidence/{run_id}/source_monitor_output.json
```

### Output secundario
- `evidence/{run_id}/source_monitor_stats.json` — stats del run (items found, deduped, errors)
- `evidence/{run_id}/source_monitor_log.txt` — log detallado para debugging

### Formato de entrega al siguiente agente
```python
{
    "run_id": "2026-05-08T08:00:00_ai-brief-latam",
    "property": "ai-brief-latam",
    "timestamp": "2026-05-08T08:15:32Z",
    "items_found": 47,
    "items_after_dedup": 31,
    "items": [
        { ... SourceItem ... },
        ...
    ],
    "errors": [],
    "stats": {
        "sources_checked": 15,
        "sources_failed": 1,
        "dedup_removed": 16,
        "avg_preliminary_score": 42.3
    }
}
```

---

## 4. Schema de datos

### SourceItem
```python
class SourceItem(BaseModel):
    id: str                      # hash(url + published_date)
    title: str
    url: HttpUrl
    source_name: str             # e.g. "TechCrunch", "Anthropic Blog"
    source_category: str         # "oficial" | "newsletters" | "community" | "latam"
    published_at: datetime
    discovered_at: datetime
    snippet: str                 # primeros 300 chars del contenido
    authors: list[str]
    tags: list[str]              # tags/categorías del feed
    language: str                # "en" | "es" | "pt"
    preliminary_score: float     # 0-100, heurístico (no LLM)
    score_breakdown: dict        # {"recency": 15, "source_weight": 20, ...}
    is_duplicate: bool
    duplicate_of: str | None     # id del item original si es dupe
    raw_metadata: dict           # metadata extra del feed/API
```

### SourceMonitorResult
```python
class SourceMonitorResult(BaseModel):
    run_id: str
    property: str
    timestamp: datetime
    items: list[SourceItem]
    errors: list[SourceError]
    stats: RunStats
```

### SourceError
```python
class SourceError(BaseModel):
    source_name: str
    error_type: str              # "connection" | "parse" | "rate_limit" | "auth"
    message: str
    timestamp: datetime
```

---

## 5. Frecuencia de ejecución

### Modo recomendado: On-demand via CLI
```bash
autopilot scan --property ai-brief-latam
```

### Razón
- En Fase 3, Manuel corre esto 1-2x/día manualmente
- No hay infra de scheduling todavía (no cloud, no cron server)
- Cuando la operación lo demande, se agrega cron local o scheduled task

### Futuro (Fase 4+)
- Cron local: cada 4 horas durante horario activo (8am-10pm LATAM)
- O trigger manual cuando Manuel quiere revisar fuentes

---

## 6. Dependencies (Python libraries)

```
# Core
feedparser>=6.0          # RSS parsing
httpx>=0.27              # HTTP client (async-capable, better than requests)
pydantic>=2.0            # Data validation and schemas

# Inoreader
# No SDK oficial — se usa httpx directamente contra REST API

# Scraping (selectivo)
beautifulsoup4>=4.12     # HTML parsing para fuentes sin RSS
lxml>=5.0                # Parser rápido para BS4

# Dedup
hashlib                  # stdlib — hashing para dedup IDs

# Utils
python-dateutil>=2.9     # Parsing de fechas variadas
pyyaml>=6.0              # Config files
rich>=13.0               # CLI output formatting (optional, nice-to-have)

# Testing
pytest>=8.0
pytest-asyncio>=0.23     # Si usamos async httpx
responses>=0.25          # Mock HTTP para tests
```

---

## 7. Integración con kernel (Control Plane — Capa 1)

### Flujo de ejecución
```
CLI command
  → core/intake.py (registra el run)
    → agents/source_monitor/agent.py (ejecuta scan)
      → core/evidence.py (guarda output en evidence/{run_id}/)
        → Signal Scorer (próximo agente, consume el output)
```

### Puntos de contacto con core/
1. **intake.py** — El source_monitor se registra como task type "scan"
2. **evidence.py** — Guarda su output en formato estándar
3. **config.py** — Lee configuración global (API keys, paths)
4. **policy_engine.py** — Consulta si hay restricciones (rate limits globales, blacklists)

### Estado compartido
- **Dedup history:** `data/source_monitor/seen_items.json` — IDs de items ya procesados
- **Evidence output:** `evidence/{run_id}/source_monitor_output.json`

### API keys necesarias
- `INOREADER_APP_ID` — OAuth app ID
- `INOREADER_APP_KEY` — OAuth app key
- `INOREADER_TOKEN` — Access token (se obtiene via OAuth flow una vez)

---

## 8. Recomendación de framework

### Comparación para este caso específico

| Criterio | Anthropic Agent SDK | LangGraph | CrewAI |
|---|---|---|---|
| **Complejidad del agent** | Overkill — Source Monitor no necesita tool-calling LLM ni conversación | Overkill — grafos de estado para un pipeline lineal simple | Overkill — multi-agent orchestration innecesaria |
| **LLM dependency** | Requiere LLM como core | Requiere LLM como core | Requiere LLM como core |
| **Source Monitor usa LLM?** | NO en esta fase — es mayormente determinístico (RSS + scoring heurístico) | NO | NO |
| **Overhead de setup** | Medio (API keys, SDK config) | Alto (LangChain ecosystem) | Alto (abstracciones, roles, crews) |
| **Debugging** | Bueno (tracing) | Complejo (graph state) | Difícil (abstraction layers) |
| **Lock-in** | Anthropic-only | LangChain ecosystem | CrewAI ecosystem |
| **Tamaño del agent** | ~200 líneas de lógica real | ~200 líneas + boilerplate de grafos | ~200 líneas + boilerplate de roles |

### Decisión: **Plain Python + Pydantic**

**Justificación:**
1. Source Monitor es 90% determinístico (fetch RSS, parse, dedupe, score con heurísticas). No necesita LLM.
2. Los 3 frameworks agregan complejidad sin beneficio porque están diseñados para agents que usan LLM como motor.
3. El scoring preliminar es aritmético (pesos × factores). El scoring con LLM es del Signal Scorer, no de este agent.
4. Plain Python con Pydantic schemas da: type safety, validación automática, serialización gratis, zero lock-in.
5. Si en el futuro Source Monitor necesita LLM (ej: clasificación de títulos ambiguos), se agrega una llamada a Claude API directa sin framework intermediario — como dice el MASTER_PLAN: "Claude (Anthropic API directa) para v1".

**Cuándo reconsiderar:**
- Si Signal Scorer + Source Monitor se fusionan y el scoring requiere LLM → considerar Anthropic Agent SDK
- Si el pipeline crece a 5+ agents con branching complejo → considerar LangGraph
- Nunca CrewAI — demasiada abstracción para este caso

---

## 9. Tests de aceptación

El agent se considera "vivo" cuando pasa estos 5 tests:

### T1 — Fetch RSS feed and parse items
```
GIVEN un RSS feed válido (fixture local o mock)
WHEN source_monitor.fetch() se ejecuta
THEN retorna una lista de SourceItem con title, url, published_at populados
AND no hay errores en el resultado
```

### T2 — Deduplication works
```
GIVEN un historial con 3 items ya vistos
AND un feed que contiene 5 items (2 nuevos + 3 repetidos)
WHEN source_monitor.fetch() se ejecuta
THEN retorna exactamente 2 items (los nuevos)
AND los 3 repetidos están marcados con is_duplicate=True
```

### T3 — Preliminary scoring assigns scores
```
GIVEN una lista de 5 SourceItems normalizados
WHEN scorer.score_preliminary(items) se ejecuta
THEN cada item tiene preliminary_score entre 0 y 100
AND score_breakdown contiene las categorías esperadas (recency, source_weight, keyword_match)
AND items están ordenados por score descendente
```

### T4 — Graceful handling of source failures
```
GIVEN una fuente RSS que retorna HTTP 500
AND otra fuente RSS que funciona correctamente
WHEN source_monitor.fetch_all() se ejecuta
THEN los items de la fuente funcional se retornan normalmente
AND la fuente fallida aparece en errors[] con error_type="connection"
AND el run NO falla completamente
```

### T5 — End-to-end scan produces valid output
```
GIVEN configuración válida de property "ai-brief-latam"
AND al menos 1 fuente RSS accesible (mock)
WHEN autopilot scan --property ai-brief-latam se ejecuta
THEN se genera evidence/{run_id}/source_monitor_output.json
AND el JSON es parseable como SourceMonitorResult
AND contiene al menos 1 item con todos los campos requeridos
```
