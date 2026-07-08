import { linearTiming, TransitionSeries } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import React from "react";
import { AbsoluteFill, CalculateMetadataFunction } from "remotion";
import { PAL, TOK } from "../kit2/tokens";
import { TRANS_CATALOG } from "../kit2/transitions";
import { CarreraBars } from "./CarreraBars";
import { CifraHero } from "./CifraHero";
import { CompararBarras } from "./CompararBarras";
import { HookKinetico } from "./HookKinetico";
import { LineaHero } from "./LineaHero";

// ============================================================================
// MASTERS REEL — el reel ENTERO en el mundo de la página: secuencia de MASTERS
// congelados. El director/ensamblador SOLO pasa datos (props) y duraciones
// derivadas de la voz; el movimiento vive en los masters + tokens. Transiciones
// sobrias del mundo: cut o fade-por-negro (los masters ya salen con su exit
// acelerado, así que el fade compone un dip limpio sobre #070707).
// ============================================================================

export type MasterBeat = {
  type: "hook" | "cifra" | "linea" | "barras" | "carrera" | "cierre";
  props: Record<string, unknown>;
  durF: number;
  // "cut" | "dip" | cualquier nombre del TRANS_CATALOG (kit2/transitions)
  trans?: string;
  transF?: number;
};

// resuelve la transición saliente de un beat → {presentation, durF} o null (cut)
const resolveTrans = (b: MasterBeat) => {
  const t = b.trans ?? "cut";
  if (t === "cut") return null;
  if (t === "dip") {
    return {
      presentation: fade(),
      durF: b.transF ?? Math.round(TOK.dur.sceneTransitionF / 2),
    };
  }
  const spec = TRANS_CATALOG[t];
  if (!spec) return { presentation: fade(), durF: b.transF ?? 14 }; // fallback sobrio
  return { presentation: spec.presentation, durF: b.transF ?? spec.defaultF };
};
export type MastersReelProps = { beats: MasterBeat[] };

const MAP: Record<MasterBeat["type"], React.FC<Record<string, unknown>>> = {
  hook: HookKinetico as never,
  cifra: CifraHero as never,
  linea: LineaHero as never,
  barras: CompararBarras as never,
  carrera: CarreraBars as never,
  cierre: HookKinetico as never,   // el cierre habla el mismo lenguaje del hook
};

export const MastersReel: React.FC<MastersReelProps> = ({ beats = [] }) => {
  return (
    <AbsoluteFill style={{ backgroundColor: PAL.bg }}>
      <TransitionSeries>
        {beats.flatMap((b, i) => {
          const Comp = MAP[b.type];
          const out: React.ReactNode[] = [
            <TransitionSeries.Sequence key={`s${i}`} durationInFrames={b.durF}>
              <Comp {...b.props} durF={b.durF} />
            </TransitionSeries.Sequence>,
          ];
          const tr = i < beats.length - 1 ? resolveTrans(b) : null;
          if (tr) {
            out.push(
              <TransitionSeries.Transition
                key={`t${i}`}
                presentation={tr.presentation}
                timing={linearTiming({ durationInFrames: tr.durF })}
              />,
            );
          }
          return out;
        })}
      </TransitionSeries>
    </AbsoluteFill>
  );
};

export const calcMastersReel: CalculateMetadataFunction<MastersReelProps> = ({ props }) => {
  const beats = props.beats || [];
  let total = 0;
  beats.forEach((b, i) => {
    total += b.durF;
    if (i < beats.length - 1) {
      const tr = resolveTrans(b);
      if (tr) total -= tr.durF;
    }
  });
  return { durationInFrames: Math.max(60, total) };
};
