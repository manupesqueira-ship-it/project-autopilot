import { linearTiming, TransitionSeries } from "@remotion/transitions";
import React from "react";
import { AbsoluteFill, CalculateMetadataFunction, Sequence } from "remotion";
import { PAL } from "./tokens";
import { Grain, MONO, PageBg, SANS } from "./world";
import { TRANS_CATALOG, TRANS_NAMES } from "./transitions";

// ============================================================================
// GALERÍA DE TRANSICIONES — para el GATE de Manuel: cada transición del
// catálogo entre dos escenas representativas del mundo (A oscura con cifra,
// B con placa clara y palabra), con su NOMBRE en pantalla. Nada entra al menú
// del director sin aprobarse aquí (mismo proceso que los 5 masters).
// ============================================================================

const SCENE_F = 34;   // frames por escena (suficiente para leer el corte)

const SceneA: React.FC<{ label: string }> = ({ label }) => (
  <AbsoluteFill style={{ fontFamily: SANS, backgroundColor: PAL.bg }}>
    <PageBg energy={0.05} />
    <div style={{ position: "absolute", top: 636, left: 120, right: 120, height: 1, background: PAL.lineSoft }} />
    <div style={{ position: "absolute", top: 700, left: 120, fontFamily: MONO, fontWeight: 500, fontSize: 170, color: PAL.ink }}>
      $128
    </div>
    <div style={{ position: "absolute", top: 920, left: 120, fontFamily: MONO, fontSize: 26, letterSpacing: "0.3em", color: PAL.dim, textTransform: "uppercase" }}>
      ESCENA A
    </div>
    <div style={{ position: "absolute", top: 90, left: 120, right: 120, fontFamily: MONO, fontSize: 34, letterSpacing: "0.18em", color: PAL.accent }}>
      {label}
    </div>
    <Grain />
  </AbsoluteFill>
);

const SceneB: React.FC<{ label: string }> = ({ label }) => (
  <AbsoluteFill style={{ fontFamily: SANS, backgroundColor: "#101210" }}>
    <PageBg energy={0.08} />
    <AbsoluteFill style={{ background: "linear-gradient(160deg, rgba(46,203,79,0.08), transparent 55%)" }} />
    <div style={{ position: "absolute", top: 800, left: 120, fontWeight: 320, fontSize: 96, color: PAL.ink, textTransform: "uppercase", letterSpacing: "0.02em" }}>
      Escena B
    </div>
    <div style={{ position: "absolute", top: 940, left: 120, fontFamily: MONO, fontSize: 26, letterSpacing: "0.3em", color: PAL.dim }}>
      LA SIGUIENTE IDEA
    </div>
    <div style={{ position: "absolute", top: 90, left: 120, right: 120, fontFamily: MONO, fontSize: 34, letterSpacing: "0.18em", color: PAL.accent }}>
      {label}
    </div>
    <Grain />
  </AbsoluteFill>
);

export type TransGalleryProps = { names?: string[] };

const pairDur = (name: string) => 2 * SCENE_F - TRANS_CATALOG[name].defaultF;

export const TransGallery: React.FC<TransGalleryProps> = ({ names = TRANS_NAMES }) => {
  let at = 0;
  return (
    <AbsoluteFill style={{ backgroundColor: PAL.bg }}>
      {names.map((name) => {
        const spec = TRANS_CATALOG[name];
        const start = at;
        at += pairDur(name);
        return (
          <Sequence key={name} from={start} durationInFrames={pairDur(name)}>
            <TransitionSeries>
              <TransitionSeries.Sequence durationInFrames={SCENE_F}>
                <SceneA label={`${name} · ${spec.defaultF}f`} />
              </TransitionSeries.Sequence>
              <TransitionSeries.Transition
                presentation={spec.presentation}
                timing={linearTiming({ durationInFrames: spec.defaultF })}
              />
              <TransitionSeries.Sequence durationInFrames={SCENE_F}>
                <SceneB label={`${name} · ${spec.uso}`} />
              </TransitionSeries.Sequence>
            </TransitionSeries>
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};

export const calcTransGallery: CalculateMetadataFunction<TransGalleryProps> = ({ props }) => {
  const names = props.names ?? TRANS_NAMES;
  return { durationInFrames: Math.max(60, names.reduce((s, n) => s + pairDur(n), 0)) };
};
