# Deep Research Prompts — Carril 2 del step-back

**Fecha:** 2026-05-18
**Propósito:** Prompts diseñados para que Manuel ejecute en ChatGPT Deep Research / Perplexity Pro / Claude.ai Research. Cada prompt apunta a validar o desafiar una decisión clave del plan actual.

> **Cómo usar:**
> 1. Copiá el prompt al final de cada sección (entre los `---`) en tu tool de Deep Research preferida.
> 2. Esperá el output (típicamente 5-20 min en modo Deep Research).
> 3. Guardá el output en `projects/dinero-ia/docs/research/deep-research/2026-05-XX_<nombre>.md`.
> 4. Avisame y revisamos juntos lo que cambia del plan actual.
>
> **Orden recomendado:** del 1 al 5. Los primeros 3 son MÁS críticos. El 4 y 5 son nice-to-have.

---

## Prompt 1 — ¿Qué tools SaaS ya hacen esto?

**Validar:** ¿Vale construir custom o existe shortcut?
**Decisión que afecta:** build vs buy. Si hay SaaS a $30-100/mo que cubre 70%+, el plan custom de Hostinger + n8n + 10 prompts pierde justificación.

```
Estoy evaluando construir un pipeline custom de automatización de contenido para Instagram + TikTok + newsletter en español neutro LATAM, sobre el tópico de noticias/análisis de Inteligencia Artificial. El pipeline incluye:

1. Monitoreo de 12+ fuentes RSS (TechCrunch AI, OpenAI Blog, etc.)
2. LLM scoring de relevancia con rúbrica custom (8 categorías incluyendo "relevancia LATAM")
3. Generación de brief editorial estructurado (formato Smart Brevity)
4. Fact-checking automático con web search
5. Generación de carousel Instagram de 5-7 slides con gpt-image-2
6. Caption + hashtags optimizados por plataforma (IG + TikTok separados)
7. Newsletter daily formato Smart Brevity (Intro + Top Story + Quick Hits)
8. Compliance check contra reglas Meta + brand voice
9. Human-in-the-loop vía Telegram (aprobar/editar/rechazar)
10. Auto-publish a IG + TikTok + newsletter Beehiiv

Mi alternativa actual: n8n self-hosted + Anthropic Claude API + OpenAI gpt-image-2 + Upload-Post + Supabase + ElevenLabs + Beehiiv. Costo estimado $48-65/mo Fase 1.

INVESTIGÁ exhaustivamente:

a) ¿Qué tools SaaS existen en 2026 que automatizan TODO o PARTE de este pipeline? Lista al menos 8 con: pricing, features cubiertas, integraciones, casos de uso documentados, opiniones reales de usuarios (Reddit, X, Trustpilot, G2, Product Hunt).

b) Para cada tool, indicá qué % del pipeline cubre y qué falta. Especial foco en: Blotato AI, Repurpose.io, Castmagic, Opus Pro, Submagic, Buffer AI, Hootsuite AI, Later AI, Beehiiv AI, ContentStudio, MeetEdgar, Lately AI.

c) ¿Hay tools específicamente para contenido en español LATAM o que manejen bien el español neutro?

d) ¿Cuál sería el stack MÁS BARATO de SaaS off-the-shelf que cubra 80%+ del pipeline?

e) Trade-offs reales build vs buy en 2026 para este caso: ¿qué pierde un operador-solo construyendo custom vs comprando SaaS?

f) Casos documentados de creators/founders que armaron pipelines similares — ¿qué eligieron y por qué? Buscá historias en Twitter, threads, podcasts founder, posts de Indie Hackers.

Devolveme análisis con citas concretas, links a fuentes, y recomendación accionable.
```

---

## Prompt 2 — Análisis competitivo profundo del espacio "AI newsletter en español"

**Validar:** ¿Hay techo de audiencia masiva en este nicho?
**Decisión que afecta:** seguir con AI Brief o pivotar a nicho menos saturado.

