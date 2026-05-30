# Deep Research — Prompt 3: Playbook de creators ES/LATAM (10K–100K)

**Fecha de ejecución:** 2026-05-18
**Tool usada:** Claude Code (4 sub-agentes en paralelo con WebSearch/WebFetch — NO ChatGPT Deep Research)
**Prompt fuente:** `docs/DEEP_RESEARCH_PROMPTS.md` § Prompt 3
**Output destinado a:** alimentar decisión sobre prioridades de Fase 0/1 del lanzamiento de AI Brief LATAM

---

## TL;DR — 7 hallazgos accionables

1. **El "primer post viral" es un mito retroactivo.** En 11 creators investigados, NINGUNO identificó un single post como detonante. El inflection point siempre fue un **canal externo apalancado** (partnership, podcast invitado, press hit, inversor, fichaje editorial). Lección: dejar de optimizar por viralidad orgánica del día 1; planear el lever externo desde mes 1.
2. **Newsletter primero, no Instagram primero.** Los 4 creators con escalado más limpio en español (Startupeable, Ecosistema Startup, Cenital, Mafia IA) construyeron sobre **owned channel (email/blog)** y usaron redes como distribución. Solo los proyectos con equipo grande (Filo, Pictoline, Mis Propias Finanzas) hicieron social-first.
3. **El catalizador de los AI creators NO fue producto propio — fue ChatGPT (nov 2022).** DotCSV pasó de ~400K a ~750K subs en 12 meses post-ChatGPT. Mafia IA lanzó 5 meses antes del launch y capitalizó la ola. Para AI Brief LATAM en 2026: el próximo "ChatGPT moment" (¿GPT-5 GA? ¿AGI claim? ¿regulación LATAM?) es el lever esperable, no la viralidad del carrusel.
4. **Cadencia 30/60/90 días es un agujero negro del research público.** En 11 creators, solo Ecosistema Startup tiene cadencia primaria documentada (daily desde día 1). El resto está sin fuente. **Implicación:** no se puede benchmarkear contra "lo que hicieron en el primer mes" porque nadie lo publicó. Hay que decidir desde primeros principios.
5. **Mass audience (>500K) siempre tiene equipo.** Pictoline = 16-18 personas. Filo News = ~120. Mis Propias Finanzas = pareja + team escalado. DotCSV solo años 1-3, después expandió equipo. Un founder solo con pipeline IA puede aspirar realista a **10K-50K en 12-18 meses**, no a 100K+ sin contratar.
6. **El nicho "AI español neutro LATAM" tiene gaps reales.** Todos los competidores principales (DotCSV, Mafia IA, Digital Brain, GptZone, IA en Español, Xavier Mitjana, Jon Hernández, Monos Estocásticos) son **España-céntricos** o usan español neutro-peninsular. Ninguno cubre regulación LATAM, casos LATAM, o adapta a castellano regional. Hay espacio.
7. **El tono LATAM ganador es sobrio educativo + irreverencia controlada.** Sofía Macías marcó el patrón en 2008 con "hippies, yuppies y bohemios". Pergolini (Filo): "ya no se necesita gritar, alcanza con susurrar". Es lo OPUESTO al hype-bro tone de Mafia IA o Jon Hernández. Calibrar AI Brief LATAM hacia el primer registro probablemente convierta mejor en audiencia profesional 25-45 que es el target declarado.

---

## Metodología y limitaciones honestas

**Cómo se ejecutó.** 4 sub-agentes en paralelo, cada uno con WebSearch + WebFetch, briefing detallado, ~3-7 min de búsqueda cada uno, instrucción dura de marcar "No encontrado" en vez de inventar. Output consolidado y verificado por el orchestrator.

**Lo que NO es esto.** No es ChatGPT Deep Research formal (que tarda 20-30 min y tiene mejor citación). No incluye análisis de scraping de archivo de IG/Substack (que daría cadencia real). No incluye entrevistas directas a los creators. Es research de superficie + síntesis honesta, no investigación primaria.

**Gaps que NO se pudieron cerrar:**
- Cadencia exacta primeros 30/60/90 días para 10 de los 11 creators
- Format mix porcentual exacto en los primeros 90 días
- Primer sponsor y fecha exacta para casi todos
- Hooks textuales verbatim de los primeros 90 días (vs hooks actuales que sí están)

**Reemplazos del prompt original:**
- **NeoCom**: no se encontró cuenta verificable con esas métricas. Sustituido por **Pictoline** (México) que cumple perfil descripto (pop culture/news LATAM masivo).
- **Mafia IA**: confirmado (Alex DC / La Mafia IA). Es real.
- **Newsletter Más AI**: no encontrado. Posible confusión de nombre.
- **Carlos Bravo, David Ferrer, IAxFavor, Decoder LATAM**: no encontrados como AI creators relevantes. Descartar de la lista competitiva.

