# Open Questions — AI Brief LATAM

**Fecha de apertura:** 2026-05-12
**Status:** preguntas abiertas que bloquean el diseño definitivo del workflow.

> Manuel responde acá (editando el archivo) o en el chat. Cada respuesta cierra una decisión y deja de ser bloqueante. Mientras no estén respondidas, el skeleton de n8n queda como borrador.

---

## Tracking de respuestas (actualizado 2026-05-18 por ADR-016)

| # | Decisión | Status |
|---|---|---|
| A | "1 pieza" definida | ✅ Respondida — ver abajo |
| B | Quality controls | ✅ Respondida — ver abajo |
| C | Storage | ✅ Respondida — Supabase (locked, account creation deferred) |
| D | Image gen | ✅ Respondida — híbrido carousel/reel decidido por brief |
| E | Audio/video timing | ✅ Respondida — audio solo en reels, voice clone ElevenLabs |
| F | Sources | 🟡 Propuesta en `sources.yaml` — Manuel confirma post-Fase -1 |
| G | Standard de calidad / visual | ⏳ Pendiente — Manuel confirma post-Fase -1 |
| H | Cursor | ✅ Respondida — diferido, no hoy |
| I | Perplexity | ✅ Respondida — diferido, no hoy |
| J | Audiencia nítida (buyer persona) | ⏳ Pendiente — se afina con data de Fase -1 |
| K | Cadencia de lanzamiento (deadlines) | ⏳ Pendiente |
| L | Handle IG + logo | ⏳ Pendiente — además nombre nuevo del proyecto post-ADR-016 |
| M | Newsletter footer (dirección física CAN-SPAM) | ⏳ Pendiente |
| N | Publisher (ADR-012 → ADR-014) | 🟡 Propuesto Upload-Post — confirmar post Deep Research |
| O | Plan n8n cloud | 🟡 Propuesto Hostinger VPS (ADR-015) — confirmar post Deep Research |
| **P** | **Calibración voz (premium / viral / híbrido)** | ✅ Cerrada por ADR-016 — **viral hype calibrado** (hook emocional + body sobrio) |
| **Q** | **Manuel-cara vs cuenta-de-marca pura** | ⏳ Pendiente — afecta growth curve 5× |
| **R** | **Success criteria explícito para abortar/pivot** | ⏳ Pendiente |
| **S** | **Sustainability del operador (vacaciones, pausas)** | ⏳ Pendiente |
| **T** | **Plan B si Meta/TikTok rompen automation** | ⏳ Pendiente |
| **U** | **Validación voz antes de invertir más (Fase -1)** | ✅ Cerrada por ADR-016 — Fase -1 implementada en ROADMAP v4 |
| **V** | **Nicho específico de how-to (post-Deep Research)** | ⏳ Pendiente outputs Prompt 4 |
| **W** | **Build vs Buy decision (Blotato evaluación)** | ⏳ Pendiente outputs Prompt 1 + Fase -1 |

---

## Respuestas registradas (2026-05-12)

### A — "1 pieza" en Fase 1: **Carousel IG + TikTok paralelos + Newsletter daily**

- **1 pieza diaria** = 1 carousel IG + 1 caption/post TikTok (mismo contenido, paralelo) + 1 sección de newsletter.
- **Cadencia newsletter:** daily al inicio (1 al día, misma hora del post matutino). Decisión revisable: si la fricción operativa es alta o el open rate baja a <25%, switchear a weekly.
- **Implicación operativa:** trigger temprano AM (sugerido ~6 AM CDMX) → pipeline corre (~30-60 min) → preview a Telegram ~7 AM → Manuel aprueba 7-8 AM → publish IG+TikTok+Newsletter ~8 AM CDMX.
- **Reels:** quedan en Fase 2 según ROADMAP (semana 3-4). No bloquea Fase 1.

### B — Quality controls: **1 gate humano antes de publicar + consistencia editorial enforced por el sistema**

