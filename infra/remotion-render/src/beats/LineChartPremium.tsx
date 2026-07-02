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
import { PremiumStage } from "../studio/PremiumStage";
import {
  AreaFill,
  BloomFlash,
  Caption,
  FloatLabel,
  FloorReflection,
  GlossyOrb,
  GlowLine,
  KitDefs,
  SemanticDivider,
} from "../kit";

// LineChartPremium — la grafica de linea semantica (verde->rojo) RECONSTRUIDA
// sobre el KIT compartido + PremiumStage (mundo vivo). Misma data/props que
// BeatLineChart (BTC) para un antes/despues honesto. Diferencia con el viejo:
// menos chrome, mas espacio negativo, trazo con bloom volumetrico, orbe que
// cabalga la punta, reflejo en el piso y UN destello blanco en el quiebre.

export type LineChartProps = {
  caption: string;
  points: number[];
  peakIndex: number;
  labels: { text: string; index: number; color?: string }[];
  peakLabel?: string;
};

const X0 = 112;
const X1 = 968;
const YTOP = 560;
const YBOT = 1150;
const MIRROR_Y = 1182; // piso (HORIZON de PremiumStage) -> reflejo debajo

const SAFE_X = 24;
const clampLabelLeft = (rawLeft: number, w: number) =>
  Math.min(Math.max(rawLeft, SAFE_X), 1080 - w - SAFE_X);

