import React from "react";
import { AbsoluteFill, Easing, Img, interpolate, OffthreadVideo, staticFile, useCurrentFrame } from "remotion";

// BtcShowcase — showcase "NOTICIA + LOGO REAL + i2v" dentro del estilo Editorial.
// Logo ₿ = SVG oficial (asset, no dibujado). Placa = clip i2v REAL de Higgsfield
// (Seedance 2.0) integrado como placa editorial con pie de foto. Movimiento
// constante (deriva) + reveals. Un solo mundo, no dos.

const INK = "#1B1712";
const PAPER = "#F1ECE1";
const ACCENT = "#9E2B22";
const MUTE = "#7A7264";
const FONT = "InterVar, Inter, Georgia, serif";
const M = 96;

const reveal = (f: number, s: number, d = 22, dur = 14): React.CSSProperties => ({
  opacity: interpolate(f, [s, s + dur], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
  transform: `translateY(${interpolate(f, [s, s + dur], [d, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) })}px)`,
});

const BtcMark: React.FC<{ size: number }> = ({ size }) => (
  <Img src={staticFile("logos/bitcoin.svg")} style={{ width: size, height: size, display: "block" }} />
);

export const BtcShowcase: React.FC = () => {
  const f = useCurrentFrame();
  const dx = Math.sin(f / 34) * 6;
  const dy = Math.cos(f / 41) * 5;
  const sc = 1 + Math.sin(f / 49) * 0.005;

  return (
    <AbsoluteFill style={{ backgroundColor: PAPER, fontFamily: FONT, color: INK }}>
      {/* marco fijo */}
      <div style={{ position: "absolute", top: 78, left: M, fontSize: 27, fontWeight: 700, letterSpacing: "0.28em" }}>DINERO&nbsp;IA</div>
      <div style={{ position: "absolute", top: 82, right: M, fontSize: 22, fontWeight: 500, letterSpacing: "0.22em", color: MUTE }}>INFORME · CRIPTO 2026</div>
      <div style={{ position: "absolute", top: 130, left: M, width: 1080 - 2 * M, height: 2, background: INK }} />
      <div style={{ position: "absolute", top: 1792, left: M, width: 1080 - 2 * M, height: 1, background: "#CDC4B2" }} />
      <div style={{ position: "absolute", top: 1820, left: M, fontSize: 25, fontWeight: 500, letterSpacing: "0.04em", color: MUTE }}>Fuente: tenencia pública de BTC · corte 2026</div>
      <div style={{ position: "absolute", top: 1820, right: M, fontSize: 25, fontWeight: 700, letterSpacing: "0.18em", color: INK }}>01</div>

      {/* contenido con deriva constante */}
      <AbsoluteFill style={{ transform: `translate(${dx}px,${dy}px) scale(${sc})`, transformOrigin: "50% 46%" }}>
        <div style={{ position: "absolute", top: 210, left: M, display: "flex", alignItems: "center", gap: 26, ...reveal(f, 4) }}>
          <BtcMark size={92} />
          <div style={{ fontSize: 30, fontWeight: 700, letterSpacing: "0.2em", color: ACCENT }}>BITCOIN · LA APUESTA</div>
        </div>

        <div style={{ position: "absolute", top: 340, left: M, right: M, fontSize: 120, fontWeight: 800, lineHeight: 1.02, letterSpacing: "-0.03em", ...reveal(f, 12, 26) }}>
          Un país apostó<br />todo al Bitcoin.
        </div>

        {/* PLACA i2v real */}
        <div style={{ position: "absolute", top: 760, left: M, right: M, height: 620, borderRadius: 20, overflow: "hidden", border: `2px solid ${INK}`, opacity: interpolate(f, [24, 40], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>
          <OffthreadVideo src={staticFile("i2v/btc_coin.mp4")} muted style={{ width: "100%", height: "100%", objectFit: "cover" }} />
          {/* viñeta para asentar en el papel */}
          <AbsoluteFill style={{ boxShadow: "inset 0 0 120px rgba(0,0,0,0.55)", pointerEvents: "none" }} />
          <div style={{ position: "absolute", left: 22, bottom: 18, fontSize: 24, fontWeight: 600, color: "#EDE6D8", letterSpacing: "0.06em", textShadow: "0 2px 8px rgba(0,0,0,0.6)" }}>El Salvador · reserva en Bitcoin</div>
        </div>

        <div style={{ position: "absolute", top: 1440, left: M, right: M, fontSize: 34, fontWeight: 400, lineHeight: 1.4, color: "#4A443B", maxWidth: 840, ...reveal(f, 44) }}>
          Compró cuando el mundo se reía. Hoy su reserva vale más que nunca.
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
