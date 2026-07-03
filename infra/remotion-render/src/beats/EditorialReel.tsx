import React from "react";
import { AbsoluteFill, Easing, Img, interpolate, OffthreadVideo, Sequence, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { MapZoomEditorial } from "./MapZoomEditorial";

// EditorialReel — motor de REEL COMPLETO en el estilo de la casa "Editorial"
// (aprobado por Manuel 2026-07-01). Marco persistente (masthead + fuente + folio)
// + escenas que se revelan con la gramática editorial. Un reel = UNA composición.
// Datos exactos; color semántico (oxblood = pérdida/acento). Timing por escena =
// duración de la voz (se pasa en props desde el timing de ElevenLabs).

// paleta THEME-AWARE (claro/oscuro). applyTheme() se llama al render con el theme del reel.
let INK = "#1B1712", PAPER = "#F1ECE1", ACCENT = "#9E2B22", GREEN = "#1F7A4D", MUTE = "#7A7264", HAIR = "#CDC4B2", SUB = "#5A544A", EMPTY = "#E6DFD0";
let DARK = false;
const applyTheme = (dark: boolean) => {
  DARK = dark;
  if (dark) { INK = "#F3EFE7"; PAPER = "#0A0B0D"; ACCENT = "#E45B4E"; GREEN = "#43B980"; MUTE = "#8A909B"; HAIR = "#2B2F38"; SUB = "#9AA0AA"; EMPTY = "#1A1D22"; }
  else { INK = "#1B1712"; PAPER = "#F1ECE1"; ACCENT = "#9E2B22"; GREEN = "#1F7A4D"; MUTE = "#7A7264"; HAIR = "#CDC4B2"; SUB = "#5A544A"; EMPTY = "#E6DFD0"; }
};
const FONT = "InterVar, Inter, Georgia, serif";
const M = 96;

const fmtNum = (v: number, decimals = 0) =>
  v.toLocaleString("en-US", { minimumFractionDigits: decimals, maximumFractionDigits: decimals });

// auto-ajuste: cifras largas (7 dígitos) no deben desbordar el ancho útil.
const fitSize = (text: string, base: number, maxW = 888, k = 0.53) =>
  Math.min(base, Math.floor(maxW / (k * Math.max(1, text.length))));

const reveal = (frame: number, start: number, dist = 22, dur = 14): React.CSSProperties => ({
  opacity: interpolate(frame, [start, start + dur], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
  transform: `translateY(${interpolate(frame, [start, start + dur], [dist, 0], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic),
  })}px)`,
});

// path bezier SUAVE (Catmull-Rom) desde puntos [x,y] — compartido por escenas de curva
const smoothPath = (p: [number, number][]) => {
  if (p.length < 2) return "";
  let d = `M ${p[0][0].toFixed(1)} ${p[0][1].toFixed(1)}`;
  for (let i = 0; i < p.length - 1; i++) {
    const [x0, y0] = p[Math.max(0, i - 1)], [x1, y1] = p[i], [x2, y2] = p[i + 1], [x3, y3] = p[Math.min(p.length - 1, i + 2)];
    const c1x = x1 + (x2 - x0) / 6, c1y = y1 + (y2 - y0) / 6, c2x = x2 - (x3 - x1) / 6, c2y = y2 - (y3 - y1) / 6;
    d += ` C ${c1x.toFixed(1)} ${c1y.toFixed(1)} ${c2x.toFixed(1)} ${c2y.toFixed(1)} ${x2.toFixed(1)} ${y2.toFixed(1)}`;
  }
  return d;
};

const semColor = (c: string | undefined, fb: string) =>
  c === "green" ? GREEN : c === "accent" ? ACCENT : c === "ink" ? INK : c === "mute" ? MUTE : fb;

const count = (frame: number, start: number, end: number, from: number, to: number) =>
  interpolate(frame, [start, end], [from, to], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic),
  });

// punto en una curva cúbica de Bézier (para el marcador que viaja por la línea)
const cubicAt = (t: number, p: number[][]) => {
  const u = 1 - t;
  const x = u * u * u * p[0][0] + 3 * u * u * t * p[1][0] + 3 * u * t * t * p[2][0] + t * t * t * p[3][0];
  const y = u * u * u * p[0][1] + 3 * u * u * t * p[1][1] + 3 * u * t * t * p[2][1] + t * t * t * p[3][1];
  return [x, y];
};

// ------- tipos de escena -------
export type Scene =
  | { type: "cover"; kicker: string; lines: { text: string; accent?: boolean }[]; foot?: string }
  | { type: "bignum"; label: string; prefix?: string; value: number; suffix?: string; sublabel?: string; accent?: boolean }
  | { type: "fallchart"; kicker?: string; fromLabel: string; from: number; toLabel: string; to: number; prefix?: string; unit?: string; deltaLabel: string; delta: number; axisRight: string; note?: string }
  | { type: "compare"; kicker?: string; left: { tag: string; value: number }; right: { tag: string; value: number }; prefix?: string; unit?: string; winner: "left" | "right"; note?: string }
  | { type: "payoff"; kicker: string; prefix?: string; value: number; suffix?: string; deltaText: string; body?: string }
  | { type: "close"; headline: { text: string; accent?: boolean }[]; sub?: string; cta: string }
  | { type: "plate"; kicker?: string; logo?: string; src: string; caption: string; note?: string }
  | { type: "mapzoom"; countryName: string; iso2: string; label: string; region?: string[]; kicker?: string }
  | { type: "hero_i2v"; src: string; kicker?: string; caption?: string; punch?: string }
  | { type: "pictogram"; kicker?: string; label: string; total?: number; highlight: number; suffix?: string; note?: string; color?: "accent" | "green" }
  | { type: "proportion"; kicker?: string; label?: string; segments: { tag: string; pct: number; color?: "accent" | "green" | "ink" | "mute" }[]; note?: string }
  | { type: "level"; kicker?: string; label?: string; fillPct: number; bigSuffix?: string; color?: "accent" | "green"; note?: string }
  | { type: "timeline"; kicker?: string; label?: string; events: { year: string; text: string; accent?: boolean }[]; note?: string }
  | { type: "donut"; kicker?: string; label?: string; segments: { tag: string; pct: number; color?: "accent" | "green" | "ink" | "mute" }[]; centerBig?: string; centerSub?: string; note?: string }
  | { type: "curve"; kicker?: string; label?: string; points: number[]; color?: "accent" | "green"; endLabel?: string; startLabel?: string; note?: string; anim?: "comet" | "spring" | "pulse" | "hero" }
  | { type: "bubbles"; kicker?: string; label?: string; items: { label: string; value: number; suffix?: string; color?: "accent" | "green" | "ink" }[]; note?: string }
  | { type: "gauge"; kicker?: string; label?: string; pct: number; leftLabel?: string; rightLabel?: string; centerBig?: string; centerSub?: string; color?: "accent" | "green"; note?: string }
  | { type: "divergence"; kicker?: string; label?: string; a: number[]; b: number[]; labelA?: string; labelB?: string; colorA?: "green" | "accent" | "ink"; colorB?: "green" | "accent" | "ink"; note?: string }
  | { type: "arcflow"; kicker?: string; label?: string; originLabel: string; targets: { label: string; sub?: string; color?: "accent" | "green" | "ink" }[]; note?: string }
  | { type: "balance"; kicker?: string; label?: string; leftLabel: string; leftValue: number; rightLabel: string; rightValue: number; prefix?: string; note?: string }
  | { type: "radialbars"; kicker?: string; label?: string; items: { label: string; value: number; color?: "accent" | "green" | "ink" }[]; centerBig?: string; centerSub?: string; note?: string }
  | { type: "spiral"; kicker?: string; label?: string; turns?: number; centerBig?: string; centerSub?: string; note?: string }
  | { type: "grow"; kicker?: string; label?: string; topLabel?: string; note?: string }
  | { type: "odometer"; kicker?: string; label?: string; value: number; prefix?: string; suffix?: string; sublabel?: string; note?: string }
  | { type: "curvedText"; kicker?: string; label?: string; text: string; sub?: string; color?: "accent" | "green" | "ink"; note?: string }
  | { type: "erosion"; kicker?: string; label?: string; fromValue: number; toValue: number; prefix?: string; fromLabel?: string; toLabel?: string; note?: string };

