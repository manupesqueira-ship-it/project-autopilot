# Voice & Tone Standard — Dinero IA

**Versión:** 1.0
**Fecha:** 2026-06-01
**Base:** research benchmark 13 creators + brand_voice.md v3
**Aplica a:** A6 Audio Director, A8c Voice Gen (ElevenLabs)

> Voice clone strategy 2-fases:
> - **Fase 1.0:** ElevenLabs voice library (español neutro LATAM masculino)
> - **Fase 1.1:** voice clone Manuel post-grabación 20-30 min
> Swap es un solo parameter change en A8c — el resto del pipeline no cambia.

---

## 1. Filosofía de tono

**Cruce buscado:** profesor cálido LATAM (Mis Propias Finanzas / Sofía Macías) + autoridad ejecutiva pausada (Codie Sanchez) + visualización tangible (Humphrey Yang).

**Lo que NO somos:**
- ❌ Hype-bro tipo Mafia IA en sus posts más vendedores
- ❌ Apocalíptico tipo Jon Hernández ("no estamos preparados para...")
- ❌ Monótono extremo tipo Graham Stephan
- ❌ Energía teatral exagerada tipo Mark Tilbury

**Lo que SÍ somos:**
- ✅ Profe que respeta tu inteligencia
- ✅ Autoridad sin condescendencia
- ✅ Cálido pero no informal-bro
- ✅ Curioso por la herramienta, no fan religioso de la IA

---

## 2. Parámetros numéricos (locked)

| Parámetro | Valor target | Tolerancia |
|---|---|---|
| **WPM (palabras por minuto)** | 170 | 165-180 |
| **Pausa estándar entre frases** | 0.4s | 0.3-0.5s |
| **Pausa larga en cifras / revelaciones** | 0.6s | 0.5-0.7s |
| **Pausa muy larga en disclaimer** | 0.8s | 0.7-0.9s |
| **Énfasis prosódico** | Cifras + power-words | Marcado en SSML |
| **Modulación de energía** | Media | Baja en context, sube en cifra, baja en CTA |

**Referencias del benchmark:**
- Humphrey Yang: 150-165 WPM (límite bajo nuestro)
- Codie Sanchez: 155-170 WPM (núcleo)
- Jenny Hoyos: 190-210 WPM (techo alto — no copiar entero)
- Nuestro target 170 WPM = sweet spot del cruce.

---

## 3. Estructura típica de script para reel 45s

| Beat | Segundos | Función | Tono |
|---|---|---|---|
| **B1 — Hook** | 0-3s | Power-word + cifra LATAM + tensión | Energía alta, ritmo rápido (180 WPM), sin pausas largas |
| **B2 — Contexto** | 3-12s | Qué pasó / por qué te tiene que importar | Energía media, ritmo natural (170 WPM), 1 pausa larga en cifra clave |
| **B3 — Peak / valor** | 12-30s | El prompt / template / dato accionable | Energía media-alta, ritmo claro (165 WPM), pausas en cifras |
| **B4 — Resolución LATAM** | 30-42s | Cómo aplica a tu caso país | Energía baja-media, ritmo pausado (160 WPM), pausas largas en aplicación |
| **B5 — Disclaimer + CTA** | 42-50s | "Esto no es asesoría..." + save/share | Energía baja, ritmo lento (150 WPM), pausa muy larga antes de disclaimer |

**Distribución de palabras total reel 45s:** ~125-135 palabras (170 WPM × 0.75 min ≈ 128).

---

## 4. Reglas de habla — español neutro LATAM

### SÍ usar
- "Vos" o "tú" según contexto (no "usted" — distancia)
- "Ustedes" para plural (no "vosotros")
- Verbo en presente, no condicional ("si pongo X" no "si pusiera X")
- "Plata" como universal LATAM (acepta MX/AR/CO/CL/PE/UY/VE)
- "Acá" o "aquí" (ambos válidos neutros)
- Pronunciar "z" y "c" como "s" (no ceceo peninsular)

### NO usar
- ❌ Peninsular: "vosotros", "vale", "tío/tía", "hostia", "mola", ceceo
- ❌ Mexicanismo extremo: "chido", "padre", "no manches", "qué onda", "órale"
- ❌ Argentinismo extremo: "vos sos", "boludo", "viste", "che", "posta"
- ❌ Caribe extremo: "pa'lante", elisiones fuertes de "s"
- ❌ Anglicismos innecesarios cuando hay equivalente ES ("update" en vez de "actualización")

