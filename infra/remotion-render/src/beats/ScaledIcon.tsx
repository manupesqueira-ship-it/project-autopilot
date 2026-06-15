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

// Iconos escalados: discos de un mismo simbolo (p.ej. $) cuyo TAMANO codifica la
// magnitud (area ~ valor), alineados a una base comun para comparar de un vistazo.
// Si son exactamente 2 items, muestra el multiplicador ("×8") en medio. Para
// "una casa cuesta 8 veces tu sueldo anual" / comparaciones de escala.
export type ScaledIconProps = {
  caption: string;
  items: { label: string; value: number; color?: string }[];
  symbol?: string;
  prefix?: string;
  suffix?: string;
  valueScale?: number;
  valueUnit?: string;
};

const BASE_Y = 1340; // base comun de los discos
const RMAX = 250;
const RMIN = 70;
// paleta CATEGORICA on-palette (Filtro A): oro/verde/teal/ambar. SIN rojo
// (rojo = SOLO perdida, regla semantica locked) ni azul/morado (reprueban Filtro A).
const PALETTE = [theme.gold, theme.green, "#5BC0BE", "#E0A93C"];

export const ScaledIcon: React.FC<ScaledIconProps> = ({
  caption,
  items,
  symbol = "$",
  prefix = "$",
  suffix = "",
  valueScale = 1,
  valueUnit = "",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const clamp = {
    extrapolateLeft: "clamp" as const,
    extrapolateRight: "clamp" as const,
  };

  const vMax = Math.max(...items.map((it) => it.value)) || 1;
  const rOf = (v: number) => RMIN + (RMAX - RMIN) * Math.sqrt(v / vMax);

  const n = items.length;
  const colW = 1080 / n;
  const fmt = (v: number) => {
    const x = v / valueScale;
    return (
      prefix +
      x.toLocaleString("en-US", { maximumFractionDigits: x < 10 ? 1 : 0 }) +
      valueUnit +
      suffix
    );
  };

  const pulse = 0.5 + 0.5 * Math.sin(frame / 12);
  const ratio = n === 2 ? items[1].value / (items[0].value || 1) : 0;
  const ratioShow = ratio >= 1 ? ratio : 1 / ratio;
  const ratioReveal = spring({ frame: frame - 60, fps, config: { damping: 13, mass: 0.7 } });

  const capWords = caption.split(" ");

  return (
    <StudioScene grid={false} spotlightColor={items[0]?.color ?? theme.gold}>
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

        {items.map((it, i) => {
          const color = it.color ?? PALETTE[i % PALETTE.length];
          const r = rOf(it.value);
          const cx = colW * (i + 0.5);
          const cy = BASE_Y - r;
          const pop = spring({ frame: frame - (12 + i * 12), fps, config: { damping: 14, mass: 0.9 } });
          const sc = 0.4 + Math.min(pop, 1) * 0.6;
          const float = Math.sin((frame + i * 18) / 20) * 6;
          const shown = interpolate(frame, [12 + i * 12, 60 + i * 12], [0, it.value], { ...clamp });
          return (
            <React.Fragment key={i}>
              <div
                style={{
                  position: "absolute",
                  left: cx - r,
                  top: cy - r + float,
                  width: r * 2,
                  height: r * 2,
                  borderRadius: "50%",
                  background: `radial-gradient(circle at 38% 32%, ${color}f2 0%, ${color}cc 55%, ${color}88 100%)`,
                  boxShadow: `0 0 ${50 + pulse * 20}px ${color}55, inset 0 6px 20px rgba(255,255,255,0.25), inset 0 -10px 30px rgba(0,0,0,0.25)`,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  opacity: Math.min(pop * 1.3, 1),
                  transform: `scale(${sc})`,
                }}
              >
                <span style={{ fontSize: r * 0.95, fontWeight: 900, color: "#0D1117", lineHeight: 1 }}>
                  {symbol}
                </span>
              </div>
              {/* valor + etiqueta debajo de la base */}
              <div
                style={{
                  position: "absolute",
                  left: cx - colW / 2,
                  top: BASE_Y + 40,
                  width: colW,
                  textAlign: "center",
                  opacity: Math.min(pop, 1),
                }}
              >
                <div style={{ fontSize: 56, fontWeight: 900, color, fontVariantNumeric: "tabular-nums", textShadow: `0 0 22px ${color}55` }}>
                  {fmt(shown)}
                </div>
                <div style={{ fontSize: 32, fontWeight: 600, color: theme.textDim, marginTop: 6 }}>
                  {it.label}
                </div>
              </div>
            </React.Fragment>
          );
        })}

        {/* base comun */}
        <div style={{ position: "absolute", left: 80, top: BASE_Y, width: 920, height: 2, background: "rgba(255,255,255,0.12)" }} />

        {/* multiplicador para comparacion de 2 */}
        {n === 2 && (
          <div
            style={{
              position: "absolute",
              left: 540 - 120,
              top: BASE_Y - 460,
              width: 240,
              textAlign: "center",
              opacity: Math.min(ratioReveal, 1),
              transform: `scale(${0.7 + Math.min(ratioReveal, 1) * 0.3})`,
            }}
          >
            <div
              style={{
                fontSize: 96,
                fontWeight: 900,
                color: theme.text,
                letterSpacing: "-0.02em",
                textShadow: "0 0 30px rgba(255,255,255,0.3)",
              }}
            >
              ×{ratioShow.toFixed(ratioShow < 10 ? 1 : 0)}
            </div>
          </div>
        )}
      </AbsoluteFill>
    </StudioScene>
  );
};