- **1 punto de aprobación humana**: chequeo rápido del post (carousel + caption + newsletter) en Telegram antes de publicar. Si lo rechaza → Manuel marca razón (diseño / información / tono) y el sistema descarta o regenera según el flag.
- **Sin aprobación intermedia**: no hay gate después del brief editorial ni después del fact-check; el sistema sigue automático hasta el preview final.
- **Consistencia editorial es responsabilidad del sistema, no del humano:**
  - **Voz/tono/copy:** enforced por brand_voice.md + prompts (a2-signal-scorer, a3-editorial, a7-copy-composer, a9-compliance)
  - **Visual:** enforced por VISUAL_STANDARD.md (a crear) + A5 Visual Director + prompts para gpt-image-2
  - **Hook + psicología:** enforced por framework Rufusocial (3 condiciones) + format pillars del research social-media-niches-2026
- **Material de investigación** que el sistema debe respetar: existe disperso en `research/`, `docs/research/deep-research/`, `brand_voice.md`. **A consolidar en `docs/POST_STANDARD.md`** como referencia única.

### C — Storage: **Supabase (DB + Storage + assets, single platform)**

- **Decisión locked, setup deferred.** Manuel pidió no crear cuenta todavía, continuar con diseño.
- **Por qué Supabase y no las otras opciones:** criterio "todo en un lugar" pesa más que "menos setup". Sheets+Drive+GitHub partido en 3 plataformas crea fricción. Supabase tiene Postgres (queries analíticas) + Storage (imágenes) + Auth (cuando llegue Fase 7 consumer product) en la misma cuenta.
- **Lo que guardamos en Supabase:**
  - Tabla `dedup_history` — items procesados (hash de URL + título) para no duplicar en 30d
  - Tabla `briefs` — todos los briefs generados (aprobados y rechazados), audit trail
  - Tabla `posts_published` — qué publicamos, cuándo, con métricas asociadas
  - Tabla `costs` — tokens consumidos por agent (Anthropic + OpenAI) para monitoreo financiero
  - Storage bucket `assets` — imágenes de gpt-image-2, videos de Seedance, audio de ElevenLabs
- **Backup adicional:** cada brief aprobado también se commitea como markdown a `projects/dinero-ia/manual-mvp/pieces/{date}_{slug}.md` en GitHub (audit trail diff-eable, narrativo).
- **Trade-off aceptado:** 30 min de setup inicial vs simplicidad operativa para los siguientes meses.

### D — Image gen: **gpt-image-2 + Seedance híbrido, decidido por brief**

- **Roles distintos:**
  - `gpt-image-2` → imágenes estáticas (slides carousel, cover hero, post estático)
  - `Seedance 2.0` → animar imágenes generadas a video (reels)
- **Decisión de formato por pieza:** el campo `formato_recomendado` del brief (ya existe en prompt a3-editorial) decide:
  - `carrusel` → gpt-image-2 × 5-7 slides
  - `reel` → gpt-image-2 (1-3 keyframes) + Seedance 2.0 anima
  - `post estático` → gpt-image-2 × 1 imagen
- **Fase 1:** carousel-only para validar pipeline simple. El campo `formato_recomendado` se registra pero no se actúa.
- **Fase 2:** se activa la rama reel cuando Seedance + ElevenLabs estén listos.
- **Override manual:** se permite subir imágenes/videos propios via n8n node "Read Binary File" cuando se quiere bypass de generación (ej: foto del founder de una startup mencionada).
- **Estilo visual:** consistente cross-piece, definido en `VISUAL_STANDARD.md` (a crear como sección de POST_STANDARD.md).

### H — Cursor: **diferido (no activar hoy)**

- **Decisión:** no agregar Cursor al stack ahora.
- **Razón:** Cursor es un editor con Claude inline. Útil **solo si Manuel edita prompts/configs manualmente**. Hoy todo el editing lo hace Claude desde este chat con acceso al repo, así que Cursor no agrega valor incremental.
- **Costo evitado:** $20 USD/mes ($240/año).
- **Reabrir cuándo:** si Manuel empieza a iterar prompts solo (sin pasar por chat) o quiere hacer ajustes finos en JSON exportado de n8n, ahí vale la suscripción.
- **Manuel pidió explícito:** "por el momento no hay que activarlos... si hoy no es una parte fundamental del proceso, no hay que usarlo".

### I — Perplexity: **diferido (no activar hoy)**

