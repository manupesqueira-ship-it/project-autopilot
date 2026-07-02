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

// BeatRealValueMelt — el "efecto tijera": tu plazo fijo SUBE en pesos (nominal,
// oro) pero la inflación derrite su PODER DE COMPRA (real, rojo). El hueco que se
// abre entre las dos = lo que te comió la inflación. Datos EXACTOS del brief
// (Argentina, jun 2026). Sin título textual encima de la gráfica: la voz narra.

export type RealValueMeltProps = {
  caption: string;
  currency?: string; // "$"
  principal: number; // 1000000
  nominalEnd: number; // 1211300
  realEnd: number; // 909400
  teaTag: string; // "plazo fijo +21%"
  inflTag: string; // "inflación 33%"
  nominalLabel: string; // "te devuelve el banco"
  realLabel: string; // "te alcanza en el súper"
  punch: string; // "−$90.600 de poder de compra"
};

const X0 = 122;
const X1 = 958;
const YTOP = 690;
const YBOT = 1086;
const SAFE = 16;
const MONTHS = 12;

const clampLeft = (raw: number, w: number) =>
  Math.min(Math.max(raw, SAFE), 1080 - w - SAFE);

const fmtAR = (n: number) =>
  new Intl.NumberFormat("es-AR", { maximumFractionDigits: 0 }).format(Math.round(n));

