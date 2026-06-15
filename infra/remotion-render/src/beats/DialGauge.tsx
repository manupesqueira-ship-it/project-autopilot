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

// Velocimetro / gauge semicircular: una sola metrica entre min y max, con aguja
// que barre y zonas semanticas (rojo->oro->verde). Para "nivel de riesgo", "que
// tan caro esta", "tasa de X%". El numero del centro cuenta hasta el valor.
export type DialGaugeProps = {
  caption: string;
  value: number;
  min?: number;
  max: number;
  label?: string;
  prefix?: string;
  suffix?: string;
  decimals?: number;
  goodHigh?: boolean; // true: mas alto = verde; false: mas alto = rojo
  tone?: string; // color explicito; si no, se deriva por zona
};

const CX = 540;
const CY = 1120;
const R = 360;
const SW = 60;
const ZONES = [theme.red, theme.gold, theme.green];

const polar = (cx: number, cy: number, r: number, deg: number) => {
  const a = (deg * Math.PI) / 180;
  return [cx + r * Math.cos(a), cy + r * Math.sin(a)] as const;
};
// arco superior: deg 180 (izq) -> 360 (der), y hacia arriba (sin negativo)
const arcPath = (r: number, fromDeg: number, toDeg: number) => {
  const [x0, y0] = polar(CX, CY, r, fromDeg);
  const [x1, y1] = polar(CX, CY, r, toDeg);
  const large = Math.abs(toDeg - fromDeg) > 180 ? 1 : 0;
  return `M ${x0} ${y0} A ${r} ${r} 0 ${large} 1 ${x1} ${y1}`;
};

export const DialGauge: React.FC<DialGaugeProps> = ({
  caption,
  value,
  min = 0,
  max,
  label,
  prefix = "",
  suffix = "%",
  decimals = 0,
  goodHigh = true,
  tone,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const clamp = {
    extrapolateLeft: "clamp" as const,
    extrapolateRight: "clamp" as const,
  };

  const f = Math.max(0, Math.min(1, (value - min) / (max - min || 1)));
  // zona semantica segun fraccion (invertida si goodHigh=false)
  const t = goodHigh ? f : 1 - f;
  const zoneColor = tone ?? (t < 0.34 ? ZONES[0] : t < 0.67 ? ZONES[1] : ZONES[2]);

  const sweep = spring({ frame: frame - 12, fps, config: { damping: 15, mass: 1.1 } });
  const fAnim = f * Math.min(sweep, 1);
  const angleDeg = 180 + 180 * fAnim; // 180=izq, 360=der
  // micro-bob continuo de la aguja tras asentar
  const bob = Math.sin(frame / 9) * 0.8 * Math.min(sweep, 1);
  const needleDeg = angleDeg + bob;
  const [nx, ny] = polar(CX, CY, R - SW / 2 - 6, needleDeg);

  const shown = interpolate(frame, [12, 70], [min, value], { ...clamp });
  const fmt = (v: number) =>
    prefix +
    v.toLocaleString("en-US", {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }) +
    suffix;

  const pulse = 0.5 + 0.5 * Math.sin(frame / 12);
  const capWords = caption.split(" ");

  return (
    <StudioScene grid spotlightColor={zoneColor}>
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
          <defs>
            <linearGradient id="gaugeGrad" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor={ZONES[0]} />
              <stop offset="50%" stopColor={ZONES[1]} />
              <stop offset="100%" stopColor={ZONES[2]} />
            </linearGradient>
          </defs>
          {/* riel de fondo */}
          <path d={arcPath(R, 180, 360)} fill="none" stroke="#FFFFFF" strokeOpacity={0.08} strokeWidth={SW} strokeLinecap="round" />
          {/* arco de color semantico hasta el valor */}
          {fAnim > 0.001 && (
            <path
              d={arcPath(R, 180, angleDeg)}
              fill="none"
              stroke="url(#gaugeGrad)"
              strokeWidth={SW}
              strokeLinecap="round"
              style={{ filter: `drop-shadow(0 0 ${10 + pulse * 10}px ${zoneColor}88)` }}
            />
          )}
          {/* ticks min/max */}
          <text {...polarText(180, R + 46)} textAnchor="middle" fill={theme.textDim} fontSize={28} fontWeight={600} style={{ fontFamily: theme.font }}>
            {fmt(min).replace(suffix, "")}
          </text>
          <text {...polarText(360, R + 46)} textAnchor="middle" fill={theme.textDim} fontSize={28} fontWeight={600} style={{ fontFamily: theme.font }}>
            {fmt(max).replace(suffix, "")}
          </text>
          {/* aguja */}
          <line x1={CX} y1={CY} x2={nx} y2={ny} stroke={theme.text} strokeWidth={8} strokeLinecap="round" style={{ filter: `drop-shadow(0 0 8px ${zoneColor})` }} />
          <circle cx={CX} cy={CY} r={22} fill={theme.text} />
          <circle cx={CX} cy={CY} r={11} fill={zoneColor} />
        </svg>

        {/* numero grande central (cifra exacta) */}
        <div
          style={{
            position: "absolute",
            top: CY - 250,
            width: "100%",
            textAlign: "center",
          }}
        >
          <div
            style={{
              fontSize: 130,
              fontWeight: 900,
              color: zoneColor,
              letterSpacing: "-0.03em",
              fontVariantNumeric: "tabular-nums",
              lineHeight: 1,
              textShadow: `0 0 ${24 + pulse * 16}px ${zoneColor}66`,
            }}
          >
            {fmt(shown)}
          </div>
          {label && (
            <div style={{ fontSize: 36, fontWeight: 600, color: theme.textDim, marginTop: 10 }}>
              {label}
            </div>
          )}
        </div>
      </AbsoluteFill>
    </StudioScene>
  );
};

// helper para posicionar los ticks de min/max como props x,y
function polarText(deg: number, r: number) {
  const a = (deg * Math.PI) / 180;
  return { x: CX + r * Math.cos(a), y: CY + r * Math.sin(a) + 10 };
}
