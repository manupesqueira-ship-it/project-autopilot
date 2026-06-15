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
import { BrandLogo } from "../studio/BrandLogo";

// Burbujas: area proporcional al valor (sqrt del valor -> radio). Para comparar
// magnitudes muy dispares (market caps, fortunas). Pop-in escalonado.
export type BubbleChartProps = {
  caption: string;
  bubbles: { label: string; value: number; color?: string; logo?: string }[];
  prefix?: string;
  suffix?: string;
  valueScale?: number; // divide el valor para mostrarlo (p.ej. 1e9 -> "B")
  valueUnit?: string;
};

// paleta CATEGORICA on-palette (Filtro A): verde/oro/teal/teal/ambar. SIN rojo
// (rojo = SOLO perdida, regla semantica locked) ni azul/morado (reprueban Filtro A).
const PALETTE = [theme.green, theme.gold, "#5BC0BE", "#1FA88B", "#E0A93C"];
// slots SEPARADOS para que las burbujas respiren (antes se amontonaban: con 5
// valores parecidos todas salian cerca de Rmax y se encimaban). Orden = mayor a
// menor; la mas grande toma el slot superior-central. Centros lo bastante
// distantes para que aun dos burbujas grandes dejen aire entre ellas.
const SLOTS: [number, number][] = [
  [540, 690],
  [280, 1030],
  [800, 1010],
  [400, 1360],
  [748, 1370],
];

export const BubbleChart: React.FC<BubbleChartProps> = ({
  caption,
  bubbles,
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

  // ordena de mayor a menor para que el mas grande tome el slot central
  const order = bubbles
    .map((b, i) => ({ b, i }))
    .sort((a, z) => z.b.value - a.b.value);
  const vMax = Math.max(...bubbles.map((b) => b.value)) || 1;
  const Rmax = 178;
  const Rmin = 70;

  const fmt = (v: number) => {
    const x = v / valueScale;
    const s = x.toLocaleString("en-US", { maximumFractionDigits: x < 10 ? 1 : 0 });
    return `${prefix}${s}${valueUnit}${suffix}`;
  };

  const capWords = caption.split(" ");

  return (
    <StudioScene grid={false} spotlightColor={bubbles[0]?.color ?? theme.green}>
      <AbsoluteFill style={{ fontFamily: theme.font }}>
        <div
          style={{
            position: "absolute",
            top: 230,
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

        {order.map((o, slot) => {
          const color = o.b.color ?? PALETTE[o.i % PALETTE.length];
          const r = Rmin + (Rmax - Rmin) * Math.sqrt(o.b.value / vMax);
          const [cx, cy] = SLOTS[slot] ?? [540, 940];
          const pop = spring({ frame: frame - (10 + slot * 9), fps, config: { damping: 13, mass: 0.8 } });
          const float = Math.sin((frame + slot * 20) / 22) * 8;
          const sc = 0.5 + Math.min(pop, 1) * 0.5;
          return (
            <div
              key={o.i}
              style={{
                position: "absolute",
                left: cx - r,
                top: cy - r + float,
                width: r * 2,
                height: r * 2,
                borderRadius: "50%",
                background: `radial-gradient(circle at 38% 32%, ${color}f2 0%, ${color}cc 55%, ${color}88 100%)`,
                boxShadow: `0 0 60px ${color}55, inset 0 6px 20px rgba(255,255,255,0.25), inset 0 -10px 30px rgba(0,0,0,0.25)`,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                opacity: Math.min(pop * 1.3, 1),
                transform: `scale(${sc})`,
              }}
            >
              {o.b.logo && (
                <div style={{ marginBottom: 6 }}>
                  <BrandLogo slug={o.b.logo} size={Math.max(r * 0.42, 40)} on="light" />
                </div>
              )}
              <div
                style={{
                  fontSize: Math.max(r * 0.2, 30),
                  fontWeight: 900,
                  color: "#0D1117",
                  letterSpacing: "-0.02em",
                  fontVariantNumeric: "tabular-nums",
                  lineHeight: 1,
                }}
              >
                {fmt(o.b.value)}
              </div>
              <div
                style={{
                  fontSize: Math.max(r * 0.12, 22),
                  fontWeight: 700,
                  color: "#0D1117cc",
                  marginTop: 4,
                  maxWidth: r * 1.7,
                  textAlign: "center",
                }}
              >
                {o.b.label}
              </div>
            </div>
          );
        })}
      </AbsoluteFill>
    </StudioScene>
  );
};
