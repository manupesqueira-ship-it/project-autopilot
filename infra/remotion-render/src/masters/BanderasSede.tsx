import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { inkFlash, PAL, TOK, tprog } from "../kit2/tokens";
import { Grain, MassCamera, MONO, PageBg, SANS } from "../kit2/world";

// ============================================================================
// MASTER #7 — BANDERAS / SEDES (mundo de la página).
// "Si me vas a hablar del Mundial, pon las banderas de México, EE.UU. y Canadá"
// (Manuel, 2026-07-03). Banderas REALES (country-flag-icons, vector oficial —
// regla dura: assets reales, nunca dibujados a mano) tratadas al mundo: placa
// enmarcada con hairline, entrada secuencial con masa, dato mono debajo de cada
// una (partidos/sedes), y el protagonista (México) con el destello. Props=datos.
// ============================================================================

import * as Flags from "country-flag-icons/react/3x2";

export type SedeItem = {
  iso2: string;        // "MX" | "US" | "CA"
  name: string;        // "MÉXICO"
  stat: string;        // "13 PARTIDOS · 3 SEDES"
  accent?: boolean;    // protagonista (destello + reposo esmeralda en el stat)
};

export type BanderasSedeProps = {
  kicker?: string;
  items?: SedeItem[];
  sub?: string;
  foot?: string;
  land?: number;       // frame donde entra el protagonista (ancla VO)
  durF?: number;
};

const D = TOK.dur;
const MX_ = 120;

export const BanderasSede: React.FC<BanderasSedeProps> = ({
  kicker = "TRES PAÍSES, UNA COPA",
  items = [],
  sub = "",
  foot = "",
  land,
  durF,
}) => {
  const frame = useCurrentFrame();
  const total = durF ?? 240;

  const ruleAt = 4;
  const kickerAt = ruleAt + Math.round(D.ruleDrawF * 0.6);
  const firstAt = kickerAt + D.enterF + 4;
  const gap = Math.round(D.barRevealF * 0.55);

  // protagonista SIEMPRE al final; su entrada se ancla al VO
  const order = [...items.map((_, i) => i).filter((i) => !items[i].accent),
                 ...items.map((_, i) => i).filter((i) => items[i].accent)];
  const enterAt: number[] = [];
  order.forEach((idx, k) => (enterAt[idx] = firstAt + k * gap));
  const accIdx = items.findIndex((x) => x.accent);
  if (accIdx >= 0 && land != null) {
    enterAt[accIdx] = Math.max(land - D.enterF, firstAt + gap);
  }

  const lastIn = Math.max(...enterAt.map((a) => a ?? firstAt), firstAt) + D.enterF;
  const subAt = lastIn + 10;
  const exitAt = total - D.exitF - 2;

  const rule = tprog(frame, ruleAt, ruleAt + D.ruleDrawF, "standard");
  const kickerT = tprog(frame, kickerAt, kickerAt + D.enterF);
  const subT = tprog(frame, subAt, subAt + D.enterF);
  const exitO = 1 - tprog(frame, exitAt, exitAt + D.exitF, "exit");

  const CARD_W = 260;
  const CARD_H = 174;
  const totalW = items.length * CARD_W + (items.length - 1) * 60;
  const startX = (1080 - totalW) / 2;

  return (
    <AbsoluteFill style={{ fontFamily: SANS }}>
      <PageBg energy={0.06} />
      <MassCamera durF={total} seed={8}>
        <div style={{ opacity: exitO }}>
          <div style={{ position: "absolute", top: 636, left: MX_, width: (1080 - 2 * MX_) * rule, height: 1, background: PAL.lineSoft }} />
          <div
            style={{
              position: "absolute", top: 668, left: MX_, right: MX_,
              fontFamily: MONO, fontWeight: 500, fontSize: 30, letterSpacing: "0.32em",
              textTransform: "uppercase", color: inkFlash(kickerT, PAL.dim),
              opacity: Math.min(1, kickerT * 1.4), transform: `translateY(${(1 - kickerT) * 10}px)`,
            }}
          >
            {kicker}
          </div>

          {items.map((it, i) => {
            const FlagComp = (Flags as Record<string, React.FC<{ style?: React.CSSProperties }>>)[it.iso2];
            const t = tprog(frame, enterAt[i] ?? firstAt, (enterAt[i] ?? firstAt) + D.enterF);
            const x = startX + i * (CARD_W + 60);
            const restStat = it.accent ? PAL.accent : PAL.faint;
            return (
              <div key={i} style={{ position: "absolute", left: x, top: 860, width: CARD_W, opacity: Math.min(1, t * 1.4), transform: `translateY(${(1 - t) * 16}px)` }}>
                {/* placa: bandera real tratada al mundo (marco hairline + leve desat) */}
                <div style={{ width: CARD_W, height: CARD_H, border: `1px solid ${PAL.lineSoft}`, overflow: "hidden", filter: "saturate(0.82) brightness(0.94)" }}>
                  {FlagComp ? <FlagComp style={{ width: "100%", height: "100%", objectFit: "cover", display: "block" }} /> : null}
                </div>
                <div style={{ marginTop: 22, fontFamily: MONO, fontWeight: 500, fontSize: 27, letterSpacing: "0.2em", color: inkFlash(t, it.accent ? PAL.ink : PAL.dim) }}>
                  {it.name}
                </div>
                <div style={{ marginTop: 8, fontFamily: MONO, fontWeight: 400, fontSize: 21, letterSpacing: "0.12em", lineHeight: 1.6, color: inkFlash(t, restStat) }}>
                  {it.stat}
                </div>
              </div>
            );
          })}

          {sub ? (
            <div
              style={{
                position: "absolute", top: 1250, left: MX_, right: MX_,
                fontFamily: SANS, fontWeight: 350, fontSize: 42, lineHeight: 1.4,
                color: inkFlash(subT, PAL.dim), opacity: Math.min(1, subT * 1.4),
                transform: `translateY(${(1 - subT) * 10}px)`, maxWidth: 760,
              }}
            >
              {sub}
            </div>
          ) : null}

          {foot ? (
            <div style={{ position: "absolute", top: 1720, left: MX_, right: MX_, fontFamily: MONO, fontWeight: 400, fontSize: 21, letterSpacing: "0.22em", textTransform: "uppercase", color: PAL.faint, opacity: Math.min(1, kickerT) }}>
              {foot}
            </div>
          ) : null}
        </div>
      </MassCamera>
      <Grain />
    </AbsoluteFill>
  );
};
