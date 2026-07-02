import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  OffthreadVideo,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { theme } from "../theme";

// MovingDataPremium — REPLANTEO del lenguaje de data-viz (rechazo Manuel
// 2026-06-26: el overlay plano sobre el video estaba "dramaticamente aburrido").
// Aqui la data NO es un HUD plano: es motion-graphics INTEGRADA al mundo i2v.
//   · cifra heroe en el espacio negativo del lecho (no una caja sobre velo)
//   · contada al RITMO de la accion (termina cuando el personaje aterriza)
//   · barrido especular sobre los digitos al aterrizar (premium, no neon)
//   · luz dorada DENTRO de la escena + pulso del colchon en el impacto
//   · regla de acento que se TRAZA + subline en stagger
//   · grade unico (grano + vineta) que funde lecho + overlay en UNA imagen
// Pensado para el clip "colchon": cae al colchon = el fondo de emergencia atrapa.

export type MovingDataPremiumProps = {
  clip: string; // stem en public/i2v/<clip>.mp4
  kicker?: string; // etiqueta chica arriba (NO subtitulo de la voz)
  prefix?: string;
  suffix?: string;
  value: number;
  subline?: string;
  accentColor?: string;
  landFrame?: number; // frame en que el personaje aterriza (sincroniza la cifra)
  revealFrame?: number; // frame en que la cifra ENTRA (cuando el cuerpo despeja el aire)
  decimals?: number;
};

const fmt = (n: number, d = 0) =>
  n.toLocaleString("es-MX", {
    minimumFractionDigits: d,
    maximumFractionDigits: d,
  });

