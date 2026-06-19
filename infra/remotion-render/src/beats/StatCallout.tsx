import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { theme } from "../theme";
import { enterProgress } from "../anim";
import { StudioScene } from "../studio/StudioScene";

// Stat callout: UN dato suelto enorme (string libre: "$700M", "8 de cada 10",
// "−63%") con contexto debajo word-by-word. A diferencia de BigNumber NO es un
// count-up numerico: el stat puede ser cualquier expresion y el peso narrativo
// lo lleva la frase de contexto. Color semantico del stat (oro=dinero,
// verde=sube, rojo=cae). Sin titulo de texto encima del dato.
export type StatCalloutProps = {
  caption?: string;
  // el dato grande, ya formateado: "$700M", "8 de cada 10", "+312%"
  stat: string;
  // color del stat: theme.gold | theme.green | theme.red (semantico)
  statColor?: string;
  // frase de contexto debajo del dato
  context: string;
  accentColor?: string;
};

export const StatCallout: React.FC<StatCalloutProps> = ({
  caption,
  stat,
  statColor = theme.gold,
  context,
  accentColor = theme.green,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const clamp = {
    extrapolateLeft: "clamp" as const,
    extrapolateRight: "clamp" as const,
  };

  // overshoot canónico §5.4 (src/anim.ts); compone con la respiración idle abajo
  const pop = enterProgress(frame, fps, 6);
  const breathe = Math.sin(frame / 13) * 5;
  const glowPulse = 0.7 + Math.sin(frame / 10) * 0.3;

  // longitud del stat -> tamaño (que quepa full-bleed en 9:16)
  const fontSize = stat.length <= 5 ? 280 : stat.length <= 9 ? 200 : 150;

  const tokens = context.split(" ");
  const C_START = 24;
  const STEP = 3;

  const ruleIn = spring({ frame: frame - 16, fps, config: { damping: 18, mass: 0.7 } });

  return (
    <StudioScene spotlightColor={statColor} grid>
      <AbsoluteFill
        style={{
          fontFamily: theme.font,
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: "0 90px",
        }}
      >
        {caption && (
          <div
            style={{
              position: "absolute",
              top: 300,
              width: "100%",
              textAlign: "center",
              fontSize: 34,
              fontWeight: 600,
              letterSpacing: "0.06em",
              textTransform: "uppercase",
              color: theme.textDim,
              opacity: interpolate(frame, [2, 12], [0, 1], clamp),
            }}
          >
            {caption}
          </div>
        )}

        {/* el dato enorme */}
        <div
          style={{
            fontSize,
            fontWeight: 900,
            color: statColor,
            letterSpacing: "-0.03em",
            lineHeight: 1,
            fontVariantNumeric: "tabular-nums",
            textAlign: "center",
            opacity: pop,
            transform: `translateY(${breathe - (1 - pop) * 30}px) scale(${0.7 + pop * 0.3})`,
            textShadow: `0 0 ${48 * glowPulse}px ${statColor}77, 0 0 ${120 * glowPulse}px ${statColor}2e`,
          }}
        >
          {stat}
        </div>

        {/* regla de acento bajo el dato */}
        <div
          style={{
            width: interpolate(ruleIn, [0, 1], [0, 220], clamp),
            height: 5,
            borderRadius: 3,
            background: accentColor,
            boxShadow: `0 0 18px ${accentColor}`,
            margin: "44px 0 40px",
            opacity: ruleIn,
          }}
        />

        {/* contexto word-by-word */}
        <div
          style={{
            textAlign: "center",
            fontSize: 52,
            fontWeight: 700,
            lineHeight: 1.3,
            letterSpacing: "-0.01em",
            color: theme.text,
            maxWidth: 880,
          }}
        >
          {tokens.map((w, i) => {
            const o = interpolate(
              frame,
              [C_START + i * STEP, C_START + 6 + i * STEP],
              [0, 1],
              clamp,
            );
            const dy = interpolate(
              frame,
              [C_START + i * STEP, C_START + 9 + i * STEP],
              [10, 0],
              clamp,
            );
            return (
              <span
                key={i}
                style={{
                  display: "inline-block",
                  opacity: o,
                  transform: `translateY(${dy}px)`,
                  marginRight: "0.24em",
                }}
              >
                {w}
              </span>
            );
          })}
        </div>
      </AbsoluteFill>
    </StudioScene>
  );
};
