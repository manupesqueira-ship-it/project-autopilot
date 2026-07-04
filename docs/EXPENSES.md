# Expenses Tracker — Project Autopilot

**Last updated:** 2026-06-28
**Owner:** Manuel · **Rule:** registrar ABSOLUTAMENTE todo. No perder cuenta de ningún gasto. Si aparece un cargo nuevo, va aquí el mismo día.

> ## 🔒 CONGELAMIENTO DE GASTOS (2026-06-03)
> Manuel: *"esta va a ser la última cosa que pago para esto."*
> **After Effects es la ÚLTIMA herramienta de paga autorizada.** A partir de aquí: CERO suscripciones/herramientas/servicios nuevos sin OK explícito de Manuel. Default = gratis/open-source. Avisar costo estimado ANTES de cualquier gasto (incluye créditos de API). Si AE no valida dentro del trial de 7 días → cancelar (costo $0), no pivotar a otra herramienta de paga.
>
> ### Actualización 2026-06-04 — Gasto controlado autorizado (opción 2)
> Manuel autorizó AFLOJAR el $0 para **compras PUNTUALES y chicas** que suban el techo de calidad (ej. plantillas premium 9:16 fuera de Envato, packs de assets 3D ~$10-40). Reglas: (1) cada compra se COTIZA y se pide OK ANTES. (2) NADA de suscripciones grandes nuevas. (3) el gasto se autofinancia cortando desperdicio (ver abajo). NO contratar diseñador / humano (rompe la tesis de automatización 100%).

> ### Actualización 2026-06-24/28 — Presupuesto del MOTOR AI desbloqueado
> Manuel levantó el congelamiento para el **motor de movimiento (i2v)**: objetivo **~$5,000 MXN/mes, techo $10,000**, calidad antes que volumen (1 reel/día). Sigue vigente: cotizar antes de gastar y registrar TODO aquí. **2026-06-28: Manuel pagó el plan de Higgsfield ($50 USD/mes)** como motor de la capa hero — primera suscripción nueva autorizada bajo este presupuesto (ver tabla de activos).

> Fuente de verdad ÚNICA de gastos. Campos en `TBD / CONFIRMAR` = necesito que Manuel me dé el dato (monto exacto, email de la cuenta, o si sigue activo).

---

## 🔍 Auditoría de cuentas — 2026-06-27

Barrido de los 3 buzones (mexonoma, manupesqueira, aibrieflatam.media). Resultado:

**Sangrías recurrentes → todas MUERTAS o por morir:**
- **Hostinger VPS** — auto-renovación **OFF**, status *Stopped*, expira **2026-07-05**. Precio real £17.99/mo (~$405 MXN, NO los "$10-15" del ledger viejo). El pipeline NO lo usa (IP 147.93.43.72 solo aparece en docs, nunca en `infra/*.py`). Verificado en los SS del panel Hostinger, no por email (no manda confirmación del toggle).
- **DigitalOcean** — team borrado, factura final **$11.14 USD**. (Era el "OceanGate" del ledger viejo.)
- **Adobe After Effects** — cancelado ×2, **$0** (no pasó del trial; camino AE/Nexrender MUERTO). Cuenta aibrieflatam.media.
- **Envato (Elements/Core)** — cancelado, termina **2026-07-04**. Cuenta aibrieflatam.media.

**Lo que SÍ sigue vivo y se queda:**
- **ElevenLabs** (voz Asgard) — único recurrente vivo del pipeline; falta confirmar plan/costo.
- **Gemini API** — ~$500 MXN de **créditos prepagados** (ver "Cargos aclarados"), disponibles para usar.

**Cargos aclarados:**
- **GCP $500 MXN (11-jun)** = compra **deliberada de créditos Gemini API** (por recom. mía), NO gasto huérfano de Veo. Cuenta aibrieflatam.media. → NO cancelar la API ni ponerle tope para matarla.
- **Canva** — nunca cobró ($0). **Ubigi** — cargo *one-time* (eSIM datos, viaje), no recurrente. **Recraft / Artlist** — sin cargo recurrente activo detectado.

**Mapa de cuentas:** manupesqueira = Hostinger · aibrieflatam.media = Adobe / Envato / Gemini-GCP · DigitalOcean = (baja).

---

## Suscripciones / servicios ACTIVOS

