import React from "react";
import { AbsoluteFill, Easing, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

// Beats para el reel "pago mínimo de la tarjeta". Todos: revelan en el primer ~40% y
// SOSTIENEN legible con slow push-in (rulebook: nunca pantalla muerta, pero dar tiempo a leer).

const INK = "#F3EFE7", PAPER = "#08090B", GREEN = "#10b981", RED = "#ef4444";
const MUTE = "#9AA0AA", ACCENT = "#E45B4E", GRAY = "#3A3A3A", GOLD = "#F7C948";
const FONT = "InterVar, Inter, sans-serif";

const money = (n: number) => "$" + Math.round(n).toLocaleString("en-US");
const grain = () => null;

// push-in lento global para que ningún plano se sienta muerto
const usePush = (amt = 0.05) => {
  const { durationInFrames } = useVideoConfig();
  const frame = useCurrentFrame();
  return 1 + interpolate(frame, [0, durationInFrames], [0, amt], { extrapolateRight: "clamp" });
};

const Masthead: React.FC = () => (
  <>
    <div style={{ position: "absolute", top: 78, left: 96, fontSize: 27, fontWeight: 700, letterSpacing: "0.28em", color: INK }}>DINERO&nbsp;IA</div>
    <div style={{ position: "absolute", top: 130, left: 96, width: 888, height: 1, background: "#2B2F38" }} />
  </>
);

// ---------- 1. CardHook ----------
export const CardHook: React.FC<{ purchase?: string; item?: string }> = ({ purchase = "$15,000", item = "una pantalla" }) => {
  const frame = useCurrentFrame();
  const push = usePush(0.06);
  const cardIn = spring({ frame: frame - 10, fps: 30, config: { damping: 14, stiffness: 90 } });
  const amtO = interpolate(frame, [30, 46], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const minO = interpolate(frame, [95, 112], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const qO = interpolate(frame, [210, 232], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const qPulse = 1 + 0.04 * Math.sin(frame / 9);
  return (
    <AbsoluteFill style={{ backgroundColor: PAPER, fontFamily: FONT }}>
      <AbsoluteFill style={{ background: "radial-gradient(60% 40% at 50% 40%, rgba(247,201,72,0.08) 0%, transparent 60%)" }} />
      <Masthead />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", transform: `scale(${push})` }}>
        {/* tarjeta */}
        <div style={{ width: 720, height: 452, borderRadius: 40, background: "linear-gradient(150deg, #1a1d24 0%, #0f1116 100%)", boxShadow: "0 40px 120px rgba(0,0,0,0.6), inset 0 2px 0 rgba(255,255,255,0.06)", position: "relative", transform: `translateY(${(1 - Math.min(1, cardIn)) * 60}px) rotateX(${(1 - Math.min(1, cardIn)) * 20}deg)`, opacity: Math.min(1, cardIn), marginTop: -120 }}>
          <div style={{ position: "absolute", top: 54, left: 54, width: 92, height: 68, borderRadius: 12, background: "linear-gradient(135deg,#e9c46a,#b8860b)" }} />
          <div style={{ position: "absolute", bottom: 120, left: 54, fontSize: 40, letterSpacing: "0.18em", color: "#8A909B", fontWeight: 600 }}>•••• •••• •••• 4829</div>
          <div style={{ position: "absolute", bottom: 48, left: 54, fontSize: 30, color: MUTE, opacity: amtO }}>{item}</div>
          <div style={{ position: "absolute", top: 150, left: 54, right: 54, fontSize: 118, fontWeight: 800, color: INK, opacity: amtO, letterSpacing: "-0.02em" }}>{purchase}</div>
        </div>
        <div style={{ fontSize: 40, fontWeight: 600, color: MUTE, marginTop: 60, opacity: minO }}>Pagas solo el <span style={{ color: GOLD, fontWeight: 800 }}>mínimo</span> cada mes.</div>
        <div style={{ fontSize: 72, fontWeight: 800, color: INK, marginTop: 34, opacity: qO, transform: `scale(${qPulse})` }}>¿Cuánto pagarás <span style={{ color: ACCENT }}>en total?</span></div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ---------- 2. MinPayFeel ----------
export const MinPayFeel: React.FC<{ min?: string }> = ({ min = "$900" }) => {
  const frame = useCurrentFrame();
  const push = usePush(0.05);
  const nO = spring({ frame: frame - 8, fps: 30, config: { damping: 13, stiffness: 120 } });
  const checks = 12;
  const capO = interpolate(frame, [150, 170], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ backgroundColor: PAPER, fontFamily: FONT }}>
      <AbsoluteFill style={{ background: "radial-gradient(55% 38% at 50% 42%, rgba(16,185,129,0.10) 0%, transparent 60%)" }} />
      <Masthead />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", transform: `scale(${push})` }}>
        <div style={{ fontSize: 34, fontWeight: 700, letterSpacing: "0.2em", color: MUTE, marginBottom: 20 }}>EL PAGO MÍNIMO</div>
        <div style={{ display: "flex", alignItems: "baseline", transform: `scale(${0.85 + 0.15 * Math.min(1, nO)})`, whiteSpace: "nowrap" }}>
          <span style={{ fontSize: 240, fontWeight: 800, color: INK, letterSpacing: "-0.03em" }}>{min}</span>
          <span style={{ fontSize: 90, fontWeight: 700, color: MUTE, marginLeft: 12 }}>/mes</span>
        </div>
        {/* 12 checks mensuales */}
        <div style={{ display: "flex", gap: 20, marginTop: 70 }}>
          {Array.from({ length: checks }).map((_, i) => {
            const on = interpolate(frame, [40 + i * 7, 48 + i * 7], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
            return <div key={i} style={{ width: 46, height: 46, borderRadius: 12, background: on > 0.5 ? GREEN : GRAY, opacity: 0.3 + 0.7 * on, transform: `scale(${0.8 + 0.2 * on})` }} />;
          })}
        </div>
        <div style={{ fontSize: 52, fontWeight: 600, color: INK, marginTop: 70, opacity: capO }}>Se siente fácil… <span style={{ color: MUTE }}>¿verdad?</span></div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ---------- 3. DebtTimeline ----------
export const DebtTimeline: React.FC<{ years?: number[]; paid?: number[]; owe?: number[] }> = ({
  years = [1, 2, 3, 4, 5],
  paid = [10800, 21600, 32400, 43200, 54000],
  owe = [14200, 13100, 11600, 9600, 6900],
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const push = usePush(0.05);
  // progreso 0..1 a lo largo de casi todo el beat (deja cola para leer)
  const prog = interpolate(frame, [30, durationInFrames - 40], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.quad) });
  const fidx = prog * (years.length - 1);
  const lo = Math.floor(fidx), hi = Math.min(years.length - 1, lo + 1), t = fidx - lo;
  const lerp = (a: number[], x = t) => a[lo] + (a[hi] - a[lo]) * x;
  const curYear = years[lo] + (years[hi] - years[lo]) * t;
  const paidNow = lerp(paid), oweNow = lerp(owe);
  const P0 = 15000;
  const titleO = interpolate(frame, [6, 20], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ backgroundColor: PAPER, fontFamily: FONT }}>
      <AbsoluteFill style={{ background: "radial-gradient(70% 50% at 50% 40%, rgba(239,68,68,0.08) 0%, transparent 60%)" }} />
      <Masthead />
      <div style={{ position: "absolute", top: 250, left: 0, right: 0, textAlign: "center", fontSize: 40, fontWeight: 700, letterSpacing: "0.14em", color: ACCENT, opacity: titleO }}>PAGANDO SOLO EL MÍNIMO</div>
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", transform: `scale(${push})` }}>
        {/* año grande */}
        <div style={{ fontSize: 200, fontWeight: 800, color: INK, letterSpacing: "-0.02em", marginBottom: 10 }}>AÑO {Math.round(curYear)}</div>
        {/* dos columnas */}
        <div style={{ display: "flex", gap: 90, marginTop: 40 }}>
          <div style={{ textAlign: "center", width: 400 }}>
            <div style={{ fontSize: 34, fontWeight: 700, letterSpacing: "0.12em", color: MUTE }}>YA PAGASTE</div>
            <div style={{ fontSize: 96, fontWeight: 800, color: GREEN, whiteSpace: "nowrap" }}>{money(paidNow)}</div>
          </div>
          <div style={{ width: 2, background: "#2B2F38" }} />
          <div style={{ textAlign: "center", width: 400 }}>
            <div style={{ fontSize: 34, fontWeight: 700, letterSpacing: "0.12em", color: MUTE }}>AÚN DEBES</div>
            <div style={{ fontSize: 96, fontWeight: 800, color: RED, whiteSpace: "nowrap" }}>{money(oweNow)}</div>
          </div>
        </div>
        {/* barra de saldo que casi no baja */}
        <div style={{ width: 820, height: 26, borderRadius: 13, background: "#1A1D22", marginTop: 80, overflow: "hidden" }}>
          <div style={{ width: `${(oweNow / P0) * 100}%`, height: "100%", background: RED, borderRadius: 13 }} />
        </div>
        <div style={{ fontSize: 32, fontWeight: 500, color: MUTE, marginTop: 26 }}>tu deuda casi no baja</div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ---------- 4. CompareBars ----------
type Bar = { label: string; value: number; display: string; sub?: string; color: "green" | "red" | "gray" };
export const CompareBars: React.FC<{ title?: string; a?: Bar; b?: Bar; maxRef?: number }> = ({
  title = "Interés vs. lo que compraste",
  a = { label: "La pantalla", value: 15000, display: "$15,000", color: "gray" as const },
  b = { label: "Los intereses", value: 17234, display: "$17,234", sub: "más que la compra", color: "red" as const },
  maxRef,
}) => {
  const frame = useCurrentFrame();
  const push = usePush(0.04);
  const col = (c: string) => (c === "green" ? GREEN : c === "red" ? RED : "#5A6472");
  const max = maxRef || Math.max(a.value, b.value) * 1.12;
  const H = 900, baseY = 1480;
  const titleO = interpolate(frame, [8, 22], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const grow = (delay: number) => interpolate(frame, [30 + delay, 70 + delay], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  const bar = (bb: Bar, x: number, delay: number) => {
    const g = grow(delay);
    const h = (bb.value / max) * H * g;
    const lblO = interpolate(frame, [64 + delay, 82 + delay], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    return (
      <div key={bb.label}>
        <div style={{ position: "absolute", left: x, top: baseY - h, width: 300, height: h, background: col(bb.color), borderRadius: 12, boxShadow: bb.color !== "gray" ? `0 0 60px ${col(bb.color)}44` : "none" }} />
        <div style={{ position: "absolute", left: x - 30, top: baseY - h - 96, width: 360, textAlign: "center", fontSize: 66, fontWeight: 800, color: col(bb.color), opacity: lblO, whiteSpace: "nowrap" }}>{bb.display}</div>
        <div style={{ position: "absolute", left: x - 30, top: baseY + 26, width: 360, textAlign: "center", fontSize: 38, fontWeight: 600, color: INK, opacity: lblO }}>{bb.label}</div>
        {bb.sub && <div style={{ position: "absolute", left: x - 30, top: baseY + 76, width: 360, textAlign: "center", fontSize: 30, fontWeight: 500, color: MUTE, opacity: lblO }}>{bb.sub}</div>}
      </div>
    );
  };
  return (
    <AbsoluteFill style={{ backgroundColor: PAPER, fontFamily: FONT }}>
      <AbsoluteFill style={{ background: "radial-gradient(70% 50% at 50% 40%, rgba(239,68,68,0.06) 0%, transparent 60%)" }} />
      <Masthead />
      <div style={{ position: "absolute", top: 250, left: 96, right: 96, textAlign: "center", fontSize: 52, fontWeight: 700, color: INK, opacity: titleO }}>{title}</div>
      <div style={{ position: "absolute", inset: 0, transform: `scale(${push})` }}>
        <div style={{ position: "absolute", left: 130, top: baseY, width: 820, height: 3, background: "#2B2F38" }} />
        {bar(a, 250, 0)}
        {bar(b, 630, 18)}
      </div>
    </AbsoluteFill>
  );
};
