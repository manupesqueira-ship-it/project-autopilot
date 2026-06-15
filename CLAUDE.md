# Dinero IA — pipeline de video financiero 9:16 (raíz: project-autopilot)

> ⚠️ **Este repo es un cementerio de pivots.** Lo ÚNICO activo hoy es **Dinero IA**:
> un sistema PROPIO que genera reels verticales de finanzas personales LATAM
> (planner → voz → render Remotion + Blender → filtros QC → ensamblado FFmpeg).
> Casi todo lo demás del repo está MUERTO o DORMIDO — ver tabla abajo antes de tocar nada.

---

## 🧭 Qué está vivo y qué no (LEER PRIMERO)

| Zona | Estado | Nota |
|---|---|---|
| `infra/` (remotion-render, assembler, voz, qc, blender, n8n) | ✅ **ACTIVO** | El pipeline real de Dinero IA. Aquí se trabaja. |
| `projects/dinero-ia/` | ✅ ACTIVO | Config, entregas, research de la property. |
| `docs/standards/DINERO_IA_STYLE_BIBLE.md` | ✅ **FUENTE DE VERDAD** | Si algo contradice este doc, gana este doc. |
| `README.md`, `.cursorrules`, MASTER_PLAN | ⚠️ **DESACTUALIZADOS** | Describen el viejo "AI Brief/Autopilot" (n8n + 11 agentes, MVP manual). NO refleja el trabajo actual. |
| `docs/` vivos: `standards/`, `runbooks/`, `voice-clone/`, `EXPENSES.md`, `DECISIONS.md` (ADR-018/019), `ROADMAP.md` | ✅ vivos | Lo único de `docs/` que sigue siendo verdad de Dinero IA. El resto se archivó. |
| `_archive/` | 💀 **archivado (recuperable)** | Viejo Autopilot (`core/`, `agents/`, `legacy/`, `workflows/` + `n8n/`, `prompts/`, `assets/`, `data/` raíz), Mira, pivots muertos (`crypto-brief-latam`, `startup-radar-latam`, `mira`), `dinero-ia/infra` (ae-pipeline+veo) y ~117 docs históricos. Gitignored: reversible vía git history + copia en disco. NO revivir sin orden. |

**Regla de oro:** ante duda sobre el estado, la verdad viva está en la **Style Bible**,
en mi memoria de proyecto, y en `git log` — NO en los docs sueltos.

---

## 🏗️ El pipeline (cómo está armado)

```
guion JSON  →  voz ElevenLabs + timestamps  →  render Remotion (beats) [+ Blender 3D]
            →  Filtro A (programático)  →  Filtro B (juez visual vs ref)  →  ensamblado FFmpeg
            →  Filtro C (video completo)  →  gate humano (Manuel)
```

| Paso | Dónde | Qué hace |
|---|---|---|
| Planner / validador | `infra/n8n/` (`planner_system_prompt.txt`, `validator.py`, `workflow_dinero_ia.json`) | Genera y valida el guion JSON (beats, cues, reglas de composición). |
| Voz | `infra/voz/tts_timestamps.py` | ElevenLabs `/with-timestamps`. Voz = **Asgard `eleven_v3`** (id `lJtjZw9ZjSbD9Zs9bOWq`). |
| Render visual | `infra/remotion-render/` (`src/beats/`, `src/theme.ts`, `src/studio/`) | Remotion 4.x local, $0. Cada beat = un componente en `src/beats/`. |
| 3D (opcional) | `infra/blender/` | Blender 5.1, OptiX en la RTX 4060 → PNG alpha → WebM → OffthreadVideo. |
| Filtros QC | `infra/qc/` (`filter_a.py`, `filter_b_prepare.py`, `filter_c_prepare.py`, `seam_check.py`) | A=programático (paleta/luminancia/safe-areas/motion); B=juez visual vs 0x100x; C=video completo + loudness. |
| Ensamblado | `infra/assembler/build916.py` | VO + renders + música ducked + SFX → `out/{slug}/{slug}_FINAL_916.mp4`. |
| Catálogo de beats | `infra/remotion-render/src/beats/` | **La fuente viva del catálogo** (crece seguido). NO confiar en un número fijo de "beat types" — leer la carpeta. |
| Gastos del pipeline | `infra/assembler/ledger.py` + `ledger.json` | Registra costo por corrida. |
| Entregas | `infra/assembler/out/{slug}/` y `projects/dinero-ia/entregas/` | El MP4 final vive aquí. |

---

## ▶️ Cómo correr (Windows, PowerShell)

```
# Un video completo end-to-end:
cd C:\Users\manup\projects\project-autopilot\infra\assembler
python build916.py guion_<slug>.json all

# Render Remotion de un beat suelto (QC visual): desde infra/remotion-render
npx remotion render <CompId> --crf=16 --concurrency=4 --timeout=600000

# Filtros QC:
python infra/qc/filter_a.py <video.mp4>      # exit 1 = FAIL
python infra/qc/filter_c_prepare.py <video>  # prepara juez del video completo
```

