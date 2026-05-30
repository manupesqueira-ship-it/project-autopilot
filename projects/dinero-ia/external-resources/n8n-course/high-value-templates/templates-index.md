# High-Value Templates — Index

**Total:** 24 templates seleccionados de 117 originales.
**Criterio:** alineación directa con ROADMAP de AI How-To LATAM o pattern operativo reutilizable.

---

## Cómo leer este índice

Cada template tiene:
- **Archivo** → nombre normalizado kebab-case
- **Pattern** → qué resuelve operacionalmente
- **Fase ROADMAP** → cuándo lo abrimos
- **Reutilización** → "ref" (mirar y aprender), "base" (puede ser punto de partida), "patrón crítico" (refleja una decisión nuestra)
- **Caveats** → qué NO hacer / qué falta para usarlo

---

## Tier S — Patterns críticos (referencia directa para implementar)

### `hitl-pattern-telegram-equiv.json`
- **Pattern:** Human-in-the-loop con Telegram inline keyboard (approve / reject / edit)
- **Fase ROADMAP:** Fase 0 (smoke test) + Fase 1 (A11 Editor)
- **Reutilización:** patrón crítico
- **Caveats:** la lógica del feedback-loop con LLM re-generation es más rica en nuestro A11 prompt. Usar como referencia de *cómo conectar Telegram nodes*, no de cómo prompt-engineerar el editor.

### `publisher-multi-platform-autoposting.json`
- **Pattern:** publica el mismo content a IG + TikTok + LinkedIn desde un solo trigger
- **Fase ROADMAP:** Fase 1 (auto-publish)
- **Reutilización:** patrón crítico — esto es exactamente lo que Upload-Post hace
- **Caveats:** verificar si usa Upload-Post node o Blotato. Si usa Blotato, mapear los nodes al equivalente Upload-Post para alinear con ADR-014.

### `publisher-blotato-plan-b.json`
- **Pattern:** Publish con Blotato (multi-platform via API)
- **Fase ROADMAP:** Fase 1 fallback si Upload-Post outage
- **Reutilización:** base (Plan B documentado)
- **Caveats:** Blotato tiene reviews mixtos (Trustpilot 2.0/5). Solo activar si Upload-Post falla.

---

## Tier A — Fase 1-1.5 (productivo)

### `linkedin-best-posting-system-fase-1-5.json`
- **Pattern:** sistema completo de posting LinkedIn (trigger → AI write → schedule → publish → engagement tracking)
- **Fase ROADMAP:** Fase 1.5 (expansión a LinkedIn)
- **Reutilización:** base
- **Caveats:** voz del template es B2B SaaS genérica. Re-promptear con `brand_voice.md` v2 (viral hype calibrado).

### `linkedin-ai-post-machine.json`
- **Pattern:** alternativa más ligera al anterior. Solo write + schedule, sin tracking.
- **Fase ROADMAP:** Fase 1.5 (versión MVP de LinkedIn)
- **Reutilización:** base

### `linkedin-agent.json`
- **Pattern:** LinkedIn agent con comportamiento conversacional (responde a DMs/comments)
- **Fase ROADMAP:** Fase 1.5+ (engagement)
- **Reutilización:** ref
- **Caveats:** automatizar responses puede violar ToS LinkedIn. Revisar antes de activar.

### `news-ai-agent-daily-reference.json`
- **Pattern:** agent que escanea fuentes news diarias y genera digest
- **Fase ROADMAP:** Fase 0-1 (alternativa a nuestro A1 Discovery + A1.5 Filter)
- **Reutilización:** ref — nuestro pipeline ya planifica esto custom, pero es buen sanity check
- **Caveats:** nuestro pipeline usa RSS + Sonnet 4.5 filter; este template usa solo HTTP scraping. Nuestro approach es más robusto.

---

## Tier A — Fase 2 (voice + video reels)

### `elevenlabs-voice-fase-2.json`
- **Pattern:** TTS de texto → audio file con ElevenLabs voice ID custom
- **Fase ROADMAP:** Fase 2 (reels narrados)
- **Reutilización:** base
- **Caveats:** voice ID hay que generarlo nosotros (Manuel debe grabar 20 min de muestra).

### `elevenlabs-vectorize-workflow.json`
- **Pattern:** generación de embedding/vectorize de voice files para clasificación
- **Fase ROADMAP:** Fase 2+ (si querés hacer A/B testing de voices)
- **Reutilización:** ref
- **Caveats:** scope avanzado. Solo si la voz original no performa y querés testear variantes.

### `seedance-demo-asmr.json` + `seedance-demo-fox-prompt.json`
- **Pattern:** imagen → video con Seedance 2.0 (dos prompts de ejemplo)
- **Fase ROADMAP:** Fase 2 (reels)
- **Reutilización:** base (entender el formato de prompt para Seedance)
- **Caveats:** prompts del template son creative/random. Para nuestro caso (editorial sobrio) habrá que reescribirlos enteros.

### `tiktok-video-machine-fase-2.json`
- **Pattern:** pipeline completo TikTok: trend research → script → voice → video → publish
- **Fase ROADMAP:** Fase 2 (TikTok producción)
- **Reutilización:** base — refleja el end-to-end de Fase 2
- **Caveats:** trend research del template está optimizado para nicho viral random. Nuestro nicho (AI How-To LATAM) requiere fuentes distintas (mantener nuestras 8 fuentes editoriales).

### `viral-ad-videos-nanobanana-veo3.json`
- **Pattern:** generación de video viral combinando NanoBanana (images) + Veo3 (video)
- **Fase ROADMAP:** Fase 2 alternativa si Seedance no rinde
- **Reutilización:** ref
- **Caveats:** Veo3 es Google, NanoBanana es de terceros. Stack más complejo que Seedance. Solo si Seedance falla en calidad.

