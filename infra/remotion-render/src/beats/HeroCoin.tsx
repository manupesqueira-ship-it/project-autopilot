import React from "react";
import {
  AbsoluteFill,
  Easing,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { theme } from "../theme";
import { StudioScene } from "../studio/StudioScene";

// Objeto hero: moneda premium foto-real generada con gpt-image (cacheada por
// moneda en public/coins/<slug>.png, fondo transparente) compuesta sobre la
// StudioScene. Remotion le da vida en 2.5D: flotacion + leve tilt 3D + barrido
// de brillo (glint) + glow + count-up opcional. La cara (BTC/USD/MXN...) la
// elige el prop `coin`. Generar/cachear con infra/assembler/gen_coin.py.
export type HeroCoinProps = {
  caption?: string;
  coin?: string; // slug de la moneda en public/coins/<slug>.png (btc, usd, mxn...)
  // count-up opcional bajo la moneda
  label?: string;
  value?: number;
  prefix?: string;
  suffix?: string;
  decimals?: number;
  subline?: string;
  coinSize?: number;
  accentColor?: string;
  countEndFrame?: number;
};

const fmt = (v: number, d: number) =>
  v.toLocaleString("en-US", {
    minimumFractionDigits: d,
    maximumFractionDigits: d,
  });

export const HeroCoin: React.FC<HeroCoinProps> = ({
  caption,
  coin = "btc",
  label,
  value,
  prefix = "$",
  suffix = "",
  decimals = 0,
  subline,
  coinSize = 660,
  accentColor = theme.gold,
  countEndFrame = 70,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const clamp = {
    extrapolateLeft: "clamp" as const,
    extrapolateRight: "clamp" as const,
  };

  const enter = spring({ frame: frame - 2, fps, config: { damping: 13, mass: 0.9 } });
  const float = Math.sin(frame / 18) * 12;
  const tiltY = Math.sin(frame / 38) * 11; // grados: leve giro 3D (catch-light)
  const glint = (frame % 78) / 78; // 0..1: barrido de brillo en loop
  const glowPulse = 0.6 + Math.sin(frame / 11) * 0.4;
  const coinY = 660; // centro vertical de la moneda: carril propio, no pisa textos

  const shown =
    value != null
      ? interpolate(frame, [18, countEndFrame], [0, value], {
          ...clamp,
          easing: Easing.bezier(0.2, 0.6, 0.35, 1),
        })
      : 0;
  const done = value != null && frame >= countEndFrame;

  return (
    <StudioScene spotlightColor={accentColor} grid>
      <AbsoluteFill style={{ fontFamily: theme.font }}>
        {caption && (
          <div
            style={{
              position: "absolute",
              top: 175,
              width: "100%",
              textAlign: "center",
              fontSize: 40,
              fontWeight: 600,
              letterSpacing: "0.04em",
              color: theme.textDim,
              opacity: interpolate(frame, [2, 12], [0, 1], clamp),
            }}
          >
            {caption}
          </div>
        )}

        {/* glow radial detras de la moneda */}
        <div
          style={{
            position: "absolute",
            left: "50%",
            top: coinY,
            width: coinSize * 1.25,
            height: coinSize * 1.25,
            marginLeft: -(coinSize * 1.25) / 2,
            marginTop: -(coinSize * 1.25) / 2,
            borderRadius: "50%",
            background: `radial-gradient(circle, ${accentColor}3a 0%, ${accentColor}14 40%, transparent 66%)`,
            filter: "blur(20px)",
            opacity: enter * glowPulse,
          }}
        />

        {/* moneda premium (gpt-image, alpha) con vida 2.5D */}
        <div
          style={{
            position: "absolute",
            left: "50%",
            top: coinY,
            width: coinSize,
            height: coinSize,
            marginLeft: -coinSize / 2,
            marginTop: -coinSize / 2,
            perspective: 1400,
            transform: `translateY(${float - (1 - enter) * 50}px) scale(${0.78 + enter * 0.22})`,
            opacity: enter,
          }}
        >
          <div
            style={{
              position: "relative",
              width: "100%",
              height: "100%",
              transform: `rotateY(${tiltY}deg)`,
              transformStyle: "preserve-3d",
            }}
          >
            <Img
              src={staticFile(`coins/${coin}.png`)}
              style={{
                width: "100%",
                height: "100%",
                objectFit: "contain",
                filter: "drop-shadow(0 16px 36px rgba(0,0,0,0.45))",
              }}
            />
            {/* barrido de brillo, recortado al disco de la moneda */}
            <div
              style={{
                position: "absolute",
                inset: "9%",
                borderRadius: "50%",
                overflow: "hidden",
                mixBlendMode: "screen",
                pointerEvents: "none",
                opacity: enter,
              }}
            >
              <div
                style={{
                  position: "absolute",
                  top: "-25%",
                  left: `${-70 + glint * 180}%`,
                  width: "55%",
                  height: "150%",
                  background:
                    "linear-gradient(100deg, transparent 0%, rgba(255,245,210,0.55) 50%, transparent 100%)",
                  transform: "skewX(-16deg)",
                }}
              />
            </div>
          </div>
        </div>

        {/* sombra de piso */}
        <div
          style={{
            position: "absolute",
            left: "50%",
            top: coinY + coinSize * 0.42,
            width: coinSize * 0.62,
            height: coinSize * 0.14,
            marginLeft: -(coinSize * 0.62) / 2,
            borderRadius: "50%",
            background: "radial-gradient(ellipse, rgba(0,0,0,0.5) 0%, transparent 70%)",
            filter: "blur(18px)",
            opacity: enter,
          }}
        />

        {/* count-up opcional */}
        {value != null && (
          <div
            style={{
              position: "absolute",
              top: 1120,
              width: "100%",
              textAlign: "center",
              opacity: interpolate(frame, [14, 26], [0, 1], clamp),
            }}
          >
            {label && (
              <div style={{ fontSize: 34, fontWeight: 500, color: theme.textDim }}>
                {label}
              </div>
            )}
            <div
              style={{
                fontSize: 120,
                fontWeight: 900,
                color: accentColor,
                letterSpacing: "-0.02em",
                fontVariantNumeric: "tabular-nums",
                marginTop: 8,
                textShadow: done
                  ? `0 0 ${40 * glowPulse}px ${accentColor}88, 0 0 ${100 * glowPulse}px ${accentColor}33`
                  : `0 0 24px ${accentColor}55`,
              }}
            >
              {prefix}
              {fmt(shown, decimals)}
              {suffix && <span style={{ fontSize: "0.5em" }}>{suffix}</span>}
            </div>
            {subline && (
              <div
                style={{
                  marginTop: 14,
                  fontSize: 40,
                  fontWeight: 700,
                  color: theme.text,
                  opacity: interpolate(frame, [countEndFrame + 4, countEndFrame + 14], [0, 1], clamp),
                }}
              >
                {subline}
              </div>
            )}
          </div>
        )}
      </AbsoluteFill>
    </StudioScene>
  );
};
