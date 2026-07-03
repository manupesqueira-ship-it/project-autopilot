import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { inkFlash, lprog, PAL, TOK, tprog } from "../kit2/tokens";
import { Grain, MassCamera, MONO, PageBg, SANS } from "../kit2/world";

// ============================================================================
// MASTER #3 — COMPARACIÓN DE BARRAS (mundo de la página).
// Barras HORIZONTALES estilo Apple M3 (la ref "súper sí"): label mono a la
// izquierda, riel hairline, valor tabular a la derecha. Jerarquía por
// LUMINANCIA (Territory): referencias en gris fantasma, protagonista en hueso.
// Coreografía: rieles/labels primero (etapa 1), barras crecen con MASA y en
// SECUENCIA (una cosa a la vez, H&R/Apple) — el protagonista SIEMPRE al final,
// su valor CUENTA mientras crece y aterriza en `land` con el destello (único
// esmeralda de la escena). Reglas de gates: slow-in + extremo lento.
// Props = SOLO datos.
// ============================================================================

export type Bar = {
  label: string;      // "INFLACIÓN"
  value: number;      // magnitud para la escala (3.9)
  display: string;    // string final exacto ("3.9%")
};

export type CompararBarrasProps = {
  kicker?: string;
  bars?: Bar[];             // 2-4; el protagonista crece AL FINAL
  accentIndex?: number;     // índice del protagonista
  sub?: string;
  foot?: string;
  land?: number;            // frame donde aterriza el valor del protagonista
  durF?: number;
};

const D = TOK.dur;
const MX = 120;
const ROW_H = 74;
const ROW_GAP = 96;
const TOP = 810;

const parseDisplay = (s: string) => {
  const m = s.match(/^([^0-9]*)([\d,]+(?:\.\d+)?)(.*)$/);
  if (!m) return { prefix: "", decimals: 0, suffix: s };
  const dec = m[2].includes(".") ? m[2].split(".")[1].length : 0;
  return { prefix: m[1], decimals: dec, suffix: m[3] };
};