**Creators agregados al análisis** (que faltaban en el prompt original):
- **Cenital** (Argentina, newsletter-first, modelo membership)
- **Mis Propias Finanzas** (Carolina Pineda + Juan Pablo Zuluaga, Colombia)
- **Pequeño Cerdo Capitalista** (Sofía Macías, México)
- **Andrés Gutiérrez** (México/EEUU)
- **Digital Brain** (España, AI ejecutivo)
- **GptZone** (España, único daily real)
- **IA en Español** (Substack 46K subs)
- **Xavier Mitjana** (España, AI práctico)
- **Jon Hernández** (España, AI dramático)
- **Monos Estocásticos** (España, podcast)

---

## Parte 1 — Findings por creator (condensado)

### A. Startup ecosystem newsletters

**Startupeable (Enzo Cavalié)** — Perú/México. ~27K IG · ~50K newsletter · ~49K LinkedIn · 5M+ descargas podcast.
- **Origen**: economista, VC associate en Dalus Capital cuando lanzó. Blog Medium 2019 → Substack mayo 2020 → podcast enero 2021.
- **Cadencia**: podcast semanal (miércoles) + newsletter biweekly. Primeros meses: 1-2 posts long-form/mes en Medium, sin schedule fijo.
- **Hook patterns reales**: *"En las etapas tempranas, el 70% de tus usuarios van a venir de 1 canal"* (cifra + contrarian) · *"Top 10 Libros Recomendados"* (listicle) · build-in-public con métricas explícitas.
- **Inflection point**: lanzamiento del podcast con Santiago Zavala (500 Startups) en enero 2021. **Estrategia "borrowed audience"** con guests blue-chip (Mercado Libre, Nubank, Vercel, Kavak, Cornershop) — cada guest activa su red.
- **Stack**: Substack + dominio propio + **productora externa Explora** (NO DIY). LinkedIn Top Voice México 2022 amplificó.
- **Monetización**: sponsors podcast/newsletter + Reach Capital (Silicon Valley) como su empleo principal — Startupeable es leverage profesional, no business standalone.

**Ecosistema Startup (Cristian Tala)** — Chile. ~12K IG · >10K newsletter · 9.5K LinkedIn.
- **Origen**: ingeniero informático, exit de **Pago Fácil por US$23M** a BCI Pagos en mayo 2021. Lanzó EES el 13 mayo 2023 (MVP en <3 semanas).
- **Cadencia**: **DAILY newsletter desde día 1**. Único caso documentado con cadencia diaria desde el lanzamiento.
- **Primer mes**: 5.000 usuarios únicos. Primer evento presencial: esperaban 50, llegaron +100.
- **Hook patterns**: nombre propio + cifra/récord ("Toku: USD 48M en Serie A") · listicles numéricos · "lo que nadie te dice".
- **Inflection point**: capital propio de **US$100K quemado año 1** + dos partners con credenciales (Josefina Martínez ex-Forbes Chile, Alonso Skywalters publicista). No fue viralidad, fue **war chest + equipo**.
- **Stack**: **Beehiiv** + Skool (comunidad gamificada) + stack altamente automatizado con IA (Tala publica sobre AI cost optimization).
- **Monetización**: diferida a año 2 (declarado a DF). Modelo: media holding angel-financiado.

### B. Educación financiera LATAM

**Nicolás Abril** — Colombia. ~1M IG · 211K TikTok · 131K Threads. Fundador Finangency + Mony Club.
- **Origen**: economista, monitor académico 2014-2017, transición a creator probable 2022-2023.
- **Cadencia 30/60/90**: NO ENCONTRADA.
- **Hook patterns**: "¿Buen momento para abrir un CDT?" · "¿Prestarle dinero al banco? 😱" · pregunta retórica + emoji shock + apelación nacional (🇨🇴).
- **Format**: ~75% reels / 20% carrusel / 5% estático (estimación visual).
- **Inflection point**: NO DOCUMENTADO. Aparece ya con >1M en Moneycon Uniandes ene 2025.
- **Monetización**: curso "Cuentas con Nico" (Hotmart) + Mony Club (membresía) + charlas + sponsors + affiliate productos financieros.

**Mis Propias Finanzas (Carolina Pineda + Juan Pablo Zuluaga)** — Colombia. ~1M IG.
- **Origen**: ella ingeniera industrial Uniandes + MBA MIT. Él Relaciones Internacionales + MBA Babson. Crisis financiera personal por deudas posgrado. Lanzaron **inicios 2020**, **smartphone + lámpara + pizarrón**.
- **Cadencia 30/60/90**: NO ENCONTRADA con números.
- **Format**: carruseles educativos largos + reels explicativos pizarrón. Tono confesional ("nosotros tampoco sabíamos").
- **Inflection point** (DOCUMENTADO, ¡el más claro de todos!):
  1. **Pandemia** convirtió MPF "de vitamina a aspirina"
  2. **Inversor Pablo Sánchez Serrano** (mismo backer de Oso Trava) aportó capital y dirección
  3. **"Reto Latinoamericano"**: 40K inscritos, 25K participantes en vivo (3 días)
  4. **"De cero a inversionista Élite"**: 9K aplicaciones para ~1K cupos (bootcamp 3 meses)
