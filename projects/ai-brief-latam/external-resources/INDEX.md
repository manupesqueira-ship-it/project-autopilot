# External Resources — AI How-To LATAM

**Última actualización:** 2026-05-18
**Propósito:** materiales de terceros (cursos, templates, deals) importados a este proyecto para acelerar Fase 0-2 sin reinventar patterns ya validados.

---

## Por qué existe esta carpeta

El 2026-05-12, durante limpieza del escritorio de Manuel, se identificó un curso de n8n con 117 templates JSON + 3 PDFs operativos guardados en OneDrive. La instrucción fue: **"copia lo que tenga alto valor operativo, descarta el ruido, normaliza nombres para que nunca se confundan con archivos del proyecto."**

Esta carpeta es el resultado. Todo lo que está acá fue evaluado, renombrado a kebab-case, y mapeado contra nuestro ROADMAP. Lo que se descartó está documentado abajo con su razón.

---

## Estructura

```
external-resources/
├── INDEX.md                                    ← este archivo
└── n8n-course/
    ├── README.md                               ← contexto del curso
    ├── 30-day-ai-automation-roadmap.pdf        ← roadmap day-by-day, validación lógica fase -1
    ├── recommended-tools-original.pdf          ← PDF original con affiliate links
    ├── recommended-tools-extracted-deals.md    ← deals limpios sin affiliate (formato consumible)
    ├── n8n-cheatsheet-dashboard.pdf            ← cheatsheet operativo n8n
    ├── n8n-cheatsheet.png                      ← mismo cheatsheet en imagen
    └── high-value-templates/                   ← 24 templates seleccionados de 117
        ├── templates-index.md                  ← mapeo template → fase ROADMAP
        └── [24 archivos .json]
```

**Total:** 28 archivos, 7.96 MB.

---

## Criterio de selección aplicado

**SE COPIÓ si cumplía al menos uno:**
1. Confirma una decisión técnica nuestra (Hostinger VPS, n8n self-hosted, community nodes).
2. Implementa un pattern que necesitamos en Fase 1-2 (HITL Telegram, multi-platform publish, voice clone).
3. Aporta referencia operativa para algo que pensábamos construir custom (research agents, content viral hooks).
4. Es activo asociado a un deal con descuento (ElevenLabs 50%, Vapi 1000 min, Hostinger template).

**NO se copió:**
- Templates de nichos sin overlap (e-commerce dropshipping, lead-gen B2B SaaS, real-estate scraping, dental clinic CRM, etc.) — ~70 de 117.
- Templates de plataformas que descartamos (Make.com, Zapier-only, Pipedream) — ~15.
- Templates demo de funcionalidades básicas que ya dominamos (HTTP request básico, Set node tutoriales, IF/Switch examples) — ~8.

**Total descartado del curso:** 93 de 117 templates. Sin pérdida — el curso original sigue en OneDrive de Manuel para acceso futuro si algún pattern reabre.

---

## Qué se evaluó y se descartó del escritorio (fuera del curso n8n)

| Carpeta/archivo | Decisión | Razón |
|---|---|---|
| `mira/` (Next.js virtual fitting room) | NO tocar | Manuel: "no quiero tocar eso". Proyecto separado, en pausa. |
| Polymarket Bot research | NO tocar | Manuel: "ya está desactivado. No lo quiero volver a tocar". |
| `bateria.html` | Descarte | Windows Battery Report — irrelevante. |
| Documentos personales varios | No revisado | Fuera del scope: solo se evaluó material AI/automation. |

---

## Cómo usar esta carpeta

**Durante Fase -1 (Validación Manual):** consultar `30-day-ai-automation-roadmap.pdf` para confirmar día por día qué deberíamos estar midiendo. No copiar el roadmap textual — solo usarlo como sanity check.

**Durante Fase 0 (smoke test n8n):** abrir `high-value-templates/hitl-pattern-telegram-equiv.json` y `publisher-multi-platform-autoposting.json` como referencia de cómo otros estructuran lo mismo que vamos a construir.

**Durante Fase 1 (pipeline texto + carousel):** `publisher-multi-platform-autoposting.json` (Upload-Post equivalente), `publisher-blotato-plan-b.json` (fallback), `linkedin-best-posting-system-fase-1-5.json`.

**Durante Fase 2 (reels + voice):** `elevenlabs-voice-fase-2.json`, `seedance-demo-*.json`, `tiktok-video-machine-fase-2.json`, `viral-ad-videos-nanobanana-veo3.json`.

**Cuando necesites deal/descuento:** `recommended-tools-extracted-deals.md` tiene los 4-5 deals limpios sin affiliate junk.

Ver `n8n-course/high-value-templates/templates-index.md` para el mapeo completo template → fase.

---

## Restricciones

- **No editar los `.json` originales.** Si un template inspira un workflow nuestro, créalo nuevo en `projects/ai-brief-latam/workflows/` y referenciá cuál template usaste de base en el comment del workflow.
- **No hostear estos templates en el VPS sin auditarlos.** Algunos tienen credentials hardcodeadas, otros tienen nodos community que requieren install previo. Tratar como **referencia de patrón**, no como código deployable.
- **No redistribuir.** El curso es material licenciado por su autor; estos archivos están acá para uso operativo personal del proyecto, no para republicar.

---

## Incidente de seguridad detectado y resuelto (2026-05-18)

GitHub Push Protection bloqueó el primer intento de commit: `ai-story-generator-viral-hooks.json:27` contenía una **OpenAI API key REAL** (`sk-proj-...`), no un placeholder. Era una credential del autor del curso, expuesta sin querer al exportar el workflow.

**Acción tomada:**
- Reemplazado el valor por `Bearer REDACTED_OPENAI_API_KEY_REPLACE_WITH_YOUR_OWN`.
- Verificado con grep que no haya más keys (`sk-`, `Bearer <token>`, `xoxb-`, `ghp_`, `AKIA`, `AIza`, etc.) en ningún otro template.
- Sin más hits.

**Lección operativa:** **siempre asumir que un workflow exportado puede tener credentials reales**, no placeholders. Antes de importar cualquier template nuevo (no solo de este curso), pasar grep por patterns de secrets. Si Manuel reportó la key al autor del curso, podría también notificarse responsablemente — pero ya está sanitizada en nuestro repo y la key debe asumirse comprometida (revocarla si era de Manuel; si era del autor, no nuestra cuestión).
