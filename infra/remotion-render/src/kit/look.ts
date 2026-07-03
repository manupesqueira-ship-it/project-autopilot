// LOOK A — LOCKED por Manuel 2026-07-03 ("me gusta la opción A").
// Fondo oscuro profundo + Inter 800 para cifras héroe + kicker rojo tracking ancho +
// color semántico saturado con glow. ÚNICA fuente de tokens del sistema de noticias.
// Ningún beat debe hardcodear colores: importa de aquí.

export const L = {
  bg: "#08090B",
  bgAlt: "#0A0B0D",
  ink: "#F3EFE7",
  mute: "#9AA0AA",
  dim: "#8A8F98",          // cifras en conteo (pre-color)
  hair: "#2B2F38",
  kicker: "#E45B4E",       // rojo editorial de kickers (NO es el rojo semántico)
  green: "#10b981",        // semántico: ganancia/sube
  red: "#ef4444",          // semántico: SOLO pérdida
  gold: "#F7C948",         // dinero/neutro cálido
  gray: "#3A3A3A",         // lecho neutro (Von Restorff)
  grayBar: "#5A6472",      // barra de referencia sin valencia
  font: "InterVar, Inter, sans-serif",
  mx: 96,                  // margen editorial
} as const;

// jerarquía tipográfica (look A)
export const TYPE = {
  masthead: { fontSize: 27, fontWeight: 700, letterSpacing: "0.28em", color: L.ink },
  kicker: { fontSize: 34, fontWeight: 700, letterSpacing: "0.24em", color: L.kicker },
  hero: { fontWeight: 800, letterSpacing: "-0.03em", fontVariantNumeric: "tabular-nums" },
  headline: { fontSize: 94, fontWeight: 800, lineHeight: 1.05, letterSpacing: "-0.02em", color: L.ink },
  sub: { fontSize: 46, fontWeight: 500, color: L.mute },
  label: { fontSize: 34, fontWeight: 700, letterSpacing: "0.12em", color: L.mute },
} as const;

export const semColor = (v?: "gain" | "loss" | "neutral") =>
  v === "gain" ? L.green : v === "loss" ? L.red : L.grayBar;
