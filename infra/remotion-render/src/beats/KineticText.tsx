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

type Word = { text: string; accent?: boolean };

export type KineticTextProps = {
  // modo legacy: un solo bloque de lineas, todas visibles a la vez
  lines?: Word[][];
  // modo estrofas: cada estrofa (grupo de lineas) entra y sale sincronizada a su
  // frase de la voz -> el kinetico cubre TODA la narracion sin frame muerto.
  stanzas?: Word[][][];
  accentColor?: string;
  startFrame?: number;
  // separacion entre palabras en frames (fallback si no hay timestamps reales)
  wordSpacing?: number;
  // frame exacto de cada palabra (timestamp real de la voz), en orden global
  // estrofa->linea->palabra. Mismo orden que arma el ensamblador.
  wordFrames?: number[];
};

const Words: React.FC<{
  lines: Word[][];
  frameOf: (globalIdx: number) => number;
  startGlobalIdx: number;
  accentColor: string;
  glowPulse: number;
}> = ({ lines, frameOf, startGlobalIdx, accentColor, glowPulse }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  let g = startGlobalIdx;
  return (
    <>
      {lines.map((line, li) => (
        <div
          key={li}
          style={{ lineHeight: 1.22, marginBottom: li < lines.length - 1 ? 14 : 0 }}
        >
          {line.map((w, wi) => {
            const t = frameOf(g++);
            const s = spring({ frame: frame - t, fps, config: { damping: 12, mass: 0.6 } });
            const o = interpolate(frame, [t, t + 5], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            });
            const accent = w.accent;
            return (
              <span
                key={wi}
                style={{
                  display: "inline-block",
                  fontSize: accent ? 104 : 80,
                  fontWeight: accent ? 900 : 700,
                  color: accent ? accentColor : theme.text,
                  letterSpacing: accent ? "-0.02em" : "-0.01em",
                  textShadow: accent
                    ? `0 0 ${36 * glowPulse}px ${accentColor}77, 0 0 ${90 * glowPulse}px ${accentColor}33`
                    : undefined,
                  opacity: o,
                  transform: `translateY(${(1 - s) * 26}px) scale(${accent ? 0.92 + s * 0.08 : 1})`,
                  marginRight: wi < line.length - 1 ? 20 : 0,
                  verticalAlign: "baseline",
                }}
              >
                {w.text}
              </span>
            );
          })}
        </div>
      ))}
    </>
  );
};

export const KineticText: React.FC<KineticTextProps> = ({
  lines,
  stanzas,
  accentColor = theme.green,
  startFrame = 6,
  wordSpacing = 5,
  wordFrames,
}) => {
  const frame = useCurrentFrame();

  const breathe = Math.sin(frame / 13) * 4;
  const glowPulse = 0.7 + Math.sin(frame / 10) * 0.3;

  // frame de la palabra #g en orden global (timestamp real si existe)
  const frameOf = (g: number) =>
    wordFrames && wordFrames[g] != null ? wordFrames[g] : startFrame + g * wordSpacing;

  // normaliza a estrofas: legacy lines = una sola estrofa
  const groups: Word[][][] = stanzas ?? (lines ? [lines] : []);

  // indice global del primer word de cada estrofa, y su frame de entrada
  const starts: number[] = [];
  const startFrames: number[] = [];
  let acc = 0;
  for (const st of groups) {
    starts.push(acc);
    startFrames.push(frameOf(acc));
    for (const ln of st) acc += ln.length;
  }

  return (
    <StudioScene spotlightColor={accentColor}>
      <AbsoluteFill
        style={{ fontFamily: theme.font, justifyContent: "center", alignItems: "center" }}
      >
        {groups.map((st, i) => {
          const enter = startFrames[i];
          const next = i + 1 < startFrames.length ? startFrames[i + 1] : Infinity;
          // entra justo antes de su 1a palabra; sale al empezar la siguiente estrofa
          const inO = interpolate(frame, [enter - 4, enter + 6], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });
          const outO =
            next === Infinity
              ? 1
              : interpolate(frame, [next - 10, next - 2], [1, 0], {
                  extrapolateLeft: "clamp",
                  extrapolateRight: "clamp",
                });
          const op = Math.min(inO, outO);
          if (op <= 0) return null;
          const slideIn = (1 - inO) * 24;
          const slideOut = next === Infinity ? 0 : (1 - outO) * -24;
          return (
            <AbsoluteFill
              key={i}
              style={{ justifyContent: "center", alignItems: "center", opacity: op }}
            >
              <div
                style={{
                  width: 880,
                  textAlign: "center",
                  transform: `translateY(${breathe + slideIn + slideOut}px)`,
                }}
              >
                <Words
                  lines={st}
                  frameOf={frameOf}
                  startGlobalIdx={starts[i]}
                  accentColor={accentColor}
                  glowPulse={glowPulse}
                />
              </div>
            </AbsoluteFill>
          );
        })}
      </AbsoluteFill>
    </StudioScene>
  );
};
