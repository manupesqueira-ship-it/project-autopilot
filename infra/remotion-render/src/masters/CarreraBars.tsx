import React, { useMemo } from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { inkFlash, PAL, TOK, tprog } from "../kit2/tokens";
import { Grain, MONO, PageBg, SANS } from "../kit2/world";

// ============================================================================
// MASTER #4 — CARRERA DE BARRAS (mundo de la página).
// El spec CANÓNICO de Bostock (Bar Chart Race Explained) a frames exactos:
// ≥75f por periodo de datos (racing.periodF), k=10 sub-keyframes por periodo
// (cada uno ≈250ms — el número de Bostock), VALORES interpolados linealmente
// (continuo, sin pulsos) y POSICIONES que deslizan entre slots de ranking en
// cada sub-keyframe — las barras nunca saltan. Colores NUESTROS (gate FT:
// "todo sí, solo que usemos nuestros propios colores"): protagonista esmeralda,
// resto escalera de azules fríos. Labels viajan con su barra; valores en
// columna tabular fija; el periodo como reloj mono de la escena. Props=datos.
// ============================================================================

export type CarreraStep = { period: string; values: Record<string, number> };

export type CarreraBarsProps = {
  kicker?: string;
  steps?: CarreraStep[];
  accentName?: string;
  prefix?: string;
  suffix?: string;
  sub?: string;
  foot?: string;
  durF?: number;
};

const D = TOK.dur;
const MX = 120;
const ROW_H = 64;
const ROW_GAP = 58;
const TOP = 780;
const K = 10; // sub-keyframes por periodo (Bostock)

export const CarreraBars: React.FC<CarreraBarsProps> = ({
  kicker = "LA CARRERA",
  steps = [],
  accentName = "",
  prefix = "",
  suffix = "",
  sub = "",
  foot = "",
  durF,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const total = durF ?? durationInFrames;

  const ruleAt = 4;
  const kickerAt = ruleAt + Math.round(D.ruleDrawF * 0.6);
  const raceAt = ruleAt + D.ruleDrawF + D.enterF + 4;
  const raceF = Math.max(1, (steps.length - 1) * TOK.racing.periodF);
  const raceEnd = raceAt + raceF;
  const exitAt = total - D.exitF - 2;

  const names = useMemo(() => Object.keys(steps[0]?.values ?? {}), [steps]);
  const maxV = useMemo(
    () => Math.max(...steps.flatMap((s) => Object.values(s.values)), 1e-9),
    [steps],
  );

  // ── Bostock a frames: valores lerp continuos; ranks en sub-keyframes ──────
  const t = Math.min(Math.max((frame - raceAt) / raceF, 0), 1) * (steps.length - 1);
  const lo = Math.min(Math.floor(t), steps.length - 2);
  const f = steps.length > 1 ? t - lo : 0;
  const valueOf = (name: string, tt: number) => {
    const l = Math.min(Math.floor(tt), steps.length - 2);
    const ff = steps.length > 1 ? tt - l : 0;
    return (steps[l]?.values[name] ?? 0) * (1 - ff) + (steps[l + 1]?.values[name] ?? 0) * ff;
  };
  const ranksAt = (tt: number) => {
    const sorted = [...names].sort((a, b) => valueOf(b, tt) - valueOf(a, tt));
    const r: Record<string, number> = {};
    sorted.forEach((n, i) => (r[n] = i));
    return r;
  };
  // posición: desliza linealmente entre slots de ranking de sub-keyframe a
  // sub-keyframe (cada sub-keyframe = periodF/K ≈ 250ms — nunca salta)
  const sub_ = t * K;
  const kLo = Math.floor(sub_) / K;
  const kHi = Math.min(Math.ceil(sub_ + 1e-9) / K, steps.length - 1);
  const kf = kHi > kLo ? (t - kLo) / (kHi - kLo) : 0;
  const rLo = ranksAt(kLo);
  const rHi = ranksAt(kHi);

  const rule = tprog(frame, ruleAt, ruleAt + D.ruleDrawF, "standard");
  const kickerT = tprog(frame, kickerAt, kickerAt + D.enterF);
  const introT = tprog(frame, raceAt - D.enterF, raceAt, "enter");
  const subT = tprog(frame, raceEnd + 8, raceEnd + 8 + D.enterF);
  const exitO = 1 - tprog(frame, exitAt, exitAt + D.exitF, "exit");

  const railW = 1080 - 2 * MX;
  const barMaxW = railW - 230;
  const period = steps[Math.min(Math.round(t), steps.length - 1)]?.period ?? "";
  const coolFor = (i: number) => PAL.cool[i % PAL.cool.length];

  return (
    <AbsoluteFill style={{ fontFamily: SANS }}>
      <PageBg energy={0.05} />
      <AbsoluteFill>
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

          {names.map((name, ni) => {
            const isP = name === accentName;
            const v = valueOf(name, t);
            const y = TOP + (rLo[name] * (1 - kf) + rHi[name] * kf) * (ROW_H + ROW_GAP);
            const w = Math.max(0, barMaxW * (v / maxV)) * introT;
            return (
              <div key={name}>
                <div
                  style={{
                    position: "absolute", top: y - 34, left: MX,
                    fontFamily: MONO, fontWeight: 400, fontSize: 24, letterSpacing: "0.16em",
                    textTransform: "uppercase", color: isP ? PAL.dim : PAL.faint, opacity: introT,
                  }}
                >
                  {name}
                </div>
                <div
                  style={{
                    position: "absolute", top: y, left: MX, width: w, height: ROW_H,
                    backgroundImage: isP ? `linear-gradient(90deg, ${PAL.accentDeep} 0%, ${PAL.accent} 100%)` : undefined,
                    backgroundColor: isP ? undefined : coolFor(ni),
                  }}
                />
                <div
                  style={{
                    position: "absolute", top: y + ROW_H / 2 - 26, right: MX, textAlign: "right",
                    fontFamily: MONO, fontWeight: 500, fontSize: 44,
                    fontVariantNumeric: "tabular-nums",
                    color: isP ? PAL.ink : PAL.faint, opacity: introT,
                  }}
                >
                  {prefix}{Math.round(v).toLocaleString("es-MX")}{suffix}
                </div>
              </div>
            );
          })}

          {/* el periodo = reloj mono de la escena */}
          <div
            style={{
              position: "absolute",
              top: TOP + names.length * (ROW_H + ROW_GAP) + 46,
              left: 0, right: 0, textAlign: "center",
              fontFamily: MONO, fontWeight: 500, fontSize: 96, letterSpacing: "0.06em",
              fontVariantNumeric: "tabular-nums", color: PAL.faint, opacity: introT,
            }}
          >
            {period}
          </div>

          {sub ? (
            <div
              style={{
                position: "absolute",
                top: TOP + names.length * (ROW_H + ROW_GAP) + 190,
                left: MX, right: MX,
                fontFamily: SANS, fontWeight: 350, fontSize: 42, lineHeight: 1.4,
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
      </AbsoluteFill>
      <Grain />
    </AbsoluteFill>
  );
};
