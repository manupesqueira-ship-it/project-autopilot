# Source Monitor Config

**Origen:** Extraído de legacy/python-mvp-2026-05-10/agents/source_monitor/
**Status:** v1 — pendiente refinamiento para uso en n8n
**Última revisión:** 2026-05-10

---

## Agent Settings

```yaml
agent:
  name: source_monitor
  version: "0.1.0"
  log_level: INFO
```

## Fetch Settings

```yaml
fetch:
  timeout_seconds: 30
  max_retries: 2
  retry_delay_seconds: 5
  max_items_per_source: 50
```

## Deduplication

```yaml
dedup:
  history_file: "data/source_monitor/seen_items.json"
  history_max_age_days: 30
```

## Hard Filters

```yaml
filters:
  max_age_days: 7    # Items older than this are dropped completely
```

## Scoring Weights (must sum to ~100 for max possible score)

```yaml
scoring:
  weights:
    recency: 20                   # How fresh (0-20)
    source_weight: 20             # Source trustworthiness (0-20)
    keyword_match: 20             # Title/snippet keyword hits (0-20)
    language_fit: 10              # Language match (0-10)
    length_signal: 10             # Content substance proxy (0-10)
    category_bonus: 10            # Priority category bonus (0-10)
```

## Recency Settings

```yaml
  recency:
    max_score_hours: 6            # Items < 6h old get full recency score
    zero_score_hours: 72          # Items > 72h old get 0 recency score
```

## Keyword Gate Threshold

```yaml
  keyword_gate_threshold: 5.0
```

Si `keyword_match < 5.0`, los bonuses de `language_fit`, `length_signal` y `category_bonus` se anulan. Previene que items off-topic ranqueen alto por bonuses.

## Keywords — ai-brief-latam

### high_priority (2x weight)

```yaml
# CORE_AI
- "AI"
- "IA"
- "inteligencia artificial"
- "LLM"
- "GPT"
- "Claude"
- "ChatGPT"
- "Gemini"
- "Llama"
- "Mistral"
- "Sonnet"
- "Opus"
- "Haiku"
- "multi-agent"
# VOICE/AUDIO
- "voice"
- "TTS"
- "speech"
- "transcribe"
- "realtime"
- "voice agent"
- "speech-to-text"
- "audio model"
- "voice synthesis"
- "voz"
- "audio"
# COMPANIES
- "OpenAI"
- "Anthropic"
- "Google DeepMind"
- "xAI"
- "Hugging Face"
- "Perplexity"
- "Cohere"
- "Stability AI"
- "Runway"
- "ElevenLabs"
- "Replicate"
# LATAM (high priority — differentiator)
- "LATAM"
- "latinoamerica"
- "México"
- "Mexico"
- "CDMX"
- "Brasil"
- "Brazil"
- "Colombia"
- "Argentina"
- "Chile"
- "Perú"
- "Mercado Libre"
- "Rappi"
- "Nubank"
- "Kavak"
- "Bitso"
# FUNDING (high signal)
- "billion"
- "million"
- "billones"
- "millones"
- "Series A"
- "Series B"
- "Series C"
- "IPO"
- "acquisition"
- "adquisición"
```

### normal (1x weight)

```yaml
# CORE_AI (secondary)
- "ML"
- "machine learning"
- "agent"
- "agente"
- "agentes verticales"
- "deep learning"
- "transformer"
- "fine-tuning"
- "RAG"
- "benchmark"
- "open source"
# COMPANIES (secondary)
- "Microsoft"
- "Meta"
- "Mistral"
# VERTICALS
- "fintech"
- "insurtech"
- "agtech"
- "healthtech"
- "legaltech"
- "edtech"
- "retailtech"
- "proptech"
# LATAM (secondary)
- "Pomelo"
- "Bancolombia"
- "BBVA"
- "Santander"
- "Clip"
- "Konfío"
- "123Seguro"
- "Stori"
- "Belvo"
# FUNDING (secondary)
- "round"
- "ronda"
- "raised"
- "levantó"
- "valuation"
- "valuación"
- "partnership"
- "deal"
```

## Priority Categories (get category_bonus)

```yaml
priority_categories:
  ai-brief-latam:
    - "oficial"
    - "latam"
```

## Output Settings

```yaml
output:
  evidence_dir: "agents/source_monitor/evidence"
  format: "json"
  include_duplicates: false
  min_score_threshold: 0
```

---

## RSS Source List (from projects/ai-brief-latam/sources.yaml)

### oficial
| Name | URL | Type | Weight |
|------|-----|------|--------|
| OpenAI Blog | https://openai.com/blog/rss.xml | rss | 2.0 |
| Anthropic Blog | https://www.anthropic.com/news | scrape | 2.0 |
| Google AI Blog | https://blog.google/technology/ai/rss/ | rss | 1.8 |

### tech_media
| Name | URL | Type | Weight |
|------|-----|------|--------|
| TechCrunch AI | https://techcrunch.com/category/artificial-intelligence/feed/ | rss | 1.8 |
| The Verge AI | https://www.theverge.com/rss/ai-artificial-intelligence/index.xml | rss | 1.5 |
| Ars Technica AI | https://feeds.arstechnica.com/arstechnica/technology-lab | rss | 1.3 |
| Wired AI | https://www.wired.com/feed/tag/ai/latest/rss | rss | 1.3 |
| Fortune AI | https://fortune.com/feed/ | rss | 1.5 |

### newsletters
| Name | URL | Type | Weight |
|------|-----|------|--------|
| Latent Space | https://www.latent.space/feed | rss | 1.5 |

### community
| Name | URL | Type | Weight |
|------|-----|------|--------|
| Hacker News | https://hnrss.org/frontpage | rss | 1.0 |

### latam
| Name | URL | Type | Weight |
|------|-----|------|--------|
| Contxto | https://contxto.com/en/feed/ | rss | 2.0 |
| LatamList | https://latamlist.com/feed/ | rss | 2.0 |