- Banco de referencias de calidad (0x100x): `C:\Users\manup\_0x100x_research\` (stills + `refs.json` + `motion_grammar.md`).
- Audio Envato (SFX + música): `C:\Users\manup\envato_audio\` (con `INVENTARIO.txt`).

---

## ⛔ Caminos MUERTOS — NUNCA re-proponer

Cada uno se probó y Manuel lo rechazó. Re-proponerlos quema su confianza:

- **Que Claude arme el video desde cero en AE/ExtendScript** → salió "chafa" (test007/8/9).
- **Templates Envato ensamblados** como video completo → look genérico/viejo, 3 lenguajes visuales incoherentes por video (gate 2026-06-11 RECHAZADO).
- **Veo / IA generativa (Kling/Hailuo/Higgsfield) como medio principal** → "falta muchísimo", cero gráficas, look-IA. Queda SOLO como posible b-roll dentro del sistema diseñado.
- **Diseñador / freelancer externo** (ni one-time) → PROHIBIDO. El sistema es 100% nuestro y automatizado.
- **Plainly / pagar AE** → solo posible motor puntual de charts, NO decidido; no pagar sin replantear con Manuel.

**Camino vigente:** sistema propio "recreación 1:1 de 0x100x + filtros QC en cadena".
Cada beat se construye clonando un plano real de la referencia (no inventar dirección de arte),
luego se parametriza con los datos exactos del guion.

---

## 🔒 Decisiones BLOQUEADAS (no re-litigar sin Manuel)

- **UN solo theme, consistente y profesional, NO viral.** NUNCA cambiar color de fondo ni
  tamaño de número entre escenas de forma decorativa.
- **Color SEMÁNTICO:** verde=sube/seguro/marca · rojo=SOLO pérdida · dorado=dinero · morado=solución. Paleta locked en Style Bible §3 y `src/theme.ts`.
- **SIN subtítulos quemados** (decisión Manuel). La voz narra; el caption no se quema.
- **Durante un chart NO va título textual encima** — el chart domina, la voz narra. Si hace falta contexto, beat de texto SEPARADO antes.
- **Datos SIEMPRE exactos del brief, nunca inventados.** Si el guion dice una cifra, el beat muestra ESA cifra. Moneda explícita (USD o MXN), nunca "$X" a secas.
- **Nicho = finanzas personales LATAM en español** colgadas de un hook macro de actualidad. Moat = precisión cultural (CETES/pesos/inflación/modismos), no el look.

---

## ⚠️ Gotchas técnicos (NO redescubrir)

- **Fuente Remotion:** `@remotion/fonts loadFont` con `url=staticFile("Inter-Variable.ttf")`
  (servidor local). NO data-URI inline, NO FontFace manual — ambos cuelgan/starvean el
  `delayRender` a `--scale=2`. Subir `--timeout` a 600000 cuando se renderiza en HD 2x.
- **`--props` de Remotion NO acepta JSON de `Out-File`** (BOM UTF-16) → escribir el JSON con la herramienta Write, no con PowerShell.
- **NO editar archivos UTF-8 con `-replace` de PowerShell** (mojibake) — usar Write/Edit.
- **Leer guiones JSON con `utf-8-sig`** (BOM de PowerShell).
- **FFmpeg concat:** usar concat FILTER (decodifica frames exactos), no el DEMUXER `-c copy` (pierde/duplica frames, tick-rate 240fps). Re-encode crf 15.
- **Audio final:** `loudnorm I=-16:TP=-1.5` (true-peak) + mux final con `-c:a copy` (re-encodear AAC reintroduce picos > -1 dBTP). Sidechain: `apad=whole_dur=total` o `-shortest` recorta el TAIL del CTA.
- **ffmpeg** (Gyan) NO está en PATH → usar ruta completa o `FFMPEG_BIN`.
- **Filtro `ass` en Windows:** correr ffmpeg con cwd=tmp y path relativo (escape de `:` falla).

---

## 💸 Dinero (CONGELAMIENTO ACTIVO)

- **Cero herramientas/suscripciones/APIs nuevas de paga sin OK explícito de Manuel.** Default gratis/open-source. Cotización real (USD + aprox MXN) ANTES de gastar — incluye créditos de API (ElevenLabs, OpenAI gpt-image-1, planner Anthropic ~$0.03-0.05/guion).
- **Registrar TODO gasto en `docs/EXPENSES.md`** el mismo día (además del `ledger.json` por corrida).
- Todo el pipeline de render corre **$0** (Remotion + Blender + FFmpeg + n8n self-hosted locales).

---

## 🔐 Seguridad

- Secretos viven SOLO en `.env` (gitignored). **NUNCA leer, imprimir, ni commitear** variables con KEY/SECRET/TOKEN/PASSWORD/CREDENTIAL ni archivos `.env*`.
- El repo es git; commits con mensajes descriptivos en inglés. No commitear archivos binarios pesados de prueba (.mp4) sin razón.

---

## 🎯 Foco actual (verificar contra Style Bible + `git log`, cambia rápido)

- **Objetivo:** 3 posts/día en horarios estratégicos → el cuello de botella es **MATERIAL** (banco de temas), no la calidad del medio.
- ✅ **Cortes abruptos RESUELTOS** (xfade real en `build916.py`, `XFADE=0.35`, dip de música en el silencio real entre voces). Catálogo de ~39 beats + director (`validator.py` R1–R11 31/31, `ledger.py`, lane A/B de rotación) ya existen.
- Plan vigente (2026-06-15): Fase 1 limpieza→`_archive/` ✅ → Fase 2 doc baseline "lo que funciona" → Fase 3 **banco de temas** (`infra/n8n/temas_cola.json`) → Fase 4 n8n semi-auto con gate humano. NO re-sembrar los guiones viejos ("esos ya fueron") ni re-proponer caminos muertos.

---

## 🤝 Cómo trabajar conmigo (Manuel)

- **No me digas "leé X archivo":** abre el archivo y pégame el contenido relevante en el chat.
- **No proponer externos** ni caminos ya muertos (ver arriba). Sistema 100% nuestro.
- **Acceso directo a remotos** (VPS/API): conseguir credenciales/`paramiko`, no usarme de puente copy-paste.
- **Cada entrega = capacidad o tema NUEVO.** No repetir el mismo demo (el beat CETES ya está quemado). Limpiar intermedios de las carpetas.
- Quiere un sistema **modular que él mismo pueda tocar** y mejorar por segmentos.
