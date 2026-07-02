import React from "react";
import { AbsoluteFill } from "remotion";

// Logo — sistema de marca editorial "DINERO IA". Wordmark + marca (un cuadro con
// la línea de valor descendente = el ADN del contenido: dinero y su valor en el
// tiempo). Un solo gesto simple, derivado de la identidad (mecánica-firma).

const INK = "#1B1712";
const PAPER = "#F1ECE1";
const ACCENT = "#9E2B22";
const FONT = "InterVar, Inter, Georgia, serif";

const Mark: React.FC<{ size: number; ink: string; accent: string }> = ({ size, ink, accent }) => {
  const s = size;
  return (
    <svg width={s} height={s} viewBox="0 0 100 100" style={{ display: "block" }}>
      <rect x="6" y="6" width="88" height="88" rx="14" fill="none" stroke={ink} strokeWidth="7" />
      <path d="M 24 34 C 40 40 52 66 76 72" fill="none" stroke={accent} strokeWidth="8" strokeLinecap="round" />
      <circle cx="76" cy="72" r="8" fill={accent} />
    </svg>
  );
};

export const Logo: React.FC<{ variant?: "wordmark" | "sheet"; bg?: "paper" | "transparent" | "ink" }> = ({
  variant = "wordmark", bg = "paper",
}) => {
  const bgColor = bg === "paper" ? PAPER : bg === "ink" ? INK : "transparent";
  const ink = bg === "ink" ? PAPER : INK;

  const Wordmark: React.FC<{ scale?: number }> = ({ scale = 1 }) => (
    <div style={{ display: "flex", alignItems: "center", gap: 34 * scale }}>
      <Mark size={132 * scale} ink={ink} accent={ACCENT} />
      <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 120 * scale, letterSpacing: "0.02em", color: ink, lineHeight: 1 }}>
        DINERO <span style={{ color: ACCENT }}>IA</span>
      </div>
    </div>
  );

  if (variant === "sheet") {
    return (
      <AbsoluteFill style={{ backgroundColor: PAPER, fontFamily: FONT, color: INK, padding: 110 }}>
        <div style={{ fontSize: 30, fontWeight: 700, letterSpacing: "0.28em", color: ACCENT }}>SISTEMA DE MARCA</div>
        <div style={{ marginTop: 90 }}><Wordmark scale={1.15} /></div>
        <div style={{ marginTop: 120, display: "flex", gap: 60, alignItems: "center" }}>
          <div style={{ background: INK, borderRadius: 24, padding: "60px 70px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 26 }}>
              <Mark size={96} ink={PAPER} accent={ACCENT} />
              <div style={{ fontWeight: 800, fontSize: 84, color: PAPER, letterSpacing: "0.02em" }}>DINERO <span style={{ color: "#E8A79F" }}>IA</span></div>
            </div>
          </div>
          <Mark size={200} ink={INK} accent={ACCENT} />
        </div>
        <div style={{ marginTop: 130, display: "flex", gap: 40 }}>
          {[["#1B1712", "TINTA"], ["#9E2B22", "OXBLOOD"], ["#F1ECE1", "PAPEL"], ["#1F7A4D", "VERDE"]].map(([c, n]) => (
            <div key={n} style={{ textAlign: "center" }}>
              <div style={{ width: 180, height: 180, background: c, borderRadius: 18, border: c === "#F1ECE1" ? `2px solid ${INK}` : "none" }} />
              <div style={{ marginTop: 18, fontSize: 26, fontWeight: 600, letterSpacing: "0.1em", color: INK }}>{n}</div>
              <div style={{ fontSize: 22, color: "#7A7264" }}>{c}</div>
            </div>
          ))}
        </div>
        <div style={{ position: "absolute", bottom: 90, left: 110, fontSize: 26, color: "#7A7264" }}>
          Tipografía: Inter · Marca = cuadro editorial + línea de valor descendente
        </div>
      </AbsoluteFill>
    );
  }

  return (
    <AbsoluteFill style={{ backgroundColor: bgColor, justifyContent: "center", alignItems: "center" }}>
      <Wordmark />
    </AbsoluteFill>
  );
};
