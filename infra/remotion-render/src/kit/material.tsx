import React from "react";
import { L } from "./look";

// MATERIALIDAD — nada en pantalla es un fill sólido plano (auditoría 2026-07-03).
// Gradiente 2-stops + rim light + doble sombra con ángulo de luz GLOBAL (arriba-izq)
// + glow físico multicapa (falloff exponencial, no un solo blur).

const lighten = (hex: string, amt: number) => {
  const n = parseInt(hex.slice(1), 16);
  const r = Math.min(255, ((n >> 16) & 255) + amt);
  const g = Math.min(255, ((n >> 8) & 255) + amt);
  const b = Math.min(255, (n & 255) + amt);
  return `rgb(${r},${g},${b})`;
};

// barra/shape con luz: gradiente vertical (luz arriba) + rim 1px + doble sombra
export const barStyle = (color: string, glow = false): React.CSSProperties => ({
  background: `linear-gradient(180deg, ${lighten(color, 38)} 0%, ${color} 55%, ${color} 100%)`,
  boxShadow: [
    "inset 0 1.5px 0 rgba(255,255,255,0.28)",          // rim superior
    "0 2px 6px rgba(0,0,0,0.55)",                       // sombra corta nítida
    "0 24px 70px rgba(0,0,0,0.45)",                     // sombra larga difusa
    ...(glow ? [`0 0 40px ${color}40`, `0 0 110px ${color}22`] : []),
  ].join(", "),
});

// glow físico multicapa para TEXTO/SVG (drop-shadows apiladas = falloff exponencial)
export const glowFilter = (color: string, k = 1) =>
  `drop-shadow(0 0 ${4 * k}px ${color}AA) drop-shadow(0 0 ${12 * k}px ${color}59) drop-shadow(0 0 ${36 * k}px ${color}33) drop-shadow(0 0 ${100 * k}px ${color}1F)`;

// panel/tarjeta editorial (tarjeta de crédito, cards)
export const cardStyle = (dark = true): React.CSSProperties => ({
  background: dark
    ? "linear-gradient(150deg, #1B1F27 0%, #101319 60%, #0C0E13 100%)"
    : "linear-gradient(150deg, #FFFFFF 0%, #F2EFE8 100%)",
  boxShadow: "inset 0 1px 0 rgba(255,255,255,0.10), 0 3px 10px rgba(0,0,0,0.5), 0 40px 120px rgba(0,0,0,0.55)",
});

// masthead editorial compartido
export const Masthead: React.FC<{ light?: boolean }> = () => (
  <>
    <div style={{ position: "absolute", top: 78, left: L.mx, fontSize: 27, fontWeight: 700, letterSpacing: "0.28em", color: L.ink, zIndex: 40 }}>
      DINERO&nbsp;IA
    </div>
    <div style={{ position: "absolute", top: 130, left: L.mx, width: 1080 - 2 * L.mx, height: 1, background: L.hair, zIndex: 40 }} />
  </>
);
