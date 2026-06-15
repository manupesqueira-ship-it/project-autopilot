import React from "react";
import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
} from "remotion";
import { theme } from "../theme";
import { StudioScene } from "../studio/StudioScene";

// Anillo de progreso (una sola meta): el arco barre desde arriba en sentido
// horario hasta el porcentaje, con un punto glossy al frente y el % contando en
// el centro. Distinto del donut (proporcion multi-segmento): esto es UNA meta.
// Para "ya pagaste X% de tu deuda", "lograste X% de tu meta de ahorro".
export type ProgressRingProps = {
  caption: string;
  percent: number; // 0-100
  label?: string;
  color?: string;
  centerSuffix?: string;
  centerDecimals?: number;
};

const CX = 540;
const CY = 940;
const R = 300;
const SW = 76;

export const ProgressRing: React.FC<ProgressRingProps> = ({
  caption,
  percent,
  label,
  color = theme.green,
  centerSuffix = "%",
  centerDecimals = 0,
}) => {
  const frame = useCurrentFrame();
  const clamp = {
    extrapolateLeft: "clamp" as const,
    extrapolateRight: "clamp" as const,
  };

  const C = 2 * Math.PI * R;
  const frac = Math.max(0, Math.min(1, percent / 100));
  const sweep = interpolate(frame, [10, 75], [0, frac], {
    ...clamp,
    easing: (t) => 1 - Math.pow(1 - t, 3),
  });
  const visLen = sweep * C;
  const shown = interpolate(frame, [10, 75], [0, percent], { ...clamp });
  const pulse = 0.5 + 0.5 * Math.sin(frame / 11);

  // punto al frente del arco (angulo: arranca arriba -90 deg, horario)
  const ang = (-90 + 360 * sweep) * (Math.PI / 180);
  const dotX = CX + R * Math.cos(ang);
  const dotY = CY + R * Math.sin(ang);

  const fmt = (v: number) =>
    v.toLocaleString("en-US", {
      minimumFractionDigits: centerDecimals,
      maximumFractionDigits: centerDecimals,
    });

  const capWords = caption.split(" ");

  return (
    <StudioScene grid spotlightColor={color}>
      <AbsoluteFill style={{ fontFamily: theme.font }}>
        <div
          style={{
            position: "absolute",
            top: 250,
            width: "100%",
            textAlign: "center",
            fontSize: 40,
            fontWeight: 500,
            color: theme.textDim,
          }}
        >
          {capWords.map((w, i) => (
            <span key={i} style={{ opacity: interpolate(frame, [2 + i * 3, 8 + i * 3], [0, 1], clamp) }}>
              {w}{" "}
            </span>
          ))}
        </div>

        <svg width="1080" height="1920" style={{ position: "absolute" }}>
          {/* riel */}
          <circle cx={CX} cy={CY} r={R} fill="none" stroke="#FFFFFF" strokeOpacity={0.08} strokeWidth={SW} />
          {/* progreso */}
          <circle
            cx={CX}
            cy={CY}
            r={R}
            fill="none"
            stroke={color}
            strokeWidth={SW}
            strokeLinecap="round"
            strokeDasharray={`${visLen} ${C}`}
            transform={`rotate(-90 ${CX} ${CY})`}
            style={{ filter: `drop-shadow(0 0 ${14 + pulse * 12}px ${color}aa)` }}
          />
          {/* punto glossy al frente */}
          {sweep > 0.003 && (
            <circle cx={dotX} cy={dotY} r={SW / 2 - 4} fill="#FFFFFF" opacity={0.9} style={{ filter: `drop-shadow(0 0 ${10 + pulse * 8}px ${color})` }} />
          )}
        </svg>

        {/* centro: % contando */}
        <div
          style={{
            position: "absolute",
            left: CX - 260,
            top: CY - 120,
            width: 520,
            textAlign: "center",
          }}
        >
          <div
            style={{
              fontSize: 150,
              fontWeight: 900,
              color,
              letterSpacing: "-0.03em",
              fontVariantNumeric: "tabular-nums",
              lineHeight: 1,
              textShadow: `0 0 ${28 + pulse * 18}px ${color}66`,
            }}
          >
            {fmt(shown)}
            <span style={{ fontSize: 80 }}>{centerSuffix}</span>
          </div>
          {label && (
            <div style={{ fontSize: 38, fontWeight: 600, color: theme.textDim, marginTop: 14 }}>
              {label}
            </div>
          )}
        </div>
      </AbsoluteFill>
    </StudioScene>
  );
};
