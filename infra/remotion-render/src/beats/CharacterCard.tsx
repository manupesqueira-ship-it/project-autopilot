import React from "react";
import {
  AbsoluteFill,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { theme } from "../theme";
import { StudioScene } from "../studio/StudioScene";

export type CharacterCardProps = {
  // slug del archivo en public/characters/<slug>.png (caricatura cacheada)
  imageSlug: string;
  name: string;
  role?: string;
  quote?: string;
  accentColor?: string;
};

export const CharacterCard: React.FC<CharacterCardProps> = ({
  imageSlug,
  name,
  role,
  quote,
  accentColor = theme.green,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const pop = spring({ frame: frame - 4, fps, config: { damping: 14, mass: 0.8 } });
  const textIn = spring({ frame: frame - 18, fps, config: { damping: 16, mass: 0.7 } });
  const float = Math.sin(frame / 16) * 8;
  const glow = 0.55 + Math.sin(frame / 12) * 0.45;

  return (
    <StudioScene spotlightColor={accentColor}>
      <AbsoluteFill
        style={{
          fontFamily: theme.font,
          alignItems: "center",
          justifyContent: "flex-start",
          paddingTop: 250,
        }}
      >
        {/* halo detras de la caricatura (estatico: pulsa por opacidad, barato GPU) */}
        <div
          style={{
            position: "absolute",
            top: 250 + 40,
            width: 760,
            height: 760,
            borderRadius: "50%",
            background: `radial-gradient(circle, ${accentColor}40 0%, ${accentColor}14 42%, transparent 68%)`,
            filter: `blur(16px)`,
            opacity: glow,
          }}
        />
        {/* sombra de piso estatica (no se mueve -> el filtro se cachea) */}
        <div
          style={{
            position: "absolute",
            top: 250 + 720,
            width: 520,
            height: 120,
            borderRadius: "50%",
            background: "radial-gradient(ellipse, rgba(0,0,0,0.55) 0%, transparent 70%)",
            filter: "blur(20px)",
          }}
        />
        <div
          style={{
            transform: `translateY(${float - (1 - pop) * 40}px) scale(${0.8 + pop * 0.2})`,
            opacity: interpolate(pop, [0, 1], [0, 1]),
          }}
        >
          <Img
            src={staticFile(`characters/${imageSlug}.png`)}
            style={{
              width: 720,
              height: "auto",
            }}
          />
        </div>

        <div
          style={{
            marginTop: -10,
            textAlign: "center",
            opacity: textIn,
            transform: `translateY(${(1 - textIn) * 26}px)`,
            width: 900,
          }}
        >
          <div
            style={{
              color: theme.text,
              fontSize: 70,
              fontWeight: 900,
              letterSpacing: "-0.02em",
              lineHeight: 1.05,
            }}
          >
            {name}
          </div>
          {role && (
            <div
              style={{
                color: theme.textDim,
                fontSize: 32,
                fontWeight: 600,
                marginTop: 10,
                letterSpacing: "0.02em",
              }}
            >
              {role}
            </div>
          )}
          {quote && (
            <div
              style={{
                marginTop: 30,
                color: accentColor,
                fontSize: 50,
                fontWeight: 800,
                lineHeight: 1.18,
                letterSpacing: "-0.01em",
                textShadow: `0 0 26px ${accentColor}55`,
              }}
            >
              <span style={{ opacity: 0.6 }}>“</span>
              {quote}
              <span style={{ opacity: 0.6 }}>”</span>
            </div>
          )}
        </div>
      </AbsoluteFill>
    </StudioScene>
  );
};
