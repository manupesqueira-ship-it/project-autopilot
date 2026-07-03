import React from "react";
import { AbsoluteFill, Easing, Img, interpolate, OffthreadVideo, Sequence, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { MapZoomEditorial } from "./MapZoomEditorial";

// EditorialReel — motor de REEL COMPLETO en el estilo de la casa "Editorial"
// (aprobado por Manuel 2026-07-01). Marco persistente (masthead + fuente + folio)
// + escenas que se revelan con la gramática editorial. Un reel = UNA composición.
// Datos exactos; color semántico (oxblood = pérdida/acento). Timing por escena =
// duración de la voz (se pasa en props desde el timing de ElevenLabs).

const INK = "#1B1712";
const PAPER = "#F1ECE1";
const ACCENT = "#9E2B22";
const GREEN = "#1F7A4D"; // ganancia real (verde editorial apagado, no neón)
const MUTE = "#7A7264";
const HAIR = "#CDC4B2";
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
  | { type: "timeline"; kicker?: string; label?: string; events: { year: string; text: string; accent?: boolean }[]; note?: string };

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
          <div style={{ position: "absolute", top: 1120, left: M, right: M, fontSize: 38, fontWeight: 400, lineHeight: 1.4, color: "#4A443B", maxWidth: 860, ...reveal(frame, 16 + scene.lines.length * 8 + 6) }}>
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
          <div style={{ position: "absolute", top: 930, left: M, right: M, fontSize: 40, fontWeight: 400, color: "#4A443B", maxWidth: 860, ...reveal(frame, 40) }}>{scene.sublabel}</div>
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
        {scene.note && <div style={{ position: "absolute", top: 1290, left: M, right: M, fontSize: 33, fontWeight: 400, lineHeight: 1.4, color: "#4A443B", maxWidth: 840, ...reveal(frame, 90) }}>{scene.note}</div>}
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
        {scene.note && <div style={{ position: "absolute", top: 1360, left: M, right: M, fontSize: 33, fontWeight: 400, lineHeight: 1.4, color: "#4A443B", maxWidth: 840, ...reveal(frame, 70) }}>{scene.note}</div>}
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
        {scene.body && <div style={{ position: "absolute", top: 1050, left: M, right: M, fontSize: 38, fontWeight: 400, lineHeight: 1.42, color: "#4A443B", maxWidth: 860, ...reveal(frame, 58) }}>{scene.body}</div>}
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
        {scene.sub && <div style={{ position: "absolute", top: 900, left: M, right: M, fontSize: 40, fontWeight: 400, lineHeight: 1.4, color: "#4A443B", maxWidth: 860, ...reveal(frame, 8 + scene.headline.length * 8 + 6) }}>{scene.sub}</div>}
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
        {scene.note && <div style={{ position: "absolute", top: 1420, left: M, right: M, fontSize: 36, fontWeight: 400, lineHeight: 1.4, color: "#4A443B", maxWidth: 860, ...reveal(frame, 30) }}>{scene.note}</div>}
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
          {scene.punch && <div style={{ marginTop: 16, fontSize: 32, fontWeight: 400, color: "#5A544A", ...reveal(frame, 30) }}>{scene.punch}</div>}
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
        {scene.label && <div style={{ position: "absolute", top: 600, left: M, right: M, fontSize: 40, fontWeight: 500, color: "#4A443B", ...reveal(frame, 10) }}>{scene.label}</div>}
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
        {scene.note && <div style={{ position: "absolute", top: gridTop + rows * (DOT + GAP) + 34, left: M, right: M, fontSize: 34, fontWeight: 400, color: "#5A544A", ...reveal(frame, t0 + scene.highlight * perDot) }}>{scene.note}</div>}
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
                <div style={{ fontSize: 35, fontWeight: 400, lineHeight: 1.25, color: "#3B372F", marginTop: 4 }}>{e.text}</div>
              </div>
            </React.Fragment>
          );
        })}
        {scene.note && <div style={{ position: "absolute", top: 1430, left: M, right: M, fontSize: 32, fontWeight: 400, color: "#5A544A", ...reveal(frame, 12 + N * 16) }}>{scene.note}</div>}
      </>
    );
  }

  if (scene.type === "proportion") {
    // PROPORCIÓN: barra 100% segmentada; cada segmento crece desde su borde en secuencia. $0.
    const barL = M, barW = 1080 - 2 * M, barY = 800, barH = 156;
    const colOf = (c?: string) => (c === "green" ? GREEN : c === "ink" ? INK : c === "mute" ? "#B8AE9B" : ACCENT);
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
              <div style={{ fontSize: 30, fontWeight: 500, color: "#5A544A", marginTop: 4 }}>{s.tag}</div>
            </div>
          );
        })}
        {scene.note && <div style={{ position: "absolute", top: 1290, left: M, right: M, fontSize: 34, fontWeight: 400, color: "#5A544A", ...reveal(frame, 44) }}>{scene.note}</div>}
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
            <rect x={vx} y={vy} width={vw} height={vh} fill="#E6DFD0" />
            <path d={wave} fill={col} />
          </g>
          <rect x={vx} y={vy} width={vw} height={vh} rx={26} fill="none" stroke={INK} strokeWidth={3} />
        </svg>
        <div style={{ position: "absolute", top: vy + vh / 2 - 90, left: 0, width: 1080, textAlign: "center" }}>
          <span style={{ fontSize: 150, fontWeight: 800, letterSpacing: "-0.04em", color: onFill ? PAPER : INK }}>{Math.round(pct)}{scene.bigSuffix ?? "%"}</span>
        </div>
        {scene.note && <div style={{ position: "absolute", top: vy + vh + 40, left: M, right: M, textAlign: "center", fontSize: 34, fontWeight: 400, color: "#5A544A", ...reveal(frame, 30) }}>{scene.note}</div>}
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
}> = ({ edition, source, scenes }) => {
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

      {/* textura papel */}
      <AbsoluteFill style={{ opacity: 0.05, mixBlendMode: "multiply", pointerEvents: "none" }}>
        <svg width="1080" height="1920"><filter id="pr"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" stitchTiles="stitch" /></filter><rect width="1080" height="1920" filter="url(#pr)" /></svg>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