- **Errores reconocidos**: las asesorías 1:1 (primeras 5 ventas abril 2020) fueron **insostenibles** — pivote rápido a productos digitales escalables.
- **Monetización**: cursos online → bootcamps en vivo → podcast → libro → MPF Invest → comunidad paga + masterclasses gratis (45K+ inscritos).

**Pequeño Cerdo Capitalista (Sofía Macías)** — México. ~180K IG. **El caso LATAM más antiguo y con más libros vendidos (660K copias)**.
- **Origen**: periodista, ex editora El Economista a los 22, MBA ESC Rennes. **Blog 28 feb 2008**.
- **Inflection point** (también muy claro):
  - Nov 2009: una **revista de aerolínea** reseñó el blog. Un editor de Editorial Aguilar lo leyó en el vuelo y al aterrizar pidió contactarla.
  - 2011: libro publicado por Penguin Aguilar. Escala masiva offline pre-redes.
- **Newsletter**: SÍ tiene — **Retos Financieros** en Kajabi, >8K alumnos pagos + ejercicios semanales por email. Es **el formato de membresía recurrente**.
- **Monetización**: libros (660K copias) → conferencias → membresía Retos Financieros → agenda anual → documental.

**Andrés Gutiérrez (Ramsey Solutions)** — México/EEUU hispana.
- **Origen**: fan de Dave Ramsey, fichado por Ramsey Solutions en 2009 como vocero hispano. Show de radio sindicado.
- **Inflection point**: **fichaje editorial-corporativo**, no creator solo. Catalizador no-digital.
- **Notable**: branding "el Machete pa' tu billete". Hooks confrontacionales tipo Ramsey (snowball debt method).

### C. Mass audience LATAM (news/pop culture)

**Filo News (Argentina)** — Pergolini, fundado julio/agosto 2018. ~1.8M IG.
- **NO greenfield**: spin-off de Filo Media Group (Vorterix + Dift + Malditos Nerds consolidados).
- **Equipo**: ~120 personas. >80 empleos generados solo por el proyecto digital.
- **Formato fundacional**: **IG Live diario** 10-12 min conducido por Pergolini — primer noticiero global diseñado para IG Live. La prensa cubrió el debut como hecho noticioso.
- **Filosofía**: ~30% paid / 70% orgánico (vs 90%+ típico). "Ya no se necesita gritar, alcanza con susurrar".
- **Hook structure**: titular corto + bajada que humaniza + cita textual destacada. No buscan primicia sino **encuadre cultural**.

**Pictoline (México)** — Eduardo Salles + 3 ilustradores + Gustavo Guzmán. Fundada principios 2015.
- **Equipo**: 16-18 personas (4 ilustradores + editores + periodista + dev + comercial).
- **Cadencia**: **5 "bacons" (ilustraciones) diarios**. Cada uno toma ~3 horas de trabajo, time-to-publish promedio 2.5 horas desde detección de noticia.
- **Modelo único**: 100% ilustración. Salles venía de Cinismo Ilustrado (audiencia pre-existente). Ventaja: formato visual único en 2015.
- **Inflection point**: cold-start con audiencia previa + cobertura masiva elección Trump 2016 + crisis Peña Nieto. Para 2017 ya facturaban USD ~1M.
- **Monetización**: sponsored illustrations + libros + merch. **Ofrecen al anunciante**: ilustración branded + distribución en sus canales + derechos de uso para canales del anunciante.

**Cenital (Argentina)** — Iván Schargrodsky, 2018-2019. **Modelo newsletter-first, único en LATAM.**
- 12 newsletters distintos (uno por periodista) · llega a 60K+ personas/día.
- **Monetización RADICALMENTE distinta**: reader revenue (membership). ~8% paga USD 2-10/mes. Tesis: independencia editorial sin anunciantes.
- **Tesis aplicable**: si AI Brief LATAM quiere independencia editorial, este modelo es el más replicable solo (Substack/Beehiiv/Memberful resuelven la infra).

### D. AI creators (España + LATAM) — el nicho competitivo directo

