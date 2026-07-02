import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";

// EditorialHouseMotion — versión ANIMADA del estilo de la casa (aprobado 2026-07-01).
// Movimiento editorial: revelado calmado y escalonado, la gráfica que se dibuja, las
// cifras que cuentan. Nada flashy. El ÚLTIMO frame == el still aprobado (editorial_premium).

const INK = "#1B1712";
const PAPER = "#F1ECE1";
const ACCENT = "#9E2B22";
const MUTE = "#7A7264";
const HAIR = "#CDC4B2";
const FONT = "InterVar, Inter, Georgia, serif";
const M = 96;

const fmt = (v: number) => "$" + Math.round(v).toLocaleString("en-US");

// rise + fade escalonado (editorial = sin rebote, calmado)
const reveal = (frame: number, start: number, dist = 22, dur = 14): React.CSSProperties => {
  const o = interpolate(frame, [start, start + dur], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const y = interpolate(frame, [start, start + dur], [dist, 0], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic),
  });
  return { opacity: o, transform: `translateY(${y}px)` };
};

const Rule: React.FC<{ y: number; frame: number; start: number; color?: string; h?: number }> = ({
  y, frame, start, color = HAIR, h = 1,
}) => {
  const w = interpolate(frame, [start, start + 18], [0, 1080 - 2 * M], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic),
  });
  return <div style={{ position: "absolute", top: y, left: M, width: w, height: h, background: color }} />;
};

export const EditorialHouseMotion: React.FC = () => {
  const frame = useCurrentFrame();

  const nominal = interpolate(frame, [26, 54], [0, 100000], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  const real = interpolate(frame, [80, 116], [100000, 96209], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.bezier(0.4, 0, 0.2, 1) });

  const dash = 900;
  const draw = interpolate(frame, [60, 100], [dash, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  const dotO = interpolate(frame, [96, 104], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ backgroundColor: PAPER, fontFamily: FONT, color: INK }}>
      <div style={{ position: "absolute", top: 78, left: M, fontSize: 27, fontWeight: 700, letterSpacing: "0.28em", ...reveal(frame, 0) }}>
        DINERO&nbsp;IA
      </div>
      <div style={{ position: "absolute", top: 82, right: M, fontSize: 22, fontWeight: 500, letterSpacing: "0.22em", color: MUTE, ...reveal(frame, 2) }}>
        INFORME · 2026
      </div>
      <Rule y={130} frame={frame} start={6} color={INK} h={2} />

      <div style={{ position: "absolute", top: 196, left: M, fontSize: 30, fontWeight: 700, letterSpacing: "0.2em", color: ACCENT, ...reveal(frame, 14) }}>
        EL COSTO DE NO MOVER TU DINERO
      </div>

      <div style={{ position: "absolute", top: 330, left: M, fontSize: 33, fontWeight: 500, color: MUTE, ...reveal(frame, 22) }}>
        Dejas en efectivo
      </div>
      <div style={{ position: "absolute", top: 372, left: M - 4, fontSize: 200, fontWeight: 800, letterSpacing: "-0.035em", lineHeight: 1, ...reveal(frame, 26, 26) }}>
        {fmt(nominal)}
      </div>

      <svg width={1080 - 2 * M} height={120} viewBox={`0 0 ${1080 - 2 * M} 120`} style={{ position: "absolute", top: 636, left: M }}>
        <path d="M 0 24 L 300 40 L 560 66 L 888 98" fill="none" stroke={INK} strokeWidth="2" opacity="0.55"
          strokeDasharray={dash} strokeDashoffset={draw} />
        <circle cx="888" cy="98" r="7" fill={ACCENT} opacity={dotO} />
      </svg>

      <div style={{ position: "absolute", top: 800, left: M, fontSize: 33, fontWeight: 500, color: MUTE, ...reveal(frame, 72) }}>
        Un año después, en poder de compra
      </div>
      <div style={{ position: "absolute", top: 842, left: M - 4, fontSize: 200, fontWeight: 800, letterSpacing: "-0.035em", lineHeight: 1, color: ACCENT, ...reveal(frame, 78, 26) }}>
        {fmt(real)}
      </div>

      <Rule y={1130} frame={frame} start={116} color={INK} h={2} />

      <div style={{ position: "absolute", top: 1180, left: M, right: M, display: "flex", alignItems: "baseline", gap: 22, ...reveal(frame, 122) }}>
        <span style={{ fontSize: 92, fontWeight: 800, letterSpacing: "-0.03em", color: ACCENT }}>−$3,791</span>
        <span style={{ fontSize: 40, fontWeight: 500, color: INK }}>se los comió la inflación</span>
      </div>
      <div style={{ position: "absolute", top: 1320, left: M, right: M, fontSize: 34, fontWeight: 400, lineHeight: 1.4, color: "#4A443B", maxWidth: 820, ...reveal(frame, 130) }}>
        El efectivo no baja de número — baja de <span style={{ fontWeight: 700, color: INK }}>valor</span>.
        Lo que hoy compra $100,000, en un año lo compras con $96,209.
      </div>

      <div style={{ position: "absolute", top: 1820, left: M, fontSize: 25, fontWeight: 500, letterSpacing: "0.04em", color: MUTE, ...reveal(frame, 138) }}>
        Fuente: INEGI — Inflación anual 3.94% (corte 2026)
      </div>
      <div style={{ position: "absolute", top: 1820, right: M, fontSize: 25, fontWeight: 700, letterSpacing: "0.18em", color: INK, ...reveal(frame, 140) }}>
        01
      </div>

      <AbsoluteFill style={{ opacity: 0.05, mixBlendMode: "multiply", pointerEvents: "none" }}>
        <svg width="1080" height="1920">
          <filter id="paperm"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" stitchTiles="stitch" /></filter>
          <rect width="1080" height="1920" filter="url(#paperm)" />
        </svg>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
