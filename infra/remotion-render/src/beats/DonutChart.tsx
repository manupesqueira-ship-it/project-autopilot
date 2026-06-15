import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { theme } from "../theme";
import { StudioScene } from "../studio/StudioScene";

// Dona de proporcion: los arcos barren en secuencia y el centro cuenta el % del
// segmento resaltado. Para "de cada peso, cuanto va a X" / composicion de algo.
export type DonutChartProps = {
  caption: string;
  segments: { label: string; value: number; color?: string }[];
  highlightIndex?: number;
  centerLabel?: string;
  // si no se da centerValue, el centro muestra el % del segmento resaltado
  centerValue?: number;
  centerPrefix?: string;
  centerSuffix?: string;
  centerDecimals?: number;
};

const CXc = 540;
const CYc = 820;
const R = 300;
const SW = 78;
// paleta CATEGORICA on-palette (Filtro A): verde/oro/teal/ambar/gris. SIN rojo
// (rojo = SOLO perdida, regla semantica locked) ni azul/morado (reprueban Filtro A).
// Para resaltar una PERDIDA, el caller pasa segment.color explicito (rojo semantico).
const PALETTE = [theme.green, theme.gold, "#5BC0BE", "#E0A93C", theme.textDim];

export const DonutChart: React.FC<DonutChartProps> = ({
  caption,
  segments,
  highlightIndex = 0,
  centerLabel,
  centerValue,
  centerPrefix = "",
  centerSuffix = "%",
  centerDecimals = 0,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const clamp = {
    extrapolateLeft: "clamp" as const,
    extrapolateRight: "clamp" as const,
  };

  const total = segments.reduce((a, s) => a + s.value, 0) || 1;
  // color REAL del segmento resaltado: si el segmento no trae color propio toma
  // el de PALETTE, igual que el arco. El centro debe matchear ese color (antes
  // caia a theme.green cuando el arco salia oro/azul de la PALETTE).
  const hiColor =
    segments[highlightIndex]?.color ??
    PALETTE[highlightIndex % PALETTE.length];
  const C = 2 * Math.PI * R;
  const sweep = interpolate(frame, [8, 70], [0, 1], {
    ...clamp,
    easing: Easing.bezier(0.3, 0.1, 0.3, 1),
  });

  const hiPct = (segments[highlightIndex]?.value / total) * 100;
  const shown =
    centerValue != null
      ? interpolate(frame, [8, 70], [0, centerValue], { ...clamp })
      : interpolate(frame, [8, 70], [0, hiPct], { ...clamp });
  const fmt = (v: number) =>
    v.toLocaleString("en-US", {
      minimumFractionDigits: centerDecimals,
      maximumFractionDigits: centerDecimals,
    });

  let accFrac = 0;
  const arcs = segments.map((s, i) => {
    const frac = s.value / total;
    const start = accFrac;
    accFrac += frac;
    const color = s.color ?? PALETTE[i % PALETTE.length];
    // longitud visible: cada arco se revela cuando el barrido pasa por el
    const visEnd = Math.min(sweep, accFrac);
    const visLen = Math.max(visEnd - start, 0) * C;
    const isHi = i === highlightIndex;
    return { s, color, start, frac, visLen, isHi };
  });

  const capWords = caption.split(" ");
  const centerPop = spring({ frame: frame - 60, fps, config: { damping: 13, mass: 0.7 } });

  return (
    <StudioScene grid spotlightColor={hiColor}>
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
          {/* riel de fondo */}
          <circle
            cx={CXc}
            cy={CYc}
            r={R}
            fill="none"
            stroke="#FFFFFF"
            strokeOpacity={0.06}
            strokeWidth={SW}
          />
          {arcs.map((a, i) => (
            <circle
              key={i}
              cx={CXc}
              cy={CYc}
              r={R}
              fill="none"
              stroke={a.color}
              strokeWidth={a.isHi ? SW + 12 : SW}
              strokeLinecap="butt"
              strokeDasharray={`${a.visLen} ${C}`}
              strokeDashoffset={-a.start * C}
              transform={`rotate(-90 ${CXc} ${CYc})`}
              style={{
                filter: a.isHi ? `drop-shadow(0 0 18px ${a.color})` : "none",
                opacity: a.isHi ? 1 : 0.92,
              }}
            />
          ))}
        </svg>

        {/* centro: % o valor */}
        <div
          style={{
            position: "absolute",
            left: CXc - 230,
            top: CYc - 110,
            width: 460,
            textAlign: "center",
          }}
        >
          <div
            style={{
              fontSize: 132,
              fontWeight: 900,
              color: hiColor,
              letterSpacing: "-0.03em",
              fontVariantNumeric: "tabular-nums",
              lineHeight: 1,
              textShadow: `0 0 38px ${hiColor}66`,
              transform: `scale(${0.9 + Math.min(centerPop, 1) * 0.1})`,
            }}
          >
            {centerPrefix}
            {fmt(shown)}
            {centerSuffix}
          </div>
          {centerLabel && (
            <div style={{ fontSize: 34, fontWeight: 600, color: theme.textDim, marginTop: 6 }}>
              {centerLabel}
            </div>
          )}
        </div>

        {/* leyenda */}
        <div
          style={{
            position: "absolute",
            top: CYc + R + 110,
            width: "100%",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 22,
          }}
        >
          {arcs.map((a, i) => {
            const o = interpolate(frame, [30 + i * 6, 40 + i * 6], [0, 1], clamp);
            return (
              <div
                key={i}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 20,
                  opacity: o,
                  transform: `translateX(${(1 - o) * -20}px)`,
                }}
              >
                <div style={{ width: 30, height: 30, borderRadius: 8, background: a.color }} />
                <div style={{ fontSize: 38, fontWeight: a.isHi ? 800 : 600, color: a.isHi ? theme.text : theme.textDim }}>
                  {a.s.label}
                </div>
                <div style={{ fontSize: 38, fontWeight: 800, color: a.color, fontVariantNumeric: "tabular-nums" }}>
                  {Math.round((a.s.value / total) * 100)}%
                </div>
              </div>
            );
          })}
        </div>
      </AbsoluteFill>
    </StudioScene>
  );
};