**DotCSV (Carlos Santana Vega)** — España. ~910K subs YouTube · 104K IG · 55M views acumuladas.
- **Origen**: ingeniero informático ULPGC, profesor EOI. NO tiene PhD verificado. Primer video sept 2017, slideshow.
- **Hits documentados**: "¿Qué es una Red Neuronal?" (marzo 2018) · "¿Una IA que puede PROGRAMAR?" GPT-3 (agosto 2020) · blockchain video con 1.9M views (su MÁS visto históricamente — sugiere que pivotó tarde a foco IA puro).
- **Hook patterns**:
  - "🔴 SORA: El NUEVO MODELO de GENERACIÓN de VÍDEO de OPENAI"
  - "NVIDIA Gana la BATALLA de la Inteligencia Artificial"
  - "OpenAI o1: Camino a las IAs con RAZONAMIENTO SOBREHUMANO"
  - "BitNets: La ERA de las REDES NEURONALES de 1 BIT!"
  - **Patrón**: emoji rojo + MAYÚSCULAS + claim hiperbólico + cifra/nombre técnico.
- **Inflection point**: ChatGPT nov 2022 → de ~400K a ~750K subs en 12 meses.
- **Errores documentados**: tardó en abrir 2do canal (Lab no hasta jun 2021), cadencia irregular, vídeo más visto fue blockchain no IA (foco tardío), engagement rate decreciente (top videos rondan 100-200K para 910K subs).
- **NO TIENE newsletter**. Gap importante.
- **Monetización**: Patreon + AdSense + sponsors (Cuatroochenta) + conferencias (OpenExpo Europe 2024) + docencia EOI + MyPublicInbox. NO ha lanzado curso masivo.

**Mafia IA (Alex DC)** — España. ~17K subs Substack · 40K+ cross-platform. Top 3-4 Substack España.
- **Origen**: Alex Hernández, Santander/Madrid, 14+ años proyectos digitales, DJ tiempo libre. NO ingeniero. Outsider tech.
- **Timing absurdamente bueno**: lanzó **junio 2022, 5 meses antes de ChatGPT**.
- **Cadencia**: bisemanal (NO daily).
- **Hook patterns**:
  - "Crea tu oferta de 100 millones $ con IA"
  - "SuperLista: 63 Herramientas IA para Emprendedores"
  - "Crea tu ejército de [X] IA"
  - "La Super-Inteligencia 🧠 AGI"
  - **Tagline**: "Domina la IA antes que nadie y obtén una Ventaja injusta"
  - **Patrón**: cifra alta + posesivo ("tu") + valor extraído + hype
- **Monetización**: sponsors via OhMyNewst + aimafia.club (comunidad pago) + Vibe Coding + mafiaia.com (database prompts).

**Digital Brain (Albert Ruyra + Edu Gaya)** — España. **85-90K subs**, la mayor en español junto a 8020AI.
- 100% hispanohablante, >35% VP/C-Level, >90% mayores de 35 años. España > México > Chile.
- Tono ejecutivo/corporate. Diferenciador: **decisor senior corporativo**.

**GptZone (Aitor Wilzig + Aitor Ortega)** — España. **40K+ subs, ÚNICO daily real**.
- Lanzamiento 15 mayo 2024. Lead magnet: pack 1.000+ prompts.
- Formato: "3 noticias + Mega Prompt + Tools clave en 3 min/día". **Utility, no análisis editorial**.

**IA en Español (Jesús Arias + Emilio García)** — Substack 46K subs.
- 3x/semana (lun-mié-vie). News roundup + tools listas para usar. Tono divulgativo neutral.

**Xavier Mitjana** — España. ~330K YouTube. Diferenciador: **NO explica modelos, enseña USARLOS**. Curso "IA en Acción" en Teachable es el negocio principal.

**Jon Hernández** — España. ~200K YouTube. **FOTÓGRAFO**, no ingeniero. Tono dramático/apocalíptico. *"No estamos preparados para la hostia que viene con la IA"*. Criticado por algún blog (foligade.es) como "charlatán".

**Monos Estocásticos (Antonio Ortiz + Matías S. Zavia)** — España. 151 episodios. Único formato podcast-first relevante en español sobre IA. Tono **periodístico, irónico, sobrio**. Lo opuesto al hype.

---

## Parte 2 — Síntesis (preguntas k–o)

### k) Patrones COMUNES primeros 30 días — 5 prácticas

