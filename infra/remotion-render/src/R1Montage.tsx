import React from "react";
import {
  AbsoluteFill,
  OffthreadVideo,
  Sequence,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { theme } from "./theme";
import { StudioScene } from "./studio/StudioScene";
import { BrandSignature } from "./studio/BrandSignature";
import { NapkinWriteOn } from "./beats/NapkinWriteOn";

// R1Montage -- reel de VALIDACION del salto de calidad (NO un video publicable).
// Encadena las piezas 3D nuevas para que Manuel juzgue luz/DoF/motion-blur (en los
// renders Blender) y el acabado bloom/grano/vineta (se aplica DESPUES con
// post_finish.py, Track A5). Es SILENCIOSO a proposito: la voz ElevenLabs es gasto
// de API gateado; el juicio de luz/DoF/bloom no la necesita.
//
// Cada segmento dura lo que su WebM (la animacion del render esta horneada a ese
// largo): hero 84f, chart 70f, demo 60f, napkin 96f. Los WebM Blender son RGBA
// transparentes -> OffthreadVideo `transparent` sobre el StudioScene (mismo patron
// que HeroBeat en Composition.tsx). El chart NO lleva tag de texto encima (regla
// locked: durante un chart no va titulo). La firma de marca (C3) va en TODO el
// montaje (placeholder procedural $0; public/brand vacio -> glifo neutro).

const HERO_F = 84;
const CHART_F = 70;
const DEMO_F = 60;
const NAPKIN_F = 96;
export const R1_TOTAL = HERO_F + CHART_F + DEMO_F + NAPKIN_F;

// fade in/out por segmento (frame local de la Sequence) -> costuras suaves sin
// depender del xfade del ensamblador (esto es un montaje de QC standalone).
const useFade = (edge = 9) => {
  const f = useCurrentFrame();
  const { durationInFrames: d } = useVideoConfig();
  return interpolate(f, [0, edge, d - edge, d], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
};

// etiqueta de QC (tenue, en el safe-area de arriba): scaffolding para que Manuel
// sepa que pieza ve. Deliberadamente dim/pequena para NO competir con el objeto.
const Tag: React.FC<{ text: string }> = ({ text }) => (
  <div
    style={{
      position: "absolute",
      top: 64,
      width: "100%",
      textAlign: "center",
      fontFamily: theme.font,
      fontSize: 25,
      fontWeight: 600,
      letterSpacing: "0.18em",
      textTransform: "uppercase",
      color: theme.textDim,
      opacity: 0.62,
    }}
  >
    {text}
  </div>
);

// objeto 3D transparente (WebM Blender) centrado sobre el StudioScene.
const Hero3DSegment: React.FC<{
  src: string;
  size?: number;
  tag?: string;
  spotlight?: string;
}> = ({ src, size = 1000, tag, spotlight = theme.green }) => {
  const op = useFade();
  return (
    <AbsoluteFill style={{ opacity: op }}>
      <StudioScene spotlightColor={spotlight} grid>
        <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
          <OffthreadVideo
            src={src}
            transparent
            muted
            style={{
              width: size,
              height: size,
              objectFit: "contain",
              marginTop: -90,
              filter: "drop-shadow(0 26px 64px rgba(0,0,0,0.5))",
            }}
          />
        </AbsoluteFill>
      </StudioScene>
      {tag && <Tag text={tag} />}
    </AbsoluteFill>
  );
};

const NapkinSegment: React.FC = () => {
  const op = useFade();
  return (
    <AbsoluteFill style={{ opacity: op }}>
      {/* copy PLACEHOLDER (lo decide Manuel) — aqui solo demuestra el write-on */}
      <NapkinWriteOn napkin="napkin_2" promise="ahorro mensual" formula="$2,000 MXN" />
      <Tag text="set-piece · servilleta · B2" />
    </AbsoluteFill>
  );
};

export const R1Montage: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: theme.bg.base }}>
      <Sequence from={0} durationInFrames={HERO_F}>
        <Hero3DSegment
          src={staticFile("r1/hero.webm")}
          tag="hero-shot · lingote · B3"
          spotlight={theme.gold}
          size={1040}
        />
      </Sequence>

      <Sequence from={HERO_F} durationInFrames={CHART_F}>
        {/* chart domina sin texto encima (regla locked) -> sin Tag */}
        <Hero3DSegment src={staticFile("r1/chart.webm")} spotlight={theme.green} size={1060} />
      </Sequence>

      <Sequence from={HERO_F + CHART_F} durationInFrames={DEMO_F}>
        <Hero3DSegment
          src={staticFile("r1/demo.webm")}
          tag="tipografía 3D extruida · A3"
          spotlight={theme.gold}
          size={1000}
        />
      </Sequence>

      <Sequence from={HERO_F + CHART_F + DEMO_F} durationInFrames={NAPKIN_F}>
        <NapkinSegment />
      </Sequence>

      {/* C3: firma de marca en CADA video (placeholder procedural $0) */}
      <BrandSignature wordmark="DINERO LATAM" placement="tl" />
    </AbsoluteFill>
  );
};
