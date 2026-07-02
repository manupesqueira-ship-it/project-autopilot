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
import { IglooStage } from "../studio/IglooStage";

export type CharacterCardProps = {
  // slug del archivo en public/characters/<slug>.png (caricatura cacheada).
  // Si viene vacio -> modo CITA: medallon ₿ + frase + atribucion (igloo.inc, $0).
  imageSlug?: string;
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

  const hasImage = Boolean(imageSlug);

  const pop = spring({ frame: frame - 4, fps, config: { damping: 14, mass: 0.8 } });
  const textIn = spring({ frame: frame - 18, fps, config: { damping: 16, mass: 0.7 } });
  const float = Math.sin(frame / 16) * 8;
  const emberBreath = 0.7 + Math.sin(frame / 22) * 0.3;

  // ---- MODO CITA (sin imagen): medallon ₿ + frase presidencial ----
  if (!hasImage) {
    const ring = spring({ frame: frame - 4, fps, config: { damping: 13, mass: 0.8 } });
    const quoteWords = (quote ?? "").split(" ");
    const attrIn = spring({
      frame: frame - 30 - quoteWords.length * 3,
      fps,
      config: { damping: 16, mass: 0.7 },
    });
    return (
      <IglooStage accent={accentColor} glowY={0.34}>
        <AbsoluteFill
          style={{
            fontFamily: theme.font,
            alignItems: "center",
            justifyContent: "flex-start",
            paddingTop: 360,
          }}
        >
          {/* medallon ₿ — la UNICA pieza (vidrio/brasa), respira al encender */}
          <div
            style={{
              position: "relative",
              width: 230,
              height: 230,
              transform: `translateY(${float * 0.5 - (1 - ring) * 30}px) scale(${0.78 + ring * 0.22})`,
              opacity: Math.min(ring * 1.3, 1),
            }}
          >
            <div
              style={{
                position: "absolute",
                inset: -40,
                borderRadius: "50%",
                background: `radial-gradient(circle, ${accentColor}33 0%, ${accentColor}10 46%, transparent 70%)`,
                opacity: emberBreath,
                filter: "blur(6px)",
              }}
            />
            <div
              style={{
                position: "absolute",
                inset: 0,
                borderRadius: "50%",
                border: `2px solid ${accentColor}66`,
                boxShadow: `0 0 30px ${accentColor}33, inset 0 0 40px ${accentColor}18`,
                background: "rgba(10,16,24,0.45)",
              }}
            />
            <div
              style={{
                position: "absolute",
                inset: 0,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 128,
                fontWeight: 300,
                color: accentColor,
                textShadow: `0 0 ${34 * emberBreath}px ${accentColor}aa`,
              }}
            >
              ₿
            </div>
          </div>

          {/* la cita: heroe, fina, esmeralda */}
          {quote && (
            <div
              style={{
                marginTop: 120,
                width: 880,
                textAlign: "center",
                color: "#EAEEF2",
                fontSize: 78,
                fontWeight: 200,
                lineHeight: 1.18,
                letterSpacing: "-0.005em",
              }}
            >
              <span style={{ color: accentColor, opacity: 0.5, fontWeight: 300 }}>“</span>
              {quoteWords.map((w, i) => {
                const t = 24 + i * 3;
                const o = interpolate(frame, [t, t + 8], [0, 1], {
                  extrapolateLeft: "clamp",
                  extrapolateRight: "clamp",
                });
                const s = spring({ frame: frame - t, fps, config: { damping: 200, mass: 0.8 } });
                return (
                  <span
                    key={i}
                    style={{
                      display: "inline-block",
                      marginRight: 18,
                      opacity: o,
                      transform: `translateY(${(1 - s) * 14}px)`,
                    }}
                  >
                    {w}
                  </span>
                );
              })}
              <span style={{ color: accentColor, opacity: 0.5, fontWeight: 300 }}>”</span>
            </div>
          )}

          {/* atribucion: NOMBRE · ROL, mayusculas finas con tracking */}
          <div
            style={{
              marginTop: 80,
              textAlign: "center",
              opacity: Math.min(attrIn * 1.3, 1),
              transform: `translateY(${(1 - attrIn) * 16}px)`,
            }}
          >
            <div
              style={{
                color: "#C9D6E2",
                fontSize: 34,
                fontWeight: 300,
                letterSpacing: "0.3em",
                textTransform: "uppercase",
              }}
            >
              {name}
            </div>
            {role && (
              <div
                style={{
                  marginTop: 16,
                  color: "#7E8C9A",
                  fontSize: 25,
                  fontWeight: 300,
                  letterSpacing: "0.28em",
                  textTransform: "uppercase",
                }}
              >
                {role}
              </div>
            )}
          </div>
        </AbsoluteFill>
      </IglooStage>
    );
  }

  // ---- MODO CARICATURA (con imagen) ----
  const glow = 0.55 + Math.sin(frame / 12) * 0.45;
  return (
    <IglooStage accent={accentColor} glowY={0.4}>
      <AbsoluteFill
        style={{
          fontFamily: theme.font,
          alignItems: "center",
          justifyContent: "flex-start",
          paddingTop: 250,
        }}
      >
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
            style={{ width: 720, height: "auto" }}
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
              color: "#EAEEF2",
              fontSize: 64,
              fontWeight: 300,
              letterSpacing: "0.06em",
              textTransform: "uppercase",
              lineHeight: 1.05,
            }}
          >
            {name}
          </div>
          {role && (
            <div
              style={{
                color: "#7E8C9A",
                fontSize: 30,
                fontWeight: 300,
                marginTop: 14,
                letterSpacing: "0.26em",
                textTransform: "uppercase",
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
                fontWeight: 300,
                lineHeight: 1.18,
                letterSpacing: "-0.005em",
                textShadow: `0 0 26px ${accentColor}55`,
              }}
            >
              <span style={{ opacity: 0.5 }}>“</span>
              {quote}
              <span style={{ opacity: 0.5 }}>”</span>
            </div>
          )}
        </div>
      </AbsoluteFill>
    </IglooStage>
  );
};
