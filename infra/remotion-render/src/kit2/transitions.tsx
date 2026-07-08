import type { TransitionPresentation, TransitionPresentationComponentProps } from "@remotion/transitions";
import React from "react";
import { AbsoluteFill, Easing } from "remotion";
import { PAL } from "./tokens";

// ============================================================================
// CATÁLOGO DE TRANSICIONES (retro 07-07: "repo sencilla de 30-40 tipos").
// MÉTODO DE CALIDAD (no es invención mía): cada mecánica es gramática de
// edición PUBLICADA — corte/dip (continuidad y capítulo, gramática clásica),
// wipe/split (paquetes broadcast Vizrt/CNBC), whip-pan y push-through
// (promos Apple/deporte), blur/grain dissolve (gramática filmica) — ejecutada
// con NUESTROS tokens (curvas MD3/mass, esmeralda SOLO en la transición,
// mundo #070707). Nada entra al menú del director sin pasar el gate de Manuel
// sobre la galería renderizada (mismo proceso que aprobó los 5 masters).
//
// Uso editorial (gramática, no decoración):
//   CONTINUIDAD  -> cut / flash    (misma idea, siguiente dato)
//   CAPÍTULO     -> dip / lumaDip  (cambio de tema, respiro)
//   FIRMA        -> inkSweep_*     (la esmeralda vive en la transición)
//   ESTRUCTURA   -> ruleWipe/split (la regla del mundo corta la escena)
//   ENERGÍA      -> whip/push/slide (aceleración narrativa, hook→dato)
//   MATERIAL     -> blurX/grainX/roll (suavidad filmica, momentos humanos)
// ============================================================================

type P = TransitionPresentationComponentProps<Record<string, never>>;
const EASE_MASS = Easing.bezier(0.55, 0, 0.12, 1);      // Tendril slow-in
const EASE_DECEL = Easing.bezier(0.05, 0.7, 0.1, 1);    // MD3 emphasized decelerate

const wrap = (component: React.FC<P>): TransitionPresentation<Record<string, never>> =>
  ({ component, props: {} });

// ── FIRMA: barrido de tinta — banda esmeralda suave revela la escena nueva
const inkSweep = (dir: "L" | "R" | "U" | "D") =>
  wrap(({ children, presentationDirection, presentationProgress }) => {
    const p = presentationProgress;
    if (presentationDirection === "exiting") return <AbsoluteFill>{children}</AbsoluteFill>;
    const horiz = dir === "L" || dir === "R";
    const from = dir === "L" || dir === "U" ? 1 : -1;
    // frente de barrido: 0→1 a lo largo del eje; la escena entra tras el frente
    const edge = p * 130 - 15; // % con margen para el halo
    const g = horiz
      ? `linear-gradient(${dir === "L" ? "90deg" : "270deg"}, black ${edge}%, transparent ${edge + 14}%)`
      : `linear-gradient(${dir === "U" ? "180deg" : "0deg"}, black ${edge}%, transparent ${edge + 14}%)`;
    const glowPos = Math.min(100, Math.max(0, edge + 7));
    return (
      <AbsoluteFill>
        <AbsoluteFill style={{ WebkitMaskImage: g, maskImage: g }}>{children}</AbsoluteFill>
        {/* halo esmeralda en el frente (la firma: el acento vive en la transición) */}
        <AbsoluteFill
          style={{
            opacity: p < 0.06 ? p / 0.06 : p > 0.94 ? (1 - p) / 0.06 : 1,
            background: horiz
              ? `linear-gradient(${dir === "L" ? "90deg" : "270deg"}, transparent ${glowPos - 6}%, ${PAL.accent}33 ${glowPos}%, transparent ${glowPos + 6}%)`
              : `linear-gradient(${dir === "U" ? "180deg" : "0deg"}, transparent ${glowPos - 6}%, ${PAL.accent}33 ${glowPos}%, transparent ${glowPos + 6}%)`,
            transform: `translate${horiz ? "X" : "Y"}(${from * 0}px)`,
          }}
        />
      </AbsoluteFill>
    );
  });