export const LineChartPremium: React.FC<LineChartProps> = ({
  caption,
  points,
  peakIndex,
  labels,
  peakLabel,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const n = points.length;
  const vMax = Math.max(...points);
  const vMin = Math.min(...points);
  const pad = (vMax - vMin) * 0.1 || 1;
  const lo = vMin - pad;
  const hi = vMax + pad;

  const xy = points.map((v, i) => ({
    x: X0 + ((X1 - X0) * i) / (n - 1),
    y: YBOT - ((YBOT - YTOP) * (v - lo)) / (hi - lo),
  }));

  const segLen: number[] = [];
  let total = 0;
  for (let i = 0; i < n - 1; i++) {
    const L = Math.hypot(xy[i + 1].x - xy[i].x, xy[i + 1].y - xy[i].y);
    segLen.push(L);
    total += L;
  }
  const cum = [0];
  for (const L of segLen) cum.push(cum[cum.length - 1] + L);
  const greenLen = cum[peakIndex];
  const redLen = total - greenLen;

  // timeline (D=160): 8-84 dibuja verde · 80-92 quiebre (divisor+destello) ·
  // 92-150 cae rojo. Entre 84 y 92 la punta se queda en el pico (el momento).
  const greenProg = interpolate(frame, [8, 84], [0, greenLen], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.3, 0.1, 0.3, 1),
  });
  const redProg = interpolate(frame, [92, 150], [greenLen, total], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.5, 0, 0.8, 1),
  });
  const drawn = frame < 92 ? greenProg : redProg;

  const posAt = (len: number) => {
    const L = Math.min(Math.max(len, 0), total - 0.001);
    let i = 0;
    while (i < n - 2 && cum[i + 1] <= L) i++;
    const t = (L - cum[i]) / segLen[i];
    return {
      x: xy[i].x + (xy[i + 1].x - xy[i].x) * t,
      y: xy[i].y + (xy[i + 1].y - xy[i].y) * t,
    };
  };
  const dot = posAt(drawn);
  const onRed = drawn > greenLen + 0.5;

  const linePath = (from: number, to: number) =>
    xy
      .slice(from, to + 1)
      .map((p, i) => `${i === 0 ? "M" : "L"}${p.x},${p.y}`)
      .join(" ");
  const areaPath = (from: number, to: number) =>
    `${linePath(from, to)} L${xy[to].x},${YBOT + 60} L${xy[from].x},${YBOT + 60} Z`;

  const greenPath = linePath(0, peakIndex);
  const redPath = peakIndex < n - 1 ? linePath(peakIndex, n - 1) : "";
  const greenDrawn = Math.min(drawn, greenLen);
  const redDrawn = Math.max(drawn - greenLen, 0);

  const peak = xy[peakIndex];
  const dividerProg = interpolate(frame, [80, 92], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.2, 0, 0.3, 1),
  });
  const flashT = interpolate(frame, [80, 86, 98], [0, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const tint = onRed ? theme.red : theme.green;

  return (
    <PremiumStage tint={tint}>
      <AbsoluteFill style={{ fontFamily: theme.font }}>
        <Caption text={caption} frame={frame} />

        <svg width="1080" height="1920" style={{ position: "absolute" }}>
          <KitDefs />
          <defs>
            <clipPath id="lcp-clipG">
              <rect x={X0 - 6} y={0} width={Math.max(dot.x - X0 + 8, 0)} height={1920} />
            </clipPath>
            <clipPath id="lcp-clipR">
              <rect x={peak.x} y={0} width={Math.max(dot.x - peak.x + 4, 0)} height={1920} />
            </clipPath>
          </defs>

          {/* reflejo en el piso (detras de todo) */}
          <FloorReflection d={greenPath} length={greenLen} drawn={greenDrawn} color={theme.green} mirrorY={MIRROR_Y} />
          {redPath && frame >= 92 && (
            <FloorReflection d={redPath} length={redLen} drawn={redDrawn} color={theme.red} mirrorY={MIRROR_Y} />
          )}

          {/* cuerpo bajo la curva */}
          <AreaFill d={areaPath(0, peakIndex)} fillId="kit-fill-green" clipPathId="lcp-clipG" />
          {peakIndex < n - 1 && (
            <AreaFill d={areaPath(peakIndex, n - 1)} fillId="kit-fill-red" clipPathId="lcp-clipR" />
          )}

          {/* trazos heroe */}
          <GlowLine d={greenPath} length={greenLen} drawn={greenDrawn} color={theme.green} />
          {redPath && (
            <GlowLine d={redPath} length={redLen} drawn={redDrawn} color={theme.red} visible={frame >= 92} />
          )}

          {/* quiebre semantico: divisor + UN destello blanco */}
          <SemanticDivider x={peak.x} yTop={peak.y - 64} yBot={YBOT + 50} progress={dividerProg} />
          <BloomFlash x={peak.x} y={peak.y} t={flashT} />

          {/* orbe que cabalga la punta */}
          {drawn > 2 && <GlossyOrb x={dot.x} y={dot.y} variant={onRed ? "red" : "green"} />}
        </svg>

        {/* etiquetas de dato (chicas, tenues, en espacio negativo arriba del punto) */}
        {labels.map((lb, k) => {
          const p = xy[lb.index];
          const trigger = cum[lb.index];
          const appearFrame =
            trigger <= greenLen
              ? 8 + (trigger / Math.max(greenLen, 1)) * 76
              : 92 + ((trigger - greenLen) / Math.max(redLen, 1)) * 58;
          const appeared = drawn >= trigger - 1;
          const s = appeared
            ? spring({ frame: frame - appearFrame, fps, config: { damping: 14, mass: 0.6 } })
            : 0;
          const LBL_W = 360;
          return (
            <FloatLabel
              key={k}
              left={clampLabelLeft(p.x - LBL_W / 2, LBL_W)}
              top={p.y - 92}
              width={LBL_W}
              text={lb.text}
              appear={s}
              color={lb.color ?? theme.textDim}
              size={30}
            />
          );
        })}

        {/* pico: cifra dorada flotante (sin caja, sin chrome) */}
        {peakLabel && (
          <div
            style={{
              position: "absolute",
              left: clampLabelLeft(peak.x - 240, 480),
              top: peak.y - 142,
              width: 480,
              textAlign: "center",
              fontFamily: theme.font,
              fontSize: 50,
              fontWeight: 800,
              color: theme.gold,
              opacity: interpolate(frame, [84, 92], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
              transform: `scale(${spring({ frame: frame - 84, fps, config: { damping: 12, mass: 0.7 } }) * 0.14 + 0.86})`,
              textShadow: `0 0 28px ${theme.gold}66`,
            }}
          >
            {peakLabel}
          </div>
        )}
      </AbsoluteFill>
    </PremiumStage>
  );
};
