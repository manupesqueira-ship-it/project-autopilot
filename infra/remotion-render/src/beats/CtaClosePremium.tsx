import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { theme } from "../theme";
import { PremiumStage } from "../studio/PremiumStage";

// b7 cierre/CTA en el MISMO mundo premium (PremiumStage) que el resto del reel,
// reemplaza la versión IglooStage. Misma mecánica que CtaClose (bookmark que late,
// palabras que entran, sub tenue), sólo cambia el escenario (piso en perspectiva
// + luz) para que el reel sea un solo plano coherente.

export type CtaClosePremiumProps = {
  text?: string;
  boldWord?: string;
  sub?: string;
  accent?: string;
};

export const CtaClosePremium: React.FC<CtaClosePremiumProps> = ({
  text = "El que aguanta, gana.",
  boldWord = "aguanta",
  sub = "mañana: cuánto pierde tu aguinaldo guardado en el banco",
  accent = theme.gold,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const iconIn = spring({ frame: frame - 6, fps, config: { damping: 11, mass: 0.7 } });
  const pulse = 1 + Math.sin(frame / 9) * 0.035;
  const glowPulse = 0.55 + Math.sin(frame / 9) * 0.2;

  const words = text.split(" ");
  const subIn = spring({
    frame: frame - 14 - words.length * 4,
    fps,
    config: { damping: 13, mass: 0.6 },
  });

  return (
    <PremiumStage tint={accent}>
      <AbsoluteFill style={{ fontFamily: theme.font, alignItems: "center" }}>
        <div
          style={{
            position: "absolute",
            top: 600,
            transform: `scale(${(0.7 + iconIn * 0.3) * pulse})`,
            opacity: Math.min(iconIn * 1.4, 1),
          }}
        >
          <svg width="150" height="180" viewBox="0 0 100 120">
            <path
              d="M 18 8 H 82 Q 88 8 88 14 V 112 L 50 86 L 12 112 V 14 Q 12 8 18 8 Z"
              fill={`${accent}26`}
              stroke={accent}
              strokeWidth={5}
              strokeLinejoin="round"
              style={{
                filter: `drop-shadow(0 0 ${14 * glowPulse}px ${accent}) drop-shadow(0 0 ${40 * glowPulse}px ${accent}66)`,
              }}
            />
          </svg>
        </div>

        <div
          style={{
            position: "absolute",
            top: 870,
            width: 860,
            textAlign: "center",
            lineHeight: 1.25,
          }}
        >
          {words.map((w, i) => {
            const t = 14 + i * 4;
            const s = spring({ frame: frame - t, fps, config: { damping: 12, mass: 0.6 } });
            const o = interpolate(frame, [t, t + 5], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            });
            const bold =
              boldWord &&
              w.replace(/[.,;:!?]/g, "").toLowerCase() === boldWord.toLowerCase();
            return (
              <span
                key={i}
                style={{
                  display: "inline-block",
                  fontSize: bold ? 76 : 60,
                  fontWeight: bold ? 600 : 200,
                  color: bold ? accent : "#EAEEF2",
                  letterSpacing: bold ? "0.04em" : "0.12em",
                  textTransform: "uppercase",
                  textShadow: bold ? `0 0 34px ${accent}66` : undefined,
                  opacity: o,
                  transform: `translateY(${(1 - s) * 20}px)`,
                  marginRight: 18,
                }}
              >
                {w}
              </span>
            );
          })}
        </div>

        {sub && (
          <div
            style={{
              position: "absolute",
              top: 1110,
              width: 820,
              textAlign: "center",
              fontSize: 29,
              fontWeight: 300,
              letterSpacing: "0.12em",
              color: "#9FB0C0",
              opacity: Math.min(subIn * 1.3, 1),
              transform: `translateY(${(1 - subIn) * 14}px)`,
            }}
          >
            {sub}
          </div>
        )}
      </AbsoluteFill>
    </PremiumStage>
  );
};
