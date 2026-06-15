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

// Muro de logos: grid de marcas (simple-icons, fallback monograma) que aparecen
// con stagger sobre tiles glass oscuros. Para "estas empresas ya lo hacen" /
// "quien esta detras". Logos on="dark" -> marcas oscuras salen blancas, el resto
// conserva su hex (no es un muro blanco que rompe el theme).
export type LogoWallProps = {
  caption?: string;
  title?: string;
  sublabel?: string;
  logos: { slug: string; label?: string }[];
  columns?: number;
  accentColor?: string;
};

const TILE_W = 280;
const TILE_H = 220;

export const LogoWall: React.FC<LogoWallProps> = ({
  caption,
  title,
  sublabel,
  logos,
  columns = 3,
  accentColor = theme.green,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const clamp = {
    extrapolateLeft: "clamp" as const,
    extrapolateRight: "clamp" as const,
  };

  const REVEAL_START = 14;
  const STEP = 6;

  return (
    <StudioScene spotlightColor={accentColor}>
      <AbsoluteFill style={{ fontFamily: theme.font }}>
        {(caption || title) && (
          <div
            style={{
              position: "absolute",
              top: 280,
              width: "100%",
              textAlign: "center",
            }}
          >
            {caption && (
              <div
                style={{
                  fontSize: 32,
                  fontWeight: 600,
                  letterSpacing: "0.05em",
                  textTransform: "uppercase",
                  color: theme.textDim,
                  opacity: interpolate(frame, [2, 12], [0, 1], clamp),
                  marginBottom: 16,
                }}
              >
                {caption}
              </div>
            )}
            {title && (
              <div
                style={{
                  fontSize: 64,
                  fontWeight: 900,
                  letterSpacing: "-0.02em",
                  color: theme.text,
                  opacity: interpolate(frame, [6, 18], [0, 1], clamp),
                }}
              >
                {title}
              </div>
            )}
            {sublabel && (
              <div
                style={{
                  marginTop: 10,
                  fontSize: 36,
                  fontWeight: 700,
                  color: accentColor,
                  textShadow: `0 0 24px ${accentColor}44`,
                  opacity: interpolate(frame, [10, 22], [0, 1], clamp),
                }}
              >
                {sublabel}
              </div>
            )}
          </div>
        )}

        <AbsoluteFill
          style={{
            alignItems: "center",
            justifyContent: "center",
            paddingTop: title ? 180 : 0,
          }}
        >
          <div
            style={{
              display: "flex",
              flexWrap: "wrap",
              justifyContent: "center",
              gap: 30,
              width: columns * TILE_W + (columns - 1) * 30,
            }}
          >
            {logos.map((l, i) => {
              const p = spring({
                frame: frame - (REVEAL_START + i * STEP),
                fps,
                config: { damping: 14, mass: 0.7 },
              });
              return (
                <div
                  key={`${l.slug}-${i}`}
                  style={{
                    width: TILE_W,
                    height: TILE_H,
                    borderRadius: 30,
                    background:
                      "linear-gradient(165deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.03) 100%)",
                    border: "1.5px solid rgba(255,255,255,0.12)",
                    boxShadow:
                      "0 20px 50px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.1)",
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: l.label ? 18 : 0,
                    opacity: p,
                    transform: `translateY(${(1 - p) * 40}px) scale(${0.86 + p * 0.14})`,
                  }}
                >
                  <BrandLogo slug={l.slug} size={104} on="dark" />
                  {l.label && (
                    <span
                      style={{
                        fontFamily: theme.mono,
                        fontSize: 26,
                        fontWeight: 600,
                        letterSpacing: "0.04em",
                        color: theme.textDim,
                      }}
                    >
                      {l.label}
                    </span>
                  )}
                </div>
              );
            })}
          </div>
        </AbsoluteFill>
      </AbsoluteFill>
    </StudioScene>
  );
};