// ------- escena render -------
const SceneView: React.FC<{ scene: Scene; durF: number; inFade?: boolean }> = ({ scene, durF, inFade }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  // TRANSICIÓN dip-a-papel (P2.2): la escena SALE fundiéndose al papel (últimos 9f) y —salvo la
  // primera— ENTRA desde el papel (primeros 8f). No consume frames extra → no desincroniza el audio.
  const outO = interpolate(frame, [durF - 9, durF - 1], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const inO = inFade ? interpolate(frame, [0, 8], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) : 1;

  let body: React.ReactNode = null;

  if (scene.type === "cover") {
    body = (
      <>
        <div style={{ position: "absolute", top: 300, left: M, fontSize: 32, fontWeight: 700, letterSpacing: "0.2em", color: ACCENT, ...reveal(frame, 8) }}>
          {scene.kicker}
        </div>
        <div style={{ position: "absolute", top: 380, left: M, right: M }}>
          {/* P0.3: el HOOK visible desde frame 0 (portada del grid + freno de scroll); el movimiento lo da el drift global */}
          {scene.lines.map((l, i) => (
            <div key={i} style={{ fontSize: 128, fontWeight: 800, lineHeight: 1.02, letterSpacing: "-0.03em", color: l.accent ? ACCENT : INK }}>
              {l.text}
            </div>
          ))}
        </div>
        {scene.foot && (
          <div style={{ position: "absolute", top: 1120, left: M, right: M, fontSize: 38, fontWeight: 400, lineHeight: 1.4, color: SUB, maxWidth: 860, ...reveal(frame, 16 + scene.lines.length * 8 + 6) }}>
            {scene.foot}
          </div>
        )}
      </>
    );
  }

  if (scene.type === "bignum") {
    const shown = count(frame, 12, 44, 0, scene.value);
    body = (
      <>
        <div style={{ position: "absolute", top: 620, left: M, fontSize: 36, fontWeight: 500, color: MUTE, ...reveal(frame, 6) }}>{scene.label}</div>
        <div style={{ position: "absolute", top: 668, left: M - 4, fontSize: fitSize(`${scene.prefix ?? ""}${fmtNum(scene.value)}`, 210), fontWeight: 800, letterSpacing: "-0.035em", lineHeight: 1, color: scene.accent ? ACCENT : INK, ...reveal(frame, 12, 26) }}>
          {scene.prefix ?? ""}{fmtNum(shown)}{scene.suffix ? <span style={{ fontSize: "0.4em", fontWeight: 700, marginLeft: 12, color: MUTE }}>{scene.suffix}</span> : null}
        </div>
        {scene.sublabel && (
          <div style={{ position: "absolute", top: 930, left: M, right: M, fontSize: 40, fontWeight: 400, color: SUB, maxWidth: 860, ...reveal(frame, 40) }}>{scene.sublabel}</div>
        )}
      </>
    );
  }

  if (scene.type === "fallchart") {
    const W = 1080 - 2 * M;
    const P = [[0, 14], [W * 0.28, 28], [W * 0.53, 94], [W, 146]];
    const dash = 940;
    const tDraw = interpolate(frame, [30, 84], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.cubic) });
    const draw = dash * (1 - tDraw);
    const shownTo = scene.from + (scene.to - scene.from) * tDraw;
    const [dotx, doty] = cubicAt(tDraw, P);
    const dotO = interpolate(frame, [30, 38], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    const wedgeO = interpolate(frame, [34, 84], [0, 0.9], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    const arrive = interpolate(frame, [84, 96], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    const pulseR = 11 + Math.sin(Math.max(0, frame - 84) / 3.5) * 4 * arrive;
    body = (
      <>
        {scene.kicker && <div style={{ position: "absolute", top: 300, left: M, fontSize: 30, fontWeight: 700, letterSpacing: "0.2em", color: ACCENT, ...reveal(frame, 4) }}>{scene.kicker}</div>}
        <div style={{ position: "absolute", top: 400, left: M, fontSize: 34, fontWeight: 500, color: MUTE, ...reveal(frame, 6) }}>{scene.fromLabel}</div>
        <div style={{ position: "absolute", top: 442, left: M - 4, fontSize: fitSize(`${scene.prefix ?? "$"}${fmtNum(scene.from)}`, 176), fontWeight: 800, letterSpacing: "-0.035em", lineHeight: 1, ...reveal(frame, 10, 24) }}>{scene.prefix ?? "$"}{fmtNum(scene.from)}</div>
        <svg width={W} height={200} viewBox={`0 0 ${W} 200`} style={{ position: "absolute", top: 648, left: M, fontFamily: FONT }}>
          <defs>
            <linearGradient id="lf" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={ACCENT} stopOpacity="0.28" /><stop offset="100%" stopColor={ACCENT} stopOpacity="0.02" />
            </linearGradient>
          </defs>
          <line x1="0" y1="14" x2={W} y2="14" stroke={INK} strokeWidth="1.5" strokeDasharray="2 8" opacity="0.5" />
          <path d={`M 0 14 C ${W * 0.28} 28 ${W * 0.53} 94 ${W} 146 L ${W} 14 Z`} fill="url(#lf)" opacity={wedgeO} />
          <path d={`M 0 14 C ${W * 0.28} 28 ${W * 0.53} 94 ${W} 146`} fill="none" stroke={ACCENT} strokeWidth="4" strokeLinecap="round" strokeDasharray={dash} strokeDashoffset={draw} />
          {Array.from({ length: 13 }, (_, i) => (<line key={i} x1={(W / 12) * i} y1="160" x2={(W / 12) * i} y2={i % 3 === 0 ? 172 : 167} stroke={INK} strokeWidth="1" opacity="0.22" />))}
          <circle cx="0" cy="14" r="6" fill={INK} />
          {/* pulso al llegar al fondo */}
          <circle cx={W} cy="146" r={pulseR} fill="none" stroke={ACCENT} strokeWidth="2" opacity={0.45 * arrive} />
          {/* marcador que VIAJA por la curva mientras se dibuja */}
          <circle cx={dotx} cy={doty} r="22" fill={ACCENT} opacity={0.16 * dotO} />
          <circle cx={dotx} cy={doty} r="11" fill={ACCENT} opacity={dotO} />
          <text x="0" y="196" fill={MUTE} fontSize="24" fontWeight="600" letterSpacing="1.6">HOY</text>
          <text x={W} y="196" textAnchor="end" fill={ACCENT} fontSize="24" fontWeight="700" letterSpacing="1.2">{scene.axisRight}</text>
        </svg>
        <div style={{ position: "absolute", top: 880, left: M, fontSize: 34, fontWeight: 500, color: MUTE, ...reveal(frame, 38) }}>{scene.toLabel}</div>
        <div style={{ position: "absolute", top: 922, left: M - 4, fontSize: fitSize(`${scene.prefix ?? "$"}${fmtNum(scene.to)}`, 176), fontWeight: 800, letterSpacing: "-0.035em", lineHeight: 1, color: ACCENT, ...reveal(frame, 40, 24) }}>{scene.prefix ?? "$"}{fmtNum(shownTo)}</div>
        <div style={{ position: "absolute", top: 1150, left: M, right: M, display: "flex", alignItems: "baseline", gap: 20, ...reveal(frame, 84) }}>
          <span style={{ fontSize: 84, fontWeight: 800, color: ACCENT, letterSpacing: "-0.03em" }}>−{scene.prefix ?? "$"}{fmtNum(scene.delta)}</span>
          <span style={{ fontSize: 38, fontWeight: 500, color: INK }}>{scene.deltaLabel}</span>
        </div>
        {scene.note && <div style={{ position: "absolute", top: 1290, left: M, right: M, fontSize: 33, fontWeight: 400, lineHeight: 1.4, color: SUB, maxWidth: 840, ...reveal(frame, 90) }}>{scene.note}</div>}
      </>
    );
  }

  if (scene.type === "compare") {
    const lh = 500; const maxV = Math.max(scene.left.value, scene.right.value);
    const half = (1080 - 2 * M - 80) / 2;
    const colY = 1240;
    // barras crecen con spring (overshoot sutil), escalonadas
    const sp = (delay: number) => Math.max(0, spring({ frame: frame - delay, fps, config: { damping: 13, mass: 0.9, stiffness: 120 } }));
    const gL = sp(16), gR = sp(26);
    // números cuentan al crecer (clamp a 0..1, sin overshoot en la cifra)
    const progL = interpolate(frame, [16, 56], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
    const progR = interpolate(frame, [26, 66], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
    const winGlow = interpolate(frame, [58, 74], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    const sweep = interpolate(frame, [40, 78], [130, -40], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    const bar = (v: number, x: number, w: number, win: boolean, g: number) => {
      const h = Math.min(1.0, v / maxV) * lh * g;
      return (
        <div style={{ position: "absolute", left: x, top: colY - h, width: w, height: h, background: win ? GREEN : "#D8CFBD", borderRadius: "8px 8px 0 0", overflow: "hidden", boxShadow: win ? `0 0 ${44 * winGlow}px rgba(31,122,77,0.45)` : "none" }}>
          {win && <div style={{ position: "absolute", left: 0, right: 0, top: `${sweep}%`, height: "45%", background: "linear-gradient(180deg, transparent, rgba(255,255,255,0.38), transparent)" }} />}
        </div>
      );
    };
    const vStyle = (win: boolean, valStr: string): React.CSSProperties => ({ fontSize: fitSize(valStr, 96, half - 10), fontWeight: 800, letterSpacing: "-0.03em", color: win ? GREEN : INK });
    body = (
      <>
        {scene.kicker && <div style={{ position: "absolute", top: 300, left: M, right: M, fontSize: 30, fontWeight: 700, letterSpacing: "0.2em", color: ACCENT, ...reveal(frame, 4) }}>{scene.kicker}</div>}
        <div style={{ position: "absolute", top: 470, left: M, ...reveal(frame, 10) }}>
          <div style={{ fontSize: 32, fontWeight: 600, color: MUTE }}>{scene.left.tag}</div>
          <div style={vStyle(scene.winner === "left", `${scene.prefix ?? "$"}${fmtNum(scene.left.value)}`)}>{scene.prefix ?? "$"}{fmtNum(scene.left.value * progL)}</div>
        </div>
        <div style={{ position: "absolute", top: 470, left: M + half + 80, ...reveal(frame, 14) }}>
          <div style={{ fontSize: 32, fontWeight: 600, color: MUTE }}>{scene.right.tag}</div>
          <div style={vStyle(scene.winner === "right", `${scene.prefix ?? "$"}${fmtNum(scene.right.value)}`)}>{scene.prefix ?? "$"}{fmtNum(scene.right.value * progR)}</div>
        </div>
        {bar(scene.left.value, M, half, scene.winner === "left", gL)}
        {bar(scene.right.value, M + half + 80, half, scene.winner === "right", gR)}
        <div style={{ position: "absolute", top: colY + 20, left: M, width: half, textAlign: "center", fontSize: 30, fontWeight: 600, color: MUTE }}>{scene.left.tag}</div>
        <div style={{ position: "absolute", top: colY + 20, left: M + half + 80, width: half, textAlign: "center", fontSize: 30, fontWeight: 600, color: scene.winner === "right" ? GREEN : MUTE }}>{scene.right.tag}</div>
        {scene.note && <div style={{ position: "absolute", top: 1360, left: M, right: M, fontSize: 33, fontWeight: 400, lineHeight: 1.4, color: SUB, maxWidth: 840, ...reveal(frame, 70) }}>{scene.note}</div>}
      </>
    );
  }

  if (scene.type === "payoff") {
    const shown = count(frame, 14, 54, 0, scene.value);
    body = (
      <>
        <div style={{ position: "absolute", top: 560, left: M, fontSize: 34, fontWeight: 700, letterSpacing: "0.18em", color: ACCENT, ...reveal(frame, 6) }}>{scene.kicker}</div>
        <div style={{ position: "absolute", top: 640, left: M - 4, fontSize: fitSize(`${scene.prefix ?? "$"}${fmtNum(scene.value)}`, 230), fontWeight: 800, letterSpacing: "-0.04em", lineHeight: 1, color: INK, ...reveal(frame, 12, 26) }}>
          {scene.prefix ?? "$"}{fmtNum(shown)}{scene.suffix ? <span style={{ fontSize: "0.36em", fontWeight: 700, marginLeft: 12, color: MUTE }}>{scene.suffix}</span> : null}
        </div>
        <div style={{ position: "absolute", top: 940, left: M, fontSize: 52, fontWeight: 700, color: ACCENT, ...reveal(frame, 50) }}>{scene.deltaText}</div>
        {scene.body && <div style={{ position: "absolute", top: 1050, left: M, right: M, fontSize: 38, fontWeight: 400, lineHeight: 1.42, color: SUB, maxWidth: 860, ...reveal(frame, 58) }}>{scene.body}</div>}
      </>
    );
  }

  if (scene.type === "close") {
    body = (
      <>
        <div style={{ position: "absolute", top: 520, left: M, right: M }}>
          {scene.headline.map((l, i) => (
            <div key={i} style={{ fontSize: 104, fontWeight: 800, lineHeight: 1.04, letterSpacing: "-0.03em", color: l.accent ? ACCENT : INK, ...reveal(frame, 8 + i * 8, 26) }}>{l.text}</div>
          ))}
        </div>
        {scene.sub && <div style={{ position: "absolute", top: 900, left: M, right: M, fontSize: 40, fontWeight: 400, lineHeight: 1.4, color: SUB, maxWidth: 860, ...reveal(frame, 8 + scene.headline.length * 8 + 6) }}>{scene.sub}</div>}
        <div style={{ position: "absolute", top: 1150, left: M, display: "flex", alignItems: "center", gap: 22, ...reveal(frame, 8 + scene.headline.length * 8 + 14) }}>
          <div style={{ width: 54, height: 54, border: `4px solid ${ACCENT}`, borderRadius: 6, position: "relative" }}>
            <div style={{ position: "absolute", left: 12, right: 12, top: 6, bottom: 14, borderLeft: `4px solid ${ACCENT}`, borderRight: `4px solid ${ACCENT}` }} />
          </div>
          <span style={{ fontSize: 40, fontWeight: 700, color: INK }}>{scene.cta}</span>
        </div>
      </>
    );
  }

  if (scene.type === "plate") {
    const plO = interpolate(frame, [8, 24], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    body = (
      <>
        {scene.kicker && (
          <div style={{ position: "absolute", top: 300, left: M, display: "flex", alignItems: "center", gap: 24, ...reveal(frame, 4) }}>
            {scene.logo && <Img src={staticFile(scene.logo)} style={{ width: 74, height: 74 }} />}
            <div style={{ fontSize: 30, fontWeight: 700, letterSpacing: "0.2em", color: ACCENT }}>{scene.kicker}</div>
          </div>
        )}
        <div style={{ position: "absolute", top: 430, left: M, right: M, height: 940, overflow: "hidden", border: `1.5px solid ${INK}`, opacity: plO }}>
          <OffthreadVideo src={staticFile(scene.src)} muted loop
            style={{ width: "100%", height: "100%", objectFit: "cover",
              filter: "grayscale(0.36) sepia(0.2) saturate(1.1) contrast(1.09) brightness(0.98)" }} />
          {/* tratamiento de marca (igual que hero_i2v): tinte oxblood + viñeta + grano = figura impresa */}
          <AbsoluteFill style={{ backgroundColor: ACCENT, opacity: 0.1, mixBlendMode: "overlay", pointerEvents: "none" }} />
          <AbsoluteFill style={{ boxShadow: "inset 0 0 110px rgba(27,23,18,0.5)", pointerEvents: "none" }} />
          <AbsoluteFill style={{ opacity: 0.06, mixBlendMode: "multiply", pointerEvents: "none" }}>
            <svg width="888" height="940"><filter id="pg"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" stitchTiles="stitch" /></filter><rect width="888" height="940" filter="url(#pg)" /></svg>
          </AbsoluteFill>
          <div style={{ position: "absolute", left: 24, bottom: 20, fontSize: 26, fontWeight: 600, color: "#EDE6D8", letterSpacing: "0.06em", textShadow: "0 2px 8px rgba(0,0,0,0.6)" }}>{scene.caption}</div>
        </div>
        {scene.note && <div style={{ position: "absolute", top: 1420, left: M, right: M, fontSize: 36, fontWeight: 400, lineHeight: 1.4, color: SUB, maxWidth: 860, ...reveal(frame, 30) }}>{scene.note}</div>}
      </>
    );
  }

  if (scene.type === "hero_i2v") {
    // FIGURA editorial: la i2v va enmarcada (márgenes de papel + borde tinta + pie
    // de foto), TRATADA al color de la marca (grade cálido desaturado + tinte oxblood
    // + grano) para que se sienta impresa/integrada, no un video crudo full-bleed.
    const PLT_T = 300, PLT_H = 1020;                 // plate con márgenes de papel (deja banda de pie segura)
    // P0.3: la figura es visible desde el frame 0 (freno de scroll / portada del grid), no arranca en blanco
    const vidO = interpolate(frame, [0, 8], [0.6, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    const zoom = 1.06 + interpolate(frame, [0, durF], [0, 0.05]); // ken-burns lento dentro del marco
    body = (
      <>
        {scene.kicker && <div style={{ position: "absolute", top: 250, left: M, fontSize: 28, fontWeight: 700, letterSpacing: "0.24em", color: ACCENT }}>{scene.kicker}</div>}
        {/* la placa-figura */}
        <div style={{ position: "absolute", top: PLT_T, left: M, width: 1080 - 2 * M, height: PLT_H, overflow: "hidden", border: `1.5px solid ${INK}`, opacity: vidO }}>
          <OffthreadVideo src={staticFile(scene.src)} muted loop
            style={{ width: "100%", height: "100%", objectFit: "cover", transform: `scale(${zoom})`,
              filter: "grayscale(0.36) sepia(0.2) saturate(1.1) contrast(1.09) brightness(0.98)" }} />
          {/* tinte de marca + viñeta para asentar en el papel */}
          <AbsoluteFill style={{ backgroundColor: ACCENT, opacity: 0.1, mixBlendMode: "overlay", pointerEvents: "none" }} />
          <AbsoluteFill style={{ boxShadow: "inset 0 0 90px rgba(27,23,18,0.5)", pointerEvents: "none" }} />
          {/* grano de papel sobre la imagen */}
          <AbsoluteFill style={{ opacity: 0.06, mixBlendMode: "multiply", pointerEvents: "none" }}>
            <svg width="888" height={PLT_H}><filter id={`hg${scene.src.length}`}><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" stitchTiles="stitch" /></filter><rect width="888" height={PLT_H} filter={`url(#hg${scene.src.length})`} /></svg>
          </AbsoluteFill>
        </div>
        {/* pie de foto editorial DEBAJO de la figura */}
        <div style={{ position: "absolute", top: PLT_T + PLT_H + 34, left: M, right: M }}>
          {scene.caption && <div style={{ fontSize: 62, fontWeight: 800, lineHeight: 1.06, letterSpacing: "-0.02em", color: INK, ...reveal(frame, 20, 20) }}>{scene.caption}</div>}
          {scene.punch && <div style={{ marginTop: 16, fontSize: 32, fontWeight: 400, color: SUB, ...reveal(frame, 30) }}>{scene.punch}</div>}
        </div>
      </>
    );
  }

  if (scene.type === "pictogram") {
    // PICTOGRAMA: rejilla de puntos; los resaltados se llenan en secuencia (staggered) con pop
    // de resorte + un contador que sube sincronizado. Muy dinámico, 100% código ($0).
    const total = scene.total ?? 100;
    const cols = 10;
    const DOT = 46, GAP = 20;
    const gridW = cols * DOT + (cols - 1) * GAP;
    const rows = Math.ceil(total / cols);
    const gridLeft = (1080 - gridW) / 2;
    const gridTop = 690;
    const fillColor = scene.color === "green" ? GREEN : ACCENT;
    const perDot = 1.5;               // frames de stagger por punto resaltado
    const t0 = 16;
    const shownFilled = Math.max(0, Math.min(scene.highlight, Math.floor((frame - t0) / perDot)));
    const bigN = Math.round(interpolate(frame, [t0, t0 + scene.highlight * perDot], [0, scene.highlight], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }));
    body = (
      <>
        {scene.kicker && <div style={{ position: "absolute", top: 300, left: M, fontSize: 30, fontWeight: 700, letterSpacing: "0.2em", color: fillColor, ...reveal(frame, 4) }}>{scene.kicker}</div>}
        <div style={{ position: "absolute", top: 396, left: M, right: M, display: "flex", alignItems: "baseline", gap: 22 }}>
          <span style={{ fontSize: 168, fontWeight: 800, letterSpacing: "-0.04em", lineHeight: 1, color: fillColor }}>{bigN}{scene.suffix ?? ""}</span>
          <span style={{ fontSize: 52, fontWeight: 700, color: INK }}>de {total}</span>
        </div>
        {scene.label && <div style={{ position: "absolute", top: 600, left: M, right: M, fontSize: 40, fontWeight: 500, color: SUB, ...reveal(frame, 10) }}>{scene.label}</div>}
        {Array.from({ length: total }).map((_, i) => {
          const r = Math.floor(i / cols), c = i % cols;
          const x = gridLeft + c * (DOT + GAP), y = gridTop + r * (DOT + GAP);
          const appear = 8 + i * 0.5;
          const s = Math.min(1, spring({ frame: frame - appear, fps, config: { damping: 13, stiffness: 160 } }));
          const on = i < shownFilled;
          const pop = on ? spring({ frame: frame - (t0 + i * perDot), fps, config: { damping: 9, stiffness: 200 } }) : 0;
          return (
            <div key={i} style={{ position: "absolute", left: x, top: y, width: DOT, height: DOT, borderRadius: 11, opacity: s, transform: `scale(${s * (1 + 0.12 * Math.min(1, pop) * (1 - Math.min(1, pop)) * 4)})`, background: on ? fillColor : "transparent", border: on ? "none" : `2.5px solid ${HAIR}` }} />
          );
        })}
        {scene.note && <div style={{ position: "absolute", top: gridTop + rows * (DOT + GAP) + 34, left: M, right: M, fontSize: 34, fontWeight: 400, color: SUB, ...reveal(frame, t0 + scene.highlight * perDot) }}>{scene.note}</div>}
      </>
    );
  }

  if (scene.type === "odometer") {
    // ODÓMETRO: cada dígito rueda en un cilindro (0-9) hasta su cifra, con vueltas extra. $0.
    const FS = 140, DH = Math.round(FS * 1.04), DW = Math.round(FS * 0.6);
    const prog = interpolate(frame, [12, 74], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
    const full = (scene.prefix ?? "") + fmtNum(scene.value) + (scene.suffix ?? "");
    body = (
      <>
        {scene.kicker && <div style={{ position: "absolute", top: 300, left: M, fontSize: 30, fontWeight: 700, letterSpacing: "0.2em", color: ACCENT, ...reveal(frame, 4) }}>{scene.kicker}</div>}
        {scene.label && <div style={{ position: "absolute", top: 372, left: M, right: M, fontSize: 56, fontWeight: 800, lineHeight: 1.05, letterSpacing: "-0.02em", color: INK, ...reveal(frame, 6) }}>{scene.label}</div>}
        <div style={{ position: "absolute", top: 800, left: 0, width: 1080, display: "flex", justifyContent: "center", alignItems: "center" }}>
          {[...full].map((ch, i) => {
            if (ch >= "0" && ch <= "9") {
              const d = +ch, total = d + 20, cur = total * prog;
              return (
                <div key={i} style={{ width: DW, height: DH, overflow: "hidden", position: "relative" }}>
                  <div style={{ position: "absolute", top: 0, left: 0, width: "100%", transform: `translateY(${(-cur * DH).toFixed(1)}px)` }}>
                    {Array.from({ length: total + 1 }).map((_, k) => (
                      <div key={k} style={{ height: DH, lineHeight: `${DH}px`, textAlign: "center", fontSize: FS, fontWeight: 800, letterSpacing: "-0.04em", color: INK }}>{k % 10}</div>
                    ))}
                  </div>
                </div>
              );
            }
            return <div key={i} style={{ height: DH, lineHeight: `${DH}px`, fontSize: FS, fontWeight: 800, letterSpacing: "-0.02em", color: ch === "," ? MUTE : INK, padding: ch === "," ? "0 3px" : "0 4px" }}>{ch}</div>;
          })}
        </div>
        {scene.sublabel && <div style={{ position: "absolute", top: 800 + DH + 30, left: M, right: M, textAlign: "center", fontSize: 36, fontWeight: 400, color: SUB, ...reveal(frame, 60) }}>{scene.sublabel}</div>}
        {scene.note && <div style={{ position: "absolute", top: 1330, left: M, right: M, textAlign: "center", fontSize: 34, fontWeight: 400, color: SUB, ...reveal(frame, 70) }}>{scene.note}</div>}
      </>
    );
  }

  if (scene.type === "curvedText") {
    // TEXTO EN CURVA: la frase cabalga una baseline en arco (SVG textPath) y se revela. $0.
    const prog = interpolate(frame, [10, 58], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
    const col = semColor(scene.color, INK);
    body = (
      <>
        {scene.kicker && <div style={{ position: "absolute", top: 300, left: M, fontSize: 30, fontWeight: 700, letterSpacing: "0.2em", color: ACCENT, ...reveal(frame, 4) }}>{scene.kicker}</div>}
        {scene.label && <div style={{ position: "absolute", top: 400, left: M, right: M, fontSize: 40, fontWeight: 500, color: SUB, ...reveal(frame, 6) }}>{scene.label}</div>}
        <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
          <defs>
            <path id="txtarc" d="M 30 1030 Q 540 740 1050 1030" fill="none" />
            <clipPath id="tclip"><rect x="0" y="0" width={30 + prog * 1030} height="1920" /></clipPath>
          </defs>
          <g clipPath="url(#tclip)">
            <text fontSize="62" fontWeight="800" fill={col} letterSpacing="0" style={{ fontFamily: FONT }}>
              <textPath href="#txtarc" startOffset="50%" textAnchor="middle">{scene.text}</textPath>
            </text>
          </g>
        </svg>
        {scene.sub && <div style={{ position: "absolute", top: 1120, left: M, right: M, textAlign: "center", fontSize: 40, fontWeight: 400, color: SUB, ...reveal(frame, 46) }}>{scene.sub}</div>}
        {scene.note && <div style={{ position: "absolute", top: 1330, left: M, right: M, textAlign: "center", fontSize: 34, fontWeight: 400, color: SUB, ...reveal(frame, 60) }}>{scene.note}</div>}
      </>
    );
  }

  if (scene.type === "erosion") {
    // EROSIÓN: un bloque pierde altura y se desgrana en partículas (inflación / comisiones comiendo valor). $0.
    const bx = 420, bw = 240, byBot = 1210, maxH = 480;
    const from = scene.fromValue, to = scene.toValue;
    const prog = interpolate(frame, [16, 86], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.cubic) });
    const cur = from + (to - from) * prog;
    const curH = maxH * (cur / from), topY = byBot - curH;
    body = (
      <>
        {scene.kicker && <div style={{ position: "absolute", top: 300, left: M, fontSize: 30, fontWeight: 700, letterSpacing: "0.2em", color: ACCENT, ...reveal(frame, 4) }}>{scene.kicker}</div>}
        {scene.label && <div style={{ position: "absolute", top: 372, left: M, right: M, fontSize: 60, fontWeight: 800, lineHeight: 1.05, letterSpacing: "-0.02em", color: INK, ...reveal(frame, 6) }}>{scene.label}</div>}
        <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
          <rect x={bx} y={byBot - maxH} width={bw} height={maxH} fill="none" stroke={HAIR} strokeWidth={2} strokeDasharray="7 9" rx={6} />
          <rect x={bx} y={topY} width={bw} height={curH} fill={INK} rx={6} />
          {Array.from({ length: 14 }).map((_, i) => {
            const sp = 18 + i * 4.2, life = frame - sp;
            if (life <= 0 || prog >= 0.99) return null;
            const px = bx + ((i * 53) % (bw - 20)) + 10, py = topY + life * 4.4 - 8;
            const op = Math.max(0, 0.7 - life / 60);
            return <circle key={i} cx={px} cy={py} r={5} fill={INK} opacity={op} />;
          })}
        </svg>
        <div style={{ position: "absolute", top: byBot - maxH - 130, left: 0, width: 1080, textAlign: "center" }}>
          <span style={{ fontSize: 110, fontWeight: 800, letterSpacing: "-0.04em", color: ACCENT }}>{scene.prefix ?? ""}{fmtNum(Math.round(cur))}</span>
        </div>
        {scene.fromLabel && <div style={{ position: "absolute", top: byBot + 24, left: bx - 260, width: 240, textAlign: "right", fontSize: 30, fontWeight: 600, color: MUTE, ...reveal(frame, 16) }}>{scene.fromLabel}</div>}
        {scene.toLabel && <div style={{ position: "absolute", top: byBot + 24, left: bx + bw + 20, width: 240, fontSize: 30, fontWeight: 600, color: ACCENT, ...reveal(frame, 70) }}>{scene.toLabel}</div>}
        {scene.note && <div style={{ position: "absolute", top: 1360, left: M, right: M, textAlign: "center", fontSize: 34, fontWeight: 400, color: SUB, ...reveal(frame, 80) }}>{scene.note}</div>}
      </>
    );
  }

  if (scene.type === "radialbars") {
    // CORONA / RAYOS: barras que crecen HACIA AFUERA desde un hub central, en cascada. Radial. $0.
    const cx = 540, cy = 902, r0 = 96, rMax = 330;
    const items = scene.items, N = items.length, maxV = Math.max(...items.map((i) => i.value)) || 1;
    body = (
      <>
        {scene.kicker && <div style={{ position: "absolute", top: 300, left: M, fontSize: 30, fontWeight: 700, letterSpacing: "0.2em", color: ACCENT, ...reveal(frame, 4) }}>{scene.kicker}</div>}
        {scene.label && <div style={{ position: "absolute", top: 372, left: M, right: M, fontSize: 64, fontWeight: 800, lineHeight: 1.05, letterSpacing: "-0.02em", color: INK, ...reveal(frame, 6) }}>{scene.label}</div>}
        <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
          <circle cx={cx} cy={cy} r={r0 - 16} fill="none" stroke={HAIR} strokeWidth={3} />
          {items.map((it, i) => {
            const ang = -Math.PI / 2 + (i / N) * 2 * Math.PI;
            const grow = interpolate(frame, [16 + i * 8, 16 + i * 8 + 22], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
            const len = r0 + (it.value / maxV) * (rMax - r0) * grow;
            return <line key={i} x1={cx + Math.cos(ang) * r0} y1={cy + Math.sin(ang) * r0} x2={cx + Math.cos(ang) * len} y2={cy + Math.sin(ang) * len} stroke={semColor(it.color, ACCENT)} strokeWidth={24} strokeLinecap="round" />;
          })}
        </svg>
        {items.map((it, i) => {
          const ang = -Math.PI / 2 + (i / N) * 2 * Math.PI, lr = r0 + (it.value / maxV) * (rMax - r0) + 44;
          const lx = cx + Math.cos(ang) * lr, ly = cy + Math.sin(ang) * lr;
          return <div key={`rl${i}`} style={{ position: "absolute", left: lx - 100, top: ly - 22, width: 200, textAlign: "center", fontSize: 30, fontWeight: 700, color: INK, ...reveal(frame, 16 + i * 8 + 18) }}>{it.label}</div>;
        })}
        {scene.centerBig && (
          <div style={{ position: "absolute", top: cy - 58, left: 0, width: 1080, textAlign: "center" }}>
            <div style={{ fontSize: 72, fontWeight: 800, letterSpacing: "-0.03em", color: INK }}>{scene.centerBig}</div>
            {scene.centerSub && <div style={{ fontSize: 24, fontWeight: 700, letterSpacing: "0.12em", color: MUTE }}>{scene.centerSub}</div>}
          </div>
        )}
        {scene.note && <div style={{ position: "absolute", top: 1330, left: M, right: M, textAlign: "center", fontSize: 34, fontWeight: 400, color: SUB, ...reveal(frame, 40) }}>{scene.note}</div>}
      </>
    );
  }

  if (scene.type === "spiral") {
    // ESPIRAL: espiral de Arquímedes que se dibuja del centro hacia afuera (crecimiento que compone). $0.
    const cx = 540, cy = 908, turns = scene.turns ?? 3.4, a = 11, steps = Math.round(turns * 64);
    const pts: [number, number][] = [];
    for (let s = 0; s <= steps; s++) { const th = (s / 64) * 2 * Math.PI, r = a * th; pts.push([cx + Math.cos(th - Math.PI / 2) * r, cy + Math.sin(th - Math.PI / 2) * r]); }
    const path = smoothPath(pts);
    const prog = interpolate(frame, [12, 94], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.cubic) });
    const ti = Math.min(pts.length - 1, Math.round(prog * (pts.length - 1))), tip = pts[ti];
    body = (
      <>
        {scene.kicker && <div style={{ position: "absolute", top: 300, left: M, fontSize: 30, fontWeight: 700, letterSpacing: "0.2em", color: ACCENT, ...reveal(frame, 4) }}>{scene.kicker}</div>}
        {scene.label && <div style={{ position: "absolute", top: 372, left: M, right: M, fontSize: 64, fontWeight: 800, lineHeight: 1.05, letterSpacing: "-0.02em", color: INK, ...reveal(frame, 6) }}>{scene.label}</div>}
        <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
          <path d={path} pathLength={1} fill="none" stroke={ACCENT} strokeWidth={7} strokeLinecap="round" strokeDasharray="1 1" strokeDashoffset={1 - prog} />
          <circle cx={tip[0]} cy={tip[1]} r={14} fill={ACCENT} />
        </svg>
        {scene.centerBig && (
          <div style={{ position: "absolute", top: cy - 56, left: 0, width: 1080, textAlign: "center" }}>
            <div style={{ fontSize: 64, fontWeight: 800, letterSpacing: "-0.03em", color: INK }}>{scene.centerBig}</div>
            {scene.centerSub && <div style={{ fontSize: 24, fontWeight: 700, letterSpacing: "0.12em", color: MUTE }}>{scene.centerSub}</div>}
          </div>
        )}
        {scene.note && <div style={{ position: "absolute", top: 1330, left: M, right: M, textAlign: "center", fontSize: 34, fontWeight: 400, color: SUB, ...reveal(frame, 90) }}>{scene.note}</div>}
      </>
    );
  }

  if (scene.type === "grow") {
    // BROTE: tallo orgánico que se dibuja hacia arriba + hojas que brotan. Crecimiento. $0.
    const cx = 540;
    const stemPts: [number, number][] = [[cx, 1330], [cx - 46, 1180], [cx + 34, 1020], [cx - 26, 858], [cx + 6, 720]];
    const stem = smoothPath(stemPts);
    const prog = interpolate(frame, [12, 84], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
    const leaves = [{ p: stemPts[1], dir: -1, at: 0.28 }, { p: stemPts[2], dir: 1, at: 0.5 }, { p: stemPts[3], dir: -1, at: 0.72 }];
    body = (
      <>
        {scene.kicker && <div style={{ position: "absolute", top: 300, left: M, fontSize: 30, fontWeight: 700, letterSpacing: "0.2em", color: GREEN, ...reveal(frame, 4) }}>{scene.kicker}</div>}
        {scene.label && <div style={{ position: "absolute", top: 372, left: M, right: M, fontSize: 64, fontWeight: 800, lineHeight: 1.05, letterSpacing: "-0.02em", color: INK, ...reveal(frame, 6) }}>{scene.label}</div>}
        <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
          <path d={stem} pathLength={1} fill="none" stroke={GREEN} strokeWidth={13} strokeLinecap="round" strokeDasharray="1 1" strokeDashoffset={1 - prog} />
          {leaves.map((lf, i) => {
            const s = interpolate(prog, [lf.at, lf.at + 0.16], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
            return <ellipse key={i} cx={lf.p[0] + lf.dir * 46} cy={lf.p[1] - 6} rx={54 * s} ry={26 * s} fill={GREEN} opacity={0.9} transform={`rotate(${lf.dir * 32} ${lf.p[0] + lf.dir * 46} ${lf.p[1] - 6})`} />;
          })}
          <circle cx={stemPts[4][0]} cy={stemPts[4][1]} r={Math.min(1, interpolate(prog, [0.9, 1], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })) * 30} fill={ACCENT} />
        </svg>
        {scene.topLabel && <div style={{ position: "absolute", top: 640, left: 0, width: 1080, textAlign: "center", fontSize: 40, fontWeight: 800, color: ACCENT, opacity: interpolate(prog, [0.9, 1], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>{scene.topLabel}</div>}
        {scene.note && <div style={{ position: "absolute", top: 1400, left: M, right: M, textAlign: "center", fontSize: 34, fontWeight: 400, color: SUB, ...reveal(frame, 80) }}>{scene.note}</div>}
      </>
    );
  }

  if (scene.type === "divergence") {
    // DIVERGENCIA / TIJERA: dos curvas suaves que se dibujan a la vez desde un origen común y se separan. $0.
    const cx0 = M, cx1 = 1080 - M, W = cx1 - cx0, cyBot = 1170, H = 470;
    const all = [...scene.a, ...scene.b], maxV = Math.max(...all), minV = Math.min(...all, 0), rng = maxV - minV || 1;
    const mk = (arr: number[]) => arr.map((v, i) => [cx0 + (i / (arr.length - 1)) * W, cyBot - ((v - minV) / rng) * H] as [number, number]);
    const pa = mk(scene.a), pb = mk(scene.b);
    const prog = interpolate(frame, [12, 84], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.cubic) });
    const colA = semColor(scene.colorA, GREEN), colB = semColor(scene.colorB, INK);
    const tip = (p: [number, number][]) => { const fi = prog * (p.length - 1), i0 = Math.floor(fi), i1 = Math.min(p.length - 1, i0 + 1), f = fi - i0; return [p[i0][0] + (p[i1][0] - p[i0][0]) * f, p[i0][1] + (p[i1][1] - p[i0][1]) * f] as [number, number]; };
    const ta = tip(pa), tb = tip(pb);
    const endIn = interpolate(prog, [0.84, 1], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    body = (
      <>
        {scene.kicker && <div style={{ position: "absolute", top: 300, left: M, fontSize: 30, fontWeight: 700, letterSpacing: "0.2em", color: ACCENT, ...reveal(frame, 4) }}>{scene.kicker}</div>}
        {scene.label && <div style={{ position: "absolute", top: 372, left: M, right: M, fontSize: 66, fontWeight: 800, lineHeight: 1.04, letterSpacing: "-0.02em", color: INK, ...reveal(frame, 6) }}>{scene.label}</div>}
        <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
          <line x1={cx0} y1={cyBot} x2={cx1} y2={cyBot} stroke={HAIR} strokeWidth={3} />
          <path d={smoothPath(pb)} pathLength={1} fill="none" stroke={colB} strokeWidth={7} strokeLinecap="round" strokeDasharray="1 1" strokeDashoffset={1 - prog} />
          <path d={smoothPath(pa)} pathLength={1} fill="none" stroke={colA} strokeWidth={7} strokeLinecap="round" strokeDasharray="1 1" strokeDashoffset={1 - prog} />
          <circle cx={tb[0]} cy={tb[1]} r={13} fill={colB} />
          <circle cx={ta[0]} cy={ta[1]} r={13} fill={colA} />
        </svg>
        {scene.labelA && <div style={{ position: "absolute", top: ta[1] - 66, left: Math.min(cx1 - 300, ta[0] - 30), width: 320, fontSize: 40, fontWeight: 800, letterSpacing: "-0.02em", color: colA, opacity: endIn }}>{scene.labelA}</div>}
        {scene.labelB && <div style={{ position: "absolute", top: tb[1] + 22, left: Math.min(cx1 - 300, tb[0] - 30), width: 320, fontSize: 40, fontWeight: 800, letterSpacing: "-0.02em", color: colB, opacity: endIn }}>{scene.labelB}</div>}
        {scene.note && <div style={{ position: "absolute", top: cyBot + 70, left: M, right: M, fontSize: 34, fontWeight: 400, color: SUB, ...reveal(frame, 84) }}>{scene.note}</div>}
      </>
    );
  }

  if (scene.type === "arcflow") {
    // ARCOS DE FLUJO: desde un origen salen arcos curvos hacia varios destinos, dibujados por un cometa. $0.
    const ox = 150, oy = 880, tx = 742, tg = scene.targets, N = tg.length;
    const tyOf = (i: number) => 660 + (N === 1 ? 260 : (i / (N - 1)) * 520);
    body = (
      <>
        {scene.kicker && <div style={{ position: "absolute", top: 300, left: M, fontSize: 30, fontWeight: 700, letterSpacing: "0.2em", color: ACCENT, ...reveal(frame, 4) }}>{scene.kicker}</div>}
        {scene.label && <div style={{ position: "absolute", top: 372, left: M, right: M, fontSize: 66, fontWeight: 800, lineHeight: 1.04, letterSpacing: "-0.02em", color: INK, ...reveal(frame, 6) }}>{scene.label}</div>}
        <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
          {tg.map((t, i) => {
            const ty = tyOf(i), midx = (ox + tx) / 2, midy = (oy + ty) / 2 - 150;
            const d = `M ${ox} ${oy} Q ${midx} ${midy} ${tx} ${ty}`;
            const appear = 18 + i * 12;
            const prog = interpolate(frame, [appear, appear + 28], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.cubic) });
            const col = semColor(t.color, ACCENT);
            const qt = prog, bx = (1 - qt) * (1 - qt) * ox + 2 * (1 - qt) * qt * midx + qt * qt * tx, by = (1 - qt) * (1 - qt) * oy + 2 * (1 - qt) * qt * midy + qt * qt * ty;
            return (
              <React.Fragment key={i}>
                <path d={d} pathLength={1} fill="none" stroke={col} strokeWidth={5} strokeLinecap="round" strokeDasharray="1 1" strokeDashoffset={1 - prog} opacity={0.9} />
                <circle cx={tx} cy={ty} r={18} fill={col} opacity={interpolate(prog, [0.9, 1], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })} />
                {prog > 0.02 && prog < 0.99 && <circle cx={bx} cy={by} r={12} fill={col} />}
              </React.Fragment>
            );
          })}
          <circle cx={ox} cy={oy} r={24} fill={INK} />
        </svg>
        <div style={{ position: "absolute", top: oy + 40, left: ox - 110, width: 220, textAlign: "center", fontSize: 32, fontWeight: 700, color: INK, ...reveal(frame, 8) }}>{scene.originLabel}</div>
        {tg.map((t, i) => (
          <div key={`t${i}`} style={{ position: "absolute", top: tyOf(i) - 24, left: tx + 34, width: 260, ...reveal(frame, 18 + i * 12 + 20) }}>
            <div style={{ fontSize: 36, fontWeight: 700, color: INK }}>{t.label}</div>
            {t.sub && <div style={{ fontSize: 26, fontWeight: 400, color: MUTE }}>{t.sub}</div>}
          </div>
        ))}
        {scene.note && <div style={{ position: "absolute", top: 1300, left: M, right: M, fontSize: 34, fontWeight: 400, color: SUB, ...reveal(frame, 60) }}>{scene.note}</div>}
      </>
    );
  }

  if (scene.type === "balance") {
    // BALANZA: viga que pivota; el lado más pesado baja. Metáfora de equilibrio (deuda vs ahorro...). $0.
    const fx = 540, fy = 900, armLen = 348;
    const lv = scene.leftValue, rv = scene.rightValue, denom = Math.max(lv, rv) || 1;
    const angTarget = Math.max(-0.34, Math.min(0.34, ((rv - lv) / denom) * 0.5));
    const prog = Math.min(1, spring({ frame: frame - 18, fps, config: { damping: 11, stiffness: 60 } }));
    const ang = angTarget * prog;
    const lx = fx - armLen * Math.cos(ang), ly = fy - armLen * Math.sin(ang);
    const rx = fx + armLen * Math.cos(ang), ry = fy + armLen * Math.sin(ang);
    const pan = (px: number, py: number, val: number, lab: string, i: number) => (
      <div key={i} style={{ position: "absolute", top: py + 40, left: px - 160, width: 320, textAlign: "center", ...reveal(frame, 26) }}>
        <div style={{ fontSize: 66, fontWeight: 800, letterSpacing: "-0.03em", color: INK }}>{scene.prefix ?? ""}{fmtNum(val)}</div>
        <div style={{ fontSize: 32, fontWeight: 500, color: SUB, marginTop: 2 }}>{lab}</div>
      </div>
    );
    body = (
      <>
        {scene.kicker && <div style={{ position: "absolute", top: 300, left: M, fontSize: 30, fontWeight: 700, letterSpacing: "0.2em", color: ACCENT, ...reveal(frame, 4) }}>{scene.kicker}</div>}
        {scene.label && <div style={{ position: "absolute", top: 372, left: M, right: M, fontSize: 66, fontWeight: 800, lineHeight: 1.04, letterSpacing: "-0.02em", color: INK, ...reveal(frame, 6) }}>{scene.label}</div>}
        <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
          <line x1={fx} y1={fy} x2={fx} y2={fy + 190} stroke={INK} strokeWidth={8} />
          <path d={`M ${fx - 60} ${fy + 190} L ${fx + 60} ${fy + 190} L ${fx} ${fy + 90} Z`} fill={INK} />
          <line x1={lx} y1={ly} x2={rx} y2={ry} stroke={INK} strokeWidth={12} strokeLinecap="round" />
          <line x1={lx} y1={ly} x2={lx} y2={ly + 100} stroke={MUTE} strokeWidth={4} />
          <line x1={rx} y1={ry} x2={rx} y2={ry + 100} stroke={MUTE} strokeWidth={4} />
          <path d={`M ${lx - 84} ${ly + 100} A 84 44 0 0 0 ${lx + 84} ${ly + 100}`} fill="none" stroke={semColor(scene.leftValue > scene.rightValue ? "accent" : "ink", INK)} strokeWidth={7} />
          <path d={`M ${rx - 84} ${ry + 100} A 84 44 0 0 0 ${rx + 84} ${ry + 100}`} fill="none" stroke={semColor(scene.rightValue > scene.leftValue ? "accent" : "ink", INK)} strokeWidth={7} />
          <circle cx={fx} cy={fy} r={16} fill={INK} />
        </svg>
        {pan(lx, ly + 100, lv, scene.leftLabel, 0)}
        {pan(rx, ry + 100, rv, scene.rightLabel, 1)}
        {scene.note && <div style={{ position: "absolute", top: 1330, left: M, right: M, textAlign: "center", fontSize: 34, fontWeight: 400, color: SUB, ...reveal(frame, 40) }}>{scene.note}</div>}
      </>
    );
  }

  if (scene.type === "gauge") {
    // GAUGE / MEDIDOR: semicírculo cuyo arco se llena + aguja que barre. Redondo, dinámico. $0.
    const cx = 540, cy = 1020, R = 330, SW = 62;
    const col = scene.color === "accent" ? ACCENT : GREEN;
    const prog = Math.min(1, spring({ frame: frame - 14, fps, config: { damping: 16, stiffness: 80 } }));
    const pct = scene.pct * prog;
    const theta = Math.PI + (pct / 100) * Math.PI;
    const px = cx + R * Math.cos(theta), py = cy + R * Math.sin(theta);
    const nx = cx + (R - 30) * Math.cos(theta), ny = cy + (R - 30) * Math.sin(theta);
    body = (
      <>
        {scene.kicker && <div style={{ position: "absolute", top: 300, left: M, fontSize: 30, fontWeight: 700, letterSpacing: "0.2em", color: col, ...reveal(frame, 4) }}>{scene.kicker}</div>}
        {scene.label && <div style={{ position: "absolute", top: 372, left: M, right: M, fontSize: 64, fontWeight: 800, lineHeight: 1.05, letterSpacing: "-0.02em", color: INK, ...reveal(frame, 6) }}>{scene.label}</div>}
        <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
          <path d={`M ${cx - R} ${cy} A ${R} ${R} 0 0 1 ${cx + R} ${cy}`} fill="none" stroke={HAIR} strokeWidth={SW} strokeLinecap="round" />
          <path d={`M ${cx - R} ${cy} A ${R} ${R} 0 0 1 ${px.toFixed(1)} ${py.toFixed(1)}`} fill="none" stroke={col} strokeWidth={SW} strokeLinecap="round" />
          <line x1={cx} y1={cy} x2={nx.toFixed(1)} y2={ny.toFixed(1)} stroke={INK} strokeWidth={9} strokeLinecap="round" />
          <circle cx={cx} cy={cy} r={26} fill={INK} />
        </svg>
        <div style={{ position: "absolute", top: cy - 210, left: 0, width: 1080, textAlign: "center" }}>
          {scene.centerBig && <div style={{ fontSize: 120, fontWeight: 800, letterSpacing: "-0.04em", lineHeight: 1, color: col }}>{scene.centerBig}</div>}
          {scene.centerSub && <div style={{ fontSize: 30, fontWeight: 700, letterSpacing: "0.14em", color: MUTE, marginTop: 8 }}>{scene.centerSub}</div>}
        </div>
        {scene.leftLabel && <div style={{ position: "absolute", top: cy + 20, left: cx - R - 30, width: 220, textAlign: "center", fontSize: 30, fontWeight: 600, color: MUTE, ...reveal(frame, 16) }}>{scene.leftLabel}</div>}
        {scene.rightLabel && <div style={{ position: "absolute", top: cy + 20, left: cx + R - 190, width: 220, textAlign: "center", fontSize: 30, fontWeight: 600, color: MUTE, ...reveal(frame, 16) }}>{scene.rightLabel}</div>}
        {scene.note && <div style={{ position: "absolute", top: cy + 110, left: M, right: M, textAlign: "center", fontSize: 34, fontWeight: 400, color: SUB, ...reveal(frame, 34) }}>{scene.note}</div>}
      </>
    );
  }

  if (scene.type === "bubbles") {
    // BURBUJAS PROPORCIONALES: círculos ∝ √valor que emergen (pop) y flotan. Orgánico, redondo. $0.
    const items = scene.items;
    const colOf = (c?: string) => (c === "green" ? GREEN : c === "ink" ? INK : ACCENT);
    const gap = 26;
    let radii = items.map((it) => 30 * Math.sqrt(it.value));
    const rawW = radii.reduce((a, r) => a + 2 * r, 0) + gap * (items.length - 1);
    const fit = Math.min(1, 980 / rawW);              // auto-ajuste al ancho seguro
    radii = radii.map((r) => r * fit);
    const totalW = radii.reduce((a, r) => a + 2 * r, 0) + gap * (items.length - 1);
    let xacc = (1080 - totalW) / 2;
    const centers = radii.map((r, i) => { const cx = xacc + r; xacc += 2 * r + gap; return [cx, 880 + (i % 2 === 0 ? -26 : 30), r] as [number, number, number]; });
    body = (
      <>
        {scene.kicker && <div style={{ position: "absolute", top: 300, left: M, fontSize: 30, fontWeight: 700, letterSpacing: "0.2em", color: ACCENT, ...reveal(frame, 4) }}>{scene.kicker}</div>}
        {scene.label && <div style={{ position: "absolute", top: 372, left: M, right: M, fontSize: 68, fontWeight: 800, lineHeight: 1.04, letterSpacing: "-0.02em", color: INK, ...reveal(frame, 6) }}>{scene.label}</div>}
        {items.map((it, i) => {
          const [cx, cyb, r] = centers[i];
          const s = Math.min(1, spring({ frame: frame - (16 + i * 11), fps, config: { damping: 11, stiffness: 150 } }));
          const fy = Math.sin(frame / 22 + i * 1.3) * 8;
          return (
            <React.Fragment key={i}>
              <div style={{ position: "absolute", left: cx - r, top: cyb - r + fy, width: 2 * r, height: 2 * r, borderRadius: "50%", background: colOf(it.color), transform: `scale(${s})`, display: "flex", alignItems: "center", justifyContent: "center", color: PAPER }}>
                <div style={{ fontSize: Math.min(r * 0.62, 88), fontWeight: 800, letterSpacing: "-0.03em" }}>{it.value}{it.suffix ?? ""}</div>
              </div>
              <div style={{ position: "absolute", left: cx - 130, top: cyb + r + fy + 16, width: 260, textAlign: "center", fontSize: 32, fontWeight: 600, color: INK, opacity: s }}>{it.label}</div>
            </React.Fragment>
          );
        })}
        {scene.note && <div style={{ position: "absolute", top: 1290, left: M, right: M, textAlign: "center", fontSize: 34, fontWeight: 400, color: SUB, ...reveal(frame, 40) }}>{scene.note}</div>}
      </>
    );
  }

  if (scene.type === "curve") {
    // CURVA / ÁREA: curva bezier suave que se dibuja. anim = motion premium-minimalista:
    //   comet (cometa+estela+anillo que pulsa) · spring (rebote+brillo que barre) · pulse (rejilla+ripples+respira).
    const CL = { extrapolateLeft: "clamp" as const, extrapolateRight: "clamp" as const };
    const cx0 = M, cx1 = 1080 - M, W = cx1 - cx0, cyBot = 1200, H = 510;
    const pts = scene.points, n = pts.length;
    const maxV = Math.max(...pts), minV = Math.min(...pts, 0), rng = maxV - minV || 1;
    const xy = pts.map((v, i) => [cx0 + (i / (n - 1)) * W, cyBot - ((v - minV) / rng) * H * 0.92] as [number, number]);
    const line = smoothPath(xy);
    const area = `${line} L ${cx1} ${cyBot} L ${cx0} ${cyBot} Z`;
    const col = scene.color === "accent" ? ACCENT : GREEN;
    const at = (t: number): [number, number] => { const fi = t * (n - 1), a = Math.floor(fi), b = Math.min(n - 1, a + 1), f = fi - a; return [xy[a][0] + (xy[b][0] - xy[a][0]) * f, xy[a][1] + (xy[b][1] - xy[a][1]) * f]; };
    const anim = scene.anim ?? "comet";
    if (anim === "hero") {
      const dE = 66;
      const ease = Easing.bezier(0.62, 0, 0.66, 0.25);   // arranca lento, DESPEGA al final (drama exponencial)
      const progAt = (f: number) => interpolate(f, [10, dE], [0, 1], { ...CL, easing: ease });
      const prog = progAt(frame);
      const clipW = cx0 + prog * W;
      const [dotX, dotY] = at(prog);
      const peak = xy[n - 1];
      const done = frame - dE;
      const endPop = spring({ frame: frame - (dE - 8), fps, config: { damping: 10, stiffness: 150 } });
      body = (
        <>
          {scene.kicker && <div style={{ position: "absolute", top: 300, left: M, fontSize: 30, fontWeight: 700, letterSpacing: "0.2em", color: col, ...reveal(frame, 4) }}>{scene.kicker}</div>}
          {scene.label && <div style={{ position: "absolute", top: 372, left: M, right: M, fontSize: 68, fontWeight: 800, lineHeight: 1.04, letterSpacing: "-0.02em", color: INK, ...reveal(frame, 6) }}>{scene.label}</div>}
          <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
            <defs>
              <linearGradient id="agrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor={col} stopOpacity="0.36" /><stop offset="1" stopColor={col} stopOpacity="0" /></linearGradient>
              <filter id="cglow" x="-70%" y="-70%" width="240%" height="240%"><feGaussianBlur stdDeviation="7" /></filter>
              <clipPath id="curveclip"><rect x="0" y="0" width={clipW} height="1920" /></clipPath>
            </defs>
            <line x1={cx0} y1={cyBot} x2={cx1} y2={cyBot} stroke={HAIR} strokeWidth={3} />
            <g clipPath="url(#curveclip)">
              <path d={area} fill="url(#agrad)" />
              <path d={line} fill="none" stroke={col} strokeWidth={22} strokeLinecap="round" opacity={0.32} filter="url(#cglow)" />
              <path d={line} fill="none" stroke={col} strokeWidth={7} strokeLinecap="round" strokeLinejoin="round" />
            </g>
            {Array.from({ length: 22 }).map((_, j) => {
              const fe = 12 + j * 2.2;
              if (frame < fe || fe > dE) return null;
              const age = frame - fe; if (age > 38) return null;
              const [ex, ey] = at(progAt(fe));
              const dx = (((j * 29) % 9) - 4) * 1.2;
              return <circle key={`t${j}`} cx={ex + dx * (age / 12)} cy={ey - age * 1.7} r={Math.max(0, 6.5 * (1 - age / 42))} fill={col} opacity={Math.max(0, 0.5 * (1 - age / 38))} />;
            })}
            {done > 0 && Array.from({ length: 16 }).map((_, b) => {
              const age = done; if (age > 26) return null;
              const ang = (b / 16) * 2 * Math.PI, dist = interpolate(age, [0, 26], [12, 155], CL);
              return <circle key={`b${b}`} cx={peak[0] + Math.cos(ang) * dist} cy={peak[1] + Math.sin(ang) * dist} r={Math.max(0, 7 * (1 - age / 26))} fill={col} opacity={Math.max(0, 1 - age / 26)} />;
            })}
            {done > 0 && [0, 22].map((off, k) => { const pf = (done + off) % 44; if (pf > 24) return null; return <circle key={`r${k}`} cx={peak[0]} cy={peak[1]} r={interpolate(pf, [0, 24], [16, 150], CL)} fill="none" stroke={col} strokeWidth={3} opacity={interpolate(pf, [0, 24], [0.5, 0], CL)} />; })}
            <circle cx={dotX} cy={dotY} r={46} fill={col} opacity={0.3} filter="url(#cglow)" />
            <circle cx={dotX} cy={dotY} r={16} fill={col} />
            <circle cx={dotX} cy={dotY} r={7} fill="#FFFFFF" />
          </svg>
          {scene.startLabel && <div style={{ position: "absolute", top: cyBot + 22, left: M, fontSize: 30, fontWeight: 600, color: MUTE, ...reveal(frame, 12) }}>{scene.startLabel}</div>}
          {scene.endLabel && <div style={{ position: "absolute", top: Math.max(560, peak[1] - 104), left: Math.min(cx1 - 300, peak[0] - 40), width: 360, fontSize: 52, fontWeight: 800, letterSpacing: "-0.02em", color: col, opacity: Math.min(1, endPop), transform: `scale(${Math.max(0, endPop)})`, transformOrigin: "left center" }}>{scene.endLabel}</div>}
          {scene.note && <div style={{ position: "absolute", top: cyBot + 90, left: M, right: M, fontSize: 34, fontWeight: 400, color: SUB, ...reveal(frame, dE + 6) }}>{scene.note}</div>}
        </>
      );
    } else {
    const dEnd = anim === "spring" ? 46 : 80;
    const prog = interpolate(frame, [12, dEnd], [0, 1], { ...CL, easing: Easing.inOut(Easing.cubic) });
    const clipW = cx0 + prog * W;
    const [dotX, dotY] = at(prog);
    const endIn = interpolate(prog, [0.85, 1], [0, 1], CL);
    const done = frame - dEnd;
    const sy = anim === "spring" ? Math.max(0.001, spring({ frame: frame - 12, fps, config: { damping: 9, stiffness: 120 } }))
      : anim === "pulse" && done > 4 ? 1 + Math.sin((frame - dEnd) / 15) * 0.014 : 1;
    const gm = `matrix(1,0,0,${sy.toFixed(4)},0,${(cyBot * (1 - sy)).toFixed(1)})`;
    const tipPulse = anim === "pulse" ? Math.sin(frame / 9) * 3 : 0;
    body = (
      <>
        {scene.kicker && <div style={{ position: "absolute", top: 300, left: M, fontSize: 30, fontWeight: 700, letterSpacing: "0.2em", color: col, ...reveal(frame, 4) }}>{scene.kicker}</div>}
        {scene.label && <div style={{ position: "absolute", top: 372, left: M, right: M, fontSize: 68, fontWeight: 800, lineHeight: 1.04, letterSpacing: "-0.02em", color: INK, ...reveal(frame, 6) }}>{scene.label}</div>}
        <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
          <defs>
            <linearGradient id="agrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor={col} stopOpacity="0.34" /><stop offset="1" stopColor={col} stopOpacity="0" /></linearGradient>
            <clipPath id="curveclip"><rect x="0" y="0" width={clipW} height="1920" /></clipPath>
          </defs>
          {anim === "pulse" && [0.66, 0.42, 0.16].map((g, k) => <line key={k} x1={cx0} y1={cyBot - H * g} x2={cx1} y2={cyBot - H * g} stroke={HAIR} strokeWidth={1.5} opacity={0.5 * interpolate(frame, [8 + k * 4, 22 + k * 4], [0, 1], CL)} />)}
          <line x1={cx0} y1={cyBot} x2={cx1} y2={cyBot} stroke={HAIR} strokeWidth={3} />
          <g transform={gm}>
            <g clipPath="url(#curveclip)">
              <path d={area} fill="url(#agrad)" />
              <path d={line} fill="none" stroke={col} strokeWidth={7} strokeLinecap="round" strokeLinejoin="round" />
            </g>
            {anim === "spring" && done > 0 && (
              <path d={line} pathLength={1} fill="none" stroke="#FFFFFF" strokeWidth={7} strokeLinecap="round" strokeDasharray="0.05 0.95" strokeDashoffset={1 - interpolate(frame, [dEnd, dEnd + 26], [0, 1], CL)} opacity={interpolate(frame, [dEnd, dEnd + 4, dEnd + 26], [0, 0.85, 0], CL)} />
            )}
          </g>
          {anim === "comet" && prog > 0.03 && prog < 0.999 && [1, 2, 3, 4, 5, 6].map((k) => { const [gx, gy] = at(Math.max(0, prog - k * 0.022)); return <circle key={k} cx={gx} cy={gy} r={13 - k * 1.5} fill={col} opacity={0.3 * (1 - k / 7)} />; })}
          {anim === "pulse" && xy.map(([px, py], i) => { const a = frame - (12 + (i / (n - 1)) * (dEnd - 12)); if (a < 0 || a > 18) return null; return <circle key={i} cx={px} cy={py} r={interpolate(a, [0, 18], [3, 30], CL)} fill="none" stroke={col} strokeWidth={2.5} opacity={interpolate(a, [0, 18], [0.6, 0], CL)} />; })}
          {anim === "pulse" && prog > 0.99 && xy.map(([px, py], i) => <circle key={`d${i}`} cx={px} cy={py} r={6} fill={col} opacity={0.9} />)}
          {anim === "comet" && done > 0 && (() => { const pf = done % 40; if (pf > 22) return null; const [ex, ey] = xy[n - 1]; return <circle cx={ex} cy={ey} r={interpolate(pf, [0, 22], [16, 130], CL)} fill="none" stroke={col} strokeWidth={3} opacity={interpolate(pf, [0, 22], [0.5, 0], CL)} />; })()}
          <circle cx={dotX} cy={dotY} r={(anim === "comet" ? 42 : 30) + tipPulse} fill={col} opacity={anim === "comet" ? 0.2 : 0.22} />
          <circle cx={dotX} cy={dotY} r={15} fill={col} />
          <circle cx={dotX} cy={dotY} r={15} fill="none" stroke={PAPER} strokeWidth={4} />
        </svg>
        {scene.startLabel && <div style={{ position: "absolute", top: cyBot + 22, left: M, fontSize: 30, fontWeight: 600, color: MUTE, ...reveal(frame, 12) }}>{scene.startLabel}</div>}
        {scene.endLabel && <div style={{ position: "absolute", top: Math.max(600, dotY - 96), left: Math.min(cx1 - 260, dotX - 60), width: 320, fontSize: 46, fontWeight: 800, letterSpacing: "-0.02em", color: col, opacity: endIn, transform: `scale(${0.8 + 0.2 * endIn})`, transformOrigin: "left center" }}>{scene.endLabel}</div>}
        {scene.note && <div style={{ position: "absolute", top: cyBot + 90, left: M, right: M, fontSize: 34, fontWeight: 400, color: SUB, ...reveal(frame, 80) }}>{scene.note}</div>}
      </>
    );
    }
  }

  if (scene.type === "donut") {
    // DONA / ANILLO: cada sector se dibuja en arco (barrido) en secuencia. Redondo, no cuadrado. $0.
    const cx = 540, cy = 838, R = 276, SW = 70;
    const C = 2 * Math.PI * R;
    const colOf = (c?: string) => (c === "green" ? GREEN : c === "ink" ? INK : c === "mute" ? MUTE : ACCENT);
    let accP = 0;
    const segs = scene.segments.map((s, i) => { const start = accP; accP += s.pct; return { ...s, start, i }; });
    body = (
      <>
        {scene.kicker && <div style={{ position: "absolute", top: 300, left: M, fontSize: 30, fontWeight: 700, letterSpacing: "0.2em", color: ACCENT, ...reveal(frame, 4) }}>{scene.kicker}</div>}
        {scene.label && <div style={{ position: "absolute", top: 372, left: M, right: M, fontSize: 64, fontWeight: 800, lineHeight: 1.05, letterSpacing: "-0.02em", color: INK, ...reveal(frame, 6) }}>{scene.label}</div>}
        <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
          <circle cx={cx} cy={cy} r={R} fill="none" stroke={HAIR} strokeWidth={SW} />
          {segs.map((s) => {
            const appear = 16 + s.i * 13;
            const grow = interpolate(frame, [appear, appear + 22], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
            const len = (s.pct / 100) * C;
            return <circle key={s.i} cx={cx} cy={cy} r={R} fill="none" stroke={colOf(s.color)} strokeWidth={SW} strokeDasharray={`${Math.max(0, len * grow - 7)} ${C}`} transform={`rotate(${-90 + (s.start / 100) * 360} ${cx} ${cy})`} />;
          })}
        </svg>
        <div style={{ position: "absolute", top: cy - 96, left: 0, width: 1080, textAlign: "center" }}>
          {scene.centerBig && <div style={{ fontSize: 138, fontWeight: 800, letterSpacing: "-0.04em", lineHeight: 1, color: INK }}>{scene.centerBig}</div>}
          {scene.centerSub && <div style={{ fontSize: 30, fontWeight: 700, letterSpacing: "0.14em", color: MUTE, marginTop: 8 }}>{scene.centerSub}</div>}
        </div>
        <div style={{ position: "absolute", top: 1244, left: M, right: M, display: "flex", justifyContent: "center", flexWrap: "wrap", gap: 40 }}>
          {segs.map((s) => (
            <div key={`lg${s.i}`} style={{ display: "flex", alignItems: "center", gap: 14, ...reveal(frame, 16 + s.i * 13 + 12) }}>
              <div style={{ width: 26, height: 26, borderRadius: "50%", background: colOf(s.color) }} />
              <div style={{ fontSize: 34, fontWeight: 600, color: INK }}>{s.tag} <span style={{ color: colOf(s.color), fontWeight: 800 }}>{s.pct}%</span></div>
            </div>
          ))}
        </div>
        {scene.note && <div style={{ position: "absolute", top: 1360, left: M, right: M, textAlign: "center", fontSize: 32, fontWeight: 400, color: SUB, ...reveal(frame, 40) }}>{scene.note}</div>}
      </>
    );
  }

  if (scene.type === "timeline") {
    // LÍNEA DE TIEMPO: la línea se dibuja hacia abajo y los eventos aparecen en secuencia. $0.
    const evs = scene.events;
    const N = evs.length;
    const lineX = M + 26, lineTop = 480, lineBottom = 1380, lineH = lineBottom - lineTop;
    const slotH = lineH / N;
    const eventY = (i: number) => lineTop + slotH * i + slotH * 0.4;
    const drawnBottom = interpolate(frame, [12, 12 + N * 16], [lineTop, lineBottom], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.cubic) });
    body = (
      <>
        {scene.kicker && <div style={{ position: "absolute", top: 300, left: M, fontSize: 30, fontWeight: 700, letterSpacing: "0.2em", color: ACCENT, ...reveal(frame, 4) }}>{scene.kicker}</div>}
        {scene.label && <div style={{ position: "absolute", top: 372, left: M, right: M, fontSize: 68, fontWeight: 800, lineHeight: 1.04, letterSpacing: "-0.02em", color: INK, ...reveal(frame, 6) }}>{scene.label}</div>}
        <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
          <line x1={lineX} y1={lineTop} x2={lineX} y2={lineBottom} stroke={HAIR} strokeWidth={4} />
          <line x1={lineX} y1={lineTop} x2={lineX} y2={drawnBottom} stroke={INK} strokeWidth={4} />
        </svg>
        {evs.map((e, i) => {
          const y = eventY(i);
          const s = Math.min(1, spring({ frame: frame - (12 + i * 16), fps, config: { damping: 13, stiffness: 150 } }));
          const col = e.accent ? ACCENT : INK;
          return (
            <React.Fragment key={i}>
              <div style={{ position: "absolute", left: lineX - 13, top: y - 13, width: 26, height: 26, borderRadius: "50%", background: col, transform: `scale(${s})`, boxShadow: `0 0 0 6px ${PAPER}` }} />
              <div style={{ position: "absolute", left: lineX + 46, top: y - 52, right: M, opacity: s, transform: `translateX(${(1 - s) * 22}px)` }}>
                <div style={{ fontSize: 46, fontWeight: 800, letterSpacing: "0.02em", color: col }}>{e.year}</div>
                <div style={{ fontSize: 35, fontWeight: 400, lineHeight: 1.25, color: SUB, marginTop: 4 }}>{e.text}</div>
              </div>
            </React.Fragment>
          );
        })}
        {scene.note && <div style={{ position: "absolute", top: 1430, left: M, right: M, fontSize: 32, fontWeight: 400, color: SUB, ...reveal(frame, 12 + N * 16) }}>{scene.note}</div>}
      </>
    );
  }

  if (scene.type === "proportion") {
    // PROPORCIÓN: barra 100% segmentada; cada segmento crece desde su borde en secuencia. $0.
    const barL = M, barW = 1080 - 2 * M, barY = 800, barH = 156;
    const colOf = (c?: string) => (c === "green" ? GREEN : c === "ink" ? INK : c === "mute" ? MUTE : ACCENT);
    let accP = 0;
    const segs = scene.segments.map((s, i) => { const start = accP; accP += s.pct; return { ...s, start, i }; });
    body = (
      <>
        {scene.kicker && <div style={{ position: "absolute", top: 300, left: M, fontSize: 30, fontWeight: 700, letterSpacing: "0.2em", color: ACCENT, ...reveal(frame, 4) }}>{scene.kicker}</div>}
        {scene.label && <div style={{ position: "absolute", top: 380, left: M, right: M, fontSize: 80, fontWeight: 800, lineHeight: 1.04, letterSpacing: "-0.02em", color: INK, ...reveal(frame, 6) }}>{scene.label}</div>}
        {segs.map((s) => {
          const x = barL + (s.start / 100) * barW;
          const wFull = (s.pct / 100) * barW;
          const appear = 16 + s.i * 11;
          const grow = interpolate(frame, [appear, appear + 18], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
          return <div key={s.i} style={{ position: "absolute", left: x, top: barY, width: Math.max(0, wFull * grow - 4), height: barH, background: colOf(s.color), borderRadius: 4 }} />;
        })}
        {segs.map((s) => {
          const cx = barL + ((s.start + s.pct / 2) / 100) * barW;
          return (
            <div key={`l${s.i}`} style={{ position: "absolute", top: barY + barH + 26, left: cx - 130, width: 260, textAlign: "center", ...reveal(frame, 16 + s.i * 11 + 10) }}>
              <div style={{ fontSize: 64, fontWeight: 800, letterSpacing: "-0.02em", color: colOf(s.color) }}>{s.pct}%</div>
              <div style={{ fontSize: 30, fontWeight: 500, color: SUB, marginTop: 4 }}>{s.tag}</div>
            </div>
          );
        })}
        {scene.note && <div style={{ position: "absolute", top: 1290, left: M, right: M, fontSize: 34, fontWeight: 400, color: SUB, ...reveal(frame, 44) }}>{scene.note}</div>}
      </>
    );
  }

  if (scene.type === "level") {
    // METÁFORA FÍSICA: un recipiente que se llena hasta un nivel, con superficie líquida ondulante. $0.
    const vw = 340, vh = 720, vx = (1080 - vw) / 2, vy = 500;
    const col = scene.color === "accent" ? ACCENT : GREEN;
    const prog = Math.min(1, spring({ frame: frame - 14, fps, config: { damping: 15, stiffness: 90 } }));
    const pct = scene.fillPct * prog;
    const filledH = (pct / 100) * vh;
    const surfaceY = vy + vh - filledH;
    const amp = 9, ph = frame / 8;
    const wave = `M ${vx} ${surfaceY.toFixed(1)} ` +
      Array.from({ length: 21 }).map((_, k) => { const x = vx + (k / 20) * vw; const y = surfaceY + Math.sin(ph + k * 0.6) * amp; return `L ${x.toFixed(1)} ${y.toFixed(1)}`; }).join(" ") +
      ` L ${vx + vw} ${vy + vh} L ${vx} ${vy + vh} Z`;
    const onFill = surfaceY < vy + vh / 2 - 30;
    body = (
      <>
        {scene.kicker && <div style={{ position: "absolute", top: 300, left: M, fontSize: 30, fontWeight: 700, letterSpacing: "0.2em", color: col, ...reveal(frame, 4) }}>{scene.kicker}</div>}
        {scene.label && <div style={{ position: "absolute", top: 372, left: M, right: M, fontSize: 60, fontWeight: 800, lineHeight: 1.05, letterSpacing: "-0.02em", color: INK, ...reveal(frame, 6) }}>{scene.label}</div>}
        <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
          <clipPath id="vclip"><rect x={vx} y={vy} width={vw} height={vh} rx={26} /></clipPath>
          <g clipPath="url(#vclip)">
            <rect x={vx} y={vy} width={vw} height={vh} fill={EMPTY} />
            <path d={wave} fill={col} />
          </g>
          <rect x={vx} y={vy} width={vw} height={vh} rx={26} fill="none" stroke={INK} strokeWidth={3} />
        </svg>
        <div style={{ position: "absolute", top: vy + vh / 2 - 90, left: 0, width: 1080, textAlign: "center" }}>
          <span style={{ fontSize: 150, fontWeight: 800, letterSpacing: "-0.04em", color: onFill ? PAPER : INK }}>{Math.round(pct)}{scene.bigSuffix ?? "%"}</span>
        </div>
        {scene.note && <div style={{ position: "absolute", top: vy + vh + 40, left: M, right: M, textAlign: "center", fontSize: 34, fontWeight: 400, color: SUB, ...reveal(frame, 30) }}>{scene.note}</div>}
      </>
    );
  }

  if (scene.type === "mapzoom") {
    body = (
      <>
        <MapZoomEditorial countryName={scene.countryName} iso2={scene.iso2} label={scene.label} region={scene.region} />
        {scene.kicker && <div style={{ position: "absolute", top: 210, left: M, fontSize: 30, fontWeight: 700, letterSpacing: "0.2em", color: ACCENT, ...reveal(frame, 6) }}>{scene.kicker}</div>}
      </>
    );
  }

  return <AbsoluteFill style={{ opacity: inO * outO }}>{body}</AbsoluteFill>;
};

export const EditorialReel: React.FC<{
  edition: string;
  source: string;
  scenes: { scene: Scene; durF: number }[];
  theme?: "light" | "dark";
}> = ({ edition, source, scenes, theme }) => {
  applyTheme(theme === "dark");           // fija la paleta ANTES de que rendericen las escenas
  const gf = useCurrentFrame();
  let acc = 0;
  const starts = scenes.map((s) => { const st = acc; acc += s.durF; return st; });

  // MOVIMIENTO CONSTANTE (principio 0x100x: nada 100% quieto): deriva + respiración
  // lentas y continuas SOLO en el contenido (el marco masthead/fuente queda fijo).
  const dx = Math.sin(gf / 34) * 7;
  const dy = Math.cos(gf / 41) * 6;
  const sc = 1 + Math.sin(gf / 49) * 0.006;

  return (
    <AbsoluteFill style={{ backgroundColor: PAPER, fontFamily: FONT, color: INK }}>
      {/* FONDO con luz volumétrica (energía de reel, no plano de presentación) */}
      {DARK ? (
        <>
          <div style={{ position: "absolute", left: 540 - 560 + Math.sin(gf / 44) * 16, top: 300, width: 1120, height: 1120, borderRadius: "50%", background: "radial-gradient(circle, #34507E4D 0%, #34507E14 42%, transparent 68%)" }} />
          <div style={{ position: "absolute", left: 540 - 400 - Math.sin(gf / 52) * 14, top: 1180, width: 800, height: 800, borderRadius: "50%", background: "radial-gradient(circle, #C9772E3A 0%, transparent 62%)" }} />
        </>
      ) : (
        <div style={{ position: "absolute", left: 540 - 520 + Math.sin(gf / 44) * 12, top: 560, width: 1040, height: 1040, borderRadius: "50%", background: `radial-gradient(circle, ${ACCENT}14 0%, ${ACCENT}07 44%, transparent 68%)` }} />
      )}
      {/* escenas (con deriva constante) */}
      <AbsoluteFill style={{ transform: `translate(${dx}px, ${dy}px) scale(${sc})`, transformOrigin: "50% 46%" }}>
        {scenes.map((s, i) => (
          <Sequence key={i} from={starts[i]} durationInFrames={s.durF}>
            <SceneView scene={s.scene} durF={s.durF} inFade={i > 0} />
          </Sequence>
        ))}
      </AbsoluteFill>

      {/* marco editorial ENCIMA de las escenas (header/footer del informe, siempre visible) */}
      <div style={{ position: "absolute", top: 78, left: M, fontSize: 27, fontWeight: 700, letterSpacing: "0.28em" }}>DINERO&nbsp;IA</div>
      <div style={{ position: "absolute", top: 82, right: M, fontSize: 22, fontWeight: 500, letterSpacing: "0.22em", color: MUTE }}>{edition}</div>
      <div style={{ position: "absolute", top: 130, left: M, width: 1080 - 2 * M, height: 2, background: INK }} />
      <div style={{ position: "absolute", top: 1548, left: M, width: 1080 - 2 * M, height: 1, background: HAIR }} />
      <div style={{ position: "absolute", top: 1574, left: M, width: 1080 - 2 * M - 90, fontSize: 23, fontWeight: 500, letterSpacing: "0.03em", color: MUTE, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{source}</div>
      {/* folio fijo (parte del marco, no deriva) */}
      {scenes.map((s, i) => (
        <Sequence key={`f${i}`} from={starts[i]} durationInFrames={s.durF}>
          <div style={{ position: "absolute", top: 1574, right: M, fontSize: 23, fontWeight: 700, letterSpacing: "0.18em", color: INK }}>
            {String(i + 1).padStart(2, "0")}
          </div>
        </Sequence>
      ))}

      {/* grano (screen en oscuro, multiply en claro) */}
      <AbsoluteFill style={{ opacity: DARK ? 0.07 : 0.05, mixBlendMode: DARK ? "screen" : "multiply", pointerEvents: "none" }}>
        <svg width="1080" height="1920"><filter id="pr"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" stitchTiles="stitch" /></filter><rect width="1080" height="1920" filter="url(#pr)" /></svg>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
