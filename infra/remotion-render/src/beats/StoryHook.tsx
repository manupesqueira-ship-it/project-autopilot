import React from "react";
import {
  AbsoluteFill,
  Audio,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { theme } from "../theme";
import { StudioScene } from "../studio/StudioScene";

// Story-teaser de Dinero LATAM: NO es el reel del feed. Una sola carta ~6s con UN
// hook que provoca curiosidad y jala al post del dia. Hereda el tema/fondo del
// sistema (StudioScene). Sin data-viz pesada: el trabajo es engagement. Lleva
// sonido (cama + whoosh + impacto) y un "punch" dorado opcional (ej "x2") que da
// un hero visual cuando el tema lo permite.
export type StoryHookProps = {
  kicker?: string; // etiqueta/marca arriba
  question: string; // el hook grande (se revela palabra por palabra)
  accentWords?: string[]; // palabras del hook en dorado (opcional)
  punch?: string; // hero dorado opcional (ej. "×2") — vacio = se omite
  cta?: string; // linea inferior que manda al post
  accent?: string;
};

const norm = (w: string) =>
  w
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .replace(/[¿?¡!.,;:"]/g, "")
    .toLowerCase();

export const StoryHook: React.FC<StoryHookProps> = ({
  kicker = "DINERO LATAM",
  question,
  accentWords = [],
  punch = "",
  cta = "te lo explico en el post de hoy",
  accent = theme.gold,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const accentSet = new Set(accentWords.map(norm));
  const words = question.split(" ");

  const kickerIn = spring({ frame: frame - 2, fps, config: { damping: 14, mass: 0.6 } });

  const lastWord = 14 + (words.length - 1) * 4;
  const punchStart = lastWord + 14;
  const ctaStart = punchStart + (punch ? 22 : 8);

  const punchSpring = spring({ frame: frame - punchStart, fps, config: { damping: 9, mass: 0.7 } });
  const punchScale = (0.5 + 0.5 * punchSpring) * (1 + Math.sin(frame / 12) * 0.03);
  const punchOpacity = interpolate(frame, [punchStart, punchStart + 6], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const ctaIn = spring({ frame: frame - ctaStart, fps, config: { damping: 13, mass: 0.6 } });
  const arrowFloat = Math.sin(frame / 7) * 10;
  const ctaPulse = 1 + Math.sin(frame / 10) * 0.04;
  const glow = 0.5 + Math.sin(frame / 10) * 0.3;
  const tapRing = (frame - ctaStart) % 26; // anillo de "tap" que late
  const tapScale = interpolate(tapRing, [0, 25], [0.7, 1.7], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const tapOpacity = interpolate(tapRing, [0, 25], [0.5, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  const breathe = 1 + Math.sin(frame / 30) * 0.012; // respiracion sutil del hook

  return (
    <StudioScene spotlightColor={accent}>
      {/* SONIDO — cama musical premium (Envato, $0) + SFX sincronizados */}
      <Audio
        src={staticFile("audio/music_minimaltechno_01.mp3")}
        startFrom={900}
        volume={(f) =>
          interpolate(f, [0, 8, 165, 180], [0, 0.5, 0.5, 0], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          })
        }
      />
      <Sequence from={2}>
        <Audio src={staticFile("audio/whoosh_01.wav")} volume={0.6} />
      </Sequence>
      {punch ? (
        <Sequence from={punchStart - 2}>
          <Audio src={staticFile("audio/impact_02.wav")} volume={0.4} />
        </Sequence>
      ) : null}
      <Sequence from={ctaStart}>
        <Audio src={staticFile("audio/tick_01.wav")} volume={0.35} />
      </Sequence>

      <AbsoluteFill style={{ fontFamily: theme.font, alignItems: "center" }}>
        {/* kicker / marca */}
        <div
          style={{
            position: "absolute",
            top: 380,
            display: "flex",
            alignItems: "center",
            gap: 16,
            opacity: Math.min(kickerIn * 1.3, 1),
            transform: `translateY(${(1 - kickerIn) * -12}px)`,
          }}
        >
          <div style={{ width: 36, height: 4, borderRadius: 2, background: accent }} />
          <span style={{ fontSize: 30, fontWeight: 800, letterSpacing: 9, color: accent }}>
            {kicker.toUpperCase()}
          </span>
          <div style={{ width: 36, height: 4, borderRadius: 2, background: accent }} />
        </div>

        {/* pregunta-hook grande, palabra por palabra (kinetica con rebote) */}
        <div
          style={{
            position: "absolute",
            top: 560,
            width: 940,
            textAlign: "center",
            lineHeight: 1.14,
            transform: `scale(${breathe})`,
          }}
        >
          {words.map((w, i) => {
            const t = 14 + i * 4;
            const s = spring({ frame: frame - t, fps, config: { damping: 11, mass: 0.6 } });
            const o = interpolate(frame, [t, t + 5], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            });
            const isAccent = accentSet.has(norm(w));
            const pop = isAccent
              ? 1 + Math.max(0, Math.sin(Math.max(0, frame - t) / 6)) * Math.max(0, 1 - (frame - t) / 18) * 0.14
              : 1;
            const ulW = isAccent
              ? interpolate(frame, [t + 4, t + 16], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })
              : 0;
            return (
              <span
                key={i}
                style={{
                  position: "relative",
                  display: "inline-block",
                  fontSize: 82,
                  fontWeight: 800,
                  color: isAccent ? accent : theme.text,
                  textShadow: isAccent
                    ? `0 0 ${28 + glow * 18}px ${accent}77`
                    : "0 2px 18px rgba(0,0,0,0.4)",
                  opacity: o,
                  transform: `translateY(${(1 - s) * 24}px) scale(${pop})`,
                  marginRight: 16,
                }}
              >
                {w}
                {isAccent ? (
                  <span
                    style={{
                      position: "absolute",
                      left: 0,
                      bottom: -8,
                      height: 6,
                      width: `${ulW * 100}%`,
                      borderRadius: 3,
                      background: accent,
                      boxShadow: `0 0 14px ${accent}`,
                    }}
                  />
                ) : null}
              </span>
            );
          })}
        </div>

        {/* hero "punch" dorado opcional (ej. x2) — llena el centro con un golpe */}
        {punch ? (
          <div
            style={{
              position: "absolute",
              top: 940,
              left: 0,
              right: 0,
              display: "flex",
              justifyContent: "center",
            }}
          >
            <div
              style={{
                position: "relative",
                width: 300,
                height: 300,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                opacity: punchOpacity,
                transform: `scale(${punchScale})`,
              }}
            >
              <div
                style={{
                  position: "absolute",
                  width: 300,
                  height: 300,
                  borderRadius: "50%",
                  background: `radial-gradient(circle, ${accent}33 0%, transparent 62%)`,
                  transform: `scale(${1 + glow * 0.18})`,
                }}
              />
              <div
                style={{
                  position: "absolute",
                  width: 236,
                  height: 236,
                  borderRadius: "50%",
                  border: `3px dashed ${accent}`,
                  boxShadow: `0 0 28px ${accent}55, inset 0 0 22px ${accent}22`,
                  transform: `rotate(${frame * 0.8}deg)`,
                }}
              />
              <span
                style={{
                  fontSize: 150,
                  fontWeight: 900,
                  color: accent,
                  letterSpacing: -4,
                  textShadow: `0 0 44px ${accent}aa`,
                }}
              >
                {punch}
              </span>
            </div>
          </div>
        ) : null}

        {/* CTA inferior: anillo de tap que late + flecha que flota + texto */}
        <div
          style={{
            position: "absolute",
            top: 1480,
            width: 860,
            textAlign: "center",
            opacity: Math.min(ctaIn * 1.3, 1),
            transform: `scale(${ctaPulse})`,
          }}
        >
          <div style={{ position: "relative", height: 90, marginBottom: 12 }}>
            <div
              style={{
                position: "absolute",
                left: "50%",
                top: 8,
                width: 70,
                height: 70,
                marginLeft: -35,
                borderRadius: "50%",
                border: `2px solid ${accent}`,
                transform: `scale(${tapScale})`,
                opacity: tapOpacity,
              }}
            />
            <div style={{ transform: `translateY(${arrowFloat}px)` }}>
              <svg
                width="66"
                height="66"
                viewBox="0 0 24 24"
                style={{ filter: `drop-shadow(0 0 ${16 * glow}px ${accent})` }}
              >
                <path
                  d="M12 4 L12 20 M12 4 L5 11 M12 4 L19 11"
                  fill="none"
                  stroke={accent}
                  strokeWidth={2.4}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </div>
          </div>
          <div style={{ fontSize: 44, fontWeight: 700, color: theme.text }}>{cta}</div>
        </div>
      </AbsoluteFill>
    </StudioScene>
  );
};