| Servicio | Plan | Costo | Ciclo | Estado | Cuenta | Para qué | Notas |
|---|---|---|---|---|---|---|---|
| **Anthropic API** | Pay-as-you-go | ~$1-3/día (variable) | uso | Activo | manup personal | Claude (agentes + Claude Code) | El gasto sube en días de desarrollo pesado |
| **OpenAI API** | Créditos | TBD/CONFIRMAR | uso | Activo (créditos) | TBD | gpt-image (stills de arranque i2v) | ¿cuántos créditos quedan? |
| **ElevenLabs** | TBD/CONFIRMAR | TBD/CONFIRMAR | mensual? | **Activo (se queda)** | (key en uso) | Voz narración (voz Asgard) | Único recurrente vivo del pipeline; confirmar plan/costo |
| **Google Gemini API** | Pay-as-you-go + créditos | **~$500 MXN prepagados** | uso | Activo | aibrieflatam.media | LLM/multimodal: director del guion, juez visual (Filtro B), planner | Créditos cargados 11-jun (ver "Cargos aclarados"). Veo 3.1 (i2v) se probó pero NO es el motor vivo |
| **fal.ai (Kling)** | Pay-per-use | ~$0.56-0.90 USD/clip | uso | Activo | TBD | i2v: objeto/personaje en movimiento (motor vivo) | Kling v3 Pro; sin suscripción |
| **Higgsfield** | **Plus — 1010 créditos/mo** | **$50 USD/mo** (~$950 MXN) | mensual | **Activo · CLI enlazado 2026-06-28** | aibrieflatam.media@gmail.com | Motor i2v capa HERO: gateway a 30+ modelos (Seedance/Kling/Veo/Minimax...) + scorer viralidad (brain_activity) | CLI v1.0.1 autenticado, workspace "Private" (a5402034-...). Costo/clip 5s: Kling3.0=10cr · SeedanceMini=12.5cr · Seedance2.0 720p=22.5cr · Seedance2.0 1080p=45cr. 1cr≈$0.05 USD. SIEMPRE cotizar con `generate cost` antes de generar. **Burn ciclo actual: ~5.6cr stills + 45cr clip hero El Salvador (2026-06-29)** |
| **Supabase** | Free? | $0 (TBD/CONFIRMAR) | -- | Activo | proyecto xmidoxxtjpifvebxnfva | Storage de videos/assets + cola de publicar | Confirmar si sigue en free tier |
| **GitHub** | Free? | $0 (TBD/CONFIRMAR) | -- | Activo | TBD | Repo de código | Confirmar si hay plan de paga |

## Historial: cancelado / expirado / por expirar

| Servicio | Costaba | Fecha baja | Razón / estado |
|---|---|---|---|
| **Hostinger VPS** | £17.99/mo (~$405 MXN) | auto-renew OFF · expira **2026-07-05** | KVM2 srv1336358 (IP 147.93.43.72). El pipeline no lo usa. Status *Stopped*. Antes mal-registrado como "$10-15 activo en uso" |
| **DigitalOcean** | uso | factura final **$11.14 USD** | Team borrado. Era el "OceanGate" del ledger viejo |
| **Adobe After Effects** | ~$23/mo (trial) | cancelado ×2 · **$0** | No pasó del trial; camino AE/Nexrender MUERTO |
| **Envato (Elements/Core)** | $16 USD/mo | cancelado · termina **2026-07-04** | Plantillas AE; camino muerto |
| **Canva Pro (trial)** | $14.99/mo | **nunca cobró ($0)** | El pipeline no usa Canva |
| **Beehiiv (trial)** | -- | ~2026-05-21 | Trial |

## Notas de auditoría (no recurrentes / sin cargo)
- **Ubigi** — cargo *one-time* (eSIM datos, viaje), NO recurrente, ajeno al pipeline.
- **Recraft / Artlist** — sin cargo recurrente activo detectado.
- **n8n** — self-hosted $0; corría en Hostinger (muere 05-jul). De todos modos el orquestador vivo es `producir.py` (n8n tiene 0 ejecuciones), así que la baja del VPS no afecta producción.

## Log de uso de API (cargos puntuales)

