import React from "react";
import { AbsoluteFill } from "remotion";

// EditorialHouse — ESTILO DE LA CASA (elegido por Manuel 2026-07-01: "Editorial").
// Refina el boceto StyleProbe a premium: grid consistente, hairlines, jerarquía
// tipográfica, mini-gráfico minimal, línea de fuente (credibilidad editorial),
// textura de papel. Fondo hueso, tinta casi-negra + UN acento oxblood. Legible,
// serio, atemporal — diferenciado de todo lo viral genérico. Datos exactos reel C.

const INK = "#1B1712";
const PAPER = "#F1ECE1";
const ACCENT = "#9E2B22"; // oxblood editorial (pérdida / kicker)
const MUTE = "#7A7264";
const HAIR = "#CDC4B2";
const FONT = "InterVar, Inter, Georgia, serif";
const M = 96; // margen

const Rule: React.FC<{ y: number; color?: string; h?: number; x?: number; w?: number }> = ({
  y, color = HAIR, h = 1, x = M, w = 1080 - 2 * M,
}) => <div style={{ position: "absolute", top: y, left: x, width: w, height: h, background: color }} />;

export const EditorialHouse: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: PAPER, fontFamily: FONT, color: INK }}>
      {/* masthead */}
      <div style={{ position: "absolute", top: 78, left: M, fontSize: 27, fontWeight: 700, letterSpacing: "0.28em" }}>
        DINERO&nbsp;IA
      </div>
      <div style={{ position: "absolute", top: 82, right: M, fontSize: 22, fontWeight: 500, letterSpacing: "0.22em", color: MUTE }}>
        INFORME · 2026
      </div>
      <Rule y={130} color={INK} h={2} />

      {/* kicker */}
      <div style={{ position: "absolute", top: 196, left: M, fontSize: 30, fontWeight: 700, letterSpacing: "0.2em", color: ACCENT }}>
        EL COSTO DE NO MOVER TU DINERO
      </div>

      {/* bloque 1 — nominal */}
      <div style={{ position: "absolute", top: 330, left: M, fontSize: 33, fontWeight: 500, color: MUTE }}>
        Dejas en efectivo
      </div>
      <div style={{ position: "absolute", top: 372, left: M - 4, fontSize: 200, fontWeight: 800, letterSpacing: "-0.035em", lineHeight: 1 }}>
        $100,000
      </div>

      {/* gráfica editorial de la CAÍDA: curva oxblood que baja + cuña de pérdida
          (brecha contra el punto de partida) + puntos inicio/fin + eje de meses.
          Etiquetas DENTRO del svg para no chocar con el bloque de abajo. */}
      <svg width={1080 - 2 * M} height={200} viewBox={`0 0 ${1080 - 2 * M} 200`} style={{ position: "absolute", top: 582, left: M, fontFamily: FONT }}>
        <defs>
          <linearGradient id="lossfill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={ACCENT} stopOpacity="0.28" />
            <stop offset="100%" stopColor={ACCENT} stopOpacity="0.02" />
          </linearGradient>
        </defs>
        {/* línea de referencia = tu punto de partida (100%) */}
        <line x1="0" y1="14" x2="888" y2="14" stroke={INK} strokeWidth="1.5" strokeDasharray="2 8" opacity="0.5" />
        {/* cuña de PÉRDIDA entre la referencia y la curva */}
        <path d="M 0 14 C 250 28 470 94 888 146 L 888 14 Z" fill="url(#lossfill)" />
        {/* la curva que cae */}
        <path d="M 0 14 C 250 28 470 94 888 146" fill="none" stroke={ACCENT} strokeWidth="4" strokeLinecap="round" />
        {/* eje de meses */}
        {Array.from({ length: 13 }, (_, i) => (
          <line key={i} x1={(888 / 12) * i} y1="160" x2={(888 / 12) * i} y2={i % 3 === 0 ? 172 : 167} stroke={INK} strokeWidth="1" opacity="0.22" />
        ))}
        {/* puntos inicio / fin */}
        <circle cx="0" cy="14" r="6" fill={INK} />
        <circle cx="888" cy="146" r="9" fill={ACCENT} />
        {/* etiquetas dentro del gráfico */}
        <text x="0" y="196" fill={MUTE} fontSize="24" fontWeight="600" letterSpacing="1.6">HOY</text>
        <text x="888" y="196" textAnchor="end" fill={ACCENT} fontSize="24" fontWeight="700" letterSpacing="1.2">−3.94% · 12 MESES</text>
      </svg>

      {/* bloque 2 — real */}
      <div style={{ position: "absolute", top: 814, left: M, fontSize: 33, fontWeight: 500, color: MUTE }}>
        Un año después, en poder de compra
      </div>
      <div style={{ position: "absolute", top: 856, left: M - 4, fontSize: 200, fontWeight: 800, letterSpacing: "-0.035em", lineHeight: 1, color: ACCENT }}>
        $96,209
      </div>

      <Rule y={1130} color={INK} h={2} />

      {/* delta */}
      <div style={{ position: "absolute", top: 1180, left: M, right: M, display: "flex", alignItems: "baseline", gap: 22 }}>
        <span style={{ fontSize: 92, fontWeight: 800, letterSpacing: "-0.03em", color: ACCENT }}>−$3,791</span>
        <span style={{ fontSize: 40, fontWeight: 500, color: INK }}>se los comió la inflación</span>
      </div>
      <div style={{ position: "absolute", top: 1320, left: M, right: M, fontSize: 34, fontWeight: 400, lineHeight: 1.4, color: "#4A443B", maxWidth: 820 }}>
        El efectivo no baja de número — baja de <span style={{ fontWeight: 700, color: INK }}>valor</span>.
        Lo que hoy compra $100,000, en un año lo compras con $96,209.
      </div>

      {/* footer / fuente (credibilidad editorial) */}
      <Rule y={1792} />
      <div style={{ position: "absolute", top: 1820, left: M, fontSize: 25, fontWeight: 500, letterSpacing: "0.04em", color: MUTE }}>
        Fuente: INEGI — Inflación anual 3.94% (corte 2026)
      </div>
      <div style={{ position: "absolute", top: 1820, right: M, fontSize: 25, fontWeight: 700, letterSpacing: "0.18em", color: INK }}>
        01
      </div>

      {/* textura de papel muy sutil */}
      <AbsoluteFill style={{ opacity: 0.05, mixBlendMode: "multiply", pointerEvents: "none" }}>
        <svg width="1080" height="1920">
          <filter id="paper"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" stitchTiles="stitch" /></filter>
          <rect width="1080" height="1920" filter="url(#paper)" />
        </svg>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
