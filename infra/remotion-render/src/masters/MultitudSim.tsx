import React, { useEffect, useMemo, useRef } from "react";
import { AbsoluteFill, random, useCurrentFrame, useVideoConfig } from "remotion";
import { holdF, inkFlash, lprog, PAL, TOK, tprog } from "../kit2/tokens";
import { Grain, MassCamera, MONO, PageBg, SANS } from "../kit2/world";

// ============================================================================
// MASTER #6 — MULTITUD (simulación de densidad, mundo de la página).
// "¿Cómo se VE un millón de personas en un solo lugar?" (pedido directo de
// Manuel, 2026-07-03): cada punto = N personas, llenando una glorieta + avenida
// (el Ángel/Reforma abstraídos al lenguaje del mundo: geometría, no mapa).
// La multitud CRECE por etapas (los 4 partidos) — cada etapa suma puntos con
// oleada desde el centro; el contador odómetro y el label del periodo avanzan
// en sincronía. Puntos = lecho dim; los RECIÉN llegados destellan esmeralda y
// reposan en hueso tenue (el acento vive en la transición). Determinista:
// random(seed) de Remotion. Props = SOLO datos.
// ============================================================================

export type MultitudStep = { label: string; count: number };

export type MultitudSimProps = {
  kicker?: string;
  steps?: MultitudStep[];       // [{label:"11 JUN", count:420000}, ...]
  perDot?: number;              // personas por punto (default 100)
  sub?: string;
  foot?: string;
  durF?: number;
};

const D = TOK.dur;
const MX = 120;
const W = 1080;
const CY = 1020;                 // centro de la glorieta
const R_GLORIETA = 210;
const AVE_H = 300;               // alto de la banda de avenida

// posición determinista del punto i (glorieta circular + avenida horizontal)
const dotPos = (i: number): [number, number] => {
  const inCircle = random(`mc${i}`) < 0.45;
  if (inCircle) {
    const a = random(`ma${i}`) * Math.PI * 2;
    const r = Math.sqrt(random(`mr${i}`)) * R_GLORIETA;
    return [W / 2 + Math.cos(a) * r, CY + Math.sin(a) * r * 0.62];
  }
  const x = MX - 40 + random(`mx${i}`) * (W - 2 * MX + 80);
  const y = CY - AVE_H / 2 + random(`my${i}`) * AVE_H;
  // hueco donde vive la glorieta para que se lea la forma
  const dx = x - W / 2;
  const dy = (y - CY) / 0.62;
  if (Math.sqrt(dx * dx + dy * dy) < R_GLORIETA * 0.5) {
    return [x < W / 2 ? x - R_GLORIETA * 0.6 : x + R_GLORIETA * 0.6, y];
  }
  return [x, y];
};

