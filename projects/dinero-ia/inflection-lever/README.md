# Inflection Lever Track — Dinero IA

**Fecha de creación:** 2026-05-29 (post-ADR-017)
**Status:** ready-to-execute en paralelo con Fase -1
**Bandwidth target:** 2-3 hs/semana de Manuel
**Objetivo Fase -1:** 1-2 conversaciones avanzadas (no necesariamente cierre), 10+ outreaches enviados

---

## Por qué existe este track

El Deep Research Report 03 (Creator Playbook) encontró que **9 de 11 creators del dataset escalaron por canal externo**, no por viralidad orgánica:

- DotCSV escaló por el "ChatGPT moment" (Nov 2022)
- Sofía Macías (PCC) escaló por una reseña en revista de aerolínea (2009) que fue leída por un editor de Penguin
- Mis Propias Finanzas escaló por inversor con red (Pablo Sánchez Serrano)
- Startupeable (Enzo Cavalié) escaló por Top Voice LinkedIn + podcast con guests blue-chip
- Ecosistema Startup (Tala) escaló por capital + 3 partners con credenciales
- Andrés Gutiérrez escaló por fichaje Ramsey Solutions
- Filo News escaló por su parent company + 120 personas

**Sin lever externo, la probabilidad de hit 10K en 12 meses baja a 25-30%. Con lever activo, sube a 45-65%.**

Este track NO es opcional. Sin Manuel ejecutándolo en paralelo con Fase -1, todo el resto del plan tiene base débil.

---

## Estructura del track

```
inflection-lever/
├── README.md                      ← este archivo
├── prospects-list.md              ← los 20 prospects refinados con handles + ángulos
├── outreach-templates.md          ← 3 variantes de mensaje (cross-promo, podcast guest, partnership)
└── outreach-log_template.md       ← template para tracking semanal
```

Manuel copia `outreach-log_template.md` cada semana como `outreach-log_YYYY-WW.md` y lo va llenando.

---

## Cómo opera el track

### Semana a semana

1. **Lunes (15 min):** Manuel revisa `prospects-list.md` y elige 5 prospects para outreach esta semana. Diversificar (no 5 del mismo bucket).
2. **Martes-Viernes (30 min/día):** Manuel envía 1-2 outreaches por día, personalizados desde los templates.
3. **Viernes (15 min):** Manuel actualiza `outreach-log_YYYY-WW.md` con status de cada outreach + respuestas.
4. **Próximo lunes:** revisar respuestas + ajustar templates si algo no funciona.

### Decisión de qué outreach hacer

| Si el prospect es… | Outreach tipo | Pedido concreto |
|---|---|---|
| Creator finanzas con audiencia (Mis Propias Finanzas, Nicolás Abril, PCC) | **Cross-promo** | Carousel mutuo / story share / mención en pieza |
| Newsletter editor (Startupeable, Cenital, Ecosistema Startup) | **Cross-promo newsletter** | Featured section en su newsletter a cambio de mención en la nuestra |
| Podcast host (The Frye Show, otros) | **Podcast guest** | Aparecer como guest hablando de "cómo usar IA para tu plata sin volverse esclavo" |
| Broker / fintech (Cocos, IOL, GBM, Bitso) | **Partnership / affiliate** | Affiliate program si tienen + featured content si no |
| Founder destacado (Pierpaolo Barbieri, Daniel Vogel, Patricio Fuks) | **Mención / colaboración** | Comentar sus posts + ofrecer colaboración editorial específica |
| Medio (Bloomberg Línea, Forbes MX) | **Press pitch** | Historia: "El primer daily AI-finanzas LATAM lanzado por un founder solo" |

### Métricas del track

| Métrica | Target Fase -1 (2 sem) | Target Fase 0+1 (1 mes más) |
|---|---|---|
| Outreaches enviados | 10+ | 25+ |
| Respuestas recibidas | 3+ (30% rate) | 8+ (32%) |
| Conversaciones avanzadas | 1-2 | 3-5 |
| Cierres (partnership, podcast, cross-promo) | 0-1 | 2-3 |
| Press hits | 0 | 0-1 |

---

## Principios del outreach (del playbook del Report 03)

1. **Valor primero, pitch después.** El primer mensaje DA, no PIDE. Compartir un insight, un prompt, un dato sobre su contenido.
2. **Específico, no genérico.** "Vi tu pieza X sobre Y y me hizo pensar en Z" > "me encanta tu contenido"
3. **Corto.** Máximo 5-6 líneas. Nadie lee outreaches largos de desconocidos.
4. **Personalizado.** Cada mensaje arranca con algo que demuestre que viste el contenido del prospect.
5. **Sin urgency falsa.** "Lanzamos en X semanas" presiona y aleja. Mejor: "estoy armando esto, ¿te interesaría conocer cuando esté listo?"
6. **No seguir más de 2 veces.** Si no respondió al 2do follow-up (espaciado 1 semana), el "no" silencioso es un "no".
7. **Trackear todo.** Sin tracking, perdés visibilidad de qué funciona.

---

## Lo que NO hacer

- ❌ Enviar el mismo mensaje copy-paste a 20 personas (Mass DM)
- ❌ Pedir RT/cross-promo en el primer mensaje
- ❌ Mencionar números agresivamente ("vamos a ser los próximos NeoCom")
- ❌ Atacar competencia ("a diferencia de X que no hace LATAM")
- ❌ Pedir feedback al primer contacto (eso reverte el flujo de valor)
- ❌ Usar IA visiblemente para escribir los outreaches (los creators de finanzas LATAM huelen LLM a 10km)

---

## Cuándo NO operar este track

- Si Fase -1 falla (engagement <1% en 5+ piezas) → pausar outreaches, no quemar relaciones con un proyecto que no validó
- Si Manuel está saturado y se siente forzando los mensajes → pausar 1 semana, retomar
- Si un prospect responde "no me interesa", marcarlo, no volver a contactar en 6+ meses

---

## Re-evaluación

Cada 4 semanas, evaluar:
- ¿Qué buckets de prospects (creators / newsletters / brokers / fintechs / founders / medios) están respondiendo mejor?
- ¿Qué templates de outreach funcionan?
- ¿Hay prospects nuevos que aparecieron en el camino?

Actualizar `prospects-list.md` agregando/quitando según data real.