### `veo3-content-machine-alt.json`
- **Pattern:** content machine solo con Veo3
- **Fase ROADMAP:** Fase 2 alternativa
- **Reutilización:** ref
- **Caveats:** Veo3 costo y disponibilidad variable. Seedance es nuestra apuesta primaria.

### `kling-2-1-video-gen-alt.json`
- **Pattern:** video gen con Kling 2.1
- **Fase ROADMAP:** Fase 2 alternativa
- **Reutilización:** ref
- **Caveats:** otra alternativa a Seedance. Tener en backlog si Seedance + Veo3 ambos fallan.

---

## Tier B — Patterns útiles para research/agents

### `research-agent-team-pattern.json`
- **Pattern:** múltiples agents coordinados (researcher + analyst + writer)
- **Fase ROADMAP:** Fase 1 (referencia para A1-A11 orquestación)
- **Reutilización:** patrón crítico para entender multi-agent en n8n
- **Caveats:** nuestro pipeline ya tiene esto modelado en AGENTS_SPEC.md. Usar como sanity check de cómo otros lo implementan en n8n específicamente.

### `research-ai-agent.json`
- **Pattern:** single research agent con web search tool
- **Fase ROADMAP:** Fase 1 (referencia para A4 fact-check con Claude web_search)
- **Reutilización:** ref
- **Caveats:** template usa Perplexity API; nosotros usaríamos Claude web_search nativo (más barato).

### `web-research-agent.json`
- **Pattern:** agent que browsea + extrae info estructurada
- **Fase ROADMAP:** Fase 1 ref
- **Reutilización:** ref

---

## Tier B — Visual / Image / Misc

### `image-ads-creator-pattern.json`
- **Pattern:** generación de creatives (ad-style images) con prompt template
- **Fase ROADMAP:** Fase 1 (referencia para A5 Visual Prompt + A8a Render Image)
- **Reutilización:** ref
- **Caveats:** template orientado a ads (CTR-driven). Nuestro estilo editorial es opuesto. Útil solo para ver cómo se estructura el prompt → image gen pipeline en n8n.

### `mcp-content-creator.json`
- **Pattern:** content creation con MCP (Model Context Protocol) servers
- **Fase ROADMAP:** Fase 3+ (si MCP madura más)
- **Reutilización:** ref
- **Caveats:** MCP ecosystem aún temprano. Mirar pero no adoptar todavía.

### `logos-creator-fase-3.json`
- **Pattern:** generación de logos/branding con AI
- **Fase ROADMAP:** Fase 3 si querés iterar branding visual del proyecto
- **Reutilización:** ref

### `ai-story-generator-viral-hooks.json`
- **Pattern:** generador de stories con hooks virales estructurados
- **Fase ROADMAP:** Fase 1 (referencia para A7 Copy Composer + hooks)
- **Reutilización:** ref — alineado con nuestro pivot "viral hype calibrado"
- **Caveats:** framework de hooks del template es genérico. Nosotros usamos Rufusocial (atención+tensión+promesa). Usar este como inspiración estructural, no como fuente de hooks.

### `multichannel-rag-agent.json`
- **Pattern:** RAG agent que responde a queries con knowledge-base propia
- **Fase ROADMAP:** Fase 4+ (si construimos chatbot del newsletter)
- **Reutilización:** ref
- **Caveats:** scope futuro. No prioritario.

### `ai-clone-personality-pattern.json`
- **Pattern:** clone de personalidad (Manuel-as-agent que responde como Manuel)
- **Fase ROADMAP:** Fase 4+ (community management automation)
- **Reutilización:** ref
- **Caveats:** ético/legal complejo. Solo si Manuel decide explícitamente que querés un agent que hable como vos.

---

## Resumen por Fase

| Fase | Templates aplicables | Notas |
|---|---|---|
| **Fase -1 (Validación Manual)** | Ninguno — fase 100% manual | Solo consultar el `30-day-ai-automation-roadmap.pdf` |
| **Fase 0 (smoke test n8n)** | `hitl-pattern-telegram-equiv.json` | Solo el Telegram pattern |
| **Fase 1 (texto + carousel)** | `publisher-multi-platform-autoposting.json`, `publisher-blotato-plan-b.json`, `research-agent-team-pattern.json`, `research-ai-agent.json`, `image-ads-creator-pattern.json`, `ai-story-generator-viral-hooks.json`, `news-ai-agent-daily-reference.json` | El núcleo productivo |
| **Fase 1.5 (LinkedIn)** | `linkedin-best-posting-system-fase-1-5.json`, `linkedin-ai-post-machine.json`, `linkedin-agent.json` | Tres opciones de menor a mayor scope |
| **Fase 2 (reels + voice)** | `elevenlabs-voice-fase-2.json`, `seedance-demo-*.json` (2), `tiktok-video-machine-fase-2.json`, `viral-ad-videos-nanobanana-veo3.json`, `veo3-content-machine-alt.json`, `kling-2-1-video-gen-alt.json` | Múltiples alternativas — Seedance primaria, Veo3/Kling fallback |
| **Fase 3+ (branding + community)** | `logos-creator-fase-3.json`, `multichannel-rag-agent.json`, `ai-clone-personality-pattern.json`, `elevenlabs-vectorize-workflow.json`, `mcp-content-creator.json` | Futuro, no prioritario |

---

## Recordatorio operativo

Estos archivos son **referencia**, no **código deployable**. Antes de copiar un workflow a nuestro n8n:
1. Auditar credentials (remover placeholders).
2. Verificar nodos community instalados.
3. Adaptar prompts a `brand_voice.md` v2 + Rufusocial hooks.
4. Crear nueva copia en `projects/ai-brief-latam/workflows/`, no editar el original.
