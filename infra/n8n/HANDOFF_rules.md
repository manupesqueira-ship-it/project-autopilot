# Director Dinero IA — reglas + validador + ledger (HANDOFF)

Capa "director": reglas codificadas + validador automático + ledger + gate humano.
Pasa de "Claude decide por gusto" a "Claude propone dentro de reglas → filtro
automático rechaza guiones malos → Manuel aprueba".

Todo es **$0**, **offline** y **sin herramientas nuevas**. El planner (que sí
gasta API ~$0.03-0.05 USD/guion) NO se corre sin tu OK.

## Archivos (qué es cada cosa)

| Archivo | Qué hace |
|---|---|
| `infra/assembler/ledger.py` | Módulo Python: registro de videos producidos. API `Ledger()`, `is_tema_repeated`, `is_combo_repeated`, `recent_beats`, `append_video`. También CLI. La FIRMA visual de un video = sus beats del medio (lista-NEGRA `SIGNATURE_EXCLUDE` = unión de `HOOK_TYPES∪CLIMAX_TYPES∪CTA_TYPES` del validador: excluye las PUNTAS, que rota R11 aparte); cualquier beat nuevo del catálogo cuenta solo. |
| `infra/assembler/ledger.json` | Fuente de verdad del ledger. **Empieza VACÍO** a propósito (los 6 guiones viejos NO se sembraron). |
| `infra/n8n/validator.py` | Lógica PURA de validación (fuente de verdad de las reglas). Importable + CLI. |
| `infra/n8n/proposer.py` | Arma un ESQUELETO de guion (tipos de beat + huecos `<<rellenar>>`) a partir de un tema. Muestrea del catálogo VIVO (`registered_beat_types()` lee Root.tsx), corre `validate()` y reintenta hasta que pase R1–R9. `$0`, NO llama a la API. |
| `infra/n8n/test_validator.py` | QC offline: 31 casos pass/fail con guiones-fixture inventados + tests de ledger, recencia (R10) y rotación de puntas (R11). `$0`, no llama API. |
| `infra/n8n/test_planner.py` | Igual que antes, PERO ya no duplica reglas: importa `validate()` + `Ledger()`. (Este sí llama a la API; correr solo con tu OK.) |
| `infra/n8n/workflow_dinero_ia.json` | El validador JS inline se reemplazó por un nodo que llama a `validator.py` (Python = única fuente de verdad). |
| `infra/n8n/planner_system_prompt.txt` | Actualizado con el arco obligatorio, visual wow, cobertura de movimiento, moneda explícita y novedad. |

## Cómo correr (todo $0)

```
# QC del validador + ledger (offline, recomendado tras cualquier cambio de reglas):
cd infra\n8n
python test_validator.py

# Validar un guion suelto a mano:
python validator.py ..\assembler\guion_X.json --ledger          # exit 0=PASS, 1=FAIL
python validator.py ..\assembler\guion_X.json --brief brief.txt # + chequeo de cifras vs brief
python validator.py ..\assembler\guion_X.json --strict          # warnings cuentan como error

# Proponer un esqueleto de guion (estructura + huecos, $0, sin API):
python proposer.py "Por que los CETES ya no rinden como antes" --ledger --out ..\assembler\guion_X.json
python proposer.py "Tema" --ndata 3   # 7 beats en vez de 6 (--ndata 2 = 6 beats)

# Ledger:
python ..\assembler\ledger.py list
python ..\assembler\ledger.py check guion_X.json                # 0=novedoso, 1=repite
python ..\assembler\ledger.py append guion_X.json               # registrar (gate humano, ver abajo)
```

## Reglas codificadas (errores duros → rechazan el guion)

- **R1** Ningún beat de aterrizaje (BigNumber/AssetCard/Versus/Bars) >2.5s sin un
  sub-evento que cubra el final. También: un hook Kinetic debe revelar ≥50% de las
  palabras de su vo (mata el "hook congelado 9s").
- **R2** ≤2 beats del mismo tipo por video y NUNCA 2 iguales seguidos.
- **R3** ≥1 visual "wow" (mapa / caricatura / gráfica espectáculo).
- **R4** Arco fijo: hook (`HOOK_TYPES` = Kinetic o StatCallout) → contexto → ≥2
  datos visuales DISTINTOS → clímax (`CLIMAX_TYPES` = BigNumber o HeroCoin, después
  de los datos) → BeatCta. La FORMA del arco está locked; lo que rota es QUÉ tipo
  llena cada punta (ver R11).
- **R5** Último beat = BeatCta; **entre 3 y 7 beats** (`MAX_BEATS=7`, así El Salvador aprobado pasa); slug válido.
- **R6** Moneda explícita (USD/MXN visible) en la cifra protagonista.
- **R7** Cada cue existe LITERAL en el `vo` de su beat (heredada).
- **R8** Tipos válidos, ≥1 gráfica de datos, caricatura dentro del roster,
  máx 1 espectáculo, beat sin vo (heredadas de test_planner).
- **R9** (con ledger) tema NO repetido y combinación visual de beats NO repetida.
- **R10** (con ledger) **recencia del MEDIO**: ningún visual de FIRMA (los beats
  del medio) usado en los últimos `RECENCY_WINDOW` videos. R9 solo bloquea la
  repetición EXACTA del combo; R10 evita que tu visual favorito salga día tras día.
  A 3 videos/día esto es lo que mantiene fresco el medio (variedad en secuencia).
  Las puntas del arco (hook, clímax-cifra, CTA) NO cuentan para la recencia: las
  rota R11 aparte.
