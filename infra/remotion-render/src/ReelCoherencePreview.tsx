import React from "react";
import { Series } from "remotion";
import { KineticTextPremium } from "./beats/KineticTextPremium";
import { ElSalvadorMapHero } from "./beats/ElSalvadorMapHero";
import { MovingHero } from "./beats/MovingHero";
import { RecoveryChartPremium } from "./beats/RecoveryChartPremium";
import { HoldingsGainBars } from "./beats/HoldingsGainBars";

// Stitch MUDO de coherencia (NO el corte final con voz/xfade — eso vive en
// build916.py). Sirve para juzgar EN VIDEO si los dos mundos cortan coherentes:
//   - beats "sobre el piso iluminado" (hook / recovery / holdings = PremiumStage)
//   - el plano establishing full-bleed (mapa = océano/void biblia igloo)
// Comparten paleta + grano + tipografía. Cortes duros a propósito (honestos).
// Orden del guion El Salvador: b1 hook -> b2 mapa -> [b3 bukele gated] -> b4
// recovery -> b5+b6 holdings (combinado: barras + ganancia hero).

export const COHERENCE_HOOK = 100;
export const COHERENCE_MAP = 120;
export const COHERENCE_BUKELE = 150;
export const COHERENCE_RECOVERY = 150;
export const COHERENCE_HOLDINGS = 150;
export const COHERENCE_TOTAL =
  COHERENCE_HOOK +
  COHERENCE_MAP +
  COHERENCE_BUKELE +
  COHERENCE_RECOVERY +
  COHERENCE_HOLDINGS;

export const ReelCoherencePreview: React.FC = () => {
  return (
    <Series>
      <Series.Sequence durationInFrames={COHERENCE_HOOK}>
        <KineticTextPremium />
      </Series.Sequence>
      <Series.Sequence durationInFrames={COHERENCE_MAP}>
        <ElSalvadorMapHero />
      </Series.Sequence>
      <Series.Sequence durationInFrames={COHERENCE_BUKELE}>
        <MovingHero clip="b3_bukele" />
      </Series.Sequence>
      <Series.Sequence durationInFrames={COHERENCE_RECOVERY}>
        <RecoveryChartPremium />
      </Series.Sequence>
      <Series.Sequence durationInFrames={COHERENCE_HOLDINGS}>
        <HoldingsGainBars />
      </Series.Sequence>
    </Series>
  );
};