```
Estoy evaluando lanzar una propiedad de medios sobre Inteligencia Artificial para audiencia LATAM (español neutro, profesionales 25-45 años) en Instagram + TikTok + newsletter Beehiiv. Mi north star es audiencia masiva (>50K-100K en 12-18 meses).

Necesito un análisis competitivo PROFUNDO de los players actuales en este espacio:

JUGADORES A INVESTIGAR (priorizar estos pero agregar más si encontrás):
- Digital Brain (newsletter ES+LATAM, ~60K subs, 42% open rate reportado)
- IA al Día (newsletter LATAM, ~20K+ subs)
- DotCSV / Carlos Santana (España, IG ~104K, YouTube ~500K+)
- Mafia IA (España)
- Newsletter Más AI (España)
- Cualquier creator/newsletter LATAM enfocado en IA que tenga >10K audiencia

PARA CADA JUGADOR, INVESTIGAR:

a) Historia: cuándo lanzaron, cómo crecieron, cuál fue el unlock que los hizo escalar (un viral, un sponsor, un cambio de formato).

b) Posicionamiento exacto: ¿news brief / educación / curaduría / opinión? ¿Audiencia objetivo declarada?

c) Formato y cadencia: ¿daily / weekly? ¿Long-form / short? ¿Tono sobrio / viral / educativo?

d) Métricas públicas o reportadas: subs, open rate, engagement rate IG, follower count, growth rate.

e) Monetización: ¿sponsors, suscripción paga, cursos, consulting? ¿Quiénes son sus sponsors actuales?

f) Voz y estilo: copiame ejemplos textuales reales de su contenido — al menos 3-5 piezas por jugador. Quiero ver cómo escriben.

g) Producción: ¿manual / automatizado / equipo? ¿Cuántas personas trabajan en cada uno?

h) Debilidades o gaps: ¿qué NO cubren? ¿Qué quejas tienen sus audiencias en comentarios?

i) Tendencia de crecimiento últimos 6 meses (mediante Wayback Machine, social blade, similar tools).

PREGUNTAS DE SÍNTESIS:

j) ¿Cuál es el TECHO de audiencia realista para una nueva entrada al espacio "AI newsletter en español LATAM" en 2026?

k) ¿Qué diferenciación REAL queda disponible? Identificá 3-5 ángulos no cubiertos.

l) ¿El espacio "AI Brief Latinoamérica" tiene espacio para un newcomer en 2026, o está saturado y el techo razonable es <15K subs en 12 meses?

m) Si NO está saturado: cuál es la mejor strategy de entrada (formato, tono, frecuencia, hook diferencial).

n) Si está saturado: cuáles son nichos adyacentes en español LATAM con MÁS techo de audiencia masiva y MENOS competencia (ej: "AI práctico how-to", "AI para X industria", crypto LATAM, etc.).

Devolveme análisis con tablas comparativas, ejemplos textuales reales, y recomendación accionable sobre seguir vs pivotar.
```

---

## Prompt 3 — Playbook de newsletters/IG en español que crecieron a 10K-100K

**Validar:** ¿Qué hicieron los exitosos en los primeros 30-90 días?
**Decisión que afecta:** prioritization de Fase 0/1. Si todos los exitosos hicieron X en mes 1 y nosotros no lo tenemos en el plan, agregar.

```
Estoy lanzando una propiedad de contenido en español LATAM (Instagram + newsletter daily) sobre temas de tecnología/IA. Quiero estudiar a fondo qué hicieron los creadores que llegaron a 10K-100K seguidores/subs en español en los últimos 5 años, especialmente en LATAM.

CREADORES A ESTUDIAR (lista no exhaustiva, agregá si encontrás más):
- Startupeable (Enzo Cavalié) — startups LATAM, 27K IG + 50K newsletter + 49K LinkedIn
- Ecosistema Startup (Cristian Tala) — startups Chile/LATAM, 12K IG + 10K+ newsletter
- Nicolas Abril — educación financiera LATAM, 1M IG
- DotCSV (Carlos Santana) — IA España, 104K IG + 500K YouTube
- Mafia IA (España)
- NeoCom — pop culture LATAM, 1.4M IG en 2 años
- Filo News — news LATAM, 1.8M IG
- Cualquier otro creator español/LATAM relevante

PARA CADA CREADOR, INVESTIGÁ:

a) Origen story: ¿quién era antes? ¿Trabajaba en algo relacionado o partió de cero?

b) Primer post viral: identificá el hit que los puso en el mapa. Si podés conseguir el link o screenshot del post, mejor.

c) Cadencia primeros 30, 60, 90 días: ¿cuántos posts/día? ¿Cuándo posteaban?

d) Format mix primeros 90 días: ¿% carousel / reels / posts estáticos / stories?

e) Hook patterns: 3-5 ejemplos textuales de hooks que más viralizaron. ¿Eran preguntas, cifras, contrarian claims, listicles?

f) Cuándo arrancaron newsletter (si tienen): ¿después de cuántos seguidores IG? ¿Lead magnet específico?

g) Punto de inflexión: ¿qué los hizo pasar de 1K → 10K? ¿Y de 10K → 100K?

h) Errores documentados: ¿qué dijeron públicamente que harían diferente?

i) Stack de herramientas: ¿manual o automatizado? ¿Qué tools usan?

j) Sponsor / monetización timeline: ¿cuándo aparece primer sponsor? ¿Cuánto cobran?

PREGUNTAS DE SÍNTESIS:

k) Patrones COMUNES en los primeros 30 días de los que escalaron: 3-5 prácticas que todos hicieron.

l) Patrones COMUNES después del primer viral: cómo capitalizaron.

m) Tiempo MEDIO desde lanzamiento hasta 10K, 50K, 100K seguidores — promedio + rango.

n) ¿Cuáles eran 100% solo-founders y cuáles tenían equipo? ¿La diferencia es relevante?

o) Si yo lanzo en 2026 con un pipeline automatizado IA + 1 pieza/día + newsletter daily, ¿qué % de chance tengo de llegar a 10K en 12 meses según los patrones que veas?

Devolveme análisis con datos específicos, ejemplos textuales/visuales (links si podés), y playbook accionable para primeros 90 días.
```

