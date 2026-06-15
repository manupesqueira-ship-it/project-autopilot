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

export type BigNumberProps = {
  caption: string;
  prefix?: string;
  value: number;
  suffix?: string;
  decimals?: number;
  color?: string;
  subline?: string;
  // inyectados por el ensamblador desde los timestamps de la voz
  countStartFrame?: number;
  countEndFrame?: number;
};

const fmt = (v: number, decimals: number) =>
  v.toLocaleString("en-US", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });

// faux-3D: pila de sombras hacia abajo = grosor del dígito (profundidad sin Blender).
// Real Blender sería el siguiente escalón; esto da el volumen $0/rápido.
const extrude = (depth = 7) =>
  Array.from({ length: depth }, (_, i) => {
    const t = i / depth;
    return `0 ${i + 1}px 0 rgba(0,0,0,${(0.3 * (1 - t)).toFixed(3)})`;
  }).join(", ");

export const BigNumberCounter: React.FC<BigNumberProps> = ({
  caption,
  prefix = "",
  value,
  suffix = "",
  decimals = 0,
  color = theme.gold,
  subline,
  countStartFrame = 10,
  countEndFrame = 70,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // count-up con desaceleración · settle con micro-overshoot
  const shown = interpolate(frame, [countStartFrame, countEndFrame], [0, value], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.2, 0.6, 0.35, 1),
  });
  const settle = spring({
    frame: frame - (countEndFrame - 6),
    fps,
    config: { damping: 12, mass: 0.7 },
  });
  const scale = 0.96 + settle * 0.04;
  const done = frame >= countEndFrame;
  const glowPulse = done ? 0.8 + Math.sin(frame / 9) * 0.2 : 1;

  const numTxt = `${prefix}${fmt(shown, decimals)}`;
  const numNode = (
    <>
      {numTxt}
      {suffix && (
        <span style={{ fontSize: "0.5em", fontWeight: 800, marginLeft: 8 }}>
          {suffix}
        </span>
      )}
    </>
  );

  // ---- sub-eventos TARDÍOS: matan los ~6s estáticos del clímax ----
  // el subline ("+77% ... · 7,474 BTC ...") se parte en chips que entran tarde, y
  // una BARRA de ganancia crece de forma CONTINUA por toda la cola (Decisión 2 del
  // validador: el clímax deja de ser estático sin apagar la regla).
  const parts = (subline ?? "").split("·").map((s) => s.trim()).filter(Boolean);
  const pctMatch = (subline ?? "").match(/([+-]?\d+(?:\.\d+)?)\s*%/);
  const pct = pctMatch ? Math.abs(parseFloat(pctMatch[1])) : null;
  const gain = !pctMatch || !pctMatch[1].startsWith("-");
  const accent = gain ? color : theme.red;

  const chip0 = countEndFrame + 22;
  const chip1 = countEndFrame + 60;
  const barA = countEndFrame + 14;
  const barB = durationInFrames - 14;
  const barW = interpolate(frame, [barA, barB], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.3, 0.18, 0.5, 0.95),
  });

  const capWords = caption.split(" ");

  const rise = (start: number): React.CSSProperties => {
    const s = spring({ frame: frame - start, fps, config: { damping: 14, mass: 0.6 } });
    return {
      opacity: interpolate(frame, [start, start + 6], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      }),
      transform: `translateY(${(1 - s) * 16}px)`,
    };
  };

  const numStyle: React.CSSProperties = {
    fontSize: 128,
    fontWeight: 900,
    color,
    letterSpacing: "-0.02em",
    fontVariantNumeric: "tabular-nums",
    // nowrap: el suffix (" USD") se quedaba en 2a linea bajo el numero ancho y
    // chocaba con la barra/chips. Una sola linea = $209,000,000 USD limpio.
    whiteSpace: "nowrap",
  };

  return (
    <StudioScene spotlightColor={color}>
      <AbsoluteFill style={{ fontFamily: theme.font }}>
        {/* caption */}
        <div
          style={{
            position: "absolute",
            top: 580,
            width: "100%",
            textAlign: "center",
            fontSize: 44,
            fontWeight: 500,
            color: theme.textDim,
          }}
        >
          {capWords.map((w, i) => {
            const o = interpolate(frame, [2 + i * 3, 8 + i * 3], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            });
            return (
              <span key={i} style={{ opacity: o }}>
                {w}{" "}
              </span>
            );
          })}
        </div>

        {/* número 3D (extrude + glow) + reflejo en el piso = profundidad */}
        <div
          style={{
            position: "absolute",
            top: 700,
            width: "100%",
            textAlign: "center",
            opacity: interpolate(frame, [8, 14], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
          }}
        >
          <div
            style={{
              ...numStyle,
              textShadow: `${extrude()}, 0 0 ${50 * glowPulse}px ${color}99, 0 0 ${120 * glowPulse}px ${color}44`,
              transform: `scale(${scale})`,
            }}
          >
            {numNode}
          </div>
          {/* reflejo (piso reflectante), tenue + difuminado */}
          <div
            aria-hidden
            style={{
              ...numStyle,
              transform: "scaleY(-1)",
              transformOrigin: "top",
              marginTop: 4,
              opacity: 0.16,
              filter: "blur(1px)",
              WebkitMaskImage:
                "linear-gradient(to bottom, rgba(0,0,0,0.6) 0%, transparent 45%)",
              maskImage:
                "linear-gradient(to bottom, rgba(0,0,0,0.6) 0%, transparent 45%)",
            }}
          >
            {numNode}
          </div>
        </div>

        {/* barra de ganancia: crece CONTINUO por la cola (mata el estático) */}
        {pct !== null && (
          <div
            style={{
              position: "absolute",
              top: 1015,
              left: "50%",
              transform: "translateX(-50%)",
              width: 520,
              ...rise(barA),
            }}
          >
            <div
              style={{
                height: 10,
                borderRadius: 6,
                background: "rgba(255,255,255,0.08)",
                overflow: "hidden",
              }}
            >
              <div
                style={{
                  height: "100%",
                  width: `${barW * 100}%`,
                  borderRadius: 6,
                  background: accent,
                  boxShadow: `0 0 18px ${accent}88`,
                }}
              />
            </div>
          </div>
        )}

        {/* chip 0: "+77% sobre lo invertido" con flecha — entra tarde */}
        {parts[0] && (
          <div
            style={{
              position: "absolute",
              top: 1058,
              width: "100%",
              textAlign: "center",
              fontSize: 40,
              fontWeight: 700,
              color: accent,
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              gap: 10,
              ...rise(chip0),
            }}
          >
            <svg
              width="26"
              height="26"
              viewBox="0 0 24 24"
              style={{ transform: gain ? "none" : "rotate(180deg)" }}
            >
              <path d="M12 4 L20 16 L12 12 L4 16 Z" fill={accent} />
            </svg>
            <span>{parts[0]}</span>
          </div>
        )}

        {/* chip 1: "7,474 BTC en reserva" — entra aún más tarde */}
        {parts[1] && (
          <div
            style={{
              position: "absolute",
              top: 1124,
              width: "100%",
              textAlign: "center",
              fontSize: 36,
              fontWeight: 600,
              color: theme.text,
              ...rise(chip1),
            }}
          >
            {parts[1]}
          </div>
        )}
      </AbsoluteFill>
    </StudioScene>
  );
};
