import React from "react";
import { AbsoluteFill, Easing, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

const INK = "#F3EFE7", PAPER = "#08090B", GREEN = "#10b981", MUTE = "#9AA0AA", ACCENT = "#E45B4E";
const FONT = "InterVar, Inter, sans-serif";

const Masthead: React.FC = () => (
  <>
    <div style={{ position: "absolute", top: 78, left: 96, fontSize: 27, fontWeight: 700, letterSpacing: "0.28em", color: INK }}>DINERO&nbsp;IA</div>
    <div style={{ position: "absolute", top: 130, left: 96, width: 888, height: 1, background: "#2B2F38" }} />
  </>
);
const push = (frame: number, dur: number, amt = 0.05) => 1 + interpolate(frame, [0, dur], [0, amt], { extrapolateRight: "clamp" });

// ---------- NewsHook ----------
export const NewsHook: React.FC<{ kicker?: string; lines?: { text: string; accent?: boolean }[]; tease?: string }> = ({
  kicker = "LA NOTICIA",
  lines = [{ text: "Una empresa vale más" }, { text: "que un país entero.", accent: true }],
  tease = "¿Cuál? Quédate…",
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const kO = interpolate(frame, [6, 20], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const teaseO = interpolate(frame, [90, 108], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ backgroundColor: PAPER, fontFamily: FONT }}>
      <AbsoluteFill style={{ background: "radial-gradient(60% 40% at 50% 42%, rgba(228,91,78,0.09) 0%, transparent 60%)" }} />
      <Masthead />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "flex-start", padding: "0 96px", transform: `scale(${push(frame, durationInFrames, 0.06)})` }}>
        <div style={{ fontSize: 34, fontWeight: 700, letterSpacing: "0.24em", color: ACCENT, opacity: kO, marginBottom: 40 }}>{kicker}</div>
        {lines.map((l, i) => {
          const o = interpolate(frame, [26 + i * 24, 42 + i * 24], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          return (
            <div key={i} style={{ fontSize: 94, fontWeight: 800, lineHeight: 1.05, letterSpacing: "-0.02em", color: l.accent ? INK : INK, opacity: o, transform: `translateY(${interpolate(o, [0, 1], [26, 0])}px)` }}>
              {l.text}
            </div>
          );
        })}
        <div style={{ fontSize: 44, fontWeight: 500, color: MUTE, marginTop: 54, opacity: teaseO }}>{tease}</div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ---------- Reveal ----------
export const Reveal: React.FC<{ name?: string; tagline?: string; color?: string }> = ({
  name = "NVIDIA", tagline = "El cerebro detrás del boom de la IA", color = "#76B900",
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const nS = spring({ frame: frame - 8, fps, config: { damping: 12, stiffness: 110 } });
  const tO = interpolate(frame, [34, 52], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const lineW = interpolate(frame, [30, 60], [0, 560], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  return (
    <AbsoluteFill style={{ backgroundColor: PAPER, fontFamily: FONT }}>
      <AbsoluteFill style={{ background: `radial-gradient(55% 40% at 50% 46%, ${color}22 0%, transparent 62%)` }} />
      <Masthead />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", transform: `scale(${push(frame, durationInFrames, 0.05)})` }}>
        <div style={{ fontSize: 220, fontWeight: 800, letterSpacing: "-0.02em", color, transform: `scale(${0.8 + 0.2 * Math.min(1, nS)})`, opacity: Math.min(1, nS), filter: `drop-shadow(0 0 60px ${color}55)` }}>{name}</div>
        <div style={{ width: lineW, height: 4, background: color, borderRadius: 2, marginTop: 10 }} />
        <div style={{ fontSize: 48, fontWeight: 500, color: INK, marginTop: 40, opacity: tO, textAlign: "center", padding: "0 90px" }}>{tagline}</div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ---------- TrendLine ----------
export const TrendLine: React.FC<{ kicker?: string; label?: string; points?: number[]; caption?: string; endTag?: string }> = ({
  kicker = "EL BOOM NO SE DETIENE",
  label = "Valor de Nvidia · últimos 5 años",
  points = [1, 2, 4, 8, 15, 20],
  caption = "creció unas 20 veces",
  endTag = "20×",
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const W = 900, H = 620, x0 = 90, y0 = 430;
  const max = Math.max(...points);
  const pts = points.map((p, i) => [x0 + (i / (points.length - 1)) * W, y0 + H - (p / max) * H]);
  const d = pts.map((p, i) => (i === 0 ? `M ${p[0]} ${p[1]}` : `L ${p[0]} ${p[1]}`)).join(" ");
  const draw = interpolate(frame, [20, durationInFrames - 40], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.quad) });
  const LEN = 1900;
  const headIdx = Math.min(pts.length - 1, Math.floor(draw * (pts.length - 1) + 0.5));
  const head = pts[headIdx];
  const kO = interpolate(frame, [6, 20], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const tagO = interpolate(frame, [durationInFrames - 60, durationInFrames - 44], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const pulse = 1 + 0.25 * Math.sin(frame / 6);
  return (
    <AbsoluteFill style={{ backgroundColor: PAPER, fontFamily: FONT }}>
      <AbsoluteFill style={{ background: "radial-gradient(70% 50% at 50% 55%, rgba(16,185,129,0.10) 0%, transparent 60%)" }} />
      <Masthead />
      <div style={{ position: "absolute", top: 250, left: 96, right: 96, textAlign: "center", fontSize: 40, fontWeight: 700, letterSpacing: "0.16em", color: GREEN, opacity: kO }}>{kicker}</div>
      <div style={{ position: "absolute", top: 316, left: 96, right: 96, textAlign: "center", fontSize: 34, fontWeight: 500, color: MUTE, opacity: kO }}>{label}</div>
      <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
        <defs>
          <linearGradient id="tg" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={GREEN} stopOpacity="0.35" />
            <stop offset="100%" stopColor={GREEN} stopOpacity="0" />
          </linearGradient>
        </defs>
        <line x1={x0} y1={y0 + H} x2={x0 + W} y2={y0 + H} stroke="#2B2F38" strokeWidth={2} />
        {draw > 0.02 && <path d={`${d} L ${head[0]} ${y0 + H} L ${x0} ${y0 + H} Z`} fill="url(#tg)" opacity={draw} clipPath="none" style={{ clipPath: `inset(0 ${(1 - draw) * 100}% 0 0)` }} />}
        <path d={d} fill="none" stroke={GREEN} strokeWidth={9} strokeLinecap="round" strokeLinejoin="round" pathLength={LEN} strokeDasharray={LEN} strokeDashoffset={LEN * (1 - draw)} style={{ filter: `drop-shadow(0 0 20px ${GREEN}88)` }} />
        <circle cx={head[0]} cy={head[1]} r={14 * pulse} fill={GREEN} style={{ filter: `drop-shadow(0 0 16px ${GREEN})` }} />
      </svg>
      <div style={{ position: "absolute", left: head[0] - 60, top: head[1] - 130, fontSize: 96, fontWeight: 800, color: GREEN, opacity: tagO }}>{endTag}</div>
      <div style={{ position: "absolute", bottom: 220, left: 96, right: 96, textAlign: "center", fontSize: 44, fontWeight: 600, color: INK, opacity: tagO }}>{caption}</div>
    </AbsoluteFill>
  );
};