export const RealValueMelt: React.FC<RealValueMeltProps> = ({
  caption,
  currency = "$",
  principal,
  nominalEnd,
  realEnd,
  teaTag,
  inflTag,
  nominalLabel,
  realLabel,
  punch,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const D = durationInFrames;

  // curvas: interpolación geométrica => arranca EXACTO en principal y termina
  // EXACTO en el endpoint (oro sube, rojo baja), con forma de compounding.
  const gN = nominalEnd / principal;
  const gR = realEnd / principal;
  const nominal = Array.from({ length: MONTHS + 1 }, (_, i) =>
    principal * Math.pow(gN, i / MONTHS),
  );
  const real = Array.from({ length: MONTHS + 1 }, (_, i) =>
    principal * Math.pow(gR, i / MONTHS),
  );

  const vMax = nominalEnd;
  const vMin = realEnd;
  const pad = (vMax - vMin) * 0.06;
  const lo = vMin - pad;
  const hi = vMax + pad;
  const xAt = (i: number) => X0 + ((X1 - X0) * i) / MONTHS;
  const yAt = (v: number) => YBOT - ((YBOT - YTOP) * (v - lo)) / (hi - lo);

  const nXY = nominal.map((v, i) => ({ x: xAt(i), y: yAt(v) }));
  const rXY = real.map((v, i) => ({ x: xAt(i), y: yAt(v) }));
  const y0 = yAt(principal); // altura de arranque compartida

  // longitudes acumuladas para dibujar con dash
  const pathLen = (pts: { x: number; y: number }[]) => {
    const seg: number[] = [];
    let total = 0;
    for (let i = 0; i < pts.length - 1; i++) {
      const L = Math.hypot(pts[i + 1].x - pts[i].x, pts[i + 1].y - pts[i].y);
      seg.push(L);
      total += L;
    }
    return { seg, total };
  };
  const nLen = pathLen(nXY);
  const rLen = pathLen(rXY);

  const polyline = (pts: { x: number; y: number }[]) =>
    pts.map((p, i) => `${i === 0 ? "M" : "L"}${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(" ");

  // timeline (fracciones de D)
  const nDraw = interpolate(frame, [D * 0.06, D * 0.46], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.3, 0.1, 0.3, 1),
  });
  const rDraw = interpolate(frame, [D * 0.4, D * 0.8], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.45, 0, 0.4, 1),
  });

  // x hasta donde está dibujada cada curva (para clip de área + dot)
  const nDrawX = X0 + (X1 - X0) * nDraw;
  const rDrawX = X0 + (X1 - X0) * rDraw;
  const wedgeX = Math.min(nDrawX, rDrawX);

  // readouts que cuentan a los valores exactos
  const nVal = interpolate(frame, [D * 0.1, D * 0.5], [principal, nominalEnd], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const rVal = interpolate(frame, [D * 0.44, D * 0.82], [principal, realEnd], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  const punchIn = spring({ frame: frame - D * 0.8, fps, config: { damping: 14, mass: 0.8 } });

  // los readouts ENTRAN con su propia línea (no antes): oro con el dibujo nominal,
  // rojo cuando arranca a derretirse el real
  const nOpacity = interpolate(frame, [D * 0.08, D * 0.18], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const rOpacity = interpolate(frame, [D * 0.42, D * 0.52], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // área del hueco (wedge) entre nominal y real, clip por x dibujado
  const wedgePath = (() => {
    const top = nXY.map((p) => `${p.x.toFixed(1)},${p.y.toFixed(1)}`);
    const bot = [...rXY].reverse().map((p) => `${p.x.toFixed(1)},${p.y.toFixed(1)}`);
    return `M${top.join(" L")} L${bot.join(" L")} Z`;
  })();

  const capWords = caption.split(" ");
  const nEnd = nXY[MONTHS];
  const rEnd = rXY[MONTHS];

  // posiciones de dot durante el dibujo
  const dotAt = (pts: { x: number; y: number }[], lenInfo: { seg: number[]; total: number }, prog: number) => {
    const target = lenInfo.total * prog;
    let acc = 0;
    for (let i = 0; i < pts.length - 1; i++) {
      if (acc + lenInfo.seg[i] >= target) {
        const t = (target - acc) / lenInfo.seg[i];
        return { x: pts[i].x + (pts[i + 1].x - pts[i].x) * t, y: pts[i].y + (pts[i + 1].y - pts[i].y) * t };
      }
      acc += lenInfo.seg[i];
    }
    return pts[pts.length - 1];
  };
  const nDot = dotAt(nXY, nLen, nDraw);
  const rDot = dotAt(rXY, rLen, rDraw);

  return (
    <PremiumStage tint={theme.gold}>
      <AbsoluteFill style={{ fontFamily: theme.font }}>
        {/* caption-kicker (NO subtítulo de la voz) palabra por palabra */}
        <div
          style={{
            position: "absolute",
            top: 300,
            width: "100%",
            textAlign: "center",
            fontSize: 42,
            fontWeight: 600,
            color: theme.textDim,
            letterSpacing: "0.005em",
          }}
        >
          {capWords.map((w, i) => {
            const o = interpolate(frame, [4 + i * 3, 12 + i * 3], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            });
            return (
              <span key={i} style={{ opacity: o }}>
                {w}{" "}
              </span>
            );
          })}
        </div>

        <svg width="1080" height="1920" style={{ position: "absolute" }}>
          <defs>
            <linearGradient id="rvNomFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={theme.gold} stopOpacity="0.22" />
              <stop offset="100%" stopColor={theme.gold} stopOpacity="0" />
            </linearGradient>
            <linearGradient id="rvWedge" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={theme.red} stopOpacity="0.34" />
              <stop offset="100%" stopColor={theme.red} stopOpacity="0.08" />
            </linearGradient>
            <radialGradient id="rvDotG" cx="34%" cy="28%" r="80%">
              <stop offset="0%" stopColor="#FFFFFF" />
              <stop offset="40%" stopColor={theme.gold} />
              <stop offset="100%" stopColor="#7A5A1F" />
            </radialGradient>
            <radialGradient id="rvDotR" cx="34%" cy="28%" r="80%">
              <stop offset="0%" stopColor="#FFFFFF" />
              <stop offset="40%" stopColor={theme.red} />
              <stop offset="100%" stopColor="#7A1F1F" />
            </radialGradient>
            <clipPath id="rvClipWedge">
              <rect x={X0 - 4} y={0} width={Math.max(wedgeX - X0 + 6, 0)} height={1920} />
            </clipPath>
            <clipPath id="rvClipN">
              <rect x={X0 - 4} y={0} width={Math.max(nDrawX - X0 + 6, 0)} height={1920} />
            </clipPath>
          </defs>

          {/* baseline punteada del principal (referencia "lo que pusiste") */}
          <line
            x1={X0}
            y1={y0}
            x2={X1}
            y2={y0}
            stroke="#FFFFFF"
            strokeWidth={2}
            strokeDasharray="2 12"
            opacity={0.28}
          />

          {/* hueco rojo = lo que se comió la inflación (aparece con el dibujo del real) */}
          {rDraw > 0.01 && (
            <path d={wedgePath} fill="url(#rvWedge)" clipPath="url(#rvClipWedge)" />
          )}

          {/* área nominal (oro) */}
          <path
            d={`${polyline(nXY)} L${X1},${YBOT + 60} L${X0},${YBOT + 60} Z`}
            fill="url(#rvNomFill)"
            clipPath="url(#rvClipN)"
          />

          {/* línea nominal (oro) con doble trazo glow */}
          <path
            d={polyline(nXY)}
            fill="none"
            stroke={theme.gold}
            strokeWidth={5.5}
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeDasharray={nLen.total}
            strokeDashoffset={nLen.total * (1 - nDraw)}
            style={{ filter: `drop-shadow(0 0 10px ${theme.gold}) drop-shadow(0 0 28px ${theme.gold}55)` }}
          />
          <path
            d={polyline(nXY)}
            fill="none"
            stroke="#FFF1D6"
            strokeWidth={1.8}
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeDasharray={nLen.total}
            strokeDashoffset={nLen.total * (1 - nDraw)}
            opacity={0.85}
          />

          {/* línea real (rojo) con doble trazo glow */}
          <path
            d={polyline(rXY)}
            fill="none"
            stroke={theme.red}
            strokeWidth={5}
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeDasharray={rLen.total}
            strokeDashoffset={rLen.total * (1 - rDraw)}
            style={{ filter: `drop-shadow(0 0 10px ${theme.red}) drop-shadow(0 0 28px ${theme.red}55)` }}
          />
          <path
            d={polyline(rXY)}
            fill="none"
            stroke="#FFDCDC"
            strokeWidth={1.6}
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeDasharray={rLen.total}
            strokeDashoffset={rLen.total * (1 - rDraw)}
            opacity={0.8}
          />

          {/* punto de arranque compartido */}
          <circle cx={X0} cy={y0} r={10} fill="#FFFFFF" opacity={0.9} />

          {/* dots que riden la punta mientras dibuja */}
          {nDraw > 0.01 && nDraw < 0.995 && (
            <g>
              <circle cx={nDot.x} cy={nDot.y} r={34} fill={theme.gold} opacity={0.22} style={{ filter: "blur(12px)" }} />
              <circle cx={nDot.x} cy={nDot.y} r={20} fill="url(#rvDotG)" style={{ filter: `drop-shadow(0 0 14px ${theme.gold})` }} />
            </g>
          )}
          {rDraw > 0.01 && rDraw < 0.995 && (
            <g>
              <circle cx={rDot.x} cy={rDot.y} r={32} fill={theme.red} opacity={0.22} style={{ filter: "blur(12px)" }} />
              <circle cx={rDot.x} cy={rDot.y} r={18} fill="url(#rvDotR)" style={{ filter: `drop-shadow(0 0 14px ${theme.red})` }} />
            </g>
          )}
        </svg>

        {/* tags de cada serie (chips) cerca del arranque, suben con el dibujo */}
        <SeriesTag
          show={frame > D * 0.12}
          frame={frame}
          fps={fps}
          appear={D * 0.12}
          color={theme.gold}
          text={teaTag}
          left={clampLeft(X0 - 6, 360)}
          top={y0 - 96}
        />

        {/* readouts finales: oro (nominal) arriba-derecha · rojo (real) abajo-derecha.
            Pin a margen derecho de 24px (right-aligned) para no rozar el safe-area. */}
        <Readout
          color={theme.gold}
          label={nominalLabel}
          value={`${currency}${fmtAR(nVal)}`}
          x={684}
          y={nEnd.y - 152}
          align="right"
          opacity={nOpacity}
        />
        <Readout
          color={theme.red}
          label={realLabel}
          value={`${currency}${fmtAR(rVal)}`}
          x={684}
          y={rEnd.y + 34}
          align="right"
          opacity={rOpacity}
        />

        {/* punch chip: lo que perdiste de poder de compra */}
        <div
          style={{
            position: "absolute",
            top: 1208,
            left: 0,
            right: 0,
            textAlign: "center",
            opacity: punchIn,
            transform: `translateY(${(1 - punchIn) * 22}px)`,
          }}
        >
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 16,
              padding: "22px 40px",
              borderRadius: 22,
              background: "rgba(255,107,107,0.12)",
              border: `2px solid ${theme.red}66`,
              boxShadow: `0 0 40px ${theme.red}33`,
            }}
          >
            <span style={{ fontSize: 46, fontWeight: 800, color: theme.red, letterSpacing: "-0.01em" }}>
              {punch}
            </span>
          </div>
          <div style={{ marginTop: 22, fontSize: 32, fontWeight: 600, color: theme.textDim }}>
            {inflTag}
          </div>
        </div>
      </AbsoluteFill>
    </PremiumStage>
  );
};

const SeriesTag: React.FC<{
  show: boolean;
  frame: number;
  fps: number;
  appear: number;
  color: string;
  text: string;
  left: number;
  top: number;
}> = ({ show, frame, fps, appear, color, text, left, top }) => {
  const s = show ? spring({ frame: frame - appear, fps, config: { damping: 14, mass: 0.7 } }) : 0;
  return (
    <div
      style={{
        position: "absolute",
        left,
        top,
        opacity: Math.min(s * 1.3, 1),
        transform: `translateY(${(1 - s) * 14}px)`,
        display: "inline-flex",
        alignItems: "center",
        gap: 12,
        padding: "12px 20px",
        borderRadius: 14,
        background: "rgba(13,17,23,0.55)",
        border: `1.5px solid ${color}55`,
      }}
    >
      <div style={{ width: 12, height: 12, borderRadius: 8, background: color, boxShadow: `0 0 12px ${color}` }} />
      <span style={{ fontSize: 30, fontWeight: 700, color: theme.text }}>{text}</span>
    </div>
  );
};

const Readout: React.FC<{
  color: string;
  label: string;
  value: string;
  x: number;
  y: number;
  align: "left" | "right";
  opacity: number;
}> = ({ color, label, value, x, y, align, opacity }) => (
  <div style={{ position: "absolute", left: x, top: y, width: 372, textAlign: align, opacity }}>
    <div style={{ fontSize: 26, fontWeight: 600, color: theme.textDim, marginBottom: 4 }}>{label}</div>
    <div
      style={{
        fontSize: 64,
        fontWeight: 800,
        color,
        letterSpacing: "-0.02em",
        lineHeight: 1,
        fontVariantNumeric: "tabular-nums",
        textShadow: `0 4px 24px rgba(0,0,0,0.6), 0 0 22px ${color}55`,
      }}
    >
      {value}
    </div>
  </div>
);
