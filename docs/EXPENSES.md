# Expenses Tracker — Project Autopilot

**Last updated:** 2026-06-14
**Owner:** Manuel · **Rule:** registrar ABSOLUTAMENTE todo. No perder cuenta de ningún gasto. Si aparece un cargo nuevo, va aquí el mismo día.

> ## 🔒 CONGELAMIENTO DE GASTOS (2026-06-03)
> Manuel: *"esta va a ser la última cosa que pago para esto."*
> **After Effects es la ÚLTIMA herramienta de paga autorizada.** A partir de aquí: CERO suscripciones/herramientas/servicios nuevos sin OK explícito de Manuel. Default = gratis/open-source. Avisar costo estimado ANTES de cualquier gasto (incluye créditos de API). Si AE no valida dentro del trial de 7 días → cancelar (costo $0), no pivotar a otra herramienta de paga.
>
> ### Actualización 2026-06-04 — Gasto controlado autorizado (opción 2)
> Manuel autorizó AFLOJAR el $0 para **compras PUNTUALES y chicas** que suban el techo de calidad (ej. plantillas premium 9:16 fuera de Envato, packs de assets 3D ~$10-40). Reglas: (1) cada compra se COTIZA y se pide OK ANTES. (2) NADA de suscripciones grandes nuevas. (3) el gasto se autofinancia cortando desperdicio (ver abajo). NO contratar diseñador / humano (rompe la tesis de automatización 100%).

> Fuente de verdad ÚNICA de gastos. Campos en `TBD / CONFIRMAR` = necesito que Manuel me dé el dato (monto exacto, email de la cuenta, o si sigue activo).

---

## Suscripciones / servicios ACTIVOS

| Servicio | Plan | Costo | Ciclo | Estado | Cuenta | Para qué | Notas |
|---|---|---|---|---|---|---|---|
| **Anthropic API** | Pay-as-you-go | ~$1-3/día (variable) | uso | Activo | manup personal | Claude (agentes + Claude Code) | El gasto sube en días de desarrollo pesado |
| **OpenAI API** | Créditos | TBD/CONFIRMAR | uso | Activo (créditos) | TBD | gpt-image / GPT | ¿cuántos créditos quedan? |
| **ElevenLabs** | TBD/CONFIRMAR | TBD/CONFIRMAR | mensual? | Activo | (key en uso) | Voz narración (voz Asgard) | Lo usamos esta sesión; confirmar plan/costo |
| **Hostinger VPS** | VPS | TBD/CONFIRMAR (~$10-15/mo?) | mensual | **Activo** | manup personal | Render Remotion + n8n (147.93.43.72) | Antes marcado "cancelado" por error — SÍ está activo y en uso |
| **Supabase** | Free? | $0 (TBD/CONFIRMAR) | -- | Activo | proyecto xmidoxxtjpifvebxnfva | Storage de videos/assets | Confirmar si sigue en free tier |
| **GitHub** | Free? | $0 (TBD/CONFIRMAR) | -- | Activo | TBD | Repo de código | Confirmar si hay plan de paga |
| **Envato Elements** | Mensual | **$16 USD/mo** | mensual | Activo (confirmado 2026-06-10) | TBD | Plantillas premium AE (motion graphics) | Autorizado por Manuel |
| **Google Gemini API (Veo)** | Pay-as-you-go (Tier 1) | solo uso, $0 USD fijo | uso | **Activo (billing ON 2026-06-11)** | cuenta Google de Manuel | Video IA generativo (Veo 3.1) para reels Dinero IA | Sin mensualidad; solo cobra renders exitosos. Veo 3.1 Fast 720p $0.10 USD/s, Standard $0.40 USD/s |

## CONFIRMAR / posible cancelación

| Servicio | Costo | Estado | Acción |
|---|---|---|---|
| **OceanGate (?)** | TBD/CONFIRMAR | **CANCELAR (Manuel OK 2026-06-04)** | Manuel autorizó cancelar. ⚠️ No tengo acceso a su portal de facturación → **Manuel debe ejecutar la cancelación** en la cuenta del servicio. |
| **n8n** | self-hosted $0 | **Decidido: self-hosted en VPS ($0)** | NO pagar Cloud. Corre en Hostinger. |

## Próximos gastos (si avanzamos el pipeline AE)