| Fecha | Servicio | Unidades | Costo est. | Qué |
|---|---|---|---|---|
| 2026-05-08 | Anthropic | ~950K tokens | ~$48 | Build + test de 9 agentes (día pesado) |
| 2026-05-10 | Anthropic | ~20K tokens | ~$1.05 | Corridas de pipeline |
| 2026-06-03 | ElevenLabs | TBD | TBD | Voz para reels test016/test017 |
| 2026-06-03 | Anthropic | TBD | TBD | Sesión de rediseño + validación pipeline |
| 2026-06-11 | Google Gemini (Veo) | 4 clips x 8s Fast 720p | $3.20 USD (~$60 MXN) | Test de look video IA (autorizado: $6.40 USD total incl. 1 clip Standard pendiente) |
| 2026-06-11 | Google Gemini (Veo) | 2 clips x 8s Fast 720p | $1.60 USD (~$30 MXN) | Reel completo 50pesos_VEO_916 (4 clips del test reusados; autorizado ~$5-7 USD, gastado $1.60). |
| 2026-06-11 | Google Gemini API (créditos) | saldo prepagado | **$500 MXN** | **Compra deliberada de créditos Gemini API** (cargo GCP, cuenta aibrieflatam.media, factura CFDI FCP-25292365). Confirmado por Manuel 2026-06-27: NO es Veo huérfano. Disponibles para director LLM / juez visual / planner. Visa term. 6534, ref CLOUD Z6QWMF |
| 2026-06-13 | Anthropic | ~3.4K tokens (in 2144/out 1269) | ~$0.04 USD (~$0.75 MXN) | Test del cerebro planner n8n (genera guion El Salvador BTC). Nota: n8n self-hosted = $0; este es el único costo nuevo por guion |
| 2026-06-14 | Anthropic (planner) | ~7.3K tokens (in ~3.7K x2 / out 2.4K) | ~$0.06 USD (~$1.10 MXN) | **Accidental:** `pytest` del repo auto-colectó `test_planner.py` (es un script con API VIVA, no un test offline) → disparó el planner Claude 2 veces antes de crashear (KeyError 'vo'). Correctivo: correr SOLO `python test_validator.py` (suite sin API), NUNCA pytest del repo entero |

## Resumen mensual

| Mes | Suscripciones | API / créditos | Bajas one-time | Total aprox |
|---|---|---|---|---|
| May 2026 | ~$0 | ~$49 USD | -- | ~$49 USD |
| Jun 2026 (parcial) | Envato $16 USD (cancelado) | **Gemini créditos $500 MXN** (prepago) + Veo $4.80 + Kling/fal ~$3.82 + OpenAI img ~$4 + ElevenLabs ~$0.67 USD | DigitalOcean $11.14 USD (final) · Hostinger £17.99 (último cargo, auto-renew OFF) | ≈ **$500 MXN** + ~$29 USD (API/créditos) + bajas |

---

## Lo que necesito de Manuel para cerrar el ledger
1. ~~OceanGate~~ → era **DigitalOcean**: cancelado, factura final $11.14 USD. ✅ RESUELTO
2. ~~Hostinger VPS costo~~ → **£17.99/mo** (~$23 USD / ~$405 MXN), auto-renew OFF, muere 2026-07-05. ✅ RESUELTO
3. **OpenAI**: cuántos créditos quedan / costo aprox al mes. ⏳ ABIERTO
4. **ElevenLabs**: qué plan tienes y cuánto cuesta. ⏳ ABIERTO (único recurrente vivo sin confirmar)
5. **Supabase y GitHub**: ¿free tier o pagas algo? ⏳ ABIERTO (casi seguro free)
6. ~~Email de cuenta de cada servicio~~ → mapeado: manupesqueira=Hostinger · aibrieflatam.media=Adobe/Envato/Gemini. ✅ RESUELTO