### Vocabulario técnico aceptable en inglés
- AI, AGI, LLM, prompt, agent, deployment, workflow, ETF, CEDEAR, fintech, broker

### Cifras en habla
**Reglas duras:**
- Siempre con moneda + país: "1,500 pesos mexicanos" no "1,500 pesos"
- Para AR específicamente, mencionar el formato: "ARS 50,000" se dice "cincuenta mil pesos argentinos"
- Para USD: "200 dólares" no "200 USD" en habla
- Porcentajes: "el 15 por ciento" no "el 15%"
- Tasas anuales: "una tasa del 40 por ciento anual" no "TNA del 40"

---

## 5. SSML markers que A6 Audio Director debe usar

A6 genera el script con SSML para que ElevenLabs interprete pacing y énfasis correctamente.

### Pausas

```xml
<break time="400ms"/>   <!-- pausa estándar entre frases -->
<break time="600ms"/>   <!-- pausa antes/después de cifra -->
<break time="800ms"/>   <!-- pausa antes del disclaimer -->
```

### Énfasis prosódico

```xml
<emphasis level="strong">cuarenta mil pesos</emphasis>   <!-- cifras grandes -->
<emphasis level="moderate">esto cambia todo</emphasis>   <!-- power-words -->
```

### Velocidad por sección

```xml
<prosody rate="fast">Por qué importa</prosody>          <!-- hook -->
<prosody rate="medium">Te explico</prosody>             <!-- contexto -->
<prosody rate="slow">Esto no es asesoría financiera</prosody>   <!-- disclaimer -->
```

### Pronunciación específica (override ElevenLabs si necesario)

```xml
<phoneme alphabet="ipa" ph="seˈðɛɾ">CEDEAR</phoneme>    <!-- pronunciación AR -->
```

---

## 6. ElevenLabs voice settings — locked

### Voice library (Fase 1.0 — arranque)

**Voice ID sugeridos (a verificar al activar cuenta):**
- **Adam (multilingual)** — masculino neutro, ~35 años, profesor cálido
- **Antoni (Spanish neutral)** — masculino LATAM neutro, autoridad amable
- **Drew (multilingual)** — masculino más maduro, ideal para autoridad

**Settings recomendados:**

```json
{
  "stability": 0.55,
  "similarity_boost": 0.75,
  "style": 0.35,
  "use_speaker_boost": true,
  "model_id": "eleven_multilingual_v2"
}
```

| Parámetro | Valor | Por qué |
|---|---|---|
| stability 0.55 | Equilibrio — bajo da emoción inconsistente, alto da robot monótono |
| similarity_boost 0.75 | Cercano al original pero permite expresividad |
| style 0.35 | Moderado — Dinero IA es serio-cálido, no dramático |
| use_speaker_boost | true | Mejora claridad consistente |
| model_id | eleven_multilingual_v2 | Mejor manejo de español + SSML |

### Voice clone Manuel (Fase 1.1 — post-grabación)

Mismo settings. Solo cambia el `voice_id` al ID generado por ElevenLabs después de procesar la grabación de 20-30 min de Manuel.

---

## 7. Modulación por sub_categoría

A6 ajusta SSML según el tipo de pieza:

| sub_categoria | Energía | Velocidad target | Pausas | Estilo |
|---|---|---|---|---|
| **inversiones** | Media | 165 WPM | Pausas largas en cifras y tasas | Autoritativo calmo |
| **presupuesto** | Media-alta | 175 WPM | Pausas normales | Confesional accesible |
| **inflacion** | Media | 170 WPM | Pausas largas en contexto país | Educativo preocupado |
| **impuestos** | Baja-media | 160 WPM | Pausas muy largas en conceptos | Tutorial paciente |
| **comparativas** | Media-alta | 175 WPM | Pausas en ganador | Test-driven |
| **retiro** | Baja | 155 WPM | Pausas reflexivas | Sabio largo plazo |
| **crypto** | Media | 170 WPM | Pausas en riesgos | Educativo cauteloso |
| **bancos** | Media | 170 WPM | Pausas en revelaciones | Mostrar-no-vender |

---

## 8. Patrones de habla a evitar

### Anti-patterns que el script NO debe contener

