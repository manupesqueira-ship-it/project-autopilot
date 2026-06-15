import React from "react";
import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
} from "remotion";
import { theme } from "../theme";
import { StudioScene } from "../studio/StudioScene";

// Area apilada en el tiempo: varias series se suman y se dibujan izq->der con un
// barrido. La serie resaltada late suave. Para "como crece la composicion de algo
// con el tiempo" (ingresos por linea, ahorro acumulado por fuente, etc).
export type StackedAreaChartProps = {
  caption: string;
  series: { label: string; values: number[]; color?: string }[];
  xLabels?: string[];
  highlightIndex?: number;
  prefix?: string;
  suffix?: string;
  valueScale?: number;
  valueUnit?: string;
};

const X0 = 120;
const X1 = 960;
const YTOP = 600;
const YBOT = 1430;
// paleta CATEGORICA on-palette (Filtro A): verde/oro/teal/teal/ambar. SIN rojo
// (rojo = SOLO perdida, regla semantica locked) ni azul/morado (reprueban Filtro A).
const PALETTE = [theme.green, theme.gold, "#5BC0BE", "#1FA88B", "#E0A93C"];

export const StackedAreaChart: React.FC<StackedAreaChartProps> = ({
  caption,
  series,
  xLabels = [],
  highlightIndex = 0,
  prefix = "$",
  suffix = "",
  valueScale = 1,
  valueUnit = "",
}) => {
  const frame = useCurrentFrame();
  const clamp = {
    extrapolateLeft: "clamp" as const,
    extrapolateRight: "clamp" as const,
  };

  const n = Math.max(...series.map((s) => s.values.length));
  const xOf = (i: number) => X0 + (X1 - X0) * (n > 1 ? i / (n - 1) : 0);

  // suma apilada por indice -> escala con el maximo total
  const totals = Array.from({ length: n }, (_, i) =>
    series.reduce((a, s) => a + (s.values[i] ?? 0), 0)
  );
  const vMax = Math.max(...totals) * 1.08 || 1;
  const yOf = (v: number) => YBOT - (YBOT - YTOP) * (v / vMax);

  // fronteras acumuladas (de abajo hacia arriba)
  const lowers: number[][] = [];
  const uppers: number[][] = [];
  let acc = Array(n).fill(0);
  series.forEach((s) => {
    const lo = acc.slice();
    acc = acc.map((a, i) => a + (s.values[i] ?? 0));
    lowers.push(lo);
    uppers.push(acc.slice());
  });

  const sweep = interpolate(frame, [10, 78], [0, 1], {
    ...clamp,
  });
  const clipW = (X1 - X0) * sweep;
  const scanX = X0 + clipW;
  const pulse = 0.5 + 0.5 * Math.sin(frame / 11);

  const fmtTotal = (v: number) => {
    const x = v / valueScale;
    return (
      prefix +
      x.toLocaleString("en-US", { maximumFractionDigits: x < 10 ? 1 : 0 }) +
      valueUnit +
      suffix
    );
  };

  const hi = highlightIndex;
  const lastTotal = totals[n - 1] ?? 0;
  const totalNow = interpolate(frame, [10, 78], [0, lastTotal], { ...clamp });

  const capWords = caption.split(" ");

  return (
    <StudioScene grid spotlightColor={series[hi]?.color ?? PALETTE[hi % PALETTE.length]}>
      <AbsoluteFill style={{ fontFamily: theme.font }}>
        <div
          style={{
            position: "absolute",
            top: 250,
            width: "100%",
            textAlign: "center",
            fontSize: 40,
            fontWeight: 500,
            color: theme.textDim,
          }}
        >
          {capWords.map((w, i) => (
            <span key={i} style={{ opacity: interpolate(frame, [2 + i * 3, 8 + i * 3], [0, 1], clamp) }}>
              {w}{" "}
            </span>
          ))}
        </div>

        <svg width="1080" height="1920" style={{ position: "absolute" }}>
          <defs>
            <clipPath id="sweepClip">
              <rect x={X0} y={YTOP - 40} width={clipW} height={YBOT - YTOP + 80} />
            </clipPath>
          </defs>
          {/* baseline */}
          <line x1={X0} y1={YBOT} x2={X1} y2={YBOT} stroke="#FFFFFF" strokeOpacity={0.12} strokeWidth={2} />

          <g clipPath="url(#sweepClip)">
            {series.map((s, si) => {
              const color = s.color ?? PALETTE[si % PALETTE.length];
              const lo = lowers[si];
              const up = uppers[si];
              const ptsUp = up.map((v, i) => `${xOf(i)},${yOf(v)}`).join(" ");
              const ptsLo = lo
                .map((v, i) => `${xOf(n - 1 - i)},${yOf(lo[n - 1 - i])}`)
                .join(" ");
              const isHi = si === hi;
              const fillOp = isHi ? 0.92 : 0.66;
              return (
                <polygon
                  key={si}
                  points={`${ptsUp} ${ptsLo}`}
                  fill={color}
                  opacity={fillOp}
                  style={{
                    filter: isHi
                      ? `drop-shadow(0 0 ${14 + pulse * 12}px ${color}aa)`
                      : "none",
                  }}
                />
              );
            })}
            {/* linea superior brillante de la serie resaltada */}
            <polyline
              points={uppers[hi].map((v, i) => `${xOf(i)},${yOf(v)}`).join(" ")}
              fill="none"
              stroke="#FFFFFF"
              strokeOpacity={0.5}
              strokeWidth={3}
            />
          </g>

          {/* scanline al frente del barrido */}
          {sweep < 0.999 && sweep > 0.001 && (
            <line
              x1={scanX}
              y1={YTOP - 30}
              x2={scanX}
              y2={YBOT}
              stroke="#FFFFFF"
              strokeOpacity={0.5}
              strokeWidth={3}
              style={{ filter: "drop-shadow(0 0 10px #FFFFFF)" }}
            />
          )}

          {/* etiquetas del eje x */}
          {xLabels.map((lbl, i) => (
            <text
              key={i}
              x={xOf(i)}
              y={YBOT + 44}
              textAnchor="middle"
              fill={theme.textDim}
              fontSize={26}
              fontWeight={600}
              opacity={interpolate(frame, [20 + i * 4, 30 + i * 4], [0, 1], clamp)}
              style={{ fontFamily: theme.font }}
            >
              {lbl}
            </text>
          ))}
        </svg>

        {/* leyenda + total acumulado */}
        <div
          style={{
            position: "absolute",
            top: YBOT + 90,
            width: "100%",
            display: "flex",
            justifyContent: "center",
            gap: 30,
            flexWrap: "wrap",
            padding: "0 80px",
            boxSizing: "border-box",
          }}
        >
          {series.map((s, si) => {
            const color = s.color ?? PALETTE[si % PALETTE.length];
            const isHi = si === hi;
            const o = interpolate(frame, [34 + si * 6, 44 + si * 6], [0, 1], clamp);
            return (
              <div key={si} style={{ display: "flex", alignItems: "center", gap: 12, opacity: o }}>
                <div style={{ width: 26, height: 26, borderRadius: 7, background: color }} />
                <div style={{ fontSize: 32, fontWeight: isHi ? 800 : 600, color: isHi ? theme.text : theme.textDim }}>
                  {s.label}
                </div>
              </div>
            );
          })}
        </div>

        {/* total grande (cifra exacta) que late suave */}
        <div
          style={{
            position: "absolute",
            top: YTOP - 150,
            width: "100%",
            textAlign: "center",
            transform: `translateY(${Math.sin(frame / 13) * 3}px)`,
          }}
        >
          <div
            style={{
              fontSize: 86,
              fontWeight: 900,
              color: theme.gold,
              letterSpacing: "-0.02em",
              fontVariantNumeric: "tabular-nums",
              lineHeight: 1,
              textShadow: `0 0 30px ${theme.gold}55`,
            }}
          >
            {fmtTotal(totalNow)}
          </div>
        </div>
      </AbsoluteFill>
    </StudioScene>
  );
};
