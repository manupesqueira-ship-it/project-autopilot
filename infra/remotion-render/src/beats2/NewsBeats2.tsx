import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { LiveBg } from "../kit/cinema";
import { L, TYPE } from "../kit/look";
import { barStyle, glowFilter, Masthead } from "../kit/material";
import { EASE, Odometer, prog, SPR, stag, useBeatDur } from "../kit/motion";

// BEATS v2 — look A locked + kit completo. Cada beat: revela temprano, SOSTIENE legible,
// y NUNCA está quieto (LiveBg respira + Camera del NewsReel + vida propia del elemento).

const semC = (v?: string) => (v === "gain" ? L.green : v === "loss" ? L.red : L.gold);

// ── 1. HOOK — titular kinético palabra por palabra ──────────────────────────
export const NewsHook2: React.FC<{
  kicker?: string; words?: { t: string; accent?: boolean }[]; tease?: string; durF?: number;
}> = ({ kicker = "LA NOTICIA", words = [], tease = "", durF }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const kO = prog(frame, 4, 16);
  const teaseO = prog(frame, 24 + words.length * 3 + 30, 24 + words.length * 3 + 46);
  return (
    <AbsoluteFill style={{ fontFamily: L.font }}>
      <LiveBg accent={L.kicker} energy={0.10} />
      <Masthead />
      <AbsoluteFill style={{ justifyContent: "center", padding: `0 ${L.mx}px` }}>
        <div style={{ ...TYPE.kicker, opacity: kO, marginBottom: 44 }}>{kicker}</div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "0 26px", maxWidth: 900 }}>
          {words.map((w, i) => {
            const at = 18 + stag(i, 3);
            const s = spring({ frame: frame - at, fps, config: SPR.SMOOTH, durationInFrames: 14 });
            const blur = 10 * (1 - s);
            return (
              <span key={i} style={{
                fontSize: 96, fontWeight: 800, lineHeight: 1.12, letterSpacing: "-0.02em",
                color: w.accent ? L.kicker : L.ink,
                opacity: s, transform: `translateY(${(1 - s) * 34}px)`, filter: `blur(${blur}px)`,
                textShadow: w.accent ? `0 0 60px ${L.kicker}55` : "none",
              }}>{w.t}</span>
            );
          })}
        </div>
        {tease ? <div style={{ ...TYPE.sub, marginTop: 56, opacity: teaseO }}>{tease}</div> : null}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ── 2. REVEAL — el sujeto, tipográfico con glow físico ──────────────────────