---

## Prompt 4 — Nichos LATAM con más techo que AI news

**Validar:** ¿Hay nichos con MÁS audiencia masiva y MENOS saturación?
**Decisión que afecta:** pivot tópico antes de comprometer 6 meses.

```
Estoy decidiendo qué nicho de contenido lanzar para alcanzar audiencia masiva en español LATAM (target: >50K-100K seguidores en 12-18 meses) vía Instagram + TikTok + newsletter Beehiiv.

Mi opción default es AI/IA noticias LATAM, pero quiero validar contra alternativas. El criterio de éxito: máximo techo de audiencia × mínima saturación competitiva × ángulo defensible para 1 operador solo (sin equipo).

NICHOS A EVALUAR (no exclusivo, agregá si ves oportunidad):
1. AI/IA noticias LATAM (mi default)
2. AI/IA práctico — how-to específico ("cómo usar X tool para Y")
3. Crypto LATAM (Bitcoin + ETH + stablecoins + tokenization)
4. Productividad / hábitos LATAM
5. Finanzas personales LATAM
6. Real estate LATAM
7. Geopolítica / crisis (análisis sobrio)
8. Pop culture / tendencias virales
9. Negocios / emprendimiento LATAM
10. Educación financiera (variante específica)
11. Health / wellness práctico LATAM
12. Tech generalista (mix de varios)

PARA CADA NICHO, INVESTIGÁ:

a) Tamaño actual de audiencia total LATAM-hispanoparlante interesada en el tópico (estimación, vía Google Trends + datos de plataformas).

b) Top 3-5 cuentas/newsletters DOMINANTES en español LATAM en ese nicho. Tamaño actual.

c) Saturación: 🟢 baja (1-3 players grandes) / 🟡 media (4-8) / 🔴 alta (>10).

d) Engagement rate típico en ese nicho (saves, comments, shares).

e) Monetizabilidad relativa: ¿hay sponsors activos pagando $X CPM? ¿Cursos? ¿Affiliate?

f) Algoritmo-friendly: ¿IG/TikTok premian ese tópico o lo penalizan? (algunos como crypto tienen restricciones).

g) Sustainability del operador solo: ¿cuánto research diario requiere? ¿Quema o se mantiene fresco?

h) Riesgo regulatorio / compliance: ¿Meta restringe? ¿FTC LATAM equivalente? ¿Legal?

i) Ejemplos de casos de éxito específicos LATAM últimos 3 años (creators que llegaron a 50K+ en ese nicho).

j) Ejemplos de fracasos públicos (qué los hundió).

PREGUNTAS DE SÍNTESIS:

k) Ranking de los 12 nichos por: techo de audiencia × inversa(saturación) × monetizabilidad × sustainability del operador solo.

l) Top 3 recomendaciones para alguien que quiere maximizar audiencia masiva.

m) ¿AI/IA news LATAM está en el top 3? Si no, ¿qué nicho específico recomendás como mejor apuesta?

n) ¿Hay nicho híbrido / combinado que tenga ventajas únicas (ej: "AI for crypto", "AI productividad")?

o) Para cada top 3, esbozá strategy de entrada (formato, frecuencia, hook diferencial).

Devolveme análisis estructurado con tabla comparativa, casos concretos, y recomendación accionable.
```

---

## Prompt 5 — Riesgos técnicos y de plataforma 2026

**Validar:** ¿Qué riesgos no estamos viendo?
**Decisión que afecta:** plan B + mitigaciones que faltan en arquitectura.