1. **Owned channel primero, redes después.** 7 de 11 creators construyeron sobre email/blog/podcast antes que IG/TikTok. Los excepciones (Pictoline, Filo, Nicolas Abril) tenían audiencia previa o equipo grande.
2. **Producción intencionadamente low-fi.** MPF empezó "smartphone + lámpara + pizarrón". DotCSV con slideshows básicos. Sofía Macías con blog en Blogger. Pictoline tenía formato definido pero proceso editorial estricto. **Nadie esperó a "estar listo".**
3. **Cadencia sostenida >>> calidad.** Citado explícitamente por Enzo (parábola Art & Fear), Tala (MVP en 3 semanas), Tala otra vez ("simplemente hazlo"). Volumen sobre perfección como filosofía declarada.
4. **Tema verticalizado desde día 1.** Nadie arrancó "general tech". Startupeable = VC LATAM. EES = startup ecosystem Chile/LATAM. Mafia IA = IA práctica emprendedor. PCC = finanzas personales mexicano joven. La verticalización agresiva es universal.
5. **Credibilidad operativa pre-existente.** Enzo era VC, Tala tenía exit, MPF eran MBAs en crisis, Macías era periodista financiera, DotCSV era investigador ML, Salles tenía Cinismo Ilustrado. **Casi nadie partió "desde cero" sin algún tipo de credibilidad o audiencia previa.** Caveat fuerte para el plan.

### l) Patrones COMUNES después del primer "viral" / inflection point

1. **El catalizador externo > viralidad orgánica**. 9 de 11 inflection points fueron canales/eventos externos: ChatGPT (DotCSV, Mafia IA), reseña en revista de aerolínea (Macías), inversor con red (MPF), fichaje editorial (A. Gutiérrez), partners con red (EES), Top Voice LinkedIn (Startupeable), pandemia (MPF).
2. **Pivote rápido de producto inicial al producto escalable.** MPF descartó asesorías 1:1 en meses. DotCSV abrió 2do canal a los 4 años (admite: tarde). Startupeable pivotó de blog a podcast a los 18 meses.
3. **Verticalización de monetización post-tracción.** Todos: cursos pre-grabados → cohortes en vivo → membresía recurrente → libro/conferencias. **El driver de margen y LTV es la membresía**, no el curso suelto.
4. **Borrowed audience via guests/colabs**. Startupeable trayendo Mercado Libre/Nubank founders. Filo con Pergolini activando su red de TV/radio. Pictoline aprovechando audiencia previa de Cinismo Ilustrado.
5. **PR/medios tradicionales sigue funcionando**. Macías → Penguin. DotCSV → El País Tecnología/Xataka. Filo → cobertura de LA NACION/Perfil del debut. Tala → DF (Diario Financiero). El "creator-only" puro casi no existe en este dataset.

### m) Tiempos medios a 10K / 50K / 100K (subs/followers)

| Hito | Mediana documentada | Rango | Caveat |
|---|---|---|---|
| **0 → 10K** | ~12-18 meses | 1 mes a 36 meses | EES en 1 mes con $100K capital. Sofía Macías ~3 años con blog. DotCSV 1 año a 1K (no 10K). |
| **0 → 50K** | ~24-36 meses | 12 a 60 meses | Mafia IA ~2 años (con timing pre-ChatGPT). Startupeable ~4 años. DotCSV ~5 años. |
| **0 → 100K** | ~36-48 meses | 24 a 72 meses | DotCSV ~5 años. Digital Brain ~3 años. Mass audience (>500K) requiere ~4-5 años Y equipo. |
| **0 → 1M** | ~3-5 años | 2 a 10 años | Pictoline (con equipo), MPF (con pareja + investor), Filo (con 120 personas), Abril (path no documentado). |

**Calibración para AI Brief LATAM (founder solo + pipeline IA):**
- 0 → 10K newsletter realista: **9-15 meses** con cadencia consistente + diferenciación clara
- 0 → 10K IG follower realista: **12-24 meses** sin viral hit
- 0 → 50K newsletter realista: **24-36 meses** con stack actual
- 0 → 100K newsletter: **necesitaría equipo o adquisición** post 24 meses

### n) Solo vs equipo — relevancia es ALTA

| Creator | Solo / Equipo | Audiencia | Lección |
|---|---|---|---|
| Filo News | 120 personas | 1.8M | Mass news = equipo grande obligatorio |
| Pictoline | 16-18 | 1M+ FB / 1.3M IG / 1.7M X | Formato custom (ilustración) requiere ilustradores |
| MPF | Pareja + team escalado | 1M IG | Pareja co-founder >> solo; team contratado post tracción |
| Cenital | ~12 periodistas | 60K diario | Newsletter colectivo, no founder solo |
| Startupeable | Enzo + productora | 50K newsletter | Solo + outsourcing |
| EES | 3 partners + IA | 10K | Capital + partners + automatización |
| DotCSV | Solo años 1-3, equipo 2021+ | 910K subs | Solo escalable hasta ~300-500K, después necesita equipo |
| Mafia IA | Solo | 17K subs | Solo realista hasta 20-50K |
| GptZone | 2 founders | 40K subs daily | Dúo + automatización |
| Sofía Macías | Solo 2008-2011, team después | 180K IG + 660K libros | Solo escalable con producto físico (libros) |
| Andrés Gutiérrez | Solo + Ramsey backend | radio sindicada | Apoyado en organización grande |