export const Reveal2: React.FC<{ name?: string; tagline?: string; color?: string; durF?: number }> = ({
  name = "NVIDIA", tagline = "", color = "#76B900", durF,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: frame - 6, fps, config: SPR.SMOOTH, durationInFrames: 22 });
  const lineW = prog(frame, 20, 52, EASE.enter) * 560;
  const tO = prog(frame, 30, 48);
  const pulse = 1 + 0.06 * Math.sin(frame / 16);
  return (
    <AbsoluteFill style={{ fontFamily: L.font }}>
      <LiveBg accent={color} energy={0.13} />
      <Masthead />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
        <div style={{
          fontSize: 210, fontWeight: 800, letterSpacing: "-0.02em", color,
          transform: `scale(${0.86 + 0.14 * s})`, opacity: s, filter: glowFilter(color, pulse),
        }}>{name}</div>
        <div style={{ width: lineW, height: 4, background: `linear-gradient(90deg, transparent, ${color}, transparent)`, borderRadius: 2, marginTop: 14 }} />
        <div style={{ fontSize: 48, fontWeight: 500, color: L.ink, marginTop: 42, opacity: tO, textAlign: "center", padding: "0 90px" }}>{tagline}</div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ── 3. SHOCK — odómetro héroe con punch en la sílaba (land del VO real) ─────
export const Shock2: React.FC<{
  value?: string; kicker?: string; caption?: string; valence?: "gain" | "loss" | "gold";
  land?: number; durF?: number;
}> = ({ value = "$3.5 billones", kicker = "", caption = "", valence = "gold", land = 40, durF }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const color = frame >= land ? semC(valence) : L.dim;
  const pop = spring({ frame: frame - land, fps, config: SPR.SNAPPY, durationInFrames: 16 });
  const scale = frame >= land ? 1 + 0.12 * (1 - pop) : 1;
  const kO = prog(frame, 8, 22);
  const cO = prog(frame, land + 6, land + 20);
  const fs = Math.min(240, Math.floor(1000 / (value.length * 0.56)));
  return (
    <AbsoluteFill style={{ fontFamily: L.font }}>
      <LiveBg accent={semC(valence)} energy={frame >= land ? 0.12 : 0.06} />
      <Masthead />
      <div style={{ position: "absolute", top: 470, left: 0, right: 0, textAlign: "center", ...TYPE.kicker, opacity: kO }}>{kicker}</div>
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
        <div style={{ transform: `scale(${scale})` }}>
          <Odometer value={value} fontSize={fs} color={color} start={8} land={land} glow={semC(valence)} glowAt={land} />
        </div>
      </AbsoluteFill>
      <div style={{ position: "absolute", bottom: 540, left: L.mx, right: L.mx, textAlign: "center", ...TYPE.sub, opacity: cO }}>{caption}</div>
    </AbsoluteFill>
  );
};

// ── 4. SCALE — zoom-out de escala (focus+context), oro protagonista vs gris ─
export const Scale2: React.FC<{
  smallLabel?: string; smallValue?: string; bigLabel?: string; bigValue?: string;
  cue?: number; durF?: number;
}> = ({ smallLabel = "", smallValue = "", bigLabel = "", bigValue = "", cue = 34, durF }) => {
  const frame = useCurrentFrame();
  const cam = interpolate(frame, [cue, cue + 40], [2.35, 1.0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE.dramatic });
  const smallH = 165, bigH = 1150, baseY = 1500;
  const camOX = 350, camOY = baseY - smallH;
  const bigGrow = prog(frame, cue + 12, cue + 46, EASE.enter);
  const bigO = prog(frame, cue + 40, cue + 54);
  const smO = prog(frame, 8, 20);
  const totalO = prog(frame, cue + 52, cue + 66);
  return (
    <AbsoluteFill style={{ fontFamily: L.font }}>
      <LiveBg accent={L.gold} energy={0.08} />
      <Masthead />
      <div style={{ position: "absolute", inset: 0, transform: `scale(${cam})`, transformOrigin: `${camOX}px ${camOY}px` }}>
        {/* referencia (gris, sin valencia) */}
        <div style={{ position: "absolute", left: camOX - 95, top: baseY - smallH, width: 190, height: smallH, borderRadius: 10, ...barStyle(L.grayBar) }} />
        <div style={{ position: "absolute", left: camOX - 160, top: baseY - smallH - 62, width: 320, textAlign: "center", fontSize: 40, fontWeight: 800, color: L.ink, opacity: smO }}>{smallValue}</div>
        <div style={{ position: "absolute", left: camOX - 160, top: baseY + 24, width: 320, textAlign: "center", fontSize: 30, fontWeight: 600, color: L.mute, opacity: smO }}>{smallLabel}</div>
        {/* protagonista (oro, glow) */}
        <div style={{ position: "absolute", left: 700 - 115, top: baseY - bigH * bigGrow, width: 230, height: bigH * bigGrow, borderRadius: 12, ...barStyle(L.gold, true) }} />
        <div style={{ position: "absolute", left: 700 - 180, top: baseY - bigH - 66, width: 360, textAlign: "center", fontSize: 46, fontWeight: 800, color: L.gold, opacity: bigO, filter: glowFilter(L.gold, 0.5) }}>{bigValue}</div>
        <div style={{ position: "absolute", left: 700 - 180, top: baseY + 24, width: 360, textAlign: "center", fontSize: 30, fontWeight: 600, color: L.mute, opacity: bigO }}>{bigLabel}</div>
        <div style={{ position: "absolute", left: 110, top: baseY, width: 860, height: 3, background: L.hair }} />
      </div>
      <div style={{ position: "absolute", bottom: 170, left: L.mx, right: L.mx, textAlign: "center", fontSize: 38, fontWeight: 600, color: L.ink, opacity: totalO }}>{smallLabel} vs {bigLabel}</div>
    </AbsoluteFill>
  );
};

// ── 5. TREND — línea con glow multicapa + área gradiente + cabeza viva ─────
export const Trend2: React.FC<{
  kicker?: string; label?: string; points?: number[]; caption?: string; endTag?: string; durF?: number;
}> = ({ kicker = "", label = "", points = [1, 2, 4, 8, 15, 20], caption = "", endTag = "", durF }) => {
  const frame = useCurrentFrame();
  const D = useBeatDur(durF);
  const W = 880, H = 600, x0 = 100, y0 = 470;
  const max = Math.max(...points);
  const pts = points.map((p, i) => [x0 + (i / (points.length - 1)) * W, y0 + H - (p / max) * H]);
  const d = pts.map((p, i) => (i === 0 ? `M ${p[0]} ${p[1]}` : `L ${p[0]} ${p[1]}`)).join(" ");
  const draw = prog(frame, 18, D - 46, EASE.update);
  const LEN = 1900;
  const hi = Math.min(pts.length - 1, draw * (pts.length - 1));
  const lo = Math.floor(hi); const t = hi - lo;
  const hx = pts[lo][0] + (pts[Math.min(lo + 1, pts.length - 1)][0] - pts[lo][0]) * t;
  const hy = pts[lo][1] + (pts[Math.min(lo + 1, pts.length - 1)][1] - pts[lo][1]) * t;
  const kO = prog(frame, 4, 18);
  const tagO = prog(frame, D - 52, D - 38);
  const pulse = 1 + 0.3 * Math.sin(frame / 5.5);
  const stroke = { fill: "none" as const, stroke: L.green, strokeLinecap: "round" as const, strokeLinejoin: "round" as const, pathLength: LEN, strokeDasharray: LEN, strokeDashoffset: LEN * (1 - draw) };
  return (
    <AbsoluteFill style={{ fontFamily: L.font }}>
      <LiveBg accent={L.green} energy={0.10} />
      <Masthead />
      <div style={{ position: "absolute", top: 250, left: L.mx, right: L.mx, textAlign: "center", ...TYPE.kicker, color: L.green, opacity: kO }}>{kicker}</div>
      <div style={{ position: "absolute", top: 318, left: L.mx, right: L.mx, textAlign: "center", fontSize: 34, fontWeight: 500, color: L.mute, opacity: kO }}>{label}</div>
      <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
        <defs>
          <linearGradient id="t2g" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={L.green} stopOpacity="0.34" />
            <stop offset="100%" stopColor={L.green} stopOpacity="0" />
          </linearGradient>
        </defs>
        {/* grid mínimo: dots de años */}
        {pts.map((p, i) => (
          <circle key={i} cx={p[0]} cy={y0 + H} r={4} fill={frame > 18 + i * 6 ? L.hair : "transparent"} />
        ))}
        <line x1={x0} y1={y0 + H} x2={x0 + W} y2={y0 + H} stroke={L.hair} strokeWidth={2} />
        {draw > 0.02 && (
          <path d={`${d} L ${hx} ${y0 + H} L ${x0} ${y0 + H} Z`} fill="url(#t2g)" style={{ clipPath: `inset(0 ${(1 - draw) * 100}% 0 0)` }} />
        )}
        {/* glow multicapa: 3 pasadas */}
        <path d={d} {...stroke} strokeWidth={22} style={{ filter: "blur(22px)", opacity: 0.30 }} />
        <path d={d} {...stroke} strokeWidth={12} style={{ filter: "blur(7px)", opacity: 0.55 }} />
        <path d={d} {...stroke} strokeWidth={7} />
        <circle cx={hx} cy={hy} r={13 * pulse} fill={L.green} style={{ filter: `drop-shadow(0 0 18px ${L.green})` }} />
      </svg>
      <div style={{ position: "absolute", left: Math.min(hx - 70, 830), top: hy - 140, fontSize: 92, fontWeight: 800, color: L.green, opacity: tagO, filter: glowFilter(L.green, 0.6) }}>{endTag}</div>
      <div style={{ position: "absolute", bottom: 250, left: L.mx, right: L.mx, textAlign: "center", fontSize: 44, fontWeight: 600, color: L.ink, opacity: tagO }}>{caption}</div>
    </AbsoluteFill>
  );
};

// ── 6. CLOSE — cierre corto que reconecta con el hook ───────────────────────
export const Close2: React.FC<{ line1?: string; punch?: string; cta?: string; durF?: number }> = ({
  line1 = "", punch = "", cta = "Guarda esto", durF,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const l1 = prog(frame, 4, 16);
  const pk = spring({ frame: frame - 16, fps, config: SPR.SMOOTH, durationInFrames: 18 });
  const ctaO = prog(frame, 40, 54);
  const pulse = 1 + 0.05 * Math.sin(frame / 12);
  return (
    <AbsoluteFill style={{ fontFamily: L.font, justifyContent: "center", alignItems: "center" }}>
      <LiveBg accent={L.green} energy={0.10} />
      <Masthead />
      <div style={{ fontSize: 54, fontWeight: 500, color: L.mute, opacity: l1, marginBottom: 26 }}>{line1}</div>
      <div style={{
        fontSize: 108, fontWeight: 800, letterSpacing: "-0.02em", color: L.ink, textAlign: "center",
        padding: "0 70px", opacity: pk, transform: `scale(${0.92 + 0.08 * pk})`, filter: glowFilter(L.green, 0.4 * pulse),
      }}>{punch}</div>
      <div style={{ position: "absolute", bottom: 330, display: "flex", alignItems: "center", gap: 18, opacity: ctaO }}>
        <div style={{ width: 20, height: 20, borderRadius: 6, ...barStyle(L.green, true) }} />
        <div style={{ fontSize: 46, fontWeight: 700, color: L.ink }}>{cta}</div>
      </div>
    </AbsoluteFill>
  );
};
