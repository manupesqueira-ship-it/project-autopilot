import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  OffthreadVideo,
  staticFile,
  useCurrentFrame,
} from "remotion";
import { theme } from "../theme";

// SigErosionHero — la MECANICA-FIRMA completa: el hero de VIDRIO (plate Blender, el
// oro que se drena = tu dinero erosionado) + overlay de texto crujiente en Remotion.
// El plate es el fondo full-bleed; el texto va en CARRILES que NO enciman la columna
// (LAYOUT_CONTRACT): numero arriba, perdida abajo. Numero sincronizado al drenado
// (frames 20->66 = fases del plate erosion_glass_anim.py).

export type SigErosionHeroProps = {
  plate: string; // nombre del mp4 en public/, p.ej. "erosion_plate.mp4"
  kicker: string;
  currency: string;
  from: number;
  to: number;
  unit: string;
  lossLabel: string;
  contextLabel: string;
};

const fmt = (v: number) => Math.round(v).toLocaleString("en-US");

const extrude = (depth = 7, hue = "0,0,0") =>
  Array.from({ length: depth }, (_, i) => {
    const t = i / depth;
    return `0 ${i + 1}px 0 rgba(${hue},${(0.32 * (1 - t)).toFixed(3)})`;
  }).join(", ");

// fases (mismas que el plate Blender)
const F_HOLD = 20;
const F_DRAIN = 66;

export const SigErosionHero: React.FC<SigErosionHeroProps> = ({
  plate,
  kicker,
  currency,
  from,
  to,
  unit,
  lossLabel,
  contextLabel,
}) => {
  const frame = useCurrentFrame();
  const loss = from - to;

  const shown = interpolate(frame, [F_HOLD, F_DRAIN], [from, to], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.4, 0.0, 0.2, 1),
  });

  const kick = interpolate(frame, [4, 16], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const numO = interpolate(frame, [8, 18], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const glow = interpolate(frame, [F_HOLD, F_DRAIN], [0.5, 0.28], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  // esquirla roja de perdida: entra durante el drenado y cae
  const shard = interpolate(frame, [F_HOLD + 14, F_DRAIN], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.3, 0.0, 0.25, 1),
  });
  const shardY = interpolate(shard, [0, 1], [-14, 0]);
  const shardO = interpolate(frame, [F_HOLD + 14, F_HOLD + 26], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const lblO = interpolate(frame, [F_DRAIN - 4, F_DRAIN + 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ backgroundColor: "#070707" }}>
      <OffthreadVideo src={staticFile(plate)} muted style={{ width: "100%", height: "100%", objectFit: "cover" }} />

      <AbsoluteFill style={{ fontFamily: theme.font }}>
        {/* kicker */}
        <div
          style={{
            position: "absolute",
            top: 92,
            width: "100%",
            textAlign: "center",
            fontSize: 30,
            fontWeight: 300,
            letterSpacing: "0.4em",
            textTransform: "uppercase",
            color: "#9FB0C0",
            opacity: kick,
          }}
        >
          {kicker}
        </div>

        {/* numero hero (oro) contando hacia abajo — carril SUPERIOR, sobre la columna */}
        <div
          style={{
            position: "absolute",
            top: 150,
            width: "100%",
            textAlign: "center",
            opacity: numO,
          }}
        >
          <span
            style={{
              fontSize: 132,
              fontWeight: 800,
              color: theme.gold,
              letterSpacing: "-0.02em",
              fontVariantNumeric: "tabular-nums",
              whiteSpace: "nowrap",
              textShadow: `${extrude(7)}, 0 0 54px rgba(212,165,116,${glow})`,
            }}
          >
            {currency}
            {fmt(shown)}
            <span style={{ fontSize: "0.42em", fontWeight: 700, marginLeft: 10, color: "#C9B79A" }}>{unit}</span>
          </span>
        </div>

        {/* perdida roja — carril INFERIOR, bajo la columna */}
        <div
          style={{
            position: "absolute",
            top: 1560,
            width: "100%",
            textAlign: "center",
            transform: `translateY(${shardY}px)`,
            opacity: shardO,
          }}
        >
          <span
            style={{
              fontSize: 72,
              fontWeight: 800,
              color: theme.red,
              fontVariantNumeric: "tabular-nums",
              textShadow: `0 0 34px rgba(255,107,107,0.5), ${extrude(5, "40,0,0")}`,
            }}
          >
            −{currency}{fmt(loss)}
          </span>
        </div>

        <div
          style={{
            position: "absolute",
            top: 1690,
            width: "100%",
            textAlign: "center",
            opacity: lblO,
          }}
        >
          <div style={{ fontSize: 40, fontWeight: 600, color: theme.text }}>{lossLabel}</div>
          <div
            style={{
              marginTop: 12,
              fontSize: 26,
              fontWeight: 300,
              letterSpacing: "0.16em",
              textTransform: "uppercase",
              color: "#8497A9",
            }}
          >
            {contextLabel}
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
