# Deep Research — Mayo 2026

**Fecha de ejecución:** 2026-05-18 (Prompts #3 y #4) + 2026-05-20 (Prompts #1, #2, #5).
**Prompts fuente:** `docs/DEEP_RESEARCH_PROMPTS.md` (commit `7225131`).
**Tool usada:** Claude Deep Research (ChatGPT-like, formato artifact con citaturn).
**Operador:** Manuel.
**Status:** completados los 5. Síntesis cruzada en `docs/DEEP_RESEARCH_SYNTHESIS.md`.

---

## Mapa de archivos

| # | Archivo | Prompt original | Tema | Tamaño |
|---|---|---|---|---:|
| 1 | `01-build-vs-buy.md` | Prompt #1 | ¿Hay un SaaS que cubra el pipeline a $30-100/mo? | 25 KB |
| 2 | `02-competitive-analysis.md` | Prompt #2 | Estado real del espacio "AI newsletter en español" | 33 KB |
| 3 | `03-creator-playbook.md` | Prompt #3 | Cómo escalaron 11 creators LATAM/ES (10K→100K) | 32 KB |
| 4 | `04-nichos-alternativos.md` | Prompt #4 | Score de 12 nichos LATAM (¿AI es el mejor?) | 14 KB |
| 5 | `05-riesgos-plataforma.md` | Prompt #5 | Riesgos técnicos/regulatorios del pipeline IA-automatizado | 35 KB |

**Total:** 5 reports, ~140 KB. Cada uno ~10-15 min de lectura.

---

## Cómo leerlos

**Si vas con tiempo (45-60 min):** leé los 5 en orden numerado. El orden refleja la dependencia lógica de las decisiones.

**Si vas con poco tiempo (20 min):** leé el `DEEP_RESEARCH_SYNTHESIS.md` en `docs/` (síntesis cruzada que extrae los 7-10 findings que cambian el plan actual). Volvé al report individual solo si necesitás profundidad en algo específico.

**Si querés saber lo más importante (5 min):** las primeras 2-3 secciones de cada report (resumen ejecutivo + tabla principal) son suficientes para captar el 80%.

---

## Próximos pasos sugeridos (post-lectura por Manuel)

1. Marcar cuáles findings confirman el plan actual vs cuáles lo cuestionan.
2. Decidir si se aplican los cambios sugeridos en `DEEP_RESEARCH_SYNTHESIS.md` § Recomendaciones.
3. Actualizar `docs/ROADMAP.md`, `docs/DECISIONS.md` y `docs/STACK.md` con los cambios aceptados.
4. Documentar decisiones rechazadas con razón (para no re-debatirlas más adelante).

---

## Limitaciones honestas del research

- Los 5 reports son Deep Research **de superficie + síntesis**, no investigación primaria (no se hicieron entrevistas a creators, no se scrapeó archivos públicos de IG/TikTok, no se compró data como Modash/HypeAuditor).
- Algunos datos son **inferencia**, no documentación oficial (los reports lo marcan explícitamente cuando aplica).
- Los **pricing y rate limits citados** son de mayo 2026; pueden cambiar.
- Los **números de audiencia** son los más recientes encontrados públicamente; algunas plataformas cambian rápido.
