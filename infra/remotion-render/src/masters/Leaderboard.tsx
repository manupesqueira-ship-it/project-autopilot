import React from "react";
import { AbsoluteFill, Img, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { holdF, inkFlash, lprog, PAL, TOK, tprog } from "../kit2/tokens";
import { Grain, MONO, PageBg, SANS, WorldPlate } from "../kit2/world";

// ============================================================================
// MASTER #6 — LEADERBOARD (retro 07-07: "logos de los países e instituciones
// que más están ganando dinero y cada uno con una gráfica").
// Gramática: ranked-bars editoriales FT/Bloomberg (referencia aprobada "todo
// sí, con nuestros colores") — filas con IDENTIDAD (logo vectorial REAL como
// asset, o monograma tipográfico limpio), barra que crece con masa, valor que
// cuenta. Von Restorff: protagonista esmeralda crece AL FINAL anclado a la
// voz; el resto reposa en la escalera azul fría. Contenido ESTÁTICO (sin
// cámara de masa — retro: los números no tiemblan).
// ============================================================================

export type LeaderRow = {
  label: string;          // "FIFA", "CDMX", "PATROCINADORES"
  value: number;          // magnitud (escala de barras)
  display: string;        // "$8,900 MDD" — lo que se muestra contando
  icon?: string;          // public/logos/x.svg|png (VECTOR REAL); sin icon → monograma
};

export type LeaderboardProps = {
  kicker?: string;
  rows?: LeaderRow[];     // ya ordenadas como deben mostrarse (max 6)
  accentIndex?: number;   // el protagonista (esmeralda, entra al último)
  sub?: string;
  foot?: string;
  bgClip?: string;
  land?: number;          // frame donde el protagonista ATERRIZA (ancla VO)
  durF?: number;
};

const D = TOK.dur;
const MX = 120;
const ROW_H = 168;

const numFrom = (display: string): { prefix: string; num: number; suffix: string } => {
  const m = display.match(/^([^0-9-]*)([\d,.]+)(.*)$/);
  if (!m) return { prefix: "", num: 0, suffix: display };
  return { prefix: m[1], num: parseFloat(m[2].replace(/,/g, "")), suffix: m[3] };
};

const fmt = (n: number, ref: string): string => {
  const decimals = ref.includes(".") ? ref.split(".")[1].replace(/[^\d]/g, "").length : 0;
  return n.toLocaleString("es-MX", { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
};

export const Leaderboard: React.FC<LeaderboardProps> = ({
  kicker = "QUIÉN GANA",
  rows = [],
  accentIndex = 0,
  sub = "",
  foot = "",
  bgClip,
  land,
  durF,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const total = durF ?? durationInFrames;

  const ruleAt = 4;
  const kickerAt = ruleAt + Math.round(D.ruleDrawF * 0.6);
  const rowsAt = kickerAt + D.enterF;
  const STAG = 11;

  // referencias (no-protagonistas) entran escalonadas; el protagonista AL FINAL,
  // estirado hasta el ancla de la voz (mismo patrón aprobado de CompararBarras)
  const othersOrder = rows.map((_, i) => i).filter((i) => i !== accentIndex);
  const enterAt = new Map<number, number>();
  othersOrder.forEach((idx, k) => enterAt.set(idx, rowsAt + k * STAG));
  const lastOther = rowsAt + Math.max(0, othersOrder.length - 1) * STAG;
  const minProtag = lastOther + STAG + 4;
  const landAt = Math.max(land ?? minProtag + D.barRevealF, minProtag + 12);
  const protagStart = Math.min(landAt - D.barRevealF, minProtag);
  enterAt.set(accentIndex, protagStart);

  const maxV = Math.max(...rows.map((r) => r.value), 1);
  const subAt = landAt + 12;
  const exitAt = total - D.exitF - 2;

  const rule = tprog(frame, ruleAt, ruleAt + D.ruleDrawF, "standard");
  const kickerT = tprog(frame, kickerAt, kickerAt + D.enterF);
  const subT = tprog(frame, subAt, subAt + D.enterF);
  const flashT = lprog(frame, landAt, landAt + Math.round(D.accentFlashF / TOK.accent.flashWindowPct));
  const exitO = 1 - tprog(frame, exitAt, exitAt + D.exitF, "exit");

  const topRows = 640;
  const barMax = 1080 - 2 * MX - 128 - 24; // ancho útil tras chip de identidad

  return (
    <AbsoluteFill style={{ fontFamily: SANS }}>
      <PageBg energy={0.05} />
      {bgClip ? <WorldPlate src={bgClip} /> : null}
      <AbsoluteFill>
        <div style={{ opacity: exitO }}>
          <div style={{ position: "absolute", top: 560, left: MX, width: (1080 - 2 * MX) * rule, height: 1, background: PAL.lineSoft }} />
          <div style={{ position: "absolute", top: 592, left: MX, right: MX, fontFamily: MONO, fontWeight: 500, fontSize: 30, letterSpacing: "0.32em", textTransform: "uppercase", color: inkFlash(kickerT, PAL.dim), opacity: Math.min(1, kickerT * 1.4), transform: `translateY(${(1 - kickerT) * 10}px)` }}>
            {kicker}
          </div>

          {rows.slice(0, 6).map((r, i) => {
            const isAccent = i === accentIndex;
            const at = enterAt.get(i) ?? rowsAt;
            const entered = tprog(frame, at, at + D.enterF);
            const barEnd = isAccent ? landAt : at + 6 + D.barRevealF;
            const barT = tprog(frame, at + 6, barEnd, "mass");
            const w = barMax * (r.value / maxV) * barT;
            const { prefix, num, suffix } = numFrom(r.display);
            const shown = `${prefix}${fmt(num * barT, r.display)}${suffix}`;
            const coolColor = PAL.cool[Math.min(othersOrder.indexOf(i) >= 0 ? othersOrder.indexOf(i) : 0, PAL.cool.length - 1)];
            const barColor = isAccent
              ? (frame < landAt ? PAL.accentDeep : inkFlash(flashT, PAL.accent))
              : coolColor;
            const valColor = isAccent
              ? (frame < landAt ? PAL.dim : inkFlash(flashT, PAL.ink))
              : PAL.dim;
            return (
              <div key={i} style={{ position: "absolute", top: topRows + i * ROW_H, left: MX, right: MX, opacity: entered, transform: `translateY(${(1 - entered) * 14}px)` }}>
                {/* identidad: logo/bandera REAL (asset del banco) o monograma tipográfico.
                    Chip rectangular: los wordmarks (FIFA) son anchos, un círculo los mata. */}
                <div style={{ position: "absolute", top: 4, left: 0, width: 104, height: 74, borderRadius: 14, background: "#15171500", display: "flex", alignItems: "center", justifyContent: "center", overflow: "hidden" }}>
                  {r.icon ? (
                    <Img src={staticFile(r.icon)} style={{ maxWidth: 96, maxHeight: 62, objectFit: "contain", filter: "grayscale(0.15) brightness(1.06)" }} />
                  ) : (
                    <span style={{ fontFamily: MONO, fontWeight: 500, fontSize: 30, color: isAccent ? PAL.ink : PAL.dim, border: `1px solid ${PAL.lineSoft}`, borderRadius: 14, width: 72, height: 62, display: "flex", alignItems: "center", justifyContent: "center" }}>
                      {r.label.slice(0, 1)}
                    </span>
                  )}
                </div>
                <div style={{ position: "absolute", left: 128, top: 0, fontFamily: MONO, fontWeight: 500, fontSize: 26, letterSpacing: "0.2em", textTransform: "uppercase", color: isAccent ? PAL.ink : PAL.dim }}>
                  {r.label}
                </div>
                <div style={{ position: "absolute", left: 128, top: 44, width: barMax, height: 16, background: "rgba(233,231,224,0.05)", borderRadius: 2 }}>
                  <div style={{ width: w, height: "100%", borderRadius: 2, background: isAccent ? `linear-gradient(90deg, ${PAL.accentDeep}, ${barColor})` : barColor }} />
                </div>
                <div style={{ position: "absolute", left: 128, top: 74, fontFamily: MONO, fontWeight: 500, fontSize: 38, fontVariantNumeric: "tabular-nums", color: valColor }}>
                  {shown}
                </div>
              </div>
            );
          })}

          {sub ? (
            <div style={{ position: "absolute", top: topRows + Math.min(rows.length, 6) * ROW_H + 26, left: MX, right: MX, fontWeight: 350, fontSize: 44, lineHeight: 1.4, color: inkFlash(subT, PAL.dim), opacity: Math.min(1, subT * 1.4), transform: `translateY(${(1 - subT) * 10}px)`, maxWidth: 760 }}>
              {sub}
            </div>
          ) : null}

          {foot ? (
            <div style={{ position: "absolute", top: 1720, left: MX, right: MX, fontFamily: MONO, fontWeight: 400, fontSize: 21, letterSpacing: "0.22em", textTransform: "uppercase", color: PAL.faint, opacity: Math.min(1, kickerT) }}>
              {foot}
            </div>
          ) : null}
        </div>
      </AbsoluteFill>
      <Grain />
    </AbsoluteFill>
  );
};

export const leaderboardTestDur = (nRows: number, sub: string) =>
  4 + 10 + TOK.dur.enterF + nRows * 11 + TOK.dur.barRevealF + 24 +
  Math.max(holdF(sub.length), TOK.hold.chartPostMotionF) + TOK.dur.exitF + 8;