export const MultitudSim: React.FC<MultitudSimProps> = ({
  kicker = "ASÍ SE VE",
  steps = [],
  perDot = 100,
  sub = "",
  foot = "",
  durF,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const total = durF ?? durationInFrames;
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const ruleAt = 4;
  const kickerAt = ruleAt + Math.round(D.ruleDrawF * 0.6);
  const simAt = kickerAt + D.enterF + 4;
  const stepF = TOK.racing.periodF;                      // 2.5s por etapa (Bostock)
  const simEnd = simAt + steps.length * stepF;
  const subAt = simEnd + 6;
  const exitAt = total - D.exitF - 2;

  const maxCount = Math.max(...steps.map((s) => s.count), 1);
  const maxDots = Math.ceil(maxCount / perDot);

  // t continuo sobre las etapas
  const tRaw = Math.min(Math.max((frame - simAt) / (steps.length * stepF), 0), 1);
  const stepIdx = Math.min(Math.floor(tRaw * steps.length), steps.length - 1);
  const stepT = tprog(frame, simAt + stepIdx * stepF, simAt + (stepIdx + 1) * stepF, "standard");
  const prevCount = stepIdx > 0 ? steps[stepIdx - 1].count : 0;
  const curCount = steps[stepIdx]?.count ?? 0;
  const shownCount = Math.round(prevCount + (curCount - prevCount) * stepT);
  const shownDots = Math.min(maxDots, Math.ceil(shownCount / perDot));
  const prevDots = Math.ceil(prevCount / perDot);

  // pinta los puntos en canvas (determinista por frame)
  useEffect(() => {
    const cv = canvasRef.current;
    if (!cv) return;
    const ctx = cv.getContext("2d");
    if (!ctx) return;
    ctx.clearRect(0, 0, W, 1920);
    for (let i = 0; i < shownDots; i++) {
      const [x, y] = dotPos(i);
      const isNew = i >= prevDots;                        // recién llegados esta etapa
      const ageT = isNew ? stepT : 1;
      if (isNew && (i - prevDots) / Math.max(shownDots - prevDots, 1) > stepT * 1.15) continue;
      const flick = 0.75 + 0.25 * Math.sin(frame / 9 + i * 1.7);   // multitud VIVA
      if (isNew && ageT < 0.85) {
        ctx.fillStyle = PAL.accent;
        ctx.globalAlpha = 0.85 * flick;
      } else {
        ctx.fillStyle = PAL.ink;
        ctx.globalAlpha = (0.16 + 0.3 * random(`mo${i}`)) * flick;
      }
      ctx.fillRect(x, y, 2.6, 2.6);
    }
    ctx.globalAlpha = 1;
  }, [frame, shownDots, prevDots, stepT]);

  const rule = tprog(frame, ruleAt, ruleAt + D.ruleDrawF, "standard");
  const kickerT = tprog(frame, kickerAt, kickerAt + D.enterF);
  const subT = tprog(frame, subAt, subAt + D.enterF);
  const exitO = 1 - tprog(frame, exitAt, exitAt + D.exitF, "exit");

  return (
    <AbsoluteFill style={{ fontFamily: SANS }}>
      <PageBg energy={0.05} />
      <MassCamera durF={total} seed={7}>
        <div style={{ opacity: exitO }}>
          <div style={{ position: "absolute", top: 560, left: MX, width: (W - 2 * MX) * rule, height: 1, background: PAL.lineSoft }} />
          <div
            style={{
              position: "absolute", top: 592, left: MX, right: MX,
              fontFamily: MONO, fontWeight: 500, fontSize: 30, letterSpacing: "0.32em",
              textTransform: "uppercase", color: inkFlash(kickerT, PAL.dim),
              opacity: Math.min(1, kickerT * 1.4), transform: `translateY(${(1 - kickerT) * 10}px)`,
            }}
          >
            {kicker}
          </div>

          {/* contador + periodo, arriba de la multitud */}
          <div style={{ position: "absolute", top: 680, left: MX, right: MX, display: "flex", alignItems: "baseline", gap: 26 }}>
            <div style={{ fontFamily: MONO, fontWeight: 500, fontSize: 108, letterSpacing: "-0.01em", fontVariantNumeric: "tabular-nums", color: tRaw >= 1 ? inkFlash(lprog(frame, simEnd, simEnd + 40), PAL.ink) : PAL.ink }}>
              {shownCount.toLocaleString("es-MX")}
            </div>
            <div style={{ fontFamily: MONO, fontWeight: 400, fontSize: 30, letterSpacing: "0.2em", color: PAL.faint }}>
              PERSONAS
            </div>
          </div>
          <div style={{ position: "absolute", top: 810, left: MX, fontFamily: MONO, fontWeight: 400, fontSize: 27, letterSpacing: "0.24em", color: PAL.dim, opacity: kickerT }}>
            {steps[stepIdx]?.label ?? ""}
          </div>

          {/* la multitud */}
          <canvas ref={canvasRef} width={W} height={1920} style={{ position: "absolute", inset: 0 }} />

          {/* leyenda de escala */}
          <div style={{ position: "absolute", top: CY + R_GLORIETA * 0.62 + 200, left: MX, fontFamily: MONO, fontWeight: 400, fontSize: 22, letterSpacing: "0.2em", color: PAL.faint, opacity: kickerT }}>
            · = {perDot} PERSONAS
          </div>

          {sub ? (
            <div
              style={{
                position: "absolute", top: CY + R_GLORIETA * 0.62 + 260, left: MX, right: MX,
                fontFamily: SANS, fontWeight: 350, fontSize: 42, lineHeight: 1.4,
                color: inkFlash(subT, PAL.dim), opacity: Math.min(1, subT * 1.4),
                transform: `translateY(${(1 - subT) * 10}px)`, maxWidth: 760,
              }}
            >
              {sub}
            </div>
          ) : null}

          {foot ? (
            <div style={{ position: "absolute", top: 1720, left: MX, right: MX, fontFamily: MONO, fontWeight: 400, fontSize: 21, letterSpacing: "0.22em", textTransform: "uppercase", color: PAL.faint, opacity: Math.min(1, kickerT) }}>
              {foot}
            </div>
          ) : null}
        </div>
      </MassCamera>
      <Grain />
    </AbsoluteFill>
  );
};

export const multitudTestDur = (nSteps: number, subLen: number) =>
  30 + nSteps * TOK.racing.periodF + holdF(subLen) + TOK.hold.chartPostMotionF + TOK.dur.exitF + 6;