// ── ESTRUCTURA: la regla 1px del mundo viaja y corta la escena (broadcast)
const ruleWipe = (axis: "H" | "V") =>
  wrap(({ children, presentationDirection, presentationProgress }) => {
    const p = presentationProgress;
    if (presentationDirection === "exiting") return <AbsoluteFill>{children}</AbsoluteFill>;
    const edge = p * 112 - 6;
    const g = axis === "H"
      ? `linear-gradient(180deg, black ${edge}%, transparent ${edge + 0.4}%)`
      : `linear-gradient(90deg, black ${edge}%, transparent ${edge + 0.4}%)`;
    return (
      <AbsoluteFill>
        <AbsoluteFill style={{ WebkitMaskImage: g, maskImage: g }}>{children}</AbsoluteFill>
        <div
          style={{
            position: "absolute",
            ...(axis === "H"
              ? { top: `${Math.min(100, Math.max(0, edge))}%`, left: 0, right: 0, height: 1 }
              : { left: `${Math.min(100, Math.max(0, edge))}%`, top: 0, bottom: 0, width: 1 }),
            background: PAL.lineSoft,
            opacity: p > 0.02 && p < 0.98 ? 1 : 0,
          }}
        />
      </AbsoluteFill>
    );
  });

// ── ESTRUCTURA: split — la escena saliente se parte en la regla y se abre
const split = (axis: "H" | "V") =>
  wrap(({ children, presentationDirection, presentationProgress }) => {
    const p = EASE_MASS(presentationProgress);
    if (presentationDirection === "entering") return <AbsoluteFill>{children}</AbsoluteFill>;
    const off = p * 52; // % que viaja cada mitad
    const clipA = axis === "H" ? `inset(0 0 50% 0)` : `inset(0 50% 0 0)`;
    const clipB = axis === "H" ? `inset(50% 0 0 0)` : `inset(0 0 0 50%)`;
    const tA = axis === "H" ? `translateY(${-off}%)` : `translateX(${-off}%)`;
    const tB = axis === "H" ? `translateY(${off}%)` : `translateX(${off}%)`;
    return (
      <AbsoluteFill>
        <AbsoluteFill style={{ clipPath: clipA, transform: tA }}>{children}</AbsoluteFill>
        <AbsoluteFill style={{ clipPath: clipB, transform: tB }}>{children}</AbsoluteFill>
      </AbsoluteFill>
    );
  });

// ── ENERGÍA: whip-pan direccional con blur de movimiento
const whip = (dir: "L" | "R" | "U" | "D") =>
  wrap(({ children, presentationDirection, presentationProgress }) => {
    const p = presentationProgress;
    const horiz = dir === "L" || dir === "R";
    const sign = dir === "L" || dir === "U" ? -1 : 1;
    const blurMax = 26;
    const blur = Math.sin(p * Math.PI) * blurMax;
    const exiting = presentationDirection === "exiting";
    const eased = EASE_MASS(p);
    const travel = exiting ? eased * 100 * sign : (eased - 1) * 100 * sign;
    return (
      <AbsoluteFill
        style={{
          transform: `translate${horiz ? "X" : "Y"}(${travel}%)`,
          filter: `blur(${blur}px)`,
        }}
      >
        {children}
      </AbsoluteFill>
    );
  });

// ── ENERGÍA: push-through — continuidad de zoom (promo)
const push = (mode: "in" | "out") =>
  wrap(({ children, presentationDirection, presentationProgress }) => {
    const p = EASE_DECEL(presentationProgress);
    const exiting = presentationDirection === "exiting";
    const scale = exiting
      ? 1 + (mode === "in" ? 0.14 : -0.1) * p
      : (mode === "in" ? 0.92 : 1.1) + (1 - (mode === "in" ? 0.92 : 1.1)) * p;
    const opacity = exiting ? 1 - p : Math.min(1, p * 1.6);
    return (
      <AbsoluteFill style={{ transform: `scale(${scale})`, opacity }}>
        {children}
      </AbsoluteFill>
    );
  });

