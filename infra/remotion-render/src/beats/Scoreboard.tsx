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

// Scoreboard: tarjetas KPI en rejilla, cada una con un numero que cuenta hacia
// arriba + delta (verde=mejora / rojo=empeora, SEMANTICO) y un brillo que late.
// Para "resumen de cifras clave" (ingresos, usuarios, margen...). El conteo +
// glow ES el motion.
export type ScoreboardProps = {
  caption: string;
  cards: {
    label: string;
    value: number;
    deltaPct?: number;
    prefix?: string;
    suffix?: string;
    decimals?: number;
    color?: string;
    // direccion "buena" del KPI. Default true (subir=bueno: ingresos, ahorro).
    // Gastos => false: subir es MALO, asi el delta no se pinta verde al subir.
    higherIsBetter?: boolean;
  }[];
};

const X0 = 90;
const W = 900;
const YTOP = 580;

export const Scoreboard: React.FC<ScoreboardProps> = ({ caption, cards }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const clamp = {
    extrapolateLeft: "clamp" as const,
    extrapolateRight: "clamp" as const,
  };

  const n = cards.length;
  const cols = n <= 2 ? 1 : 2;
  const rows = Math.ceil(n / cols);
  const GAP = 36;
  const cardW = (W - GAP * (cols - 1)) / cols;
  const cardH = Math.min((1430 - YTOP - GAP * (rows - 1)) / rows, 360);

  const pulse = 0.5 + 0.5 * Math.sin(frame / 11);
  const capWords = caption.split(" ");

  const fmt = (v: number, c: ScoreboardProps["cards"][number]) =>
    (c.prefix ?? "") +
    v.toLocaleString("en-US", {
      minimumFractionDigits: c.decimals ?? 0,
      maximumFractionDigits: c.decimals ?? 0,
    }) +
    (c.suffix ?? "");

  return (
    <StudioScene grid spotlightColor={cards[0]?.color ?? theme.green}>
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

        {cards.map((c, i) => {
          const col = i % cols;
          const row = Math.floor(i / cols);
          const left = X0 + col * (cardW + GAP);
          const top = YTOP + row * (cardH + GAP);
          const color = c.color ?? theme.green;

          const appear = spring({ frame: frame - (10 + i * 7), fps, config: { damping: 15, mass: 0.8 } });
          const a = Math.min(appear, 1);
          // conteo hacia arriba
          const countT = interpolate(frame, [12 + i * 7, 40 + i * 7], [0, 1], clamp);
          const shown = c.value * (0.3 + 0.7 * Math.min(countT, 1)) * 0 + c.value * Math.min(countT, 1);
          const up = (c.deltaPct ?? 0) >= 0;
          // color SEMANTICO, no por signo: bueno si la direccion coincide con la
          // "buena" del KPI (higherIsBetter). Gastos al alza => malo => rojo.
          const good = up === (c.higherIsBetter ?? true);
          const dc = good ? theme.green : theme.red;

          return (
            <div
              key={i}
              style={{
                position: "absolute",
                left,
                top,
                width: cardW,
                height: cardH,
                borderRadius: 26,
                background: "rgba(255,255,255,0.04)",
                border: `1px solid ${color}55`,
                boxShadow: `0 0 ${16 + pulse * 16}px ${color}3a, inset 0 1px 0 rgba(255,255,255,0.06)`,
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
                padding: "0 40px",
                boxSizing: "border-box",
                opacity: a,
                transform: `translateY(${(1 - a) * 24}px)`,
              }}
            >
              <div style={{ fontSize: 30, fontWeight: 600, color: theme.textDim, marginBottom: 10 }}>
                {c.label}
              </div>
              <div style={{ display: "flex", alignItems: "baseline", gap: 18 }}>
                <div style={{ fontSize: 78, fontWeight: 900, color, lineHeight: 1, fontVariantNumeric: "tabular-nums" }}>
                  {fmt(shown, c)}
                </div>
                {c.deltaPct != null && (
                  <div style={{ fontSize: 32, fontWeight: 800, color: dc, fontVariantNumeric: "tabular-nums", opacity: Math.min(countT * 1.5, 1) }}>
                    {up ? "▲" : "▼"} {up ? "+" : "−"}{Math.abs(c.deltaPct).toFixed(1)}%
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </AbsoluteFill>
    </StudioScene>
  );
};