- **R11** (con ledger) **rotación de PUNTAS**: el hook, el clímax y el cierre deben
  DIFERIR del video ANTERIOR (ventana = 1). Hoy hook ∈ {Kinetic, StatCallout} y
  clímax ∈ {BigNumber, HeroCoin} → alternan video a video. El cierre tiene un solo
  tipo (BeatCta) → su slot se OMITE hasta que exista un 2º CTA: la regla se
  auto-activa sola cuando ese slot gana un 2º tipo. R10 cuida el MEDIO; R11 las
  PUNTAS. El proposer y el planner ya alternan las puntas solos (su loop de
  reintento absorbe R11, igual que R10).

Warnings (no rechazan salvo `--strict`):
- **W-num** una cifra mostrada no aparece en el brief (posible dato inventado).
- **W-cur** cifras secundarias sin moneda explícita.
- **W-round** un beat muestra una cifra exacta ≥ `ROUND_THRESHOLD` (1 millón) pero el `vo` NO la redondea. La narración debería decir "alrededor de cuarenta millones" mientras el visual mantiene la cifra exacta del brief (suena natural sin perder precisión). Palabras de redondeo que apagan el warning: `HEDGE_WORDS` (alrededor, aproximadamente, unos, casi, cerca, ronda…).

## Perillas (constantes en `validator.py`, arriba del archivo)

`SPEAKING_RATE_WPS=2.6`, `STATIC_MAX_S=2.5`, `LATE_FRAC=0.5`, `KINETIC_COVER=0.5`,
`MIN_BEATS=3`, `MAX_BEATS=7`, `RECENCY_WINDOW=3` (R10: cuántos videos atrás mira la
recencia; subir = más variedad, más presión al planner; 0 la desactiva),
`ROUND_THRESHOLD=1_000_000`, `HEDGE_WORDS`, los sets
`WOW`, `LANDING`, `SPECT`, `CHARTS`, `DATA_VISUAL`, y las PUNTAS del arco
`HOOK_TYPES` / `CLIMAX_TYPES` / `CTA_TYPES` (abrir un slot a un tipo nuevo lo suma
a la rotación R11; recuerda espejarlo en `SIGNATURE_EXCLUDE` de ledger.py).
La duración de cada beat se ESTIMA (palabras ÷ tasa de habla) porque el validador
no tiene la voz real; por eso R1 es la regla más heurística.

**Catálogo VIVO:** los tipos válidos NO están hardcodeados — `registered_beat_types()`
lee los `id="Beat..."` de `remotion-render/src/Root.tsx` en cada corrida (hoy ~39
beats). Cuando agregues un beat nuevo a Root.tsx, el validador lo acepta solo; si
quieres que cuente como gráfica/wow/dato, súmalo al set correspondiente arriba del
archivo (`CHARTS`/`WOW`/`DATA_VISUAL`).

## DECISIONES (2 resueltas, 1 pendiente)

1. ✅ **RESUELTO: hasta 7 beats.** `MAX_BEATS=7` (El Salvador v3 aprobado tiene 7,
   con `=6` fallaba R5). El planner prompt ahora dice "4 a 7 beats (ideal 5-6)".

3. ✅ **RESUELTO (lane B — rotación de puntas, hook + clímax).** R11 + `HOOK_TYPES`
   abierto a `BeatStatCallout` y `CLIMAX_TYPES` con `BeatHeroCoin` (ambos ya
   existían y están registrados en Root.tsx, **$0, sin componente nuevo, sin tocar
   la FORMA del arco R4**). El proposer y el planner alternan las puntas solos.
   **PENDIENTE: 2º CTA.** El cierre no rota porque solo existe `BeatCta`; rotarlo
   necesita un componente nuevo (arte = gate de Manuel). Cuando exista: agrégalo a
   `CTA_TYPES` (validator) **y** a `SIGNATURE_EXCLUDE` (ledger), y R11 se auto-activa
   para el cierre. Falta también el visto bueno visual de Manuel a StatCallout-como-hook
   y HeroCoin-como-clímax en un render real.

2. **R1 marcó el BeatBigNumber final de El Salvador como "estático".**
   No es un falso positivo: ese número aterriza al ~25% del beat y la voz sigue
   ~7s más sin que cambie nada — es justo lo que anotaste como
   "los últimos ~30s un poquito aburridos". El validador detecta lo mismo que
   tú a ojo. ¿Lo dejamos estricto (empuja a guiones más dinámicos) o lo suavizo?

## Gate humano + ledger (importante)

El workflow valida y bloquea guiones malos/repetidos ANTES de gastar voz/render,
pero **NO** registra en el ledger automáticamente. El registro es el gate humano:
tras revisar y aprobar el video, corres
`python infra\assembler\ledger.py append guion_X.json`.
Así el ledger solo guarda videos que TÚ aprobaste, y solo entonces empieza a
bloquear ese tema/combo en el futuro.

## Qué NO toqué

`build916.py`, `src/` de Remotion, los 6 guiones viejos, `out/`. El guion de
El Salvador solo se LEYÓ como ejemplo de esquema.