export const CompararBarras: React.FC<CompararBarrasProps> = ({
  kicker = "LA COMPARACIÓN",
  bars = [],
  accentIndex = 0,
  sub = "",
  foot = "",
  land,
  durF,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const total = durF ?? durationInFrames;

  const ruleAt = 4;
  const kickerAt = ruleAt + Math.round(D.ruleDrawF * 0.6);
  const railsAt = ruleAt + D.ruleDrawF;                 // etapa 1: rieles + labels

  // orden de crecimiento: referencias primero (en su orden), protagonista al final
  const growOrder = [...bars.map((_, i) => i).filter((i) => i !== accentIndex), accentIndex];
  const overlapF = Math.round(D.barRevealF * 0.7);
  const growStart: number[] = [];
  growOrder.forEach((barIdx, k) => {
    growStart[barIdx] = railsAt + D.enterF + 4 + k * overlapF;
  });
  // ancla del VO: el protagonista TERMINA en land (clamp: nunca antes de que
  // los rieles existan + su propia rodada completa)
  const protagDefaultEnd = growStart[accentIndex] + D.barRevealF;
  const landAt = Math.max(land ?? protagDefaultEnd, railsAt + D.enterF + 4 + D.barRevealF);
  const protagStart = landAt - D.barRevealF;
  growStart[accentIndex] = protagStart;

  const subAt = landAt + 10;
  const exitAt = total - D.exitF - 2;

  const rule = tprog(frame, ruleAt, ruleAt + D.ruleDrawF, "standard");
  const kickerT = tprog(frame, kickerAt, kickerAt + D.enterF);
  const subT = tprog(frame, subAt, subAt + D.enterF);
  const flashT = lprog(frame, landAt, landAt + Math.round(D.accentFlashF / TOK.accent.flashWindowPct));
  const exitO = 1 - tprog(frame, exitAt, exitAt + D.exitF, "exit");

  const maxV = Math.max(...bars.map((b) => b.value), 1e-9);
  const railW = 1080 - 2 * MX;
  const barMaxW = railW - 210; // aire para el valor a la derecha

  return (
    <AbsoluteFill style={{ fontFamily: SANS }}>
      <PageBg energy={0.05} />
      <MassCamera durF={total} seed={4}>
        <div style={{ opacity: exitO }}>
          <div style={{ position: "absolute", top: 636, left: MX, width: railW * rule, height: 1, background: PAL.lineSoft }} />
          <div
            style={{
              position: "absolute", top: 668, left: MX, right: MX,
              fontFamily: MONO, fontWeight: 500, fontSize: 30, letterSpacing: "0.32em",
              textTransform: "uppercase", color: inkFlash(kickerT, PAL.dim),
              opacity: Math.min(1, kickerT * 1.4), transform: `translateY(${(1 - kickerT) * 10}px)`,
            }}
          >
            {kicker}
          </div>

          {bars.map((b, i) => {
            const y = TOP + i * (ROW_H + ROW_GAP);
            const isP = i === accentIndex;
            // etapa 1: riel + label (stagger corto)
            const railT = tprog(frame, railsAt + i * 2, railsAt + i * 2 + D.enterF, "standard");
            // etapa 2: la barra crece con MASA (slow-in)
            const grow = tprog(frame, growStart[i], growStart[i] + D.barRevealF, "mass");
            const { prefix, decimals, suffix } = parseDisplay(b.display);
            const shown = isP
              ? `${prefix}${(b.value * grow).toFixed(decimals)}${suffix}`
              : b.display;
            const valueColor = isP
              ? (frame < landAt ? PAL.faint : inkFlash(flashT, PAL.ink))
              : PAL.faint;
            // gate "demasiado empresarial": protagonista REPOSA en esmeralda
            // (gradiente sutil), referencias en azul frío del look bible
            const barFill = isP
              ? `linear-gradient(90deg, ${PAL.accentDeep} 0%, ${PAL.accent} 100%)`
              : PAL.cool[Math.min(i, PAL.cool.length - 1)];
            return (
              <div key={i}>
                {/* label mono arriba del riel */}
                <div
                  style={{
                    position: "absolute", top: y - 42, left: MX,
                    fontFamily: MONO, fontWeight: 400, fontSize: 26, letterSpacing: "0.18em",
                    textTransform: "uppercase", color: isP ? PAL.dim : PAL.faint, opacity: railT,
                  }}
                >
                  {b.label}
                </div>
                {/* riel hairline */}
                <div style={{ position: "absolute", top: y + ROW_H / 2, left: MX, width: railW * railT, height: 1, background: PAL.lineSoft }} />
                {/* barra: crece por ancho con masa */}
                <div
                  style={{
                    position: "absolute", top: y, left: MX,
                    width: Math.max(0, barMaxW * (b.value / maxV) * grow),
                    height: ROW_H,
                    backgroundImage: isP ? barFill : undefined,
                    backgroundColor: isP ? undefined : barFill,
                  }}
                />
                {/* valor tabular a la derecha; el protagonista CUENTA y flashea */}
                <div
                  style={{
                    position: "absolute", top: y + ROW_H / 2 - 30, right: MX, textAlign: "right",
                    fontFamily: MONO, fontWeight: 500, fontSize: 52,
                    fontVariantNumeric: "tabular-nums",
                    color: valueColor,
                    opacity: isP ? (grow > 0.02 ? 1 : 0) : Math.min(1, grow * 1.6),
                  }}
                >
                  {shown}
                </div>
              </div>
            );
          })}

          {sub ? (
            <div
              style={{
                position: "absolute",
                top: TOP + bars.length * (ROW_H + ROW_GAP) + 40,
                left: MX, right: MX,
                fontFamily: SANS, fontWeight: 350, fontSize: 44, lineHeight: 1.4,
                color: inkFlash(subT, PAL.dim), opacity: Math.min(1, subT * 1.4),
                transform: `translateY(${(1 - subT) * 10}px)`, maxWidth: 760,
              }}
            >
              {sub}
            </div>
          ) : null}

          {foot ? (
            <div
              style={{
                position: "absolute", top: 1720, left: MX, right: MX,
                fontFamily: MONO, fontWeight: 400, fontSize: 21, letterSpacing: "0.22em",
                textTransform: "uppercase", color: PAL.faint, opacity: Math.min(1, kickerT),
              }}
            >
              {foot}
            </div>
          ) : null}
        </div>
      </MassCamera>
      <Grain />
    </AbsoluteFill>
  );
};
