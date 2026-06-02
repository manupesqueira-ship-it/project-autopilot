# Music Standard — Dinero IA

**Versión:** 1.0
**Fecha:** 2026-06-01
**Base:** research benchmark — patrón cruzado música top performers
**Aplica a:** A6 Audio Director (selección de mood), A8d Music Selection, A8e Compositor (mix)

> Música como complemento, NO como protagonista. Si saca atención del mensaje, falla.
> Mejor sin música que con música mediocre.

---

## 1. Filosofía musical

**Cruce buscado del benchmark:**
- **Rowan Cheung** (synthwave corporate tech) + **Riley Brown** (lo-fi hip-hop) = AI vibe sin ser hype
- **Codie Sanchez / Graham Stephan** (mínima o nada) = autoridad financiera
- **Jenny Hoyos** (beat bajo que sube en el peak) = retention engineering

**Estética final Dinero IA:** beat lo-fi cálido con elementos electrónicos sutiles. Sin EDM, sin reggaetón, sin orchestral épico.

---

## 2. Parámetros locked

| Parámetro | Valor | Detalle |
|---|---|---|
| **BPM target** | 75 | Rango aceptable 70-85 |
| **Volumen base bajo voz** | -20 LUFS | Rango -18 a -22 LUFS |
| **Volumen en silencio (no voz)** | -14 LUFS | Sube 6 LUFS cuando no hay narración |
| **Volumen en disclaimer** | -24 LUFS | Casi imperceptible — protagonismo total al mensaje legal |
| **Estilo dominante** | Lo-fi hip-hop instrumental cálido | Sin lyrics, sin samples vocales |
| **Instrumentación predominante** | Piano eléctrico + drums suaves + bajo sub | Sin guitarra distorsionada, sin sintes leads agresivos |
| **Duración mínima del track** | 60s | Cubre cualquier reel hasta 55s con safety |

---

## 3. Mood × sub_categoría

A6 Audio Director selecciona el mood según el tipo de pieza:

| sub_categoria | Mood | BPM | Características | Ejemplo de descripción |
|---|---|---|---|---|
| **inversiones** | Contemplative confident | 70-75 | Piano arpeggio + bajo cálido | "calm but determined, low key piano with sub bass" |
| **presupuesto** | Optimistic warm | 75-82 | Lo-fi hip-hop + glockenspiel | "warm lo-fi hip-hop, chill but engaging" |
| **inflacion** | Tense reflective | 70-78 | Piano + strings suaves + drums minimal | "thoughtful, slight tension, piano-driven" |
| **impuestos** | Steady focus | 72-80 | Lo-fi minimal | "focused, neutral, lo-fi hip-hop background" |
| **comparativas** | Curious upbeat | 78-85 | Drums activos + synth pad | "curious and energetic, mid-tempo lo-fi" |
| **retiro** | Calm wisdom | 65-72 | Piano + ambient pad | "wise and calm, ambient piano, contemplative" |
| **crypto** | Tech tension | 75-82 | Synthwave sutil + drums | "subtle synthwave, slight unease, modern" |
| **bancos** | Investigation | 70-78 | Lo-fi noir | "investigative, slightly mysterious, lo-fi" |
| **comparativas IA** | Tech curious | 80-85 | Synthwave corporate | "corporate synthwave, optimistic about tech" |

---

## 4. Pattern de mix con voz (A8e Compositor)

### Reglas duras de ducking

El audio de voz (A8c output) tiene prioridad absoluta. La música hace ducking automático cuando hay voz:

```
Volumen música:
- Sin voz: -14 LUFS (full presence)
- Con voz: -20 LUFS (ducked, -6 LUFS)
- Disclaimer activo: -24 LUFS (-10 LUFS)
- Pausas largas (>1s): up a -16 LUFS (sube 4 LUFS)
```

### Curva de volumen por beat del reel

```
B1 Hook (0-3s):
  Volumen: -18 LUFS, beat marcado, intro impactante

B2 Contexto (3-12s):
  Volumen: -20 LUFS, beat sostenido, sin variación

B3 Peak/valor (12-30s):
  Volumen: -19 LUFS, leve subida en revelación de cifra principal
  Highlight musical: 1 single hit/pulse en segundo de cifra grande

B4 Resolución LATAM (30-42s):
  Volumen: -21 LUFS, beat más suave, prepara cierre

B5 Disclaimer (42-50s):
  Volumen: -24 LUFS, casi imperceptible, deja brillar la voz seria
```

---

## 5. Fuentes de música licensed (locked)

**Stack recomendado en orden de prioridad:**

### Opción A — Epidemic Sound (preferida)
- **Plan:** Personal Subscription, $9-13/mo
- **Por qué:** mejor catálogo lo-fi hip-hop instrumental cálido. Licencia comercial incluida. API + Zapier nativos.
- **Setup:** crear cuenta con `aibrieflatam.media@gmail.com`. Curar playlist "Dinero IA — Lo-Fi" con 30-40 tracks BPM 70-85 que cumplan specs §3.