1. **"Hola amigos / hola comunidad"** — apertura genérica de creator-talk
2. **"Súper..."** como intensificador ("super interesante", "super barato")
3. **"Literalmente..."** mal usado
4. **"Te voy a contar..."** (filler — empezar directo)
5. **"En este video..."** (meta-referencia innecesaria)
6. **"Si te gustó..."** al final (genérico — preferir CTA específico)
7. **"Te lo juro / te lo prometo"** (sospecha hype)
8. **"Esto te va a cambiar la vida"** (banned por compliance reglas 8/15)

### Filler words OK en moderación

- "Bueno..." (al inicio de explicación) — OK 1× max
- "Ahora..." (transición) — OK 2× max
- "Te explico..." (preámbulo de step) — OK 1× max

---

## 9. Pronunciación de marcas y productos

A6 marca pronunciaciones específicas en SSML para evitar interpretaciones gringas:

| Producto / marca | Pronunciación correcta | SSML |
|---|---|---|
| Cocos Capital | "co-cos capital" (no "ko-kos") | `<phoneme alphabet="ipa" ph="ˈko.kos ka.piˈtal">Cocos Capital</phoneme>` |
| IOL | letra por letra: "i-o-ele" | `<say-as interpret-as="characters">IOL</say-as>` |
| GBM | "ge-be-eme" | `<say-as interpret-as="characters">GBM</say-as>` |
| Bitso | "bít-so" | natural |
| Buenbit | "buen-bit" | natural |
| Mercado Pago | natural | natural |
| Claude | "klod" (no "klaude") | `<phoneme alphabet="ipa" ph="kloːd">Claude</phoneme>` |
| ChatGPT | "chat-ge-pe-te" | `<say-as interpret-as="characters">GPT</say-as>` |
| CEDEAR | "se-de-ar" (AR specific) | `<phoneme alphabet="ipa" ph="seˈðɛɾ">CEDEAR</phoneme>` |
| ETF | letra por letra | `<say-as interpret-as="characters">ETF</say-as>` |
| FCI | "efe-ce-i" | `<say-as interpret-as="characters">FCI</say-as>` |
| INDEC | "in-dec" | natural |
| Anthropic | "an-tró-pik" | `<phoneme alphabet="ipa" ph="anˈtɾo.pik">Anthropic</phoneme>` |

---

## 10. Checklist para A9 Compliance — voice

- [ ] WPM dentro de 165-180 target
- [ ] Pausa antes del disclaimer ≥ 0.7s
- [ ] Cifras pronunciadas con moneda + país completos
- [ ] Productos mencionados con pronunciación correcta SSML
- [ ] Sin filler banned (super, literalmente, etc.)
- [ ] Sin claims "te cambia la vida"
- [ ] Energía baja-media en disclaimer (no enérgica)
- [ ] Voice ID actual (library Fase 1.0 o clone Manuel Fase 1.1) consistente con todo el reel

---

## 11. Sample script (referencia rápida)

```
<prosody rate="fast">
<emphasis level="strong">Subí mi extracto a Claude</emphasis>.
<break time="400ms"/>
Encontró cuatro <emphasis level="strong">suscripciones fantasma</emphasis>
por <emphasis level="strong">cuarenta mil pesos mexicanos</emphasis>.
</prosody>

<break time="600ms"/>

<prosody rate="medium">
Esto es lo que hace cualquier IA con tu data bancaria.
<break time="400ms"/>
Te muestro cómo en 30 segundos.
</prosody>

<break time="400ms"/>

<prosody rate="medium">
Paso uno: descargás tu extracto en PDF desde el portal de tu banco.
<break time="400ms"/>
Paso dos: lo subís a <phoneme alphabet="ipa" ph="kloːd">Claude</phoneme>
y le pegás este prompt.
<break time="600ms"/>
"<emphasis level="moderate">Listame las suscripciones recurrentes
de los últimos tres meses con monto y fecha exacta</emphasis>".
</prosody>

<break time="800ms"/>

<prosody rate="slow">
Importante.
<break time="600ms"/>
Esto es educativo, no asesoría financiera.
Antes de cancelar cualquier cargo, verificá que no esté ligado
a un servicio que sí usás.
</prosody>
```

**Análisis del sample:**
- 132 palabras → 47 segundos a 170 WPM
- Hook 0-3s con `prosody rate="fast"` + emphasis strong en cifra
- Cierre 42-47s con `prosody rate="slow"` + pausa 0.8s antes de disclaimer
- Pronunciación Claude marcada con IPA para evitar "klau-de"
