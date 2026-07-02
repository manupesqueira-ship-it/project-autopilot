import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { IglooStage } from "../studio/IglooStage";
import { WINTER, WinterDefs, IceShards, rng } from "../studio/winter";

// SF-3 / beat clímax (v2) — EL DESHIELO. El hielo se hace añicos, estalla luz
// esmeralda y la GANANCIA (+$209,000,000) erupciona hacia arriba entre las
// grietas, con brasas doradas subiendo. La catarsis que paga el "aguantó".

const W = 1080;
const H = 1920;
const CX = W / 2;
const CY = 880;

export const ThawClimax: React.FC<{
  gainValue?: string;
  pctLabel?: string;
}> = ({ gainValue = "+$209,000,000", pctLabel = "+77% SOBRE LO INVERTIDO" }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const r = rng(21);

  const shatter = interpolate(frame, [0, 26], [0, 0.62], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  // destello blanco-esmeralda UNICO (sube y baja)
  const flashT = interpolate(frame, [2, 12, 30], [0, 1, 0.18], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const numSpring = spring({ frame: frame - 8, fps, config: { damping: 12, mass: 0.8 } });
  const numScale = 0.7 + numSpring * 0.3;
  const numY = (1 - numSpring) * 70;
  const pct = interpolate(frame, [22, 36], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <IglooStage accent={WINTER.green} glowY={0.48} grainSeed={3}>
      <AbsoluteFill style={{ fontFamily: "InterVar, Inter, sans-serif" }}>
        <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{ position: "absolute", inset: 0 }}>
          <WinterDefs />

          {/* fisura vertical esmeralda detras del numero */}
          <g opacity={0.6 * shatter * 1.6}>
            <path
              d={`M ${CX} 360 L ${CX - 22} 620 L ${CX + 18} 900 L ${CX - 16} 1180 L ${CX + 10} 1420`}
              fill="none"
              stroke={WINTER.greenHot}
              strokeWidth={4}
              style={{ filter: `drop-shadow(0 0 16px ${WINTER.green})` }}
            />
          </g>

          {/* oleada esmeralda */}
          <circle
            cx={CX}
            cy={CY}
            r={120 + shatter * 520}
            fill={WINTER.green}
            opacity={0.18 * (1 - shatter)}
            style={{ filter: "url(#w-blur-lg)" }}
          />

          {/* añicos de hielo radiando */}
          <IceShards cx={CX} cy={CY} count={26} spread={620} t={Math.min(shatter / 0.62, 1) * 0.6} seed={7} />

          {/* destello blanco unico */}
          {flashT > 0.02 && (
            <circle cx={CX} cy={CY} r={80 + flashT * 320} fill="#FFFFFF" opacity={0.55 * flashT} style={{ filter: "url(#w-blur-lg)" }} />
          )}

          {/* brasas doradas subiendo */}
          {Array.from({ length: 12 }).map((_, i) => {
            const ex = CX + (r() - 0.5) * 760;
            const ey = CY + 360 - r() * 760 * shatter;
            const er = 3 + r() * 7;
            return (
              <circle key={i} cx={ex} cy={ey} r={er} fill={WINTER.goldHot} opacity={0.7 * shatter} style={{ filter: "url(#w-blur-sm)" }} />
            );
          })}
        </svg>

        {/* GANANCIA — erupciona hacia arriba */}
        <div
          style={{
            position: "absolute",
            top: CY - 120,
            width: "100%",
            textAlign: "center",
            color: "#EAFFF8",
            fontSize: 118,
            fontWeight: 800,
            letterSpacing: "-0.02em",
            fontVariantNumeric: "tabular-nums",
            transform: `translateY(${numY}px) scale(${numScale})`,
            textShadow: `0 0 40px ${WINTER.green}, 0 0 90px ${WINTER.green}66`,
          }}
        >
          {gainValue}
        </div>

        {/* +77% stamp */}
        <div
          style={{
            position: "absolute",
            top: CY + 40,
            width: "100%",
            textAlign: "center",
            color: WINTER.green,
            fontSize: 44,
            fontWeight: 700,
            letterSpacing: "0.06em",
            opacity: pct,
            transform: `scale(${0.9 + pct * 0.1})`,
          }}
        >
          {pctLabel}
        </div>

        {/* kicker pequeño arriba */}
        <div
          style={{
            position: "absolute",
            top: 250,
            width: "100%",
            textAlign: "center",
            color: "#5FD9BE",
            fontSize: 30,
            fontWeight: 300,
            letterSpacing: "0.42em",
            textTransform: "uppercase",
            opacity: 0.82,
          }}
        >
          El hielo se rompió
        </div>
      </AbsoluteFill>
    </IglooStage>
  );
};