### Opción B — Artlist
- **Plan:** Creator, $9.99/mo (anual) o $14.99/mo (mensual)
- **Por qué:** catálogo amplio, mood tags muy bien organizados. UI superior.
- **Diferencia con Epidemic:** Artlist es más cinematográfico, Epidemic más urbano. Para Dinero IA queremos cruce — testear ambos primero.

### Opción C — Free (fallback)
- **YouTube Audio Library** (royalty-free) — catálogo limitado pero gratis
- **Pixabay Music** — calidad variable
- **Solo si A o B fallan o si arrancamos antes de activar cuenta**

---

## 6. Licensing — reglas duras compliance

| Regla | Detalle |
|---|---|
| Solo música con licencia comercial Instagram + TikTok | Verificar antes de cada track en Epidemic/Artlist (filtros específicos) |
| NO usar IG/TT music library de pop comercial | Penaliza alcance + posible takedown si la cuenta crece |
| NO usar tracks marcados "personal use only" | Aunque digan "free" |
| NO usar tracks con sample de canciones populares | Algoritmo detecta y baja reach |
| Atribución solo si la licencia lo exige (la mayoría de Epidemic NO) | Si exige: crédito en caption "Music: [artist] via Epidemic Sound" |
| Si el track tiene voice samples o lyrics, NO usar | Compite con la narración |

---

## 7. Catálogo curado inicial — guía para selección manual

**Tags a buscar en Epidemic Sound / Artlist:**

Top filtros:
- Mood: "Calm", "Focused", "Confident", "Hopeful"
- Genre: "Lo-fi", "Chillhop", "Cinematic Electronic", "Ambient"
- Tempo: 70-85 BPM
- Vocals: "No vocals" (filtro estricto)
- Length: 60-120s (cubre reels + margen)
- Instruments: Piano, Electric Piano, Lo-Fi Drums, Sub Bass, Ambient Pad

Anti-filtros:
- ❌ Genre: EDM, Reggaeton, Pop, Rock, Trap, Drill
- ❌ Mood: Aggressive, Tense (excepto curated specific), Dark, Romantic
- ❌ Vocals: cualquiera

**Catálogo objetivo Pre-Fase 1:** 30-40 tracks curados Manuel/Claude en una playlist Spotify reference + descargados a Supabase Storage `dinero-ia-assets/music-library/`.

---

## 8. A8d Music Selection — workflow

Cuando A6 Audio Director determina el mood (basado en sub_categoria + brief_content), A8d ejecuta:

```
1. Query playlist curated en Supabase Storage `music-library/{mood_tag}/`
2. Filtrar por:
   - BPM range del mood (rango §3)
   - Duración ≥ duración_reel + 5s buffer
   - No usado en últimas 14 piezas (anti-repetición)
3. Selección aleatoria entre tracks restantes
4. Download URL del track al compositor A8e
5. Log selección en `music_usage_log` table (para anti-repetición)
```

**Si no hay tracks disponibles que cumplan filtros → fallback a track default "Dinero IA — neutral background" + alerta Telegram a Manuel.**

---

## 9. Configuración de mezcla A8e (FFmpeg recipe)

A8e Compositor mezcla 3 streams:

```bash
# Pseudo-recipe FFmpeg
ffmpeg \
  -i video.mp4 \
  -i voice.mp3 \
  -i music.mp3 \
  -filter_complex "
    [1:a]volume=1.0[voice];
    [2:a]volume=0.25,sidechaincompress=threshold=0.1:ratio=8:attack=20:release=200[music_ducked];
    [voice][music_ducked]amix=inputs=2:duration=longest:dropout_transition=2[audio]
  " \
  -map 0:v -map "[audio]" \
  -c:v copy -c:a aac -b:a 192k \
  output.mp4
```

**Sidechain compression:** la voz dispara el ducking de la música automáticamente. Ratio 8:1 = bajada agresiva en presence de voz. Attack 20ms / Release 200ms = ducking suave sin pop audible.

---

## 10. Anti-patterns musicales

NO usar:
- ❌ Música con BPM > 100 (rompe ritmo conversacional)
- ❌ Música con drop EDM (rompe atención)
- ❌ Música con vocals de cualquier tipo
- ❌ Música popular reconocible (canciones de chart)
- ❌ Mismo track 2 veces en 14 días
- ❌ Música con fade-in/fade-out > 3s (tiempo perdido en reel corto)
- ❌ Música épica/orchestral con strings dominantes (cae a documental hollywood)
- ❌ Lo-fi súper popular que ya está saturado en LATAM finance creator content (track "ya escuché en 50 reels")

---

## 11. Checklist para A9 Compliance — música

- [ ] Track tiene licencia comercial verificada Instagram + TikTok
- [ ] BPM dentro de 70-85
- [ ] Mood matchea sub_categoria correcta
- [ ] Volumen base -20 LUFS bajo voz (no más alto)
- [ ] Volumen en disclaimer -24 LUFS o menos
- [ ] Ducking automático funciona (voz audible en todo momento)
- [ ] No track usado en últimas 14 piezas
- [ ] No vocals en track
- [ ] No samples reconocibles de canciones populares
