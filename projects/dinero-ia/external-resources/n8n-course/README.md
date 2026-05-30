# n8n Course — material importado

**Origen:** curso de n8n + AI automation guardado en OneDrive de Manuel.
**Fecha de importación:** 2026-05-12.
**Razón de importación:** alineación múltiple con decisiones nuestras (Hostinger VPS, n8n self-hosted, Upload-Post community node, ElevenLabs, multi-platform publish).

---

## Qué contiene este folder

### PDFs operativos (3)

| Archivo | Contenido | Cómo aplica |
|---|---|---|
| `30-day-ai-automation-roadmap.pdf` | Roadmap día-por-día de 30 días para "lanzar un side-project de AI automation desde cero" | Sanity check para Fase -1 / Fase 0. Confirma la lógica "validar antes de construir" del Critical Review. NO seguir literal — solo usar para verificar que no nos saltamos un paso obvio. |
| `recommended-tools-original.pdf` | Lista de ~30 herramientas con affiliate links del autor del curso | Referencia. La versión limpia con solo los deals útiles está en `recommended-tools-extracted-deals.md` (creada por nosotros). |
| `n8n-cheatsheet-dashboard.pdf` | Cheatsheet de nodos n8n más usados + atajos + patterns comunes | Útil mientras Manuel aprende n8n. Imprimible. |

### Imagen

| Archivo | Notas |
|---|---|
| `n8n-cheatsheet.png` | Mismo cheatsheet que el PDF, en PNG. Útil para preview rápido sin abrir PDF. |

### Templates JSON (24)

Ver `high-value-templates/templates-index.md` para el detalle de cada template, su pattern, y la fase del ROADMAP donde aplica.

**Resumen rápido:**
- **Publishers (3):** Upload-Post equivalente, Blotato Plan B, multi-platform autoposting
- **HITL (1):** Telegram approval pattern (lo que necesitamos para A11 Editor)
- **Voice/Video Fase 2 (8):** ElevenLabs, Seedance, TikTok machine, Kling, Veo3, NanoBanana
- **LinkedIn Fase 1.5 (3):** posting system, AI post machine, agent
- **Research/Agents (4):** team pattern, single agent, web research, news daily
- **Visual/Image (3):** image ads creator, MCP content creator, logos
- **Misc/Reference (2):** AI clone personality, multichannel RAG

---

## Lo que el curso confirma de nuestras decisiones

1. **n8n self-hosted en Hostinger** → el curso recomienda esto explícitamente. Confirma ADR-015.
2. **Community nodes (Upload-Post, Blotato)** → templates del curso usan exactamente estos nodes. Confirma ADR-014.
3. **ElevenLabs como TTS** → el curso lo trata como standard de facto para voice clone con descuento incluido. Confirma ADR-008.
4. **Telegram para HITL** → template dedicado, no es una invención nuestra. Confirma decisión K (OPEN_QUESTIONS).
5. **Validar primero, construir después** → el 30-day roadmap arranca con "qué nicho, qué oferta, qué audiencia" antes de tocar n8n. Coincide 1:1 con la conclusión 4 del Critical Review (Fase -1).

## Lo que el curso NO cubre (y debemos resolver nosotros)

- **Voz editorial en español LATAM** (todo el curso es en inglés, anglo-céntrico).
- **Compliance financiero** (el curso no toca el problema de "no prometer resultados" — Manuel sí debe).
- **Smart Brevity / Axios style** (curso es más performance marketing que editorial).
- **Hooks Rufusocial framework** (curso usa otro framework de hooks, menos riguroso).
- **Few-shot prompting con briefs validados** (el curso usa zero-shot, nosotros vamos few-shot).

---

## Restricciones de uso

- **Patterns sí, código no.** Los `.json` muestran cómo otra persona resolvió un problema. No están listos para deploy en nuestro VPS (credentials placeholder, posiblemente nodos community no instalados).
- **No editar originales.** Si un template inspira un workflow nuestro, crear uno nuevo en `projects/ai-brief-latam/workflows/` con referencia al template fuente.
- **No redistribuir.** Material licenciado por el autor del curso.

---

## Si necesitás algo que no se copió

El curso original sigue completo en OneDrive de Manuel (~117 templates totales). Los 93 que no se copiaron eran nichos sin overlap con nuestro proyecto (e-commerce, lead-gen B2B SaaS, real-estate, dental, etc.). Si alguno aplica en una fase futura (ej. monetización con cursos = lead-gen reabre), se puede importar selectivamente en ese momento.