// ── ENERGÍA: slide-over en curva de masa (sin blur, más sobrio que whip)
const slide = (dir: "L" | "R" | "U" | "D") =>
  wrap(({ children, presentationDirection, presentationProgress }) => {
    const p = EASE_MASS(presentationProgress);
    if (presentationDirection === "exiting") {
      return <AbsoluteFill style={{ opacity: 1 - p * 0.35 }}>{children}</AbsoluteFill>;
    }
    const horiz = dir === "L" || dir === "R";
    const sign = dir === "L" || dir === "U" ? -1 : 1;
    return (
      <AbsoluteFill style={{ transform: `translate${horiz ? "X" : "Y"}(${sign * (1 - p) * 100}%)` }}>
        {children}
      </AbsoluteFill>
    );
  });

// ── MATERIAL: cross-dissolve a través de blur / velo de grano / dip parcial
const blurX = wrap(({ children, presentationDirection, presentationProgress }) => {
  const p = presentationProgress;
  const exiting = presentationDirection === "exiting";
  const blur = Math.sin(p * Math.PI) * 14;
  return (
    <AbsoluteFill style={{ opacity: exiting ? 1 - p : p, filter: `blur(${blur}px)` }}>
      {children}
    </AbsoluteFill>
  );
});

const grainX = wrap(({ children, presentationDirection, presentationProgress }) => {
  const p = presentationProgress;
  const exiting = presentationDirection === "exiting";
  const veil = Math.sin(p * Math.PI);
  return (
    <AbsoluteFill style={{ opacity: exiting ? 1 - p : p }}>
      {children}
      {!exiting ? (
        <AbsoluteFill
          style={{
            opacity: veil * 0.5,
            backgroundImage:
              "url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='128' height='128'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/></filter><rect width='128' height='128' filter='url(%23n)' opacity='0.55'/></svg>\")",
            mixBlendMode: "overlay",
          }}
        />
      ) : null}
    </AbsoluteFill>
  );
});

const lumaDip = wrap(({ children, presentationDirection, presentationProgress }) => {
  const p = presentationProgress;
  const exiting = presentationDirection === "exiting";
  const dark = Math.sin(p * Math.PI) * 0.62;
  return (
    <AbsoluteFill style={{ opacity: exiting ? 1 - p : p }}>
      {children}
      <AbsoluteFill style={{ background: `rgba(7,7,7,${dark})` }} />
    </AbsoluteFill>
  );
});

// ── CONTINUIDAD: corte con destello (2 frames de acento, broadcast)
const flashCut = wrap(({ children, presentationDirection, presentationProgress }) => {
  const p = presentationProgress;
  const exiting = presentationDirection === "exiting";
  const flash = Math.max(0, 1 - Math.abs(p - 0.5) * 6);
  return (
    <AbsoluteFill style={{ opacity: exiting ? (p < 0.5 ? 1 : 0) : p >= 0.5 ? 1 : 0 }}>
      {children}
      {!exiting ? (
        <AbsoluteFill style={{ background: PAL.accent, opacity: flash * 0.12 }} />
      ) : null}
    </AbsoluteFill>
  );
});

// ── MATERIAL: rodada de odómetro de cuadro completo (habla el idioma de CifraHero)
const roll = (dir: "U" | "D") =>
  wrap(({ children, presentationDirection, presentationProgress }) => {
    const p = EASE_DECEL(presentationProgress);
    const sign = dir === "U" ? -1 : 1;
    const exiting = presentationDirection === "exiting";
    const y = exiting ? p * 100 * sign : (p - 1) * 100 * sign;
    return (
      <AbsoluteFill style={{ transform: `translateY(${y}%)` }}>{children}</AbsoluteFill>
    );
  });

// ============================================================================
// EL MENÚ — nombre → presentación + duración default (frames) + gramática.
// Variantes _f = rápida (energía) · _s = lenta (respiro). 40 entradas.
// ============================================================================
export type TransSpec = {
  presentation: TransitionPresentation<Record<string, never>>;
  defaultF: number;
  uso: string;
};

// duraciones en kit2/trans_defaults.json — ÚNICA fuente (también la lee el
// ensamblador Python para calcular los empalmes del timeline)
import DEF from "./trans_defaults.json";
const E = (presentation: TransitionPresentation<Record<string, never>>, defaultF: number, uso: string): TransSpec =>
  ({ presentation, defaultF, uso });

