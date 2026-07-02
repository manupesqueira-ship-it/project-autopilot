import React from "react";
import {
  AbsoluteFill,
  OffthreadVideo,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { theme } from "../theme";
import { PremiumStage } from "../studio/PremiumStage";

// b1 hook — texto cinético en el MISMO mundo premium (PremiumStage) que las
// gráficas aprobadas, para que el reel sea un solo plano coherente. Misma
// mecánica que KineticText (palabras que entran sincronizadas a la voz, acento
// esmeralda en las clave), sólo cambia el escenario (piso en perspectiva + luz).

type Word = { text: string; accent?: boolean };

export type KineticTextPremiumProps = {
  lines?: Word[][];
  stanzas?: Word[][][];
  accentColor?: string;
  startFrame?: number;
  wordSpacing?: number;
  wordFrames?: number[];
  logo?: string; // "bitcoin" ancla el sujeto con la marca ₿ vectorial (no IA)
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
            const s = spring({ frame: frame - t, fps, config: { damping: 200, mass: 0.9 } });
            const o = interpolate(frame, [t, t + 9], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            });
            const accent = w.accent;
            return (
              <span
                key={wi}
                style={{
                  display: "inline-block",
                  fontSize: accent ? 96 : 68,
                  fontWeight: accent ? 400 : 200,
                  color: accent ? accentColor : "#EAEEF2",
                  letterSpacing: accent ? "0.05em" : "0.16em",
                  textTransform: "uppercase",
                  textShadow: accent
                    ? `0 0 ${26 * glowPulse}px ${accentColor}66, 0 0 ${70 * glowPulse}px ${accentColor}26`
                    : undefined,
                  opacity: o,
                  transform: `translateY(${(1 - s) * 22}px)`,
                  marginRight: wi < line.length - 1 ? 24 : 0,
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

export const KineticTextPremium: React.FC<KineticTextPremiumProps> = ({
  lines = [
    [{ text: "Un" }, { text: "país", accent: true }, { text: "entero" }],
    [{ text: "apostó" }, { text: "todo" }],
    [{ text: "al" }, { text: "Bitcoin", accent: true }],
  ],
  stanzas,
  accentColor = theme.green,
  startFrame = 6,
  wordSpacing = 7,
  wordFrames,
  logo,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames, fps } = useVideoConfig();

  const breathe = Math.sin(frame / 42) * 3;
  const glowPulse = 0.72 + Math.sin(frame / 22) * 0.22;

  // El hook NUNCA se congela: push-in continuo de todo el plano + deriva lenta
  // del bloque (parallax). La voz dura ~13s; el visual sigue vivo todo el beat.
  const push = interpolate(frame, [0, durationInFrames], [1.0, 1.06], {
    extrapolateRight: "clamp",
  });
  const driftY = interpolate(frame, [0, durationInFrames], [12, -12], {
    extrapolateRight: "clamp",
  });

  // moneda ₿ (Higgsfield i2v, NO a mano): es el héroe del hook. Aparece temprano
  // y sostiene el plano; el clip de ~5s se estira a todo el beat -> cámara lenta
  // cinematográfica que casa con el mundo negro mate de la biblia.
  const showCoin = logo === "bitcoin";
  const coinIn = interpolate(frame, [6, 30], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const coinPlayback = Math.min(1, (5.0 * fps) / durationInFrames);

  const frameOf = (g: number) =>
    wordFrames && wordFrames[g] != null ? wordFrames[g] : startFrame + g * wordSpacing;

  const groups: Word[][][] = stanzas ?? (lines ? [lines] : []);

  const starts: number[] = [];
  const startFrames: number[] = [];
  let acc = 0;
  for (const st of groups) {
    starts.push(acc);
    startFrames.push(frameOf(acc));
    for (const ln of st) acc += ln.length;
  }

  return (
    <PremiumStage tint={accentColor}>
      <AbsoluteFill style={{ transform: `scale(${push})`, transformOrigin: "50% 47%" }}>
        {showCoin && (
          <>
            {/* moneda ₿ Higgsfield a sangre. screen-blend: el vacío negro del clip
                cae y el mundo PremiumStage sigue vivo detrás (coherencia del reel). */}
            <AbsoluteFill style={{ opacity: coinIn }}>
              <OffthreadVideo
                src={staticFile("i2v/btc_coin_hook.mp4")}
                muted
                playbackRate={coinPlayback}
                style={{
                  width: "100%",
                  height: "100%",
                  objectFit: "cover",
                  objectPosition: "center 28%",
                  mixBlendMode: "screen",
                }}
              />
            </AbsoluteFill>
            {/* velo inferior: la moneda manda arriba, el texto se lee abajo. */}
            <AbsoluteFill
              style={{
                background:
                  "linear-gradient(180deg, transparent 42%, rgba(7,10,15,0.55) 54%, rgba(7,10,15,0.96) 64%, #070707 76%)",
                opacity: coinIn,
              }}
            />
          </>
        )}
        <AbsoluteFill
          style={{
            fontFamily: theme.font,
            justifyContent: "center",
            alignItems: "center",
            transform: `translateY(${driftY + (showCoin ? 430 : 0)}px)`,
          }}
        >
          {groups.map((st, i) => {
          const enter = startFrames[i];
          const next = i + 1 < startFrames.length ? startFrames[i + 1] : Infinity;
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
      </AbsoluteFill>
    </PremiumStage>
  );
};
