# Handoff — Expansión del catálogo de charts (Dinero IA)

Beats nuevos + 2 tweaks. Todo $0, sin herramientas nuevas. Cada beat hereda
`theme` + `StudioScene`, color semántico (verde=sube/seguro, rojo=pérdida,
dorado=dinero), SIN título textual encima del gráfico, micro-motion continuo,
safe-areas libres (top 11% / bottom 17%). Datos 100% por props.

Verificación: still por beat desde `infra/remotion-render`:
`npx.cmd remotion still <BeatId> ../assembler/out/_stills/<x>.png --frame=N --log=error`

---

## Tweaks a beats existentes

### BubbleChart.tsx
- Burbujas menos amontonadas: slots reposicionados (`SLOTS`) y radios reducidos
  (`Rmax=178`, `Rmin=70`).
- Logos vía `BrandLogo on="light"` (las burbujas son discos claros).
- **Nota logos:** `microsoft` y `amazon` ya NO existen como slugs en
  simple-icons (verificado por node) → caen a monograma automáticamente. No se
  persiguió: se dejaron como monograma (no se tocó `studio/BrandLogo.tsx` para
  no salirme del lane ni chocar con otro Claude). `apple`, `nvidia`, `google`
  sí resuelven.

### DonutChart.tsx
- El % central usaba `theme.green` aunque el segmento resaltado fuera dorado.
  Ahora se calcula `hiColor` (color del segmento resaltado) y se pasa al número
  central, al `spotlightColor` y al `textShadow` → centro y arco coinciden.

---

## Beats nuevos

### Batch 2

**BeatStackedArea** — `StackedAreaChart.tsx`
Áreas apiladas en el tiempo, revelado por barrido (clipPath), serie resaltada late.
Props: `caption`, `series:{label,values[],color?}[]`, `xLabels?`,
`highlightIndex?`, `prefix`, `suffix`, `valueScale`, `valueUnit`.
Total grande siempre en dorado (es total de dinero).

**BeatDialGauge** — `DialGauge.tsx`
Gauge semicircular, aguja con spring + micro-bobeo, número central cuenta.
Zonas rojo→dorado→verde. Props: `caption`, `value`, `min`, `max`, `label`,
`prefix`, `suffix`, `decimals`, `goodHigh`, `tone`.

**BeatSlope** — `SlopeChart.tsx`
Pendiente de 2 puntos (antes→después), líneas dibujan izq→der, sube=verde /
baja=rojo (o color explícito). Props: `caption`, `leftLabel`, `rightLabel`,
`items:{label,left,right,color?}[]`, `prefix`, `suffix`, `decimals`.

**BeatProgressRing** — `ProgressRing.tsx`
Un solo anillo de progreso (distinto del Donut), arco barre en sentido horario
desde arriba, punto líder con brillo, % central cuenta. Props: `caption`,
`percent`, `label`, `color`, `centerSuffix`, `centerDecimals`.

### Batch 3

**BeatLollipop** — `LollipopChart.tsx`
Lollipop horizontal; si los items traen `value2` se vuelve dumbbell (brecha
entre 2 grupos). Props: `caption`, `items:{label,value,value2?,color?}[]`,
`prefix`, `suffix`, `max?`, `highlightIndex?`, `legend1?`, `legend2?`.
Dumbbell: C1=dorado (grupo1), C2=verde (grupo2); valores siempre a los extremos.

**BeatFunnel** — `FunnelChart.tsx`
Trapecios que se angostan arriba→abajo, color verde→dorado→rojo por etapa,
% respecto al tope. Props: `caption`, `stages:{label,value}[]`, `prefix`,
`suffix`, `asPercentOfTop`.

**BeatHistogram** — `Histogram.tsx`
Barras de distribución adyacentes con marcador vertical opcional ("tú estás
aquí"). Props: `caption`, `bins:number[]`, `xLabels?`, `markerIndex?`,
`markerLabel?`, `color`. Barras no marcadas atenuadas.

**BeatScaledIcon** — `ScaledIcon.tsx`
Discos/símbolos escalados (área ∝ valor, vía sqrt), alineados a baseline;
muestra ×N cuando hay exactamente 2 items. Props: `caption`,
`items:{label,value,color?}[]`, `symbol`, `prefix`, `suffix`, `valueScale`,
`valueUnit`.

### Batch 4

**BeatHeatmap** — `Heatmap.tsx`
Rejilla de celdas por intensidad; diverging (rojo↔verde alrededor de 0) o
sequential. Celda más extrema resaltada + late. Props: `caption`,
`rows:{label,values[]}[]`, `colLabels?`, `diverging`, `suffix`, `prefix`,
`decimals`. Helper `mix(a,b,t)` (lerp hex).

**BeatTickerTape** — `TickerTape.tsx`
Cinta de precios: 3 filas con velocidades/direcciones distintas, scroll continuo
con wrap modular (el scroll ES el micro-motion). Verde sube / rojo baja, chips
con `BrandLogo`. Fades laterales. Props: `caption`,
`items:{symbol,price,changePct,logo?}[]`, `prefix`, `decimals`, `speed`.

**BeatTreemap** — `Treemap.tsx`
Rectángulos con área ∝ valor (slice-and-dice recursivo, alternando eje, sin
librería). El mayor se resalta + late. Props: `caption`,
`items:{label,value,color?}[]`, `prefix`, `suffix`, `valueScale`, `valueUnit`,
`asPercent`.

**BeatRadar** — `RadarChart.tsx`
Spider/radar con anillos, radios y 1-2 polígonos que crecen desde el centro,
vértices laten, leyenda. Props: `caption`, `axes:string[]`,
`series:{label,values[],color?}[]`, `max?`.

**BeatScoreboard** — `Scoreboard.tsx`
Tarjetas KPI en rejilla; cada una cuenta hacia arriba + delta (verde/rojo por
signo) y glow que late. Props: `caption`,
`cards:{label,value,deltaPct?,prefix?,suffix?,decimals?,color?}[]`.

**BeatSankey** — `SankeyFlow.tsx`
Sankey simple (1 fuente → N destinos): barra origen a la izquierda se reparte
en cintas con grosor ∝ valor hacia nodos a la derecha; shimmer que fluye.
Props: `caption`, `source:{label,value?}`,
`targets:{label,value,color?}[]`, `prefix`, `suffix`, `valueScale`,
`valueUnit`, `asPercent`.

---

## Registro en Root.tsx
Todos registrados de forma ADITIVA (import + `withSeams` + `<Composition>` con
id único y `defaultProps`), antes de `BeatCta`. No se tocó ningún archivo del
DO-NOT-TOUCH (build916, StudioScene, SeamFx, theme, n8n, guiones, out/).

## Gotcha encontrado
esbuild en este repo NO permite `a ?? b || c` sin paréntesis. Patrón correcto:
`max ?? (Math.max(...) || 1)`. Apareció en LollipopChart y RadarChart.
