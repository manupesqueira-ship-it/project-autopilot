import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { theme } from "../theme";
import { StudioScene } from "../studio/StudioScene";
import { BrandLogo } from "../studio/BrandLogo";

type Side = {
  name: string;
  ticker: string;
  logo: string;
  value: number;
  tag?: string;
};

export type VersusProps = {
  caption: string;
  left: Side;
  right: Side;
  prefix?: string;
  winner: "left" | "right";
  // inyectados por el ensamblador desde los timestamps de la voz
  leftEndFrame?: number;
  rightEndFrame?: number;
};

const fmt = (v: number) => Math.round(v).toLocaleString("en-US");

const CW = 880;
const CH = 430;
const CX = 100;
const Y_TOP = 450;
const Y_BOT = 1000;

export const VersusCards: React.FC<VersusProps> = ({
  caption,
  left,
  right,
  prefix = "$",
  winner,
  leftEndFrame = 60,
  rightEndFrame = 110,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const clamp = {
    extrapolateLeft: "clamp" as const,
    extrapolateRight: "clamp" as const,
  };
  const revealFrame = rightEndFrame;
  const revealed = frame >= revealFrame;
  const reveal = spring({
    frame: frame - revealFrame,
    fps,
    config: { damping: 12, mass: 0.7 },
  });

  const capWords = caption.split(" ");

  const Card = (side: Side, y: number, endFrame: number, isTop: boolean) => {
    const isWinner = (winner === "left") === isTop;
    const enter = spring({
      frame: frame - (isTop ? 4 : 10),
      fps,
      config: { damping: 14, mass: 0.8 },
    });
    const slide = (1 - enter) * (isTop ? -160 : 160);
    const breathe = Math.sin(frame / 14 + (isTop ? 0 : 2.2)) * 3;
    const shown = interpolate(frame, [18, endFrame], [0, side.value], {
      ...clamp,
      easing: Easing.bezier(0.2, 0.6, 0.35, 1),
    });
    const done = frame >= endFrame;
    const glowPulse = done ? 0.8 + Math.sin(frame / 9) * 0.2 : 1;
    const counterColor = revealed && isWinner ? theme.green : theme.gold;
    const dim = revealed && !isWinner ? 1 - reveal * 0.45 : 1;
    const winScale = revealed && isWinner ? 1 + reveal * 0.035 : 1;
    const border =
      revealed && isWinner
        ? `2px solid ${theme.green}AA`
        : "1.5px solid rgba(255,255,255,0.14)";
    const winGlow =
      revealed && isWinner
        ? `, 0 0 ${70 * glowPulse}px ${theme.green}33, 0 0 ${26 * glowPulse}px ${theme.green}44`
        : "";

    return (
      <div
        style={{
          position: "absolute",
          left: CX,
          top: y,
          width: CW,
          height: CH,
          borderRadius: 40,
          background:
            "linear-gradient(165deg, rgba(255,255,255,0.075) 0%, rgba(255,255,255,0.035) 55%, rgba(255,255,255,0.05) 100%)",
          border,
          boxShadow: `0 26px 70px rgba(0,0,0,0.45), inset 0 1px 0 rgba(255,255,255,0.12)${winGlow}`,
          opacity: Math.min(enter * 1.3, 1) * dim,
          transform: `translateX(${slide}px) translateY(${breathe}px) scale(${(0.95 + enter * 0.05) * winScale})`,
        }}
      >
        <div
          style={{
            position: "absolute",
            left: 56,
            top: 56,
            width: 128,
            height: 128,
            borderRadius: "50%",
            background: "rgba(255,255,255,0.08)",
            border: "1px solid rgba(255,255,255,0.14)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <BrandLogo slug={side.logo} size={72} on="dark" />
        </div>
        <div style={{ position: "absolute", left: 216, top: 62 }}>
          <div style={{ fontSize: 52, fontWeight: 800, color: theme.text }}>
            {side.name}
          </div>
          <div
            style={{
              fontFamily: theme.mono,
              fontSize: 26,
              fontWeight: 500,
              color: theme.textDim,
              letterSpacing: "0.12em",
              marginTop: 4,
            }}
          >
            {side.ticker}
          </div>
        </div>
        <div
          style={{
            position: "absolute",
            left: 0,
            bottom: 52,
            width: "100%",
            textAlign: "center",
            fontSize: 94,
            fontWeight: 900,
            color: counterColor,
            letterSpacing: "-0.02em",
            fontVariantNumeric: "tabular-nums",
            textShadow: done
              ? `0 0 ${38 * glowPulse}px ${counterColor}88, 0 0 ${96 * glowPulse}px ${counterColor}33`
              : `0 0 22px ${counterColor}55`,
          }}
        >
          {prefix}
          {fmt(shown)}
          {side.tag && (
            <span
              style={{
                fontSize: 38,
                fontWeight: 800,
                marginLeft: 18,
                color: revealed && isWinner ? theme.green : theme.textDim,
                opacity: done ? 1 : 0,
              }}
            >
              {side.tag}
            </span>
          )}
        </div>
      </div>
    );
  };

  const vsIn = spring({ frame: frame - 14, fps, config: { damping: 12, mass: 0.6 } });

  return (
    <StudioScene spotlightColor={revealed ? theme.green : theme.gold}>
      <AbsoluteFill style={{ fontFamily: theme.font }}>
        <div
          style={{
            position: "absolute",
            top: 290,
            width: "100%",
            textAlign: "center",
            fontSize: 40,
            fontWeight: 500,
            color: theme.textDim,
          }}
        >
          {capWords.map((w, i) => {
            const o = interpolate(frame, [2 + i * 3, 8 + i * 3], [0, 1], clamp);
            return (
              <span key={i} style={{ opacity: o }}>
                {w}{" "}
              </span>
            );
          })}
        </div>

        {Card(left, Y_TOP, leftEndFrame, true)}
        {Card(right, Y_BOT, rightEndFrame, false)}

        <div
          style={{
            position: "absolute",
            left: 540 - 52,
            top: (Y_TOP + CH + Y_BOT) / 2 - 52,
            width: 104,
            height: 104,
            borderRadius: "50%",
            background: "rgba(13,17,23,0.9)",
            border: "1.5px solid rgba(255,255,255,0.22)",
            boxShadow: `0 0 ${30 + Math.sin(frame / 9) * 10}px rgba(255,255,255,0.14), 0 14px 40px rgba(0,0,0,0.5)`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: 40,
            fontWeight: 900,
            color: theme.text,
            letterSpacing: "0.04em",
            opacity: Math.min(vsIn * 1.3, 1),
            transform: `scale(${0.7 + vsIn * 0.3})`,
          }}
        >
          VS
        </div>
      </AbsoluteFill>
    </StudioScene>
  );
};
