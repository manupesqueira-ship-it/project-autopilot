import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { theme } from "../theme";

export const StudioScene: React.FC<{
  children: React.ReactNode;
  grid?: boolean;
  spotlightColor?: string;
  push?: boolean;
}> = ({ children, grid = true, spotlightColor = theme.green, push = true }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const scale = push
    ? interpolate(frame, [0, durationInFrames], [1, 1.045], {
        easing: Easing.bezier(0.33, 0, 0.67, 1),
      })
    : 1;

  // Costuras entre beats: las maneja el xfade real del ensamblador (assemble()
  // en build916.py) + el dip de musica. Aqui el contenido se muestra completo;
  // la opacidad por-beat fue insuficiente (el fondo compartido no daba contraste
  // de pausa y los whips la pisaban).
  return (
    <AbsoluteFill style={{ background: theme.bg.gradient }}>
      {/* spotlight radial — "oscuro pero BIEN ILUMINADO" con luz NEUTRA: el color
          lo pone el CONTENIDO (el número verde = ganancia), no el cuarto. Antes el
          wash verde 15% teñía todo y aplanaba los beats de texto (verde-sobre-verde
          mata el pop). Core blanco más fuerte = sigue bien iluminado, no vacío negro. */}
      <AbsoluteFill
        style={{
          background: `radial-gradient(ellipse 74% 48% at 50% 42%, rgba(255,255,255,0.11) 0%, rgba(255,255,255,0.05) 26%, ${spotlightColor}10 52%, transparent 76%)`,
        }}
      />
      {/* piso con luz para subir luminancia */}
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(180deg, transparent 66%, rgba(160,176,200,0.10) 86%, rgba(170,186,210,0.16) 100%)",
        }}
      />
      {grid && (
        <svg
          width="1080"
          height="1920"
          style={{ position: "absolute", opacity: 0.5 }}
        >
          <defs>
            <radialGradient id="gridfade" cx="38%" cy="32%" r="55%">
              <stop offset="0%" stopColor="white" stopOpacity="0.07" />
              <stop offset="100%" stopColor="white" stopOpacity="0" />
            </radialGradient>
            <mask id="gridmask">
              <rect width="1080" height="1920" fill="url(#gridfade)" />
            </mask>
          </defs>
          <g mask="url(#gridmask)">
            {Array.from({ length: 14 }).map((_, i) => (
              <line
                key={`v${i}`}
                x1={i * 84}
                y1={0}
                x2={i * 84}
                y2={1920}
                stroke="white"
                strokeWidth={1.4}
              />
            ))}
            {Array.from({ length: 24 }).map((_, i) => (
              <line
                key={`h${i}`}
                x1={0}
                y1={i * 84}
                x2={1080}
                y2={i * 84}
                stroke="white"
                strokeWidth={1.4}
              />
            ))}
          </g>
        </svg>
      )}
      <AbsoluteFill style={{ transform: `scale(${scale})` }}>
        {children}
      </AbsoluteFill>
      {/* viñeta suave (no agresiva) */}
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(ellipse 95% 72% at 50% 46%, transparent 62%, rgba(0,0,0,0.42) 100%)",
          pointerEvents: "none",
        }}
      />
      {/* grano 3-5% */}
      <AbsoluteFill style={{ opacity: theme.grainOpacity, pointerEvents: "none" }}>
        <svg width="1080" height="1920">
          <filter id="grain">
            <feTurbulence
              type="fractalNoise"
              baseFrequency="0.9"
              numOctaves="2"
              seed={7}
            />
            <feColorMatrix type="saturate" values="0" />
          </filter>
          <rect width="1080" height="1920" filter="url(#grain)" />
        </svg>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
