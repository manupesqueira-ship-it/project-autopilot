import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { theme } from "../theme";
import { StudioScene } from "../studio/StudioScene";
import { BrandLogo } from "../studio/BrandLogo";

// Testimonio: cita de una persona/fuente real. Comilla grande dorada, cita
// word-by-word (con goldWords opcionales), atribucion abajo con avatar (logo de
// marca o monograma de la inicial — NO genera caras). Composicion limpia y
// centrada, sin card pesado -> no parece plantilla de "review".
export type TestimonialProps = {
  caption?: string;
  quote: string;
  name: string;
  role?: string;
  // slug simple-icons para el avatar (org); si falta -> monograma de la inicial
  avatarSlug?: string;
  // palabras de la cita en oro (match exacto por token, sin puntuacion)
  goldWords?: string[];
  accentColor?: string;
};

export const Testimonial: React.FC<TestimonialProps> = ({
  caption,
  quote,
  name,
  role,
  avatarSlug,
  goldWords = [],
  accentColor = theme.green,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const clamp = {
    extrapolateLeft: "clamp" as const,
    extrapolateRight: "clamp" as const,
  };

  const breathe = Math.sin(frame / 15) * 4;
  const markIn = spring({ frame: frame - 2, fps, config: { damping: 13, mass: 0.8 } });

  const goldSet = React.useMemo(
    () => new Set(goldWords.map((w) => w.toLowerCase())),
    [goldWords],
  );
  const tokens = quote.split(" ");
  const Q_START = 16;
  const STEP = 3.2;
  const attribIn = spring({
    frame: frame - (Q_START + tokens.length * STEP + 6),
    fps,
    config: { damping: 16, mass: 0.7 },
  });

  return (
    <StudioScene spotlightColor={accentColor} grid={false}>
      <AbsoluteFill
        style={{
          fontFamily: theme.font,
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: "0 110px",
        }}
      >
        {caption && (
          <div
            style={{
              position: "absolute",
              top: 280,
              width: "100%",
              textAlign: "center",
              fontSize: 32,
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

        {/* comilla grande dorada */}
        <div
          style={{
            fontSize: 280,
            lineHeight: 0.7,
            fontWeight: 900,
            color: theme.gold,
            opacity: markIn * 0.85,
            transform: `translateY(${(1 - markIn) * 30 + breathe}px) scale(${0.8 + markIn * 0.2})`,
            textShadow: `0 0 50px ${theme.gold}44`,
            marginBottom: 10,
            height: 150,
          }}
        >
          &ldquo;
        </div>

        {/* cita word-by-word */}
        <div
          style={{
            textAlign: "center",
            fontSize: 66,
            fontWeight: 800,
            lineHeight: 1.22,
            letterSpacing: "-0.015em",
            color: theme.text,
            transform: `translateY(${breathe}px)`,
            maxWidth: 860,
          }}
        >
          {tokens.map((w, i) => {
            const o = interpolate(
              frame,
              [Q_START + i * STEP, Q_START + 6 + i * STEP],
              [0, 1],
              clamp,
            );
            const dy = interpolate(
              frame,
              [Q_START + i * STEP, Q_START + 9 + i * STEP],
              [12, 0],
              clamp,
            );
            const isGold = goldSet.has(
              w.toLowerCase().replace(/[.,;:¡!¿?"“”]/g, ""),
            );
            return (
              <span
                key={i}
                style={{
                  display: "inline-block",
                  opacity: o,
                  transform: `translateY(${dy}px)`,
                  color: isGold ? theme.gold : theme.text,
                  textShadow: isGold ? `0 0 28px ${theme.gold}55` : "none",
                  marginRight: "0.26em",
                }}
              >
                {w}
              </span>
            );
          })}
        </div>

        {/* divisor + atribucion */}
        <div
          style={{
            marginTop: 64,
            display: "flex",
            alignItems: "center",
            gap: 26,
            opacity: attribIn,
            transform: `translateY(${(1 - attribIn) * 22}px)`,
          }}
        >
          <div
            style={{
              width: 116,
              height: 116,
              borderRadius: "50%",
              background: avatarSlug ? "#FFFFFF" : `${accentColor}22`,
              border: avatarSlug ? "none" : `2.5px solid ${accentColor}77`,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              flexShrink: 0,
              boxShadow: `0 0 30px ${accentColor}22, 0 12px 34px rgba(0,0,0,0.4)`,
            }}
          >
            {avatarSlug ? (
              <BrandLogo slug={avatarSlug} size={68} on="light" />
            ) : (
              <span
                style={{
                  fontSize: 60,
                  fontWeight: 900,
                  color: accentColor,
                }}
              >
                {name.charAt(0).toUpperCase()}
              </span>
            )}
          </div>
          <div style={{ textAlign: "left" }}>
            <div
              style={{
                fontSize: 46,
                fontWeight: 800,
                color: theme.text,
                letterSpacing: "-0.01em",
                lineHeight: 1.05,
              }}
            >
              {name}
            </div>
            {role && (
              <div
                style={{
                  fontFamily: theme.mono,
                  fontSize: 28,
                  fontWeight: 500,
                  color: theme.textDim,
                  letterSpacing: "0.03em",
                  marginTop: 8,
                }}
              >
                {role}
              </div>
            )}
          </div>
        </div>
      </AbsoluteFill>
    </StudioScene>
  );
};