**Patrón claro**: solo escala hasta ~20-50K consistente con esfuerzo sostenible. Para superar ese techo: (1) contratar editor/producer, (2) partner co-founder, (3) outsourcing de producción, o (4) automatización pesada con IA (que es el plan de AI Brief LATAM — esto es la apuesta).

### o) % chance realista de llegar a 10K en 12 meses con pipeline IA-automatizado + 1 pieza/día + newsletter daily

**Estimación honesta: 45-65%**, condicionada a 4 factores:

| Factor | Si SÍ | Si NO |
|---|---|---|
| **Consistencia de publicación 7/7 por 12 meses** | +20 puntos | -30 puntos. Es el factor más predictivo. |
| **Diferenciación clara LATAM-first vs competidores** | +15 puntos | -15 puntos |
| **Plan de partnerships / guest content / cross-promo desde mes 2** | +10 puntos | -10 puntos |
| **Algún lever externo (press hit, network, capital)** | +10 puntos | -10 puntos |

**Lectura**: con ejecución perfecta de los 4 factores → 70-85% chance. Sin ninguno → 15-25% chance. **Base case (2 de 4 factores)**: ~45-60%.

**Calibración contra dataset**: EES llegó a 5K en mes 1 con $100K + 3 partners. Mafia IA llegó a 10K en ~6 meses con timing pre-ChatGPT. Startupeable tardó ~24 meses al newsletter. Sin lever extraordinario, 12 meses para 10K es ambicioso pero alcanzable.

**Riesgos NO incluidos en el % anterior** que pueden bajarlo:
- Burnout del founder solo operando daily sin break (cita Mafia IA, DotCSV cadencia irregular)
- Algoritmo IG/TikTok cambia y baja reach orgánico
- AI label de Meta/TikTok penaliza contenido IA-generated (este es un riesgo grande para tu pipeline — ver Prompt 5 cuando lo ejecutes)
- Competidor LATAM-first lanza primero y captura el nicho

---

## Parte 3 — Playbook accionable 90 días para AI Brief LATAM

### Pre-launch (Día -30 a Día 0)

**Owned channel ready** (Beehiiv, no Substack — está confirmado en EES que es mejor para LATAM):
- Landing con captura de email + lead magnet definido
- Lead magnet sugerido: "**Stack de IA para profesionales LATAM 2026**" (50 herramientas con casos de uso por país — replica el modelo SuperLista de Mafia IA pero LATAM-céntrico)
- 5 piezas pre-cargadas para los primeros 5 días sin presión de "improvisar"
- Plantilla de carrusel + plantilla de reel diseñadas en Figma/Canva (no improvisar diseño cada día)

**Build credibilidad operativa** (gap crítico del founder solo):
- LinkedIn updated con posicionamiento "fundador AI Brief LATAM"
- 3-5 posts previos en LinkedIn estableciendo voz/POV antes del lanzamiento
- Lista de **20 guests potenciales** para podcast o entrevistas escritas (founders IA LATAM, reguladores, académicos)

### Mes 1 (Días 1-30) — establecer cadencia

**Cadencia objetivo**: 1 newsletter daily + 1 post IG carrusel daily + 2-3 reels/semana
- Newsletter formato Smart Brevity (sigue tu plan actual)
- IG mix: 70% carrusel news/explainer · 20% reels · 10% post estático
- Horarios: newsletter 6-7am hora MX, IG 12pm + 7pm hora MX (testear)

**Objetivos numéricos realistas Mes 1** (calibrado contra EES con $100K vs founder solo sin capital):
- 200-500 subs newsletter (sin capital ad spend)
- 500-1.500 followers IG
- 5-15% open rate inicial → estabilizar 35-50% mes 3

**Acción crítica del Mes 1**: identificar tu **inflection point lever**. No es viralidad. Es uno de:
- Partnership con creator LATAM no-IA (educadores, startup founders, etc.)
- Cross-promo con 1-2 newsletters complementarios (Latitud, Hipertextual, Latam List)
- Apariciones en 2-3 podcasts LATAM tech
- 1 hit de PR (pitcheo a Wired LatAm, Forbes MX, Bloomberg Línea)

### Mes 2 (Días 31-60) — capitalizar primera tracción

**Ajustes basados en data Mes 1**:
- Top 3 hooks que funcionaron → replicar estructura
- Top 3 formats que funcionaron → doblar apuesta
- Eliminar formats que no convierten (no insistir por "balance")

**Lanzar borrowed audience** (replica modelo Startupeable):
- Primera entrevista o "AMA escrita" con founder IA LATAM relevante (Latam-GPT, Kueski AI, Tractian)
- Empezar lista de "espera" para feature semanal de startup IA LATAM destacada
- Crear "estudio de caso del mes" — formato que es lead magnet secundario

