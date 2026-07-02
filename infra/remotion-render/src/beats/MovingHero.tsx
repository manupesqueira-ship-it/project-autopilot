import React from "react";
import {
  AbsoluteFill,
  Img,
  OffthreadVideo,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { theme } from "../theme";

// BeatHeroShot — el beat que SE MUEVE (la firma del canal). Dos motores:
//
//  1) clip i2v (still gpt-image-1 + movimiento Kling) a pantalla completa: ACTIVO
//     DE PAGA cacheado en public/i2v/<clip>.mp4 (caricatura-fino que SE MUEVE).
//
//  2) photo: FOTO REAL de una figura publica mencionada (Bukele, Milei, Trump…) en
//     public/photos/<photo>.jpg. b-roll NO hablado, $0, determinista: push-in
//     lentisimo (Ken Burns) + grade cinematografico OSCURO para que el retrato se
//     siente en el mundo igloo.inc del reel (vignette al rostro, wash navy frio,
//     grano). Sin morphing de IA sobre una cara real (eso se veia "chafa").
//
// Encima, OPCIONAL, un KICKER (titular-gancho) que entra suave y vive en la franja
// inferior sobre un velo. El clip i2v suele ser MAS corto que el beat (la voz
// manda) -> playbackRate<1 lo estira en camara lenta.
export type MovingHeroProps = {
  clip?: string; // stem del mp4 en public/i2v/<clip>.mp4 (motor i2v de paga)
  photo?: string; // stem del jpg en public/photos/<photo>.jpg (foto real, $0)
  kicker?: string; // titular-gancho opcional (español, NO subtítulo de la voz)
  accentColor?: string;
  playbackRate?: number; // estira el clip i2v en cámara lenta (<=1)
};

// Retrato real + Ken Burns + grade cinematográfico oscuro (igloo.inc).
const PhotoHero: React.FC<{ photo: string }> = ({ photo }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  // push-in continuo TODO el beat (sin congelar): 1.05 -> 1.16, deriva mínima.
  // transform-origin sesgado al rostro -> la cámara entra a la cara, no al torso.
  const prog = interpolate(frame, [0, durationInFrames], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const scale = 1.05 + prog * 0.11;
  const ty = (0.5 - prog) * 1.4; // %

  return (
    <AbsoluteFill>
      <Img
        src={staticFile(`photos/${photo}.jpg`)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          objectPosition: "center 30%",
          transform: `scale(${scale}) translateY(${ty}%)`,
          transformOrigin: "50% 32%",
        }}
      />
      {/* vignette al rostro: oscurece bordes y enfoca la cara */}
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(125% 95% at 50% 34%, transparent 36%, rgba(7,11,18,0.64) 100%)",
        }}
      />
      {/* gradiente cine arriba/abajo (sienta el retrato en lo oscuro + velo CTA) */}
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(180deg, rgba(9,13,20,0.55) 0%, transparent 24%, transparent 60%, rgba(7,10,15,0.80) 100%)",
        }}
      />
      {/* wash navy (cohesión con el mundo del reel + enfría los blancos del traje) */}
      <AbsoluteFill
        style={{
          backgroundColor: theme.bg.base,
          mixBlendMode: "soft-light",
          opacity: 0.5,
        }}
      />
      {/* grano fino (igloo.inc): textura, mata el look "foto de stock plana" */}
      <AbsoluteFill
        style={{ opacity: 0.05, mixBlendMode: "overlay", pointerEvents: "none" }}
      >
        <svg width="100%" height="100%">
          <filter id="heroGrain">
            <feTurbulence
              type="fractalNoise"
              baseFrequency="0.9"
              numOctaves={2}
              stitchTiles="stitch"
            />
          </filter>
          <rect width="100%" height="100%" filter="url(#heroGrain)" />
        </svg>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

export const MovingHero: React.FC<MovingHeroProps> = ({
  clip,
  photo,
  kicker,
  accentColor = theme.green,
  playbackRate = 1,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // el kicker entra tras ~14f: sube unos px con un spring suave
  const k = spring({ frame: frame - 14, fps, config: { damping: 16, mass: 0.8 } });
  const kickerY = (1 - k) * 40;

  return (
    <AbsoluteFill
      style={{ backgroundColor: theme.bg.base, fontFamily: theme.font }}
    >
      {photo ? (
        <PhotoHero photo={photo} />
      ) : (
        <OffthreadVideo
          src={staticFile(`i2v/${clip}.mp4`)}
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
          muted
          playbackRate={playbackRate}
        />
      )}

      {kicker && (
        <>
          {/* velo inferior: legibilidad del titular sin tapar al objeto (centrado) */}
          <AbsoluteFill
            style={{
              background:
                "linear-gradient(180deg, transparent 55%, rgba(7,10,15,0.55) 80%, rgba(7,10,15,0.88) 100%)",
              opacity: k,
            }}
          />
          <div
            style={{
              position: "absolute",
              left: 84,
              right: 84,
              bottom: 360,
              textAlign: "center",
              transform: `translateY(${kickerY}px)`,
              opacity: k,
            }}
          >
            <div
              style={{
                width: 64,
                height: 5,
                borderRadius: 3,
                margin: "0 auto 28px",
                background: accentColor,
                boxShadow: `0 0 18px ${accentColor}aa`,
              }}
            />
            <div
              style={{
                fontSize: 64,
                fontWeight: 800,
                lineHeight: 1.08,
                letterSpacing: "-0.01em",
                color: theme.text,
                textShadow: "0 4px 28px rgba(0,0,0,0.65)",
              }}
            >
              {kicker}
            </div>
          </div>
        </>
      )}
    </AbsoluteFill>
  );
};