- **Decisión:** no agregar Perplexity al stack ahora.
- **Razón:** Perplexity Pro es útil para (a) lectura matinal con citas, (b) Deep Research on-demand, (c) fact-check manual de backup. Pero **no reemplaza** al A4 Fact-Checker del pipeline (Claude web_search nativo via template #4399, ya integrado a n8n). El A4 corre automático en el workflow; Perplexity sería para Manuel personalmente, no para el pipeline.
- **Costo evitado:** $20 USD/mes ($240/año).
- **Reabrir cuándo:** si AI How-To LATAM valida y necesita Deep Research frecuente, o si los 5 prompts del 2026-05-18 (`DEEP_RESEARCH_PROMPTS.md`) requieren tool más robusta que ChatGPT Plus.
- **Manuel pidió explícito:** "por el momento no hay que activarlos... si hoy no es una parte fundamental del proceso, no hay que usarlo".

---

### E — Audio: **solo en reels, voice clone ElevenLabs 100% (tu voz)**

- **Carouseles silenciosos** — research confirma no requieren audio para performar.
- **Reels con audio:** ElevenLabs con voice clone de Manuel (ADR-008).
- **No requiere investigación adicional** — el research existente confirma el path:
  - Voz humana > IA en trust/loyalty (production-stack-research)
  - Voz clonada con TU voz cuenta como humana
  - Reels con audio original ganan distribución
  - "Made with AI" label penaliza -15 a -80% (production-stack-research)
- **Open item:** grabación de 20 min de voz de Manuel para ElevenLabs (script ya existe en `docs/voice-clone/recording-script.md`). Sin fecha comprometida. **No bloquea Fase 1.**

---

## Lo que YA está decidido (de docs + ADRs vigentes a 2026-05-12)

Antes de las preguntas, lo que ya no se discute (a menos que vos lo abras):

| Decisión | Source | Status |
|---|---|---|
| Orquestador: n8n cloud | ADR-009 | Firme |
| LLM editorial: Claude Opus 4 (calidad) | ADR-009 + AGENTS_SPEC | Firme |
| LLM scoring: Claude Sonnet 4.5 (barato) | AGENTS_SPEC + skeleton | Firme |
| Image gen: gpt-image-2 (no Canva primary, no Pillow) | ADR-013 | Firme |
| Voice clone: ElevenLabs 100% | ADR-008 | Firme pero pendiente grabación |
| Volumen: 1 pieza/día Fase 1 | ADR-011 | Firme |
| Ángulo editorial: generalista LATAM | ADR-010 | Firme con refinamiento mes 2 |
| Publisher: Upload-Post (resuelve ADR-012) | ADR-014 | Propuesto — Manuel confirma |
| Voz: Smart Brevity + Morning Brew + español neutro CDMX | brand_voice.md | Firme |
| Hooks: framework Rufusocial (atención + tensión + promesa) | brand_voice.md | Firme |
| 11 agents conceptuales | AGENTS_SPEC.md | Firme conceptualmente, falta implementación |

---

## Decisiones operacionales adicionales (abiertas 2026-05-12)

Items que descubrí en el diseño y necesitan tu definición. NO son críticos para Fase 0 (smoke test) pero sí destraban Fase 1.

### J — Audiencia objetivo nítida (buyer persona)

**Por qué pregunto:** `brand_voice.md` dice "tech-savvy LATAM". Eso cubre desde founders hasta ejecutivos de banco, devs, marketers, estudiantes. **Cada uno necesita briefs distintos.** El campo `relevancia_latam` del scorer A2 funciona mucho mejor con un buyer persona concreto.

**Ejemplo de lo que pido:** "Carlos, 32 años, manager en banco MX, usa ChatGPT a diario pero no le pidas que entienda papers. Le importa cómo usar IA para automatizar trabajo, no la architecture detrás. Lee Bloomberg, no arXiv."

**Opciones rápidas:**
- Opción 1: Founder/operador startup LATAM (early stage)
- Opción 2: Manager/director en corporativo LATAM tradicional (banco, retail, telco)
- Opción 3: Profesional knowledge-worker individual (consultor, abogado, médico)
- Opción 4: Inversionista/VC LATAM (busca señales de mercado)
- Opción 5: Mix (mañana 80/20 de cuál)

### K — Cadencia de lanzamiento

**Por qué pregunto:** sin deadline, el diseño puede iterar infinito. Con deadline, prioritizamos Fase 0 ejecutable sobre refinamientos.

- K1. ¿Hay fecha objetivo de **primer post público**?
- K2. ¿Hay fecha objetivo de **Fase 1 corriendo estable**?
- K3. ¿Hay algún evento (conference, launch público) que ancore una fecha?

### L — Handle de Instagram + logo

**Por qué pregunto:** sin handle reservado + sin logo, no hay publishing real. Aunque sea logo placeholder.

- L1. ¿Tenés handle reservado en IG? (ej: @aibrieflatam, @aibrief.latam) Si no, ¿cuál preferís?
- L2. ¿Hay logo o lo diseñamos? Si vas a diseñar uno, ¿quién (vos, freelance, AI)?
- L3. ¿Misma estrategia para TikTok handle?

### M — Newsletter footer (CAN-SPAM compliance)

**Por qué pregunto:** cuando arme Beehiiv, el footer obligatoriamente debe tener dirección física de la entidad emisora. Es ley en USA y buena práctica globalmente.

- M1. ¿Qué dirección física usar? Opciones:
  - Casa de Manuel (más simple, exposes private address)
  - Apartado postal (compra ~$50/año, más privacy)
  - Coworking / dirección comercial alquilada
  - Dirección de empresa LLC si AI Brief LATAM se incorpora formalmente

### P — Calibración voz: ✅ Viral hype calibrado (cerrada por ADR-016, 2026-05-18)

- **Decisión:** hook emocional/contrarian (primeros 3s reel / 125 chars caption) + body sobrio Smart Brevity.
- **Por qué:** Critical Review identificó que cuentas LATAM que llegan a >1M usaron hooks emocionales (NeoCom 1.4M, Filo 1.8M); las "sobrias" tienen techo ~30K. Para north star "audiencia masiva", necesitamos viral hype.
- **Compromiso:** captamos atención como virales, entregamos valor como premium. No es contradictorio.
- **Aplicar:** `brand_voice.md` ya actualizado (2026-05-18). Prompts A2/A3/A7 pendientes update post-Fase -1.

### U — Validación voz antes de invertir más: ✅ Fase -1 (cerrada por ADR-016, 2026-05-18)

- **Decisión:** Fase -1 "Validación Manual" agregada al ROADMAP v4 — Manuel publica 5-10 piezas con prompts directos en Claude.ai antes de comprometer pipeline.
- **Criterio de éxito:** >2% engagement promedio. Si menos, NO construir Fase 0/1.
- **Tracker:** simple .md en `projects/dinero-ia/manual-mvp/validation-fase-minus-1.md` (a crear cuando arranque).

### Q — Manuel-cara vs cuenta-de-marca pura

**Por qué pregunto:** las cuentas de personalidad crecen 5-10× más rápido que las de marca pura. Pero "experimento de automatización" implica que el creator NO se ponga la cara (la IA es el creator). Hay tensión.

**Opciones:**
- Opción 1: Manuel pone la cara (reels con su voz/cara, IG bio con foto). **Crece más rápido** pero "experimento automatización" se diluye.
- Opción 2: Cuenta de marca pura (sin cara, narrador clonado, mascot eventual). **Más fiel al experimento** pero growth 5-10× más lento.
- Opción 3: Híbrido — Manuel aparece ocasionalmente (1×/semana) como "creator behind the scenes", pero 80% del contenido es marca.

### R — Success criteria explícito para abortar/pivot

**Por qué pregunto:** sin criterio claro de "esto no funcionó", racionalizamos cualquier resultado. Necesitamos compromiso ex-ante.

**Opciones de criterio:**
- Fase -1: <1% engagement promedio en 10 piezas → abortar nicho actual, pivot.
- Fase 1 (Mes 1): <100 followers IG nuevos + <50 newsletter subs → pivot.
- Fase 1 (Mes 3): <500 followers IG total + <200 newsletter subs → pivot.
- Fase 1 (Mes 6): <1K followers IG + <500 newsletter subs → considerar otro nicho.

### S — Sustainability del operador (vacaciones, pausas, burnout)

**Por qué pregunto:** plan asume 1 pieza/día por 365 días. Sin plan de pausas, hay riesgo burnout en mes 3-6.

**Opciones:**
- Opción 1: Buffer de 7-14 piezas pre-aprobadas siempre listas. Permite 1-2 semanas off sin gap visible.
- Opción 2: Cadencia oficial 5×/semana (lunes-viernes), fin de semana off por default.
- Opción 3: Sprints — 30 días daily + 14 días off cada trimestre.

### T — Plan B si Meta/TikTok rompen automation

**Por qué pregunto:** Meta ha restringido automation tools 3 veces (2018, 2021, 2024). TikTok endureció labels AI 2025-2026. Si rompen Upload-Post API, el pipeline falla.

**Opciones de mitigación:**
- Opción 1: Newsletter como propiedad primaria (no dependiente de algoritmos). IG/TikTok como adquisición secundaria.
- Opción 2: Posteo manual de respaldo cuando automation falla (~10 min/pieza).
- Opción 3: Diversificación a más plataformas independientes (Threads, Bluesky, WhatsApp Channels).

### V — Nicho específico de how-to (post Deep Research)

**Por qué pregunto:** "AI How-To LATAM" es la dirección general. Falta nicho específico: ¿AI práctico genérico? ¿Herramientas específicas (Claude, ChatGPT, Notion AI)? ¿Por industria (marketing, ventas, RRHH)?

**Esto se contesta con outputs del Deep Research Prompt 4** (nichos alternativos con más techo).

### W — Build vs Buy decision (Blotato AI)

**Por qué pregunto:** Blotato AI cubre ~70% del pipeline custom a $29-97/mo. Critical Review sugiere evaluar antes de construir.

**Plan de validación:**
- Manuel comprá Blotato free trial / paid 1 mes en paralelo a Fase -1.
- Generá 5 piezas con su AI Agent Carousel Maker.
- Comparar contra 5 piezas manuales de Fase -1.
- Decidir: full Blotato / full custom / híbrido.

**Esto se afina con output del Deep Research Prompt 1** (tools que ya hacen esto).

---

### N — Decisión publisher (ADR-012 → ADR-014)

**Pendiente desde sesión 2.** Necesario para spec del node A10 de Fase 1.

- N1. ¿Buffer ($15/mo, maduro) | Blotato ($14/mo, carousel-first) | Upload-Post (self-hosted, control total) | Meta Graph API directo (gratis, complejo)?

### O — Decisión plan n8n cloud

**Pendiente.** Starter (€24/mo) NO alcanza para Fase 1 (4,500 ejec/mes estimado).

- O1. ¿n8n Pro €60/mo (cómodo) | self-hosted Hostinger VPS €5-7/mo (más mantenimiento) | mantener Starter reduciendo polling a 1×/día?

---

## Lo que YO asumí y no debería (mea culpa)

Cosas que metí en el skeleton sin confirmar con vos:

1. Que "1 pieza/día" = 1 carousel IG + variación TikTok (asumí que es una sola unidad multi-canal, no varias piezas independientes)
2. Que Supabase es la DB target para dedup history y archivo (no está confirmado — podría ser Google Drive, Airtable, n8n internal)
3. Que el formato default es carousel y los reels llegan en Fase 2 (vos podés querer reels desde día 1)
4. Que hay 1 solo punto de aprobación humana (final, antes de publicar) — vos podés querer 2-3 puntos
5. Que las 12 fuentes de `sources.yaml` son definitivas
6. Que el fact-check automático LLM es suficiente sin verificación humana
7. Que las imágenes generadas se almacenan en n8n binary storage temporal (no en disco permanente con archivo)
8. Que Cursor y Perplexity NO entran en el stack (no estaban en STACK.md)
9. Que el podcast (Fase 4) está suficientemente lejos para no influir en arquitectura ahora

Si alguna de esas asunciones está mal, decímelo en las preguntas abajo.

---

## Preguntas críticas (bloquean el diseño)

### A) Qué es exactamente "una pieza"

A1. **¿Qué cuenta como 1 unidad de contenido en Fase 1?**
- Opción 1: 1 carousel IG = 1 pieza. TikTok es un crosspost separado. Newsletter llega en Fase 3.
- Opción 2: 1 pieza = carousel IG + caption TikTok + sección de newsletter (todo en paralelo desde día 1).
- Opción 3: 1 carousel IG O 1 reel (alternancia por día). Newsletter llega en Fase 3.
- Opción 4: Otro.

A2. **Cuando dijiste "1 post/día" en ADR-011, ¿era 1 post total o 1 pieza compuesta?**
- (Si Opción 1 de A1 → 1 carousel/día. Si Opción 2 → 1 carousel + 1 TikTok + 1 sección newsletter/día.)

A3. **¿Cuándo entran los reels?** En el ROADMAP están en Fase 2 (semana 3-4). ¿Sigue siendo así o querés reels desde Fase 1?
- Opción 1: Reels estrictamente Fase 2. Carousel-only en Fase 1.
- Opción 2: Reels desde Fase 1, paralelos a carousel.
- Opción 3: Reels en Fase 1 pero solo para piezas con score muy alto (>80) — premium pieces.

### B) Quality controls — cuándo y cuántos

B1. **¿Cuántos puntos de aprobación humana querés?** Mis 3 opciones:
- Opción 1 (1 gate, mínima fricción): aprobación SOLO al final, con el post completo (caption + imágenes + hashtags) listo para publicar. Si está mal, rechazás todo y se descarta.
- Opción 2 (2 gates, balanceado): aprobación 1 después de A4 fact-check (apruebas el brief editorial); aprobación 2 al final con el post completo. Si gate 1 te gusta pero gate 2 no, se itera solo en imágenes/copy sin regenerar brief.
- Opción 3 (3 gates, máxima control): aprobación 1 = elegir tema entre top 3 scored; aprobación 2 = brief editorial; aprobación 3 = post completo.

B2. **¿Confiás en el fact-check 100% LLM (Claude + web_search)** o querés un human review obligatorio cuando hay flags?
- Opción 1: Confiás en LLM, FLAG no bloquea (queda anotado).
- Opción 2: FLAG bloquea y va a Telegram con highlights.
- Opción 3: Todos los items pasan por human review brevemente, no importa el verdict.

B3. **¿Querés que rejects/edits queden registrados** (para mejorar prompts después, tipo "human-feedback learning")?
- Opción 1: Sí, cada edit/rechazo se guarda con contexto.
- Opción 2: No por ahora, agregamos en Fase 1.5 o más adelante.

### C) Storage y archivo

C1. **¿Dónde se guardan los items procesados (dedup history, briefs aprobados, posts publicados)?**
- Opción 1: Supabase (Postgres) — vos lo creás, te paso schema. Mejor para queries analíticas.
- Opción 2: Google Sheets — más simple, podés ver en navegador, peor para queries complejas.
- Opción 3: n8n static workflow data — gratis pero acoplado a n8n, difícil de exportar.
- Opción 4: Airtable — visual + queries OK + integración n8n directa.

C2. **¿Dónde se guardan las imágenes generadas + assets binarios?**
- Opción 1: Supabase Storage (si elegís Supabase para C1).
- Opción 2: Google Drive (carpeta del proyecto, accesible visualmente).
- Opción 3: Cloudinary (mejor performance + CDN, paid después de free tier).
- Opción 4: n8n binary storage (efímero, se borra; OK para Fase 0 pero no producción).

C3. **¿Querés que cada pieza generada se archive como markdown en GitHub** (igual que el MVP Python guardaba en `projects/dinero-ia/manual-mvp/pieces/{date}_{slug}.md`)?
- Opción 1: Sí, archivo en GitHub commiteado por el workflow (audit trail permanente + searchable + diff-able).
- Opción 2: No, suficiente con DB/Drive.

### D) Image generation (gpt-image-2)

D1. **¿Para qué exactamente generamos imágenes con gpt-image-2?**
- Opción 1: 1 carousel de 5-7 slides (cada slide es 1 imagen 1080x1080).
- Opción 2: Solo 1 imagen cover hero (para reel thumbnail / newsletter header).
- Opción 3: Carousel + cover newsletter (varias generaciones por pieza).
- Opción 4: Mix dinámico según `formato_recomendado` del brief (carrusel vs reel vs post estático).

D2. **¿Querés un estilo visual consistente o variable?**
- Opción 1: 1 estilo locked. Cada slide del carousel usa la misma paleta + tipografía + framing.
- Opción 2: Estilo definido por sub-categoría (ej: piezas sobre regulación = serio, piezas sobre productos = colorido).
- Opción 3: A5 (Visual Director) decide caso por caso desde Fase 1.

D3. **¿Watermark "AI Brief LATAM" en las imágenes?**
- Opción 1: Sí, esquina inferior derecha, sutil.
- Opción 2: Sí, pero solo en última slide (call-to-action).
- Opción 3: No, mejor logo orgánico via diseño en lugar de overlay.

### E) Audio y video

E1. **¿Audio en posts no-reel (carouseles, posts estáticos)?**
- Insight del research: Reels con audio original ganan distribución, pero carousel no requiere audio para performar bien.
- Opción 1: No, audio solo en reels.
- Opción 2: Sí, agregamos audio ambient a carousels también (música stock).
- Opción 3: Sí, voz narrada en carousels también (ElevenLabs leyendo el caption como audio overlay).

E2. **¿Seedance 2.0 entra cuándo exactamente?**
- ROADMAP dice Fase 2 (semana 3-4). 
- Opción 1: Estrictamente Fase 2, después de validar carousel.
- Opción 2: Fase 1 si Manuel quiere reels desde día 1 (depende de A3).
- Opción 3: Postergar Seedance, usar reels más simples (slideshow de imágenes + voz) en Fase 2.

E3. **ElevenLabs voice clone**: ADR-008 dice voice clone 100%. La grabación de 20 min está pendiente.
- E3a. ¿Cuándo podés hacer la grabación? Eso bloquea Fase 2 entera.
- E3b. ¿La voz clonada se usa para TODO (reels, podcast, audio en carousels) o solo para algunos?
- E3c. ¿Querés un "estilo de lectura" definido (energético, calmo, formal, casual) o varía por pieza?

E4. **¿Vale la pena audio en TODO el contenido?** Manuel preguntó esto explícitamente.
- Mi take: **No automáticamente sí**. El research dice voz humana > AI, pero la voz humana clonada (ElevenLabs con tu voz real) está bien. Lo que mata engagement es voz robótica genérica. Si la voz suena a vos, sí vale. Si suena artificial, no.
- Tu llamada: ¿vamos con audio en reels desde Fase 2 (con tu voz clonada), o esperamos a tener resultado de la grabación para decidir?

### F) Sources de información

F1. **¿Las 12 fuentes de `sources.yaml` son las definitivas para Fase 1?**

Las que están listadas hoy:
- **Oficial:** OpenAI Blog (RSS), Anthropic Blog (scrape), Google AI Blog (RSS) → 3 fuentes
- **Tech media:** TechCrunch AI, The Verge AI, Ars Technica, Wired AI, Fortune AI → 5 fuentes
- **Newsletters:** Latent Space → 1 fuente
- **Community:** Hacker News → 1 fuente
- **LATAM:** Contxto, LatamList → 2 fuentes

Notable: 10 de 12 son anglo. **Solo 2 son LATAM nativas** (Contxto + LatamList). Eso es flojo para "AI Brief LATAM".

- Opción 1: Aceptar la lista actual (mayoría anglo, traducís el ángulo LATAM tú vía editorial prompt).
- Opción 2: Expandir LATAM agregando Bloomberg Línea Tech, Forbes Latam Tech, Pulso Social Colombia, La Nación Tecnología, Genbeta, Infobae Tech, etc.
- Opción 3: Agregar fuentes regulatorias LATAM (CNV Argentina, CNBV México, BCB Brasil) si una pieza específica de how-to toca regulación. Default: NO (multi-property diferido por ADR-016).
- Opción 4: Otra combinación.

F2. **¿Querés monitorear founders/voces LATAM en X/Twitter?** (Ej: Pierpaolo Barbieri Ualá, Marcelo Claure, Daniel Vogel Bitso, etc.)
- Opción 1: Sí, hacemos lista curada de ~20 cuentas LATAM y polleamos sus posts.
- Opción 2: No, X tiene rate limits restrictivos y la calidad varía.
- Opción 3: Sí pero como Fase 1.5 o más adelante, no urgente.

F3. **¿Inoreader o feedly como hub intermedio?** El production-stack-research del 2026-05-07 lockeaba Inoreader Free para discovery manual. Si todo va por n8n, ¿Inoreader sale del stack?
- Opción 1: Inoreader fuera, n8n hace todo el RSS directo.
- Opción 2: Inoreader sigue (mejor curación pre-n8n), n8n consume el Inoreader OPML feed.

### G) Standard de calidad — bar para publicar

G1. **¿Qué cuentas son tu referencia visual para "esto es lo que quiero que parezca"?**
- Opción 1: The Rundown AI (USA, minimalista tech)
- Opción 2: Ecosistema Startup (LATAM, casual sobrio)
- Opción 3: Startupeable (LATAM, premium analítico)
- Opción 4: DotCSV (España, tech denso)
- Opción 5: Mafia IA (España, marketing-aspiracional)
- Opción 6: Otra cuenta concreta.

G2. **¿Bar mínimo para publicar?** (Cuándo se descarta una pieza)
- Opción A: Si fact-check verdict = REJECT, descarta automático.
- Opción B: Si compliance verdict = REJECT, descarta automático.
- Opción C: Si signal_score < umbral (cuál?), descarta automático.
- Opción D: Si la pieza tiene >2 risk_flags, descarta automático.
- (Vos elegís cuáles aplican, podés combinar.)

G3. **¿Modo de voz visual?**
- Opción 1: Dark mode (negro/grafito + acentos), tech-minimal.
- Opción 2: Light mode (blanco/cream + acentos), editorial-magazine.
- Opción 3: Híbrido (carousel decide según contenido).

---

## Preguntas no críticas pero útiles

### H) Cursor — ¿lo usamos?

Mi take honesto: **Cursor es IDE para código**, no para correr workflows. n8n es 100% browser-based. Casos donde Cursor podría servirnos:
1. Editar el JSON v2 manualmente antes de import (alternativa al patch programático en Python que propongo).
2. Editar los prompts en `projects/dinero-ia/prompts/*.md` con sugerencias inline.
3. Iterar el JSON post-export (n8n permite export JSON, lo editás en Cursor, reimportás).

Si te resulta más cómodo editar JSON visualmente con autocompletado y errores en línea, Cursor es bueno para eso. Si preferís que yo haga los patches con Python sobre el archivo del repo (que es lo que vengo haciendo), Cursor no agrega valor.

H1. **¿Usamos Cursor para alguna parte del flujo?**
- Opción 1: No, dejame los patches a mí con Python sobre el repo.
- Opción 2: Sí, te paso los diffs y vos los aplicás en Cursor (más control fino).
- Opción 3: Híbrido (yo hago patches grandes, vos hacés ajustes finos en Cursor).

### I) Perplexity — ¿lo agregamos al stack?

Mi take: Perplexity sirve para **research profunda** (lo que hacen los Deep Research que procesamos hace 4 días). Pero para el pipeline diario:
- Como fact-checker → existe alternativa nativa de Claude (web_search Tool del template #4399). Anthropic web_search es más barato y mejor integrado a n8n.
- Como source monitor → posible (Perplexity puede sintetizar "qué pasó hoy en AI"), pero no reemplaza fuentes RSS confiables.
- Como reasearch on-demand → útil si Manuel necesita profundizar un tema concreto manualmente, no necesariamente parte del workflow.

I1. **¿Agregamos Perplexity Pro ($20/mes) al stack?**
- Opción 1: No, Claude web_search nativo cubre el fact-check.
- Opción 2: Sí, para deep research on-demand del operador (Manuel) y como backup del fact-check.
- Opción 3: Sí, lo metemos como fact-checker primario (Claude editorial → Perplexity verification).

---

## El siguiente paso depende de tus respuestas

Una vez que respondas las preguntas críticas (A, B, C, D, E), reescribo el `N8N_WORKFLOW_SKELETON.md` con un diseño que refleje TU producto, no mis asunciones. Después de eso, recién tiene sentido tocar el JSON.

Si querés, podés responder en este chat (1 mensaje con respuestas a las preguntas que te interesen) o editar este archivo directamente.

**No hace falta responder todo de una vez.** Las preguntas críticas (A, B, C, D, E) son las que bloquean. F, G, H, I se pueden ir resolviendo después.