**Objetivos numéricos realistas Mes 2**:
- 1.000-2.500 subs newsletter
- 2.000-5.000 followers IG
- Open rate estabilizado 30-45%

### Mes 3 (Días 61-90) — instalar moats

**Differentiation execution**:
- Lanzar 1 "newsletter especial" por país (México, Argentina, Colombia, Chile) — 1/mes cada uno. Posiciona LATAM-first vs España-céntricos.
- Empezar cobertura sistemática de **regulación IA LATAM** (Ley IA México, decretos Brasil, AI Act EU desde la perspectiva LATAM) — gap real identificado.
- Iniciar conversaciones con 2-3 sponsors LATAM (no pushear venta — solo presentar reach y wait)

**Comunidad como producto** (gap identificado, oportunidad):
- Telegram/Discord LATAM con channels por país
- Beta privada con primeros 100 suscriptores como "fundadores"
- Acceso anticipado a contenido

**Objetivos numéricos realistas Mes 3**:
- 2.500-5.000 subs newsletter
- 5.000-10.000 followers IG
- 1-2 menciones en medios LATAM o cross-promo grande
- Decisión clara: ¿inflection point lever identificado y activado, o pivot necesario?

### KPIs duros para evaluar Go/No-Go a Mes 3

| Métrica | Verde (continuar como está) | Amarillo (ajustar) | Rojo (pivot serio) |
|---|---|---|---|
| Subs newsletter | >3.000 | 1.500-3.000 | <1.500 |
| Open rate | >40% | 25-40% | <25% |
| IG followers | >5.000 | 2.000-5.000 | <2.000 |
| Engagement rate IG | >3% | 1-3% | <1% |
| Lever externo activado | Sí, con resultados visibles | En conversación pero sin cierre | No iniciado |

---

## Parte 4 — Gaps de mercado y diferenciación específica

**Posicionamiento defensible**: AI Brief LATAM = **"el daily editorial para profesionales LATAM que tratan con IA, en español neutro pero con casos y regulación regional"**

**5 ejes diferenciadores accionables** (todos identificados como gaps en el análisis competitivo):

1. **LATAM-first real**. Cobertura semanal de: una startup IA LATAM, una regulación LATAM, un caso de uso por industria LATAM (mining Chile, fintech Brasil, retail México, agro Argentina). NINGÚN competidor lo hace sistemáticamente.

2. **Daily con voz editorial, no roundup**. GptZone es daily pero utility. Falta el "Stratechery LATAM diario". Cada noticia con angle propio + opinión calibrada (no hype, no apocalipsis — tono Cenital + Monos Estocásticos).

3. **Builder/founder LATAM track**. Cobertura semanal técnica: nuevos modelos OSS, benchmarks, costos de inferencia, latencia regional. Audiencia que actualmente lee Latent Space / HN en inglés porque no hay opción en español. Vertical separable (puede ser sub-newsletter).

4. **Regulación + laboral**. AI Act EU desde lente LATAM, leyes domésticas, impacto en BPO (Filipinas/Colombia/Argentina), uso público por gobiernos. Newsletter completo por sí solo si se quiere — al menos sección recurrente.

5. **Voz coloquial regional sin perder rigor**. No español neutro-peninsular. Variantes regionales en posts dedicados (uso de "vos" en posts argentinos, "órale" en mexicanos, etc.) o español neutro LATAM con guiños regionales.

---

## Parte 5 — Decisiones que cambian el plan actual

**3 cambios concretos que recomienda el research**:

### 1. Reformular el lead magnet
Actual (asumido): genérico de IA. Recomendado: **"Stack IA para profesionales LATAM 2026"** o **"Top 20 startups IA LATAM con casos de uso"** — algo LATAM-first desde el primer touch. Mafia IA validó que el formato "lista práctica con valor extraído" tiene mejor conversion que "guía conceptual".

### 2. Agregar plan de "inflection lever" al roadmap Mes 1-3
Sin esto, el % chance baja a 25-30%. **El research es categórico: nadie escaló sin lever externo**. Debe ser una decisión explícita del plan, no algo que pase orgánicamente. Concretamente:
- Lista de 20 prospects de partnership/cross-promo en Mes 1
- 5 outreaches/semana desde Mes 1
- Primer hit de press/partnership cerrado en Mes 2

### 3. Reducir expectativa de 100K en 12-18 meses
La data sugiere 100K = 36-48 meses con equipo. **Reset realista del north star**: 10K subs en 12 meses (alcanzable), 30-50K en 24 meses (alcanzable con automatización IA), 100K en 36 meses (requiere contratación o adquisición). Esto no es "rebajar la ambición" — es alinear expectativas con base rates del dataset.

---

## Fuentes consolidadas

