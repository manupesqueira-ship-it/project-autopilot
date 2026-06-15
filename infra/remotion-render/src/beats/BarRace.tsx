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

export type Racer = {
  label: string;
  startAge: number;
  tag?: string;
};

export type BarRaceProps = {
  caption: string;
  monthly: number;
  rate: number;
  ageStart: number;
  ageEnd: number;
  racers: Racer[];
  prefix?: string;
  winnerIndex?: number;
  countEndFrame?: number;
  pulseFrames?: number[];
};

const fmt = (v: number) => Math.round(v).toLocaleString("en-US");

const TRACK_X = 130;
const TRACK_W = 540;
const ROW_Y0 = 770;
const ROW_H = 235;
const BAR_H = 64;

export const BarRace: React.FC<BarRaceProps> = ({
  caption,
  monthly,
  rate,
  ageStart,
  ageEnd,
  racers,
  prefix = "$",
  winnerIndex = 0,
  countEndFrame = 240,
  pulseFrames,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const clamp = {
    extrapolateLeft: "clamp" as const,
    extrapolateRight: "clamp" as const,
  };

  const RACE_START = 12;
  const raceEnd = countEndFrame;
  const r = rate / 12;
  const valueAt = (age: number, startAge: number) => {
    const months = Math.max(0, (age - startAge) * 12);
    return months === 0 ? 0 : monthly * ((Math.pow(1 + r, months) - 1) / r);
  };
  const finalMax = Math.max(...racers.map((rc) => valueAt(ageEnd, rc.startAge)));

  // lineal para poder invertir edad→frame (pop de activación por fila)
  const age = interpolate(frame, [RACE_START, raceEnd], [ageStart, ageEnd], clamp);
  const ageToFrame = (a: number) =>
    RACE_START + ((a - ageStart) / (ageEnd - ageStart)) * (raceEnd - RACE_START);

  const lastPulse = pulseFrames?.length
    ? Math.max(...pulseFrames)
    : raceEnd;
  const revealF = lastPulse + 26;
  const revealed = frame >= revealF;
  const glowPulse = 0.8 + Math.sin(frame / 9) * 0.2;
  const breathe = Math.sin(frame / 14) * 4;

  const capWords = caption.split(" ");

  return (
    <StudioScene spotlightColor={revealed ? theme.green : undefined}>
      <AbsoluteFill style={{ fontFamily: theme.font }}>
        <div
          style={{
            position: "absolute",
            top: 290,
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
            position: "absolute",
            top: 420,
            width: "100%",
            textAlign: "center",
            transform: `translateY(${breathe}px)`,
            opacity: interpolate(frame, [6, 14], [0, 1], clamp),
          }}
        >
          <div
            style={{
              fontSize: 30,
              fontWeight: 500,
              color: theme.textDim,
              letterSpacing: "0.22em",
              textTransform: "uppercase",
            }}
          >
            edad
          </div>
          <div
            style={{
              fontFamily: theme.mono,
              fontSize: 130,
              fontWeight: 800,
              color: theme.text,
              fontVariantNumeric: "tabular-nums",
              lineHeight: 1.05,
              textShadow: `0 0 ${30 * glowPulse}px rgba(255,255,255,0.25)`,
            }}
          >
            {Math.floor(age)}
            <span style={{ fontSize: 44, fontWeight: 600, color: theme.textDim, marginLeft: 14 }}>
              años
            </span>
          </div>
          <div
            style={{
              margin: "14px auto 0",
              width: 460,
              height: 5,
              borderRadius: 3,
              background: "rgba(255,255,255,0.10)",
            }}
          >
            <div
              style={{
                width: `${((age - ageStart) / (ageEnd - ageStart)) * 100}%`,
                height: "100%",
                borderRadius: 3,
                background: theme.green,
                boxShadow: `0 0 12px ${theme.green}AA`,
              }}
            />
          </div>
        </div>

        <div style={{ transform: `translateY(${breathe}px)` }}>
          {racers.map((rc, i) => {
            const y = ROW_Y0 + i * ROW_H;
            const enter = spring({
              frame: frame - 6 - i * 5,
              fps,
              config: { damping: 14, mass: 0.7 },
            });
            const actF = ageToFrame(rc.startAge);
            const active = frame >= actF;
            const activate = spring({
              frame: frame - actF,
              fps,
              config: { damping: 11, mass: 0.6 },
            });
            const val = valueAt(Math.min(age, ageEnd), rc.startAge);
            const w = Math.max((val / finalMax) * TRACK_W, active ? 8 : 0);
            const isWinner = i === winnerIndex;
            const dimmed = revealed && !isWinner;

            const pf = i > 0 && pulseFrames ? pulseFrames[i - 1] : raceEnd;
            const pulse = interpolate(frame, [pf, pf + 5, pf + 18], [0, 1, 0], clamp);

            const barBg = revealed && isWinner
              ? `linear-gradient(90deg, ${theme.green}66, ${theme.green})`
              : "linear-gradient(90deg, rgba(160,176,200,0.35), rgba(190,205,228,0.75))";
            const valColor = revealed && isWinner ? theme.green : theme.gold;

            return (
              <div
                key={i}
                style={{
                  position: "absolute",
                  left: TRACK_X,
                  top: y,
                  width: 1080 - TRACK_X * 2 + 130,
                  opacity: Math.min(enter * 1.3, 1) * (dimmed ? 0.5 : 0.55 + Math.min(activate, 1) * 0.45),
                  transform: `translateY(${(1 - enter) * 40}px) scale(${1 + pulse * 0.03 + (revealed && isWinner ? 0.015 : 0)})`,
                  transformOrigin: "left center",
                }}
              >
                <div
                  style={{
                    fontSize: 41,
                    fontWeight: 700,
                    color: active ? theme.text : theme.textDim,
                    marginBottom: 14,
                    transform: `scale(${0.96 + Math.min(activate, 1) * 0.04})`,
                    transformOrigin: "left center",
                  }}
                >
                  {rc.label}
                  {!active && (
                    <span
                      style={{
                        fontSize: 28,
                        fontWeight: 500,
                        color: theme.textDim,
                        marginLeft: 18,
                        padding: "4px 14px",
                        borderRadius: 16,
                        border: "1px solid rgba(255,255,255,0.18)",
                      }}
                    >
                      esperando…
                    </span>
                  )}
                  {revealed && rc.tag && (
                    <span
                      style={{
                        fontFamily: theme.mono,
                        fontSize: 27,
                        fontWeight: 600,
                        color: isWinner ? theme.green : theme.textDim,
                        marginLeft: 18,
                        padding: "4px 14px",
                        borderRadius: 16,
                        border: `1px solid ${isWinner ? theme.green + "88" : "rgba(255,255,255,0.18)"}`,
                      }}
                    >
                      {rc.tag}
                    </span>
                  )}
                </div>
                <div style={{ display: "flex", alignItems: "center" }}>
                  <div
                    style={{
                      width: TRACK_W,
                      height: BAR_H,
                      borderRadius: 14,
                      background: "rgba(255,255,255,0.05)",
                      border: "1px solid rgba(255,255,255,0.08)",
                      overflow: "hidden",
                      flexShrink: 0,
                    }}
                  >
                    <div
                      style={{
                        width: w,
                        height: "100%",
                        borderRadius: 13,
                        background: barBg,
                        boxShadow:
                          revealed && isWinner
                            ? `0 0 ${28 * glowPulse}px ${theme.green}99`
                            : pulse > 0
                              ? `0 0 ${20 * pulse}px rgba(255,255,255,0.5)`
                              : "none",
                      }}
                    />
                  </div>
                  <div
                    style={{
                      marginLeft: 26,
                      fontSize: 50,
                      fontWeight: 900,
                      color: valColor,
                      letterSpacing: "-0.01em",
                      fontVariantNumeric: "tabular-nums",
                      whiteSpace: "nowrap",
                      textShadow:
                        revealed && isWinner
                          ? `0 0 ${26 * glowPulse}px ${theme.green}88`
                          : pulse > 0
                            ? `0 0 ${24 * pulse}px ${theme.gold}AA`
                            : `0 0 16px ${valColor}44`,
                      opacity: active ? 1 : 0,
                    }}
                  >
                    {prefix}
                    {fmt(val)}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </AbsoluteFill>
    </StudioScene>
  );
};
