import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { inkFlash, PAL, TOK, tprog } from "../kit2/tokens";
import { Grain, MassCamera, MONO, PageBg, SANS } from "../kit2/world";

// ============================================================================
// MASTER #5 — HOOK KINÉTICO (mundo de la página).
// El titular que frena el scroll: grotesca FINA en MAYÚS con tracking (look
// bible), palabra por palabra con LA firma de Terminal — cada palabra entra
// con el destello gris→esmeralda→hueso (DIA: siempre la misma regla, solo
// cambia el contenido). La(s) palabra(s) acento REPOSAN en esmeralda (el
// único acento en reposo de la escena, como el stat verde del plan maestro).
// Cadencia legible (Netflix 17cps ≈ nunca más de ~3 palabras/s). Props=datos.
// ============================================================================

export type HookKineticoProps = {
  kicker?: string;
  words?: { t: string; accent?: boolean }[];
  tease?: string;
  foot?: string;
  land?: number;        // frame donde entra la PRIMERA palabra acento (ancla VO)
  durF?: number;
};

const D = TOK.dur;
const MX = 120;
const WORD_STAG = 9;    // ~0.3s por palabra ≈ 3.3 palabras/s (tope de lectura)

export const HookKinetico: React.FC<HookKineticoProps> = ({
  kicker = "LA NOTICIA",
  words = [],
  tease = "",
  foot = "",
  land,
  durF,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const total = durF ?? durationInFrames;

  const ruleAt = 4;
  const kickerAt = ruleAt + Math.round(D.ruleDrawF * 0.6);
  const wordsAt = kickerAt + D.enterF + 2;

  // ancla del VO: si viene land, la primera palabra acento entra EXACTO ahí
  const accentIdx = Math.max(0, words.findIndex((w) => w.accent));
  const defaultAccentAt = wordsAt + accentIdx * WORD_STAG;
  const shift = land != null ? land - defaultAccentAt : 0;
  const startAt = wordsAt + shift;

  const lastWordAt = startAt + (words.length - 1) * WORD_STAG;
  const teaseAt = lastWordAt + D.enterF + 10;
  const exitAt = total - D.exitF - 2;

  const rule = tprog(frame, ruleAt, ruleAt + D.ruleDrawF, "standard");
  const kickerT = tprog(frame, kickerAt, kickerAt + D.enterF);
  const teaseT = tprog(frame, teaseAt, teaseAt + D.enterF);
  const exitO = 1 - tprog(frame, exitAt, exitAt + D.exitF, "exit");

  return (
    <AbsoluteFill style={{ fontFamily: SANS }}>
      <PageBg energy={0.06} />
      <MassCamera durF={total} seed={5}>
        <div style={{ opacity: exitO }}>
          <div style={{ position: "absolute", top: 560, left: MX, width: (1080 - 2 * MX) * rule, height: 1, background: PAL.lineSoft }} />
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

          {/* titular: grotesca fina MAYÚS, palabra por palabra con LA firma */}
          <div
            style={{
              position: "absolute", top: 730, left: MX, right: MX,
              display: "flex", flexWrap: "wrap", columnGap: 26, rowGap: 14,
              maxWidth: 860,
            }}
          >
            {words.map((w, i) => {
              const at = startAt + i * WORD_STAG;
              const t = tprog(frame, at, at + D.enterF);
              const rest = w.accent ? PAL.accent : PAL.ink;
              return (
                <span
                  key={i}
                  style={{
                    fontFamily: SANS, fontWeight: 320, fontSize: 84, lineHeight: 1.18,
                    textTransform: "uppercase", letterSpacing: "0.05em",
                    color: inkFlash(t, rest),
                    opacity: Math.min(1, t * 1.5),
                    transform: `translateY(${(1 - t) * 14}px)`,
                  }}
                >
                  {w.t}
                </span>
              );
            })}
          </div>

          {tease ? (
            <div
              style={{
                position: "absolute", top: 730 + Math.ceil(words.length / 3.2) * 118 + 70,
                left: MX, right: MX,
                fontFamily: SANS, fontWeight: 350, fontSize: 44, lineHeight: 1.4,
                color: inkFlash(teaseT, PAL.dim), opacity: Math.min(1, teaseT * 1.4),
                transform: `translateY(${(1 - teaseT) * 10}px)`, maxWidth: 720,
              }}
            >
              {tease}
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
