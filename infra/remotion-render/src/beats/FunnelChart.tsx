import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { theme } from "../theme";
import { StudioScene } from "../studio/StudioScene";

// Embudo: etapas que se angostan de arriba hacia abajo, ancho proporcional al
// valor + % de retencion respecto al tope. Para conversion ("de cada 100 que
// empiezan, cuantos llegan") o filtrado. Color verde->oro: arriba verde (los
// muchos), abajo oro = los pocos valiosos que convirtieron (dinero/valor). SIN
// rojo: la caida la cuentan la FORMA del embudo y el %, no el color — el escalon
// de abajo suele ser la META, no una perdida (el rojo queda reservado a perdida
// real). Dos tiers discretos (no gradiente) para que cada etapa caiga exacto en
// un token de paleta; un blend verde->oro cruzaria amarillo-verde fuera de banda.
export type FunnelChartProps = {
  caption: string;
  stages: { label: string; value: number }[];
  prefix?: string;
  suffix?: string;
  asPercentOfTop?: boolean; // muestra % respecto al tope
};

const CX = 540;
const WMAX = 760;
const YTOP = 580;
const YBOT = 1480;
const ZONES = [theme.green, theme.gold];

export const FunnelChart: React.FC<FunnelChartProps> = ({
  caption,
  stages,
  prefix = "",
  suffix = "",
  asPercentOfTop = true,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const clamp = {
    extrapolateLeft: "clamp" as const,
    extrapolateRight: "clamp" as const,
  };

  const n = stages.length;
  const top = stages[0]?.value || 1;
  const wOf = (v: number) => Math.max(WMAX * (v / top), 120);
  const gap = 14;
  const stageH = (YBOT - YTOP - gap * (n - 1)) / n;

  const zoneColor = (i: number) => {
    const t = i / Math.max(n - 1, 1);
    return t < 0.5 ? ZONES[0] : ZONES[1];
  };

  const fmt = (v: number) =>
    prefix + Math.round(v).toLocaleString("en-US") + suffix;

  const pulse = 0.5 + 0.5 * Math.sin(frame / 12);
  const capWords = caption.split(" ");

  return (
    <StudioScene grid spotlightColor={ZONES[0]}>
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
          {stages.map((st, i) => {
            const yT = YTOP + i * (stageH + gap);
            const yB = yT + stageH;
            const wTopFull = wOf(st.value);
            const wBotFull = wOf(stages[i + 1]?.value ?? st.value);
            const color = zoneColor(i);
            const appear = spring({ frame: frame - (12 + i * 12), fps, config: { damping: 15, mass: 0.9 } });
            const a = Math.min(appear, 1);
            const wTop = wTopFull * a;
            const wBot = wBotFull * a;
            const isLast = i === n - 1;
            const pts = [
              [CX - wTop / 2, yT],
              [CX + wTop / 2, yT],
              [CX + wBot / 2, yB],
              [CX - wBot / 2, yB],
            ]
              .map((p) => p.join(","))
              .join(" ");
            return (
              <g key={i} opacity={a}>
                <polygon
                  points={pts}
                  fill={color}
                  opacity={0.9}
                  style={{
                    filter: isLast
                      ? `drop-shadow(0 0 ${12 + pulse * 12}px ${color}aa)`
                      : `drop-shadow(0 0 10px ${color}55)`,
                  }}
                />
                {/* valor dentro */}
                <text x={CX} y={(yT + yB) / 2 - 6} textAnchor="middle" fill="#0D1117" fontSize={44} fontWeight={900} style={{ fontFamily: theme.font, fontVariantNumeric: "tabular-nums" }}>
                  {fmt(st.value)}
                </text>
                {/* etiqueta + % */}
                <text x={CX} y={(yT + yB) / 2 + 34} textAnchor="middle" fill="#0D1117cc" fontSize={26} fontWeight={700} style={{ fontFamily: theme.font }}>
                  {st.label}
                  {asPercentOfTop && i > 0
                    ? `  ·  ${Math.round((st.value / top) * 100)}%`
                    : ""}
                </text>
              </g>
            );
          })}
        </svg>
      </AbsoluteFill>
    </StudioScene>
  );
};
