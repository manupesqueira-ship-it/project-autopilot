import React from "react";
import {
  AbsoluteFill,
  interpolate,
  OffthreadVideo,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { theme } from "./theme";
import { StudioScene } from "./studio/StudioScene";

// Showcase del hero 3D BESPOKE (Blender): composicion de monedas de oro renderizada
// en Cycles/OptiX bajo un HDRI CC0 real -> WebM transparente compuesto sobre la
// StudioScene oscura locked. El objeto YA trae su vida (push-in + deriva + motion
// blur del render), por eso aqui NO se le agrega float/tilt CSS (doble-movimiento).
// Solo el contexto de estudio: spotlight dorado, glow radial detras y sombra de piso.
// SIN texto horneado ni overlay (la cifra exacta la pone Remotion en un beat aparte);
// esto muestra el CRAFT del objeto. $0, brand-safe, 100% nuestro.
export const HeroCoin3D: React.FC<{ size?: number }> = ({ size = 1380 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = spring({ frame, fps, config: { damping: 16, mass: 0.9 } });
  const glowPulse = 0.62 + Math.sin(frame / 13) * 0.38;
  // El cluster de monedas vive en el TERCIO INFERIOR del render 1080² (la esfera
  // envolvente deja aire arriba). size>frame + cy alto lo suben al centro optico y
  // lo agrandan -> el hero MANDA el cuadro, con carril de caption arriba y numero abajo.
  const cy = 690;

  return (
    <StudioScene spotlightColor={theme.gold} grid push={false}>
      {/* glow radial dorado detras del hero -> pop premium sobre el fondo oscuro */}
      <div
        style={{
          position: "absolute",
          left: "50%",
          top: cy,
          width: size * 1.08,
          height: size * 1.08,
          marginLeft: -(size * 1.08) / 2,
          marginTop: -(size * 1.08) / 2,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${theme.gold}33 0%, ${theme.gold}12 42%, transparent 66%)`,
          filter: "blur(26px)",
          opacity: enter * glowPulse,
        }}
      />

      {/* objeto 3D transparente (WebM Blender), centrado en su carril */}
      <div
        style={{
          position: "absolute",
          left: "50%",
          top: cy,
          width: size,
          height: size,
          marginLeft: -size / 2,
          marginTop: -size / 2,
          opacity: enter,
          transform: `translateY(${(1 - enter) * 36}px)`,
        }}
      >
        <OffthreadVideo
          src={staticFile("hero/coins.webm")}
          transparent
          muted
          style={{
            width: "100%",
            height: "100%",
            objectFit: "contain",
            filter: "drop-shadow(0 28px 60px rgba(0,0,0,0.55))",
          }}
        />
      </div>

      {/* sombra de piso eliptica bajo el hero */}
      <div
        style={{
          position: "absolute",
          left: "50%",
          top: cy + size * 0.33,
          width: size * 0.6,
          height: size * 0.13,
          marginLeft: -(size * 0.6) / 2,
          borderRadius: "50%",
          background: "radial-gradient(ellipse, rgba(0,0,0,0.55) 0%, transparent 70%)",
          filter: "blur(22px)",
          opacity: interpolate(enter, [0, 1], [0, 1]),
        }}
      />
    </StudioScene>
  );
};