| Servicio | Costo est. | Cuándo | Notas |
|---|---|---|---|
| **Adobe After Effects** | ~$23/mo (trial 7 días gratis) | Solo si una plantilla pasa el filtro de calidad | Necesario para Nexrender. Trial primero, no pagar hasta validar |

## Historial: cancelado / expirado

| Servicio | Costaba | Fecha | Razón |
|---|---|---|---|
| Canva Pro (trial) | $14.99/mo | **CANCELAR (Manuel OK 2026-06-04)** | El pipeline no usa Canva. ⚠️ Manuel debe ejecutar la cancelación en su cuenta Canva antes de que cobre. |
| Beehiiv (trial) | -- | ~2026-05-21 | Trial |

## Log de uso de API (cargos puntuales)

| Fecha | Servicio | Unidades | Costo est. | Qué |
|---|---|---|---|---|
| 2026-05-08 | Anthropic | ~950K tokens | ~$48 | Build + test de 9 agentes (día pesado) |
| 2026-05-10 | Anthropic | ~20K tokens | ~$1.05 | Corridas de pipeline |
| 2026-06-03 | ElevenLabs | TBD | TBD | Voz para reels test016/test017 |
| 2026-06-03 | Anthropic | TBD | TBD | Sesión de rediseño + validación pipeline |
| 2026-06-11 | Google Gemini (Veo) | 4 clips x 8s Fast 720p | $3.20 USD (~$60 MXN) | Test de look video IA (autorizado: $6.40 USD total incl. 1 clip Standard pendiente) |
| 2026-06-11 | Google Gemini (Veo) | 2 clips x 8s Fast 720p | $1.60 USD (~$30 MXN) | Reel completo 50pesos_VEO_916 (4 clips del test reusados; autorizado ~$5-7 USD, gastado $1.60). Saldo cargado por Manuel: $500 MXN |
| 2026-06-13 | Anthropic | ~3.4K tokens (in 2144/out 1269) | ~$0.04 USD (~$0.75 MXN) | Test del cerebro planner n8n (genera guion El Salvador BTC). Nota: n8n self-hosted = $0; este es el único costo nuevo por guion |
| 2026-06-14 | Anthropic (planner) | ~7.3K tokens (in ~3.7K x2 / out 2.4K) | ~$0.06 USD (~$1.10 MXN) | **Accidental:** `pytest` del repo auto-colectó `test_planner.py` (es un script con API VIVA, no un test offline) → disparó el planner Claude 2 veces antes de crashear (KeyError 'vo'). Correctivo: correr SOLO `python test_validator.py` (suite sin API), NUNCA pytest del repo entero |

## Resumen mensual

| Mes | Suscripciones | API | Total |
|---|---|---|---|
| May 2026 | ~$0 | ~$49 | ~$49 |
| Jun 2026 (parcial) | $16 (Envato) + TBD | TBD | TBD |

---

## Lo que necesito de Manuel para cerrar el ledger
1. **OceanGate**: nombre exacto del servicio + costo mensual (para registrarlo y decidir si cancelar).
2. **Hostinger VPS**: costo mensual exacto.
3. **OpenAI**: cuántos créditos quedan / costo aprox al mes.
4. **ElevenLabs**: qué plan tienes y cuánto cuesta.
5. **Supabase y GitHub**: ¿free tier o pagas algo?
6. Email de cuenta de cada servicio (para no perder de dónde sale cada cargo).

- 2026-06-13 · OpenAI gpt-image-1 (high 1024x1536) · caricatura 'bukele' · ~$0.17 USD · Dinero IA beats de personaje (cacheada)
- 2026-06-13 · OpenAI gpt-image-1 (high 1024x1536) · caricatura 'economista' · ~$0.17 USD · Dinero IA beats de personaje (cacheada)
- 2026-06-13 · ElevenLabs eleven_v3 (voz Asgard) · re-TTS 3 beats El Salvador (b1/b3/b4, ~83 palabras / ~500 chars) · ~$0.10 USD est. (plan/tarifa TBD) · redondeo de números HABLADOS: "más de 200 millones", "alrededor de", "casi 480 millones" (el visual mantiene la cifra exacta del brief)
- 2026-06-15 · OpenAI gpt-image-1 (high 1024x1024) · moneda hero 'btc' · ~$0.12 USD · Dinero IA BeatHeroCoin (cacheada)