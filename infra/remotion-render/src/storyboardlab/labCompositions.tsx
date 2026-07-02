import React from "react";
import { Composition } from "remotion";
import { Styleframe, LAB_W, LAB_H } from "./Styleframe";
import { ContactSheet } from "./ContactSheet";
import { SideBySide } from "./SideBySide";
import { ErosionRace } from "./ErosionRace";
import { FullReelC, FULL_REEL_C_DURATION } from "./FullReelC";
import { s0_inicial, s0_maxinfo, s0_salida, s1_comparison, reelC_storyboard } from "./reel_c_frames";

// Compositions del STORYBOARD LAB (aisladas; no tocan el pipeline).
// Para exportar un styleframe a PNG:
//   npx remotion still src/index.ts Lab-ReelC-S0-maxinfo out/c0_maxinfo.png
// Para verlo con safe-areas/grid: abrir Remotion Studio y togglear los props.
export const StoryboardLabCompositions: React.FC = () => {
  return (
    <>
      <Composition
        id="Lab-Styleframe"
        component={Styleframe}
        durationInFrames={30}
        fps={30}
        width={LAB_W}
        height={LAB_H}
        defaultProps={{ spec: s0_maxinfo, showSafe: true, showGrid: false, showUI: true, gridCols: 12 }}
      />
      <Composition
        id="Lab-ReelC-S0-inicial"
        component={Styleframe}
        durationInFrames={30}
        fps={30}
        width={LAB_W}
        height={LAB_H}
        defaultProps={{ spec: s0_inicial, showSafe: false, showGrid: false, showUI: false, gridCols: 12 }}
      />
      <Composition
        id="Lab-ReelC-S0-maxinfo"
        component={Styleframe}
        durationInFrames={30}
        fps={30}
        width={LAB_W}
        height={LAB_H}
        defaultProps={{ spec: s0_maxinfo, showSafe: false, showGrid: false, showUI: false, gridCols: 12 }}
      />
      <Composition
        id="Lab-ReelC-S0-salida"
        component={Styleframe}
        durationInFrames={30}
        fps={30}
        width={LAB_W}
        height={LAB_H}
        defaultProps={{ spec: s0_salida, showSafe: false, showGrid: false, showUI: false, gridCols: 12 }}
      />
      <Composition
        id="Lab-ReelC-Storyboard"
        component={ContactSheet}
        durationInFrames={30}
        fps={30}
        width={LAB_W}
        height={LAB_H}
        defaultProps={{ frames: reelC_storyboard, thumbW: 300, title: "Reel C — storyboard (6 escenas)" }}
      />
      <Composition
        id="Lab-SideBySide"
        component={SideBySide}
        durationInFrames={30}
        fps={30}
        width={1100}
        height={980}
        defaultProps={{ ours: s1_comparison, refImageSrc: null, refSpec: null, colW: 520 }}
      />
      <Composition
        id="Lab-ReelC-ErosionRace"
        component={ErosionRace}
        durationInFrames={220}
        fps={30}
        width={LAB_W}
        height={LAB_H}
      />
      <Composition
        id="Lab-ReelC-Full"
        component={FullReelC}
        durationInFrames={FULL_REEL_C_DURATION}
        fps={30}
        width={LAB_W}
        height={LAB_H}
      />
    </>
  );
};
