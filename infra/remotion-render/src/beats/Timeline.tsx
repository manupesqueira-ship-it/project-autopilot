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

export type TimelineNodeT = {
  year: string;
  title: string;
  amount?: string;
  tone?: "green" | "red" | "gold" | "white";
};

export type TimelineProps = {
  caption: string;
  nodes: TimelineNodeT[];
  growFrames?: number[];
};

const TONES: Record<string, string> = {
  green: theme.green,
  red: theme.red,
  gold: theme.gold,
  white: "#E8ECF4",
};

// Y1 corto: el bloque de texto del último nodo cuelga ~130px bajo el nodo
// y no debe entrar a la safe-area inferior (y>1594)
const LINE_X = 240;
const Y0 = 570;
const Y1 = 1430;

export const Timeline: React.FC<TimelineProps> = ({
  caption,
  nodes,
  growFrames,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const clamp = {
    extrapolateLeft: "clamp" as const,
    extrapolateRight: "clamp" as const,
  };

  const n = nodes.length;
  const gf =
    growFrames && growFrames.length === n
      ? growFrames
      : nodes.map((_, i) => 20 + (i * (durationInFrames - 70)) / Math.max(n - 1, 1));
  const nodeY = (i: number) => Y0 + (i * (Y1 - Y0)) / Math.max(n - 1, 1);

  // dot viajero: avanza por tramos entre los frames de activación
  let dotY = Y0;
  if (frame >= gf[n - 1]) {
    dotY = Y1;
  } else if (frame > gf[0]) {
    for (let i = 0; i < n - 1; i++) {
      if (frame >= gf[i] && frame < gf[i + 1]) {
        dotY = interpolate(frame, [gf[i], gf[i + 1]], [nodeY(i), nodeY(i + 1)], clamp);
        break;
      }
    }
  }

  const enter = spring({ frame: frame - 4, fps, config: { damping: 14, mass: 0.8 } });
  const breathe = Math.sin(frame / 14) * 4;
  const glowPulse = 0.8 + Math.sin(frame / 9) * 0.2;
  const capWords = caption.split(" ");
  const lastTone = TONES[nodes[n - 1].tone ?? "white"];

  return (
    <StudioScene spotlightColor={frame >= gf[n - 1] ? lastTone : undefined}>
      <AbsoluteFill style={{ fontFamily: theme.font }}>
        <div
          style={{
            position: "absolute",
            top: 300,
            width: "100%",
            textAlign: "center",
            fontSize: 42,
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

        <div
          style={{
            transform: `translateY(${(1 - enter) * 50 + breathe}px)`,
            opacity: Math.min(enter * 1.3, 1),
          }}
        >
          <div
            style={{
              position: "absolute",
              left: LINE_X - 3,
              top: Y0,
              width: 6,
              height: Y1 - Y0,
              borderRadius: 3,
              background: "rgba(255,255,255,0.09)",
            }}
          />
          <div
            style={{
              position: "absolute",
              left: LINE_X - 3,
              top: Y0,
              width: 6,
              height: Math.max(dotY - Y0, 0),
              borderRadius: 3,
              background: "linear-gradient(180deg, rgba(190,205,228,0.5), rgba(220,232,250,0.95))",
              boxShadow: "0 0 14px rgba(200,215,240,0.5)",
            }}
          />

          {frame >= gf[0] && frame < gf[n - 1] + 8 && (
            <>
              <div
                style={{
                  position: "absolute",
                  left: LINE_X - 26,
                  top: dotY - 26,
                  width: 52,
                  height: 52,
                  borderRadius: "50%",
                  background: "rgba(220,232,250,0.25)",
                  filter: "blur(10px)",
                }}
              />
              <div
                style={{
                  position: "absolute",
                  left: LINE_X - 12,
                  top: dotY - 12,
                  width: 24,
                  height: 24,
                  borderRadius: "50%",
                  background: "#FFFFFF",
                  boxShadow: "0 0 16px rgba(255,255,255,0.9), 0 0 36px rgba(200,215,240,0.6)",
                }}
              />
            </>
          )}

          {nodes.map((node, i) => {
            const y = nodeY(i);
            const tone = TONES[node.tone ?? "white"];
            const act = spring({
              frame: frame - gf[i],
              fps,
              config: { damping: 11, mass: 0.6 },
            });
            const active = frame >= gf[i];
            const isLast = i === n - 1;
            const nodeGlow = active && (isLast ? true : frame < gf[Math.min(i + 1, n - 1)]);

            return (
              <React.Fragment key={i}>
                <div
                  style={{
                    position: "absolute",
                    left: LINE_X - 21,
                    top: y - 21,
                    width: 42,
                    height: 42,
                    borderRadius: "50%",
                    background: active ? tone : "rgba(13,17,23,0.9)",
                    border: active
                      ? `3px solid ${tone}`
                      : "3px solid rgba(255,255,255,0.22)",
                    boxShadow: nodeGlow
                      ? `0 0 ${26 * glowPulse}px ${tone}AA, 0 0 ${60 * glowPulse}px ${tone}44`
                      : active
                        ? `0 0 12px ${tone}66`
                        : "none",
                    transform: `scale(${active ? 0.8 + Math.min(act, 1.15) * 0.25 : 0.8})`,
                  }}
                />
                <div
                  style={{
                    position: "absolute",
                    left: LINE_X + 78,
                    top: y - 58,
                    width: 660,
                    opacity: active ? Math.min(act * 1.3, 1) : 0.25,
                    transform: `translateX(${active ? (1 - Math.min(act, 1)) * 30 : 0}px)`,
                  }}
                >
                  <div
                    style={{
                      fontFamily: theme.mono,
                      fontSize: 33,
                      fontWeight: 600,
                      color: active ? tone : theme.textDim,
                      letterSpacing: "0.16em",
                      textTransform: "uppercase",
                    }}
                  >
                    {node.year}
                  </div>
                  <div
                    style={{
                      fontSize: 46,
                      fontWeight: 700,
                      color: theme.text,
                      lineHeight: 1.15,
                      marginTop: 6,
                    }}
                  >
                    {node.title}
                  </div>
                  {node.amount && (
                    <div
                      style={{
                        fontSize: 58,
                        fontWeight: 900,
                        color: tone,
                        letterSpacing: "-0.01em",
                        fontVariantNumeric: "tabular-nums",
                        marginTop: 6,
                        textShadow: nodeGlow
                          ? `0 0 ${24 * glowPulse}px ${tone}88`
                          : `0 0 12px ${tone}44`,
                      }}
                    >
                      {node.amount}
                    </div>
                  )}
                </div>
              </React.Fragment>
            );
          })}
        </div>
      </AbsoluteFill>
    </StudioScene>
  );
};