- 2026-06-13 · OpenAI gpt-image-1 (high 1024x1536) · caricatura 'bukele' · ~$0.17 USD · Dinero IA beats de personaje (cacheada)
- 2026-06-13 · OpenAI gpt-image-1 (high 1024x1536) · caricatura 'economista' · ~$0.17 USD · Dinero IA beats de personaje (cacheada)
- 2026-06-13 · ElevenLabs eleven_v3 (voz Asgard) · re-TTS 3 beats El Salvador (b1/b3/b4, ~83 palabras / ~500 chars) · ~$0.10 USD est. (plan/tarifa TBD) · redondeo de números HABLADOS: "más de 200 millones", "alrededor de", "casi 480 millones" (el visual mantiene la cifra exacta del brief)
- 2026-06-15 · OpenAI gpt-image-1 (high 1024x1024) · moneda hero 'btc' · ~$0.12 USD · Dinero IA BeatHeroCoin (cacheada)
- 2026-06-15 · ElevenLabs eleven_v3 (voz Asgard) · TTS 5 beats edu_interes_compuesto (~144 palabras / ~780 chars, ~49s audio) · ~$0.15 USD est. (plan/tarifa TBD) · 1er video del loop semi-auto desde la cola de temas; voz redondea ("cerca de un millón y medio", "más de dos millones doscientos mil") y el visual muestra la cifra exacta
- 2026-06-18 · ElevenLabs eleven_v3 (voz Asgard) · TTS 5 beats edu_efecto_latte_latam (~137 palabras / ~740 chars, ~49s audio) · ~$0.14 USD est. (plan/tarifa TBD) · PRUEBA del loop completo producir.py end-to-end (1ª corrida real del orquestador): build+QC OK → gate Telegram APPROVED → encolado en Supabase para auto-publicar ~8pm CDMX. Único costo de la corrida (render/ensamblado/upload/publicar = $0)
- 2026-06-18 · ElevenLabs eleven_v3 (voz Asgard) · re-TTS 5 beats edu_efecto_latte_latam · ~$0.14 USD est. (plan/tarifa TBD) · FIX del bug "ano"→"año" que reportó Manuel: el guion se reescribió con ñ/acentos (día/año/más), lo que rebusto el cache de TTS y re-sintetizó las voces. El row viejo (con "ano") se borró de la cola; no se publica. Render/upload/ensamblado = $0. NOTA: el re-envío a Telegram tras el fix usó --skip-build = $0 (sin voz nueva); solo se cambió el nombre del objeto en Storage (cache-bust por hash) para que Telegram dejara de servir la copia vieja cacheada
- 2026-06-18 · ElevenLabs eleven_v3 (voz Asgard) · TTS 5 beats edu_regla_72 (~141 palabras, ~62s VO) · ~$0.14 USD est. (plan/tarifa TBD) · 2ª corrida real de producir.py (tema tomado solo de la cola). Build+QC ENTREGA OK → subido a Supabase. El gate de Telegram crasheó en un 429 transitorio ("Too Many Requests: retry after 5") porque _call convertía cualquier HTTPError en SystemExit → la corrida salió exit 1 y el video NO se encoló. FIX en telegram_bot._call: honra retry_after y reintenta en 429/5xx/blip de red (el long-poll de horas ya no muere por un hipo). Recuperación = re-correr con --skip-build = $0 (sin voz nueva). Este ~$0.14 es el ÚNICO cargo de edu_regla_72; render/ensamblado/upload = $0
- 2026-06-19 · OpenAI gpt-image-1 (high 1024x1536) x2 · set-piece 'napkin' · ~$0.38 USD · Dinero IA hook object
- 2026-06-24 · OpenAI gpt-image-1 (high 1024x1536) · objeto-heroe 'chip_ia' · ~$0.19 USD · Dinero IA arquetipo 3 (still i2v, cacheada)
- 2026-06-25 · fal kling_v3_pro i2v · shot 'b1_hook_chip_imperio' 5.0s · ~$0.56 USD · Dinero IA objeto/personaje en movimiento
- 2026-06-25 · OpenAI gpt-image-1 (high 1024x1536) · objeto-heroe 'b1_hero_colchon' · ~$0.19 USD · Dinero IA arquetipo 3 (still i2v, cacheada)
- 2026-06-25 · fal kling_v3_pro i2v · shot 'b1_hero_colchon' 5.0s · ~$0.56 USD · Dinero IA objeto/personaje en movimiento
- 2026-06-26 · OpenAI gpt-image-1 (high 1024x1536) x1 · escena 'colchon_b3' · ~$0.17 USD · Dinero IA still caricatura-fino (arranque i2v, concepto colchon)
- 2026-06-26 · OpenAI gpt-image-1 (high 1024x1536) x1 · escena 'colchon_b4' · ~$0.17 USD · Dinero IA still caricatura-fino (arranque i2v, concepto colchon)
- 2026-06-26 · OpenAI gpt-image-1 (high 1024x1536) x1 · escena 'colchon_b5' · ~$0.17 USD · Dinero IA still caricatura-fino (arranque i2v, concepto colchon)
- 2026-06-26 · fal kling_v3_pro i2v · shot 'colchon_b3' 8.0s · ~$0.90 USD · Dinero IA objeto/personaje en movimiento
- 2026-06-26 · fal kling_v3_pro i2v · shot 'colchon_b4' 8.0s · ~$0.90 USD · Dinero IA objeto/personaje en movimiento
- 2026-06-26 · fal kling_v3_pro i2v · shot 'colchon_b5' 8.0s · ~$0.90 USD · Dinero IA objeto/personaje en movimiento
- 2026-06-26 · OpenAI gpt-image-1 (high 1024x1536) x3 · look-test 'motion-graphics premium' · ~$0.51 USD · Dinero IA still madurado (eleccion de look, post slice v2)
- 2026-06-26 · OpenAI gpt-image-1 (high 1024x1536) x5 · look-test premium · refinamiento flavor B (dimensional premium) · ~$0.85 USD · Dinero IA still madurado (eleccion de look, post slice v2)
- 2026-06-26 · OpenAI gpt-image-1 (high 1024x1536) · caricatura 'milei' · ~$0.17 USD · Dinero IA beats de personaje (cacheada)
- 2026-06-26 · OpenAI gpt-image-1 (high 1024x1536) · caricatura 'milei' · ~$0.17 USD · Dinero IA beats de personaje (cacheada)
- 2026-06-28 · ElevenLabs eleven_v3 (voz Asgard) · TTS VO Reel C 'reelc_vo' (~98 chars / 16 palabras / 6.72s) · ~$0.02 USD est. (plan/tarifa TBD) · capa de voz del animatic 2D ErosionRace (lab, parche #76); única síntesis del loop, render/SFX/música/mux = $0
- 2026-06-28 · ElevenLabs eleven_v3 (voz Asgard) · TTS VO Reel C COMPLETO 'reelc_full_vo' (~830 chars / 155 palabras / 56.88s) · ~$0.16 USD est. (plan/tarifa TBD) · narración del reel completo de 6 escenas (hook→setup→carrera→payoff→regla→mañana, lab parche #76). El VO redondea los números hablados ("unos noventa y seis mil", "ciento siete mil", "alrededor de seis mil") y el visual muestra la cifra EXACTA ($96,209 · $107,170 · $102,242 · $6,033). Única síntesis del loop; render/SFX (música minimal_04 + 9 SFX Envato)/mux = $0
- 2026-06-28 · **Higgsfield — plan mensual $50 USD/mo** (~$950 MXN, suscripción NUEVA recurrente) · motor i2v de la capa HERO (gateway 30+ modelos + scorer de viralidad) · pagado por Manuel, autorizado bajo el presupuesto del motor AI (~$5K MXN/mo desbloqueado 2026-06-24). **CLI enlazado 2026-06-28** (cuenta aibrieflatam.media@gmail.com, workspace "Private", plan **plus = 1010 créditos/ciclo**). Reemplaza/complementa a fal.ai-Kling como motor i2v (decidir tras bake-off de modelos). Costo verificado por clip 5s: Kling3.0=10cr · SeedanceMini=12.5cr · Seedance2.0 720p=22.5cr · Seedance2.0 1080p=45cr → 1010cr ≈ 22 clips premium (1080p) o ~100 clips Kling/ciclo, antes de iteraciones
- 2026-06-29 · Higgsfield stills — styleframes hero "El Salvador BTC" · start_v1 (Seedream4.5)=1cr + bake-off 3 estilos (soul_cinematic=0.12cr · nano_banana_2=2cr · flux_2=1cr) + end_v1 (flux_2 2k)=1.5cr · **~5.6 créditos** (del bucket mensual de 1010, NO cargo nuevo en USD) · elección de look: Manuel eligió **FLUX.2 photoreal cinematográfico**; par START→END locked para interpolación
- 2026-06-29 · Higgsfield i2v · **seedance_2_0 1080p 9:16 5s std** (start_image=styC_flux + end_image=end_v1, generate_audio=false) · clip HERO "El Salvador" (push-in aéreo, orbe dorado desciende y enciende el país) · **45 créditos (~$2.25 USD)** del bucket mensual · 1er clip i2v con el look profesional locked; autorizado por Manuel (eligió premium directo). Costo confirmado con `generate cost` antes de gastar
- 2026-06-29 · Higgsfield stills — look-lock "El Salvador BTC v2" (crash pilar-hielo · holdings hielo→oro · clímax shatter) · soul_cinematic 2k 9:16 x3 · **~0.36 créditos** (bucket mensual de 1010, NO cargo nuevo USD) · RECHAZADO por Manuel: "lo estás exagerando demasiado, no me gusta nada · premium minimalista, no sobre-complicar" → recalibrar a restraint extremo (menos drama/color/caos, más espacio negativo)
- 2026-06-30 · OpenAI gpt-image-1 (high 1024x1536) · caricatura 'bukele_cine' · ~$0.17 USD · Dinero IA beats de personaje (cacheada)
- 2026-06-30 · fal kling_v3_pro i2v · shot 'b3_bukele' 8.0s · ~$0.90 USD · Dinero IA objeto/personaje en movimiento
- 2026-06-30 · ElevenLabs eleven_v3 (voz Asgard) · re-TTS b5_holdings FUSIONADO 'el_salvador_bitcoin_apuesta' (414 chars / 66 palabras / 29.68s) · ~$0.08 USD est. (plan/tarifa TBD) · ensamblado del reel completo El Salvador BTC: se fusionaron b5(tenencias)+b6(ganancia) en UN beat (HoldingsGainBars) para no enseñar la cifra +$209M dos veces seguidas ("no repetir el mismo demo"). ÚNICA síntesis de la corrida (b1/b2/b3/b4/b7 = cache hit, $0); render/mux/QC = $0. El VO redondea ("alrededor de 270 millones", "casi 209 millones") y el visual muestra la cifra EXACTA ($270,000,000 · $479,000,000 · +$209,000,000 · +77%)
- 2026-07-02 · Higgsfield i2v · **seedance_2_0 1080p 9:16 5s std ×3** — reel FLAGSHIP "petróleo" (oil_barril fa63f03e · oil_surtidor 6ceafcf0 · oil_billete 7c4239a7) · **135 créditos (~$6.75 USD)** del bucket mensual · heroes i2v (crudo desbordándose · surtidor · billete ardiendo), integrados como figura editorial. Costo verificado antes de generar. Glitch de auth a media corrida (billete re-creado 1×, sin cargo duplicado); saldo ciclo ≈ **1749 créditos**
- 2026-07-02 · ElevenLabs eleven_v3 (voz Asgard) · re-TTS rebuild 'btc_apuesta' (5 beats, corrección de dato hablado $475M→$477M en b4) · ~$0.10 USD est. (plan/tarifa TBD) · P0.1 del plan maestro: la cifra hablada debe cuadrar con la fórmula 7,700 BTC × $61,900. Render/mux/QC = $0
- 2026-07-02 · Workflows Anthropic (ultracode) · 2 mesas multi-agente (arquitectura 7 agentes + auditoría 50 agentes) para el plan maestro `docs/SISTEMA_DINERO_IA.md` · ~3.9M tokens subagente (uso de API Claude de la sesión, no cargo separado). Diagnóstico + arquitectura de agentes + reglas + roadmap P0-P2- 2026-07-03 · Anthropic API (claude-sonnet-5, director) · 1 corrida news_director.py v2 (validación de contrato, brief Nvidia) · ~$0.04 USD (~$0.75 MXN) · Dinero IA: prueba en vivo del contrato director v2 (schema assemble_news + menú 12 beats)
- 2026-07-03 · Anthropic API (claude-sonnet-5, director) · 3 corridas news_director (contrato v3 + reel nvidia_masters + reel mundial) · ~$0.12 USD (~$2.2 MXN) · Dinero IA motor diario
- 2026-07-04 · ElevenLabs (key nueva de Manuel) · audición 7 voces (~900 chars) + VO reel mundial voz Alberto (~800 chars, con cache idempotente) · costo en chars del plan · Dinero IA voz del canal elegida: Alberto Rodríguez l1zE9xgNpUTaQCZzpNJa