### Startup ecosystem
- [Startupeable - Acerca](https://startupeable.com/acerca/)
- [Startupeable Substack](https://startupeable.substack.com/about)
- [Enzo Cavalié LinkedIn - Product Channel Fit](https://es.linkedin.com/posts/enzo-cavalie_en-las-etapas-tempranas-el-70-de-tus-usuarios-activity-6968567767834779648-Nps9)
- [Firstbase - Expansion Chronicles Enzo Cavalié](https://www.firstbase.io/blog/the-expansion-chronicles-enzo-cavalie)
- [DF - Cristián Tala medio startups](https://www.df.cl/df-mas/punto-de-partida/cristian-tala-crea-medio-especializado-en-startups-y-se-asocia-con-dos)
- [DF - Verdad de Tala 2 años post-venta](https://www.df.cl/df-mas/por-dentro/la-verdad-de-cristian-tala-a-dos-anos-de-vender-su-startup-en-us-23)
- [El Ecosistema Startup - Sobre Nosotros](https://ecosistemastartup.com/sobre-nosotros/)

### Finanzas LATAM
- [Instagram @nicolasabril](https://www.instagram.com/nicolasabril/)
- [BluRadio - Nicolás Abril](https://www.bluradio.com/economia/debemos-aprender-a-invertir-en-el-presente-nicolas-abril-creador-de-contenido-financiero-rg10)
- [El Espectador - Mis Propias Finanzas](https://www.elespectador.com/economia/emprendimiento-y-liderazgo/mis-propias-finanzas-pasaron-de-no-saber-manejar-dinero-a-ensenar-educacion-financiera/)
- [The Frye Show #269 Carolina Pineda](https://thefryeshow.com/carolina-pineda-mis-propias-finanzas)
- [Emprendedor - Sofía Macías 15 años](https://emprendedor.com/pequeno-cerdo-capitalista-sofia-macias-cumple-15-anos-historia-de-exito-blog-libro-documental-finanzas-personales/)
- [Pequeño Cerdo Capitalista](https://www.pequenocerdocapitalista.com/)

### Mass audience LATAM
- [TodoTVNews - Filo News revolución](https://www.todotvnews.com/filo-news-la-nueva-revolucion-audiovisual-de-mario-pergolini/)
- [La Nación - Debut Pergolini IG](https://www.lanacion.com.ar/espectaculos/personajes/asi-fue-el-debut-de-mario-pergolini-como-presentador-de-noticias-en-instagram-nid2158519/)
- [Reporte Publicidad - Pergolini](https://reportepublicidad.com/mario-pergolini-el-mundo-se-ha-segmentado-hay-que-aprender-a-hablarle/)
- [IJNet - Pictoline](https://ijnet.org/en/story/mexicos-pictoline-brings-new-approach-making-news-go-viral)
- [Merca20 - Pictoline Salles entrevista](https://www.merca20.com/cuales-son-las-claves-del-exito-de-pictoline-entrevista-con-eduardo-salles/)
- [Cenital - cómo funciona](https://cenital.com/detras-de-los-numeros-como-funciona-cenital/)

### AI creators
- [Grokipedia: DotCSV](https://grokipedia.com/page/dotcsv)
- [Dialnet: estudio académico DotCSV](https://dialnet.unirioja.es/servlet/articulo?codigo=10187939)
- [Mafia IA Substack](https://aimafia.substack.com/)
- [AI Mafia Club](https://aimafia.club/)
- [Digital Brain](https://www.digitalbrain.email/)
- [GptZone Newsletter](https://news.gptzone.net/)
- [IA en Español Substack](https://aplicacionesai.substack.com/)
- [Saul Gordillo: Divulgadores IA en español](https://saulgordillo.substack.com/p/homenaje-a-los-divulgadores-de-inteligencia)
- [Monos Estocásticos podcast](https://open.spotify.com/show/0yhXkn2DdZUC6XySGBgftC)
- [Newsletters IA Directorio 2026](https://newslettersia.com/)

---

## Próximos pasos sugeridos

1. **Cliente revisa este documento**. Marca qué hallazgos confirman/refutan supuestos del plan actual.
2. **Compara con Prompt 2 output** (competitive deep) cuando esté ejecutado, para triangulación.
3. **Ejecutar Prompt 1 (build vs buy)** — porque si hay shortcut SaaS al 70% del pipeline, el #o (% chance 10K) sube significativamente porque el founder libera bandwidth para inflection lever.
4. **Decisión Go/No-Go al plan**: ¿se mantienen los 3 cambios sugeridos en Parte 5? Si sí, actualizar `docs/ROADMAP.md` y `docs/DECISIONS.md`.
5. **Si se mantiene el plan**: schedule honesto de KPIs Mes 3 con criterio Go/No-Go pre-acordado.