```
Estoy diseñando un pipeline automatizado de contenido (Instagram + TikTok + newsletter) usando IA generativa (Claude + gpt-image-2 + ElevenLabs voice clone) para lanzar una propiedad de medios LATAM en 2026.

INVESTIGÁ exhaustivamente los riesgos siguientes:

a) **Meta API / Instagram Content Publishing API restrictions 2025-2026:**
   - Cambios documentados últimos 12 meses en políticas de auto-posting
   - Restricciones específicas a tools de tercera parte (Buffer, Upload-Post, Blotato, Hootsuite)
   - Casos públicos de cuentas suspendidas o limitadas por uso de automation
   - Limitaciones técnicas vigentes (cuántos posts/día, qué formats permite la API, etc.)
   - Forecast: ¿qué cambios se anticipan próximos 6-12 meses?

b) **TikTok automation policies:**
   - Estado actual de Content Posting API
   - Restricciones a auto-uploads vs manual
   - "AI-generated content" labels: cuándo se requieren, penalización por no marcar
   - Casos de cuentas suspendidas por uso de automation tools

c) **"Made with AI" labels — Meta + TikTok + LinkedIn:**
   - Política actual exacta de cada plataforma
   - Cómo detectan AI content (watermarks, metadata, classifiers)
   - Penalización en reach documentada (research papers, posts oficiales, leaked memos)
   - Voice clone (ElevenLabs): ¿se detecta como AI o pasa como humano?
   - Imagen generada (gpt-image-2): ¿detección actual qué % accuracy?
   - Estrategias documentadas de creators para minimizar el label

d) **OpenAI gpt-image-2 + Anthropic Claude API risks:**
   - Cambios de pricing previstos 2026 (research últimos changelog)
   - Rate limits actuales y previstos
   - Restricciones de contenido (qué prompts rechaza)
   - Disponibilidad para uso comercial sin restricciones

e) **n8n self-hosted risks:**
   - Vulnerabilidades de seguridad documentadas últimos 12 meses
   - Best practices de hardening para producción
   - Riesgo de community nodes (Upload-Post node) — historial de bugs

f) **Burnout y sustainability de creators automatizados:**
   - Estudios sobre creator burnout 2024-2026
   - Casos documentados de creators que pararon por automation backfiring
   - Best practices para sustainability operando solo

g) **Newsletter / Beehiiv specific risks:**
   - Deliverability issues recientes
   - Gmail/Outlook tab placement changes (Promotions vs Primary)
   - CAN-SPAM enforcement en LATAM
   - Beehiiv cambios de pricing 2025-2026

PREGUNTAS DE SÍNTESIS:

h) Top 5 riesgos REALES (no teóricos) para un pipeline IA-automatizado en 2026.

i) Para cada uno, mitigaciones concretas que están aplicando creators exitosos.

j) Decisiones de arquitectura que SE AGRADECEN en 12 meses cuando algo cambie (resilience).

k) Si tuvieras que apostar: ¿cuál plataforma (IG, TikTok, newsletter) es la más SEGURA para invertir esfuerzo en 2026-2027?

Devolveme análisis con citas a fuentes oficiales/news, ejemplos de casos reales, y framework de mitigaciones aplicables a mi caso.
```

---

## Cómo procesar los resultados

Cuando Manuel ejecute los prompts y tenga outputs:

1. **Guardar cada output** en `projects/dinero-ia/docs/research/deep-research/2026-05-XX_<nombre>.md`
2. **Avisarme** que están listos
3. **Yo hago crítica honesta** de cada output (al igual que las del 2026-05-08): bias detection, claims sin evidencia, recomendaciones débiles
4. **Sesión de síntesis** combinada con `docs/CRITICAL_REVIEW.md` (carril 1) y las respuestas del carril 3
5. **Decisión:** ¿el plan actual sigue? ¿pivotamos? ¿qué cambia?

## Estimación de tiempo

| Item | Tiempo Manuel | Tiempo procesamiento Deep Research |
|---|---|---|
| Prompt 1 (build vs buy) | 1 min copy-paste | 10-20 min |
| Prompt 2 (competitive) | 1 min | 15-25 min |
| Prompt 3 (playbook) | 1 min | 15-25 min |
| Prompt 4 (nichos alternativos) | 1 min | 15-25 min |
| Prompt 5 (riesgos) | 1 min | 10-20 min |
| **Total** | **~5 min Manuel** | **~65-115 min procesamiento (en background)** |

Manuel puede lanzarlos todos en paralelo si la tool lo permite (ChatGPT Deep Research permite multi-thread; Perplexity Pro un thread a la vez pero rápido).

## Tool recommendada

| Tool | Pros | Contras | Best for |
|---|---|---|---|
| **ChatGPT Deep Research** (Plus/Pro) | Mejor citas, output más estructurado, multi-source | Tarda más (10-30 min) | Prompts 2, 3, 4 (research profundo con muchas fuentes) |
| **Perplexity Pro** | Más rápido (~5 min), mejor en consultas técnicas | Menos profundo | Prompts 1, 5 (técnico, comparativas) |
| **Claude.ai Research mode** | Razonamiento profundo, output narrativo | Citas menos rigurosas | Prompts 4 (síntesis) |

Mi sugerencia: **prompts 1 y 5 en Perplexity Pro, prompts 2-3-4 en ChatGPT Deep Research**.