export const TRANS_CATALOG: Record<string, TransSpec> = {
  // FIRMA — barrido de tinta (esmeralda SOLO aquí)
  inkSweep_L: E(inkSweep("L"), 14, "FIRMA capítulo con energía; ←"),
  inkSweep_R: E(inkSweep("R"), 14, "FIRMA capítulo con energía; →"),
  inkSweep_U: E(inkSweep("U"), 14, "FIRMA revelación hacia arriba"),
  inkSweep_D: E(inkSweep("D"), 14, "FIRMA descenso/consecuencia"),
  inkSweep_Lf: E(inkSweep("L"), 9, "FIRMA rápida ←"),
  inkSweep_Rf: E(inkSweep("R"), 9, "FIRMA rápida →"),
  // ESTRUCTURA — la regla del mundo
  ruleWipe_H: E(ruleWipe("H"), 16, "ESTRUCTURA la regla baja y corta"),
  ruleWipe_V: E(ruleWipe("V"), 16, "ESTRUCTURA la regla cruza"),
  split_H: E(split("H"), 15, "ESTRUCTURA la escena se abre en la regla (horizontal)"),
  split_V: E(split("V"), 15, "ESTRUCTURA la escena se abre en la regla (vertical)"),
  // ENERGÍA — whip / push / slide
  whip_L: E(whip("L"), 10, "ENERGÍA aceleración ←"),
  whip_R: E(whip("R"), 10, "ENERGÍA aceleración →"),
  whip_U: E(whip("U"), 10, "ENERGÍA subida (dato mejora)"),
  whip_D: E(whip("D"), 10, "ENERGÍA caída (dato empeora)"),
  whip_Ls: E(whip("L"), 15, "ENERGÍA ← suave"),
  whip_Rs: E(whip("R"), 15, "ENERGÍA → suave"),
  push_in: E(push("in"), 13, "ENERGÍA entrar al detalle (zoom-continuidad)"),
  push_out: E(push("out"), 13, "ENERGÍA abrir al contexto"),
  push_in_s: E(push("in"), 19, "ENERGÍA entrar al detalle, lenta"),
  push_out_s: E(push("out"), 19, "ENERGÍA abrir al contexto, lenta"),
  slide_L: E(slide("L"), 14, "ENERGÍA sobrio; la escena nueva cubre ←"),
  slide_R: E(slide("R"), 14, "ENERGÍA sobrio →"),
  slide_U: E(slide("U"), 14, "ENERGÍA sobrio ↑"),
  slide_D: E(slide("D"), 14, "ENERGÍA sobrio ↓"),
  slide_Ls: E(slide("L"), 20, "ENERGÍA ← lento (cambio de capítulo sin dip)"),
  slide_Us: E(slide("U"), 20, "ENERGÍA ↑ lento"),
  // MATERIAL — filmico
  blurX: E(blurX, 14, "MATERIAL disolvencia suave (momento humano)"),
  blurX_f: E(blurX, 9, "MATERIAL disolvencia rápida"),
  blurX_s: E(blurX, 22, "MATERIAL disolvencia lenta (cierre emotivo)"),
  grainX: E(grainX, 14, "MATERIAL velo de grano (archivo/memoria)"),
  grainX_s: E(grainX, 20, "MATERIAL grano lento"),
  lumaDip: E(lumaDip, 12, "CAPÍTULO respiro parcial (más ágil que dip)"),
  lumaDip_s: E(lumaDip, 18, "CAPÍTULO respiro parcial lento"),
  roll_U: E(roll("U"), 13, "MATERIAL rodada de odómetro ↑ (idioma CifraHero)"),
  roll_D: E(roll("D"), 13, "MATERIAL rodada ↓"),
  roll_Us: E(roll("U"), 19, "MATERIAL rodada ↑ lenta"),
  // CONTINUIDAD — acentos de corte
  flash: E(flashCut, 5, "CONTINUIDAD corte con destello (2f acento)"),
  flash_s: E(flashCut, 8, "CONTINUIDAD destello suave"),
};

// el JSON manda sobre los literales de arriba (una sola fuente de duraciones)
for (const k of Object.keys(TRANS_CATALOG)) {
  const d = (DEF as Record<string, number>)[k];
  if (typeof d === "number") TRANS_CATALOG[k].defaultF = d;
}

export const TRANS_NAMES = Object.keys(TRANS_CATALOG);