export const MovingDataPremium: React.FC<MovingDataPremiumProps> = ({
  clip,
  kicker,
  prefix = "",
  suffix = "",
  value,
  subline,
  accentColor = theme.gold,
  landFrame,
  revealFrame,
  decimals = 0,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const D = durationInFrames;
  const land = landFrame ?? Math.round(D * 0.8);

  // la cifra NO debe chocar con el cuerpo que cae (regla: no encimar). Entra solo
  // cuando el personaje despeja el espacio negativo superior (verificado en
  // pixeles del lecho: ~0.36·D) y de ahi cuenta hasta CERRAR en el aterrizaje.
  const reveal0 = revealFrame ?? Math.round(D * 0.36);
  const countStart = reveal0;
  const reveal = interpolate(frame, [reveal0, reveal0 + 22], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  // cifra ATADA a la caida: cuenta 0 -> value y "cierra" cuando aterriza
  const shown = interpolate(frame, [countStart, land], [0, value], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  // entradas/impacto
  const kickIn = spring({ frame: frame - reveal0, fps, config: { damping: 18, mass: 0.8 } });
  const grow = spring({ frame: frame - countStart, fps, config: { damping: 16, mass: 0.9 } });
  const impactBump =
    frame >= land ? Math.sin(Math.min((frame - land) / 11, 1) * Math.PI) * 0.06 : 0;
  const numScale = 0.9 + 0.1 * grow + impactBump;

  // barrido especular sobre los digitos (una vez, al aterrizar)
  const sweep = interpolate(frame, [land, land + 26], [130, -40], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // regla de acento que se traza + subline
  const ruleW = interpolate(frame, [land + 2, land + 24], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const subIn = spring({ frame: frame - (land + 10), fps, config: { damping: 18, mass: 0.9 } });

  // luz dorada DENTRO de la escena (sube con la cuenta, pulso en el impacto)
  const lightOp =
    interpolate(frame, [countStart, land], [0, 0.42], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    }) + impactBump * 2.2;

  // pulso verde del colchon en el aterrizaje (la data toca el mundo)
  const cushionPulse =
    frame >= land - 4 ? Math.sin(Math.min((frame - (land - 4)) / 16, 1) * Math.PI) * 0.5 : 0;

  // vida: parallax sutil + push lento (la data vive en el espacio de la escena)
  const driftX = Math.cos(frame / 80) * 5;
  const driftY = Math.sin(frame / 60) * 6;
  const slowPush = interpolate(frame, [0, D], [0.992, 1.006]);

  return (
    <AbsoluteFill style={{ backgroundColor: theme.bg.base, fontFamily: theme.font }}>
      <OffthreadVideo
        src={staticFile(`i2v/${clip}.mp4`)}
        style={{ width: "100%", height: "100%", objectFit: "cover" }}
        muted
      />

      {/* scrim SUPERIOR tenue (navy del propio lecho) -> legibilidad sin "caja" */}
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(180deg, rgba(13,17,23,0.72) 0%, rgba(13,17,23,0.30) 26%, transparent 48%)",
        }}
      />

      {/* pulso del colchon (abajo-centro) cuando la cifra cierra */}
      <AbsoluteFill
        style={{
          background: `radial-gradient(36% 20% at 50% 74%, ${theme.green}55 0%, transparent 70%)`,
          opacity: cushionPulse,
          mixBlendMode: "screen",
        }}
      />

      {/* luz dorada en la escena, detras de la cifra */}
      <AbsoluteFill
        style={{
          background: `radial-gradient(46% 26% at 50% 24%, ${accentColor}66 0%, transparent 68%)`,
          opacity: Math.min(lightOp, 0.8),
          mixBlendMode: "screen",
          filter: "blur(8px)",
        }}
      />

      {/* grupo de DATA en el espacio negativo superior */}
      <div
        style={{
          position: "absolute",
          top: 300,
          left: 64,
          right: 64,
          textAlign: "center",
          opacity: reveal,
          transform: `translate(${driftX}px, ${driftY + (1 - reveal) * 28}px) scale(${slowPush})`,
        }}
      >
        {kicker && (
          <div
            style={{
              fontSize: 30,
              fontWeight: 700,
              letterSpacing: "0.34em",
              textTransform: "uppercase",
              color: theme.textDim,
              opacity: kickIn * 0.92,
              transform: `translateY(${(1 - kickIn) * -14}px)`,
              marginBottom: 26,
            }}
          >
            {kicker}
          </div>
        )}

        {/* cifra heroe: numero grande + unidad chica (jerarquia premium) */}
        <div
          style={{
            display: "inline-flex",
            alignItems: "baseline",
            justifyContent: "center",
            transform: `scale(${numScale})`,
            transformOrigin: "center",
            filter: `drop-shadow(0 10px 40px rgba(0,0,0,0.55))`,
          }}
        >
          <span
            style={{
              fontSize: 158,
              fontWeight: 800,
              letterSpacing: "-0.035em",
              lineHeight: 1,
              fontVariantNumeric: "tabular-nums",
              backgroundImage: `linear-gradient(100deg, ${accentColor} 0%, ${accentColor} 42%, #FFF4DD 50%, ${accentColor} 58%, ${accentColor} 100%)`,
              backgroundSize: "300% 100%",
              backgroundPosition: `${sweep}% 0`,
              WebkitBackgroundClip: "text",
              backgroundClip: "text",
              color: "transparent",
            }}
          >
            {prefix}
            {fmt(shown, decimals)}
          </span>
          {suffix && (
            <span
              style={{
                fontSize: 56,
                fontWeight: 700,
                marginLeft: 14,
                color: accentColor,
                opacity: 0.92,
              }}
            >
              {suffix}
            </span>
          )}
        </div>

        {/* regla de acento que se traza */}
        <div style={{ height: 34, marginTop: 18, position: "relative" }}>
          <div
            style={{
              position: "absolute",
              left: "50%",
              transform: "translateX(-50%)",
              width: `${ruleW * 280}px`,
              height: 4,
              borderRadius: 3,
              background: accentColor,
              boxShadow: `0 0 18px ${accentColor}aa`,
            }}
          />
        </div>

        {subline && (
          <div
            style={{
              fontSize: 36,
              fontWeight: 600,
              color: theme.text,
              opacity: subIn * 0.95,
              transform: `translateY(${(1 - subIn) * 16}px)`,
              marginTop: 6,
            }}
          >
            {subline}
          </div>
        )}
      </div>

      {/* ---- GRADE unico: grano + vineta sobre lecho + overlay = UNA imagen ---- */}
      <AbsoluteFill style={{ pointerEvents: "none" }}>
        <svg width="100%" height="100%" style={{ position: "absolute", inset: 0 }}>
          <filter id="mdp-grain">
            <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="7" stitchTiles="stitch" />
            <feColorMatrix type="saturate" values="0" />
          </filter>
          <rect
            width="100%"
            height="100%"
            filter="url(#mdp-grain)"
            opacity={theme.grainOpacity + 0.02}
            style={{ mixBlendMode: "overlay" } as React.CSSProperties}
          />
        </svg>
      </AbsoluteFill>
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(120% 80% at 50% 42%, transparent 52%, rgba(0,0,0,0.36) 100%)",
          pointerEvents: "none",
        }}
      />
    </AbsoluteFill>
  );
};
