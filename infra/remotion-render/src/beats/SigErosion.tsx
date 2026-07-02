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
import { IglooStage } from "../studio/IglooStage";

// SigErosion — PROTOTIPO de MECÁNICA-FIRMA (2026-07-01).
// El gesto ownable de Dinero IA: una cifra en oro (dinero) que se EROSIONA a su
// valor real; el trozo perdido se desprende como una esquirla ROJA (pérdida, único
// uso legítimo del rojo) que cae. Firma = gramática de transición: entre dos hechos
// que CONTRASTAN (nominal->real), deformación intensa; datos exactos del reel C.
// Todo código determinista sobre IglooStage (look igloo.inc). Sin partículas a mano:
// el calor/brasa orgánico iría BAKEADO por i2v en una capa posterior.

export type SigErosionProps = {
  kicker: string; // "EN EFECTIVO"
  currency: string; // "$"
  from: number; // 100000
  to: number; // 96209
  unit: string; // "MXN"
  lossLabel: string; // "lo que se comió la inflación"
  contextLabel: string; // "inflación 3.94% · 12 meses"
};

const fmt = (v: number) =>
  Math.round(v).toLocaleString("en-US");

// faux-3D: pila de sombras = grosor del dígito (profundidad $0, sin Blender).
const extrude = (depth = 8, hue = "0,0,0") =>
  Array.from({ length: depth }, (_, i) => {
    const t = i / depth;
    return `0 ${i + 1}px 0 rgba(${hue},${(0.34 * (1 - t)).toFixed(3)})`;
  }).join(", ");

export const SigErosion: React.FC<SigErosionProps> = ({
  kicker,
  currency,
  from,
  to,
  unit,
  lossLabel,
  contextLabel,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const loss = from - to;

  // --- fases ---
  const E0 = 46; // inicia erosión
  const E1 = 88; // termina erosión

  // entrada del número: pop con overshoot sutil (anim SPRING.entrance)
  const pop = spring({ frame: frame - 8, fps, config: { damping: 13, mass: 0.85, stiffness: 120 } });
  const enterScale = 0.9 + pop * 0.1;

  // erosión: cuenta hacia abajo, ease-in-out lento (igloo = calma)
  const eron = interpolate(frame, [E0, E1], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.4, 0.0, 0.2, 1),
  });
  const shown = from - loss * eron;

  // gesto-firma: la cifra "asienta" hacia abajo y enfría su brillo al erosionarse
  const settleScale = interpolate(eron, [0, 1], [1, 0.972]);
  const sinkY = interpolate(eron, [0, 1], [0, 10]);
  const glow = interpolate(eron, [0, 1], [0.55, 0.28]); // el oro se enfría, no muere

  // esquirla roja de pérdida: se desprende y cae (aparece con la erosión)
  const shard = interpolate(frame, [E0 + 10, E1], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.3, 0.0, 0.25, 1),
  });
  const shardY = interpolate(shard, [0, 1], [0, 120]);
  const shardOpacity = interpolate(shard, [0, 0.25, 0.85, 1], [0, 1, 1, 0.62]);

  // subrayado rojo que barre bajo la cifra al erosionar
  const sweep = interpolate(frame, [E0, E0 + 26], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  // labels finales
  const lblO = interpolate(frame, [E1 - 6, E1 + 10], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const kick = interpolate(frame, [2, 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  const numColor = theme.gold;

  return (
    <IglooStage accent={eron > 0.5 ? theme.red : theme.gold} glowY={0.48}>
      <AbsoluteFill style={{ fontFamily: theme.font }}>
        {/* kicker */}
        <div
          style={{
            position: "absolute",
            top: 620,
            width: "100%",
            textAlign: "center",
            fontSize: 32,
            fontWeight: 300,
            letterSpacing: "0.4em",
            textTransform: "uppercase",
            color: "#8497A9",
            opacity: kick,
          }}
        >
          {kicker}
        </div>

        {/* número hero (oro) — extrude + glow, asienta y enfría al erosionar */}
        <div
          style={{
            position: "absolute",
            top: 760,
            width: "100%",
            textAlign: "center",
            transform: `translateY(${sinkY}px) scale(${enterScale * settleScale})`,
            opacity: interpolate(frame, [8, 16], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          }}
        >
          <span
            style={{
              fontSize: 150,
              fontWeight: 800,
              color: numColor,
              letterSpacing: "-0.02em",
              fontVariantNumeric: "tabular-nums",
              whiteSpace: "nowrap",
              textShadow: `${extrude(8)}, 0 0 60px rgba(212,165,116,${glow})`,
            }}
          >
            {currency}
            {fmt(shown)}
            <span style={{ fontSize: "0.42em", fontWeight: 700, marginLeft: 12, color: "#C9B79A" }}>{unit}</span>
          </span>

          {/* subrayado rojo que barre bajo la cifra (pérdida) */}
          <div
            style={{
              margin: "22px auto 0",
              width: `${sweep * 44}%`,
              height: 3,
              borderRadius: 3,
              background: theme.red,
              boxShadow: `0 0 18px ${theme.red}`,
              opacity: 0.9 * sweep,
            }}
          />
        </div>

        {/* esquirla ROJA de pérdida: se desprende y cae */}
        <div
          style={{
            position: "absolute",
            top: 980,
            width: "100%",
            textAlign: "center",
            transform: `translateY(${shardY}px)`,
            opacity: shardOpacity,
          }}
        >
          <span
            style={{
              fontSize: 66,
              fontWeight: 800,
              color: theme.red,
              letterSpacing: "-0.01em",
              fontVariantNumeric: "tabular-nums",
              textShadow: `0 0 34px rgba(255,107,107,0.5), ${extrude(5, "40,0,0")}`,
            }}
          >
            −{currency}{fmt(loss)}
          </span>
        </div>

        {/* labels finales */}
        <div
          style={{
            position: "absolute",
            top: 1180,
            width: "100%",
            textAlign: "center",
            opacity: lblO,
          }}
        >
          <div style={{ fontSize: 40, fontWeight: 600, color: theme.text, letterSpacing: "-0.01em" }}>
            {lossLabel}
          </div>
          <div
            style={{
              marginTop: 14,
              fontSize: 27,
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
    </IglooStage>
  );
};
