import React from "react";
import { useCurrentFrame } from "remotion";

// ============================================================================
// winter.tsx — primitivos del lenguaje "invierno cripto / brasa" (concepto v2
// El Salvador). UNA fuente de verdad: hielo, escarcha, brasa (₿), columnas que
// transmutan de hielo a oro, y añicos. Se componen DENTRO de IglooStage (negro
// mate, luz volumetrica fria, vineta, grano) para que TODO sea un solo mundo.
// Color: azul-hielo = invierno/duda (ambiente) · rojo = SOLO precio cayendo ·
// oro = Bitcoin (la brasa) · esmeralda = recuperacion/victoria.
// ============================================================================

export const WINTER = {
  ice: "#6FB7D8", // azul-hielo brillante (acento frio)
  iceMid: "#3E7E9E",
  iceDeep: "#16344A", // azul congelado profundo
  icePale: "#CFEAF4", // rime / escarcha clara
  frost: "#E6F3F8",
  gold: "#D4A574", // Bitcoin / brasa
  goldHot: "#FFE3B0",
  goldDeep: "#5E3A12",
  green: "#00D9A5",
  greenHot: "#9BFFE6",
  greenDeep: "#00684F",
  red: "#FF6B6B",
  redPale: "#FFD9D9",
};

// PRNG determinista (mulberry32) — añicos/escarcha estables frame a frame.
export function rng(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// Defs compartidos — incluir UNA vez por <svg> antes de usar los primitivos.
export const WinterDefs: React.FC = () => (
  <defs>
    <linearGradient id="w-ice" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stopColor={WINTER.icePale} stopOpacity="0.9" />
      <stop offset="34%" stopColor={WINTER.ice} stopOpacity="0.5" />
      <stop offset="100%" stopColor={WINTER.iceDeep} stopOpacity="0.7" />
    </linearGradient>
    <linearGradient id="w-gold" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stopColor={WINTER.goldHot} />
      <stop offset="46%" stopColor={WINTER.gold} />
      <stop offset="100%" stopColor={WINTER.goldDeep} />
    </linearGradient>
    <linearGradient id="w-emerald" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stopColor={WINTER.greenHot} />
      <stop offset="55%" stopColor={WINTER.green} />
      <stop offset="100%" stopColor={WINTER.greenDeep} />
    </linearGradient>
    <linearGradient id="w-redbleed" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stopColor={WINTER.red} stopOpacity="0" />
      <stop offset="60%" stopColor={WINTER.red} stopOpacity="0.5" />
      <stop offset="100%" stopColor={WINTER.red} stopOpacity="0.92" />
    </linearGradient>
    <linearGradient id="w-sheen" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stopColor="#FFFFFF" stopOpacity="0" />
      <stop offset="50%" stopColor="#FFFFFF" stopOpacity="0.5" />
      <stop offset="100%" stopColor="#FFFFFF" stopOpacity="0" />
    </linearGradient>
    <radialGradient id="w-ember" cx="50%" cy="44%" r="60%">
      <stop offset="0%" stopColor="#FFFFFF" />
      <stop offset="24%" stopColor={WINTER.goldHot} />
      <stop offset="62%" stopColor={WINTER.gold} />
      <stop offset="100%" stopColor={WINTER.goldDeep} stopOpacity="0" />
    </radialGradient>
    <filter id="w-blur-sm" x="-80%" y="-80%" width="260%" height="260%">
      <feGaussianBlur stdDeviation="6" />
    </filter>
    <filter id="w-blur-lg" x="-160%" y="-160%" width="420%" height="420%">
      <feGaussianBlur stdDeviation="26" />
    </filter>
  </defs>
);

// Ember — la brasa ₿: halo calido + nucleo blanco-caliente + glifo ₿ grabado.
// Es lo UNICO calido del cuadro frio; respira (no congelada).
export const Ember: React.FC<{
  cx: number;
  cy: number;
  r?: number;
  phase?: number;
  intensity?: number; // 0..1
}> = ({ cx, cy, r = 58, phase = 0, intensity = 1 }) => {
  const frame = useCurrentFrame();
  const breath = 0.84 + 0.16 * Math.sin(frame / 15 + phase);
  const k = breath * intensity;
  return (
    <g>
      <circle
        cx={cx}
        cy={cy}
        r={r * 2.6 * k}
        fill="url(#w-ember)"
        opacity={0.55 * intensity}
        style={{ filter: "url(#w-blur-lg)", mixBlendMode: "screen" }}
      />
      <circle cx={cx} cy={cy} r={r * k} fill="url(#w-ember)" />
      <text
        x={cx}
        y={cy + r * 0.36}
        textAnchor="middle"
        fontFamily="InterVar, Inter, Helvetica, Arial, sans-serif"
        fontWeight={800}
        fontSize={r * 1.18}
        fill="#3A2208"
        opacity={0.9 * intensity}
        style={{ filter: "drop-shadow(0 0 9px #FFE3B0)" }}
      >
        ₿
      </text>
    </g>
  );
};

// rimePath — cristales de escarcha a lo largo de un borde vertical (mas densos y
// grandes arriba, donde "congela" primero). Devuelve triangulitos.
function frostCrystals(
  xEdge: number,
  yTop: number,
  yBot: number,
  dir: 1 | -1,
  seed: number
): { d: string; o: number }[] {
  const r = rng(seed);
  const steps = 16;
  const out: { d: string; o: number }[] = [];
  for (let i = 0; i <= steps; i++) {
    const top = i / steps; // 0 arriba .. 1 abajo
    const y = yTop + (yBot - yTop) * top;
    const size = (1 - top * 0.7) * (8 + r() * 14);
    const out_x = xEdge + dir * size;
    const h = size * (0.5 + r() * 0.7);
    out.push({
      d: `M${xEdge},${y - h} L${out_x},${y} L${xEdge},${y + h} Z`,
      o: 0.5 + (1 - top) * 0.5,
    });
  }
  return out;
}

// IceColumn — columna volumetrica del precio/valor. variant "ice" = helada azul
// con rime y grietas; "gold" = oro-esmeralda con brasas subiendo (recuperacion).
export const IceColumn: React.FC<{
  x: number;
  w: number;
  yTop: number;
  yBot: number;
  variant: "ice" | "gold";
  seed?: number;
  shedIce?: boolean; // chunks de hielo desprendiendose (transmutacion)
}> = ({ x, w, yTop, yBot, variant, seed = 3, shedIce = false }) => {
  const r = rng(seed * 13 + 1);
  const isGold = variant === "gold";
  const cx = x + w / 2;
  const cap = 22;

  // grietas internas (pocas, finas)
  const cracks: string[] = [];
  for (let i = 0; i < 3; i++) {
    let px = x + w * (0.25 + r() * 0.5);
    let py = yTop + 40;
    let d = `M${px},${py}`;
    const segs = 4 + Math.floor(r() * 3);
    for (let s = 0; s < segs; s++) {
      px += (r() - 0.5) * w * 0.5;
      py += (yBot - yTop) / segs;
      d += ` L${px.toFixed(1)},${py.toFixed(1)}`;
    }
    cracks.push(d);
  }

  const leftFrost = frostCrystals(x, yTop, yBot, -1, seed + 2);
  const rightFrost = frostCrystals(x + w, yTop, yBot, 1, seed + 9);

  return (
    <g>
      {/* halo trasero */}
      <rect
        x={x - 30}
        y={yTop - 30}
        width={w + 60}
        height={yBot - yTop + 60}
        rx={40}
        fill={isGold ? WINTER.gold : WINTER.ice}
        opacity={isGold ? 0.34 : 0.22}
        style={{ filter: "url(#w-blur-lg)" }}
      />
      {/* base glow (esmeralda si oro = victoria; frio si hielo) */}
      <ellipse
        cx={cx}
        cy={yBot + 6}
        rx={w * 0.95}
        ry={46}
        fill={isGold ? WINTER.green : WINTER.iceMid}
        opacity={isGold ? 0.5 : 0.3}
        style={{ filter: "url(#w-blur-lg)" }}
      />
      {/* cuerpo */}
      <rect
        x={x}
        y={yTop}
        width={w}
        height={yBot - yTop}
        rx={cap}
        fill={isGold ? "url(#w-gold)" : "url(#w-ice)"}
        stroke={isGold ? WINTER.goldHot : WINTER.icePale}
        strokeWidth={2}
        strokeOpacity={0.6}
      />
      {/* sheen vertical interno */}
      <rect
        x={x + w * 0.16}
        y={yTop + 6}
        width={w * 0.2}
        height={yBot - yTop - 12}
        rx={10}
        fill="url(#w-sheen)"
        opacity={0.5}
      />
      {/* grietas */}
      {cracks.map((d, i) => (
        <path
          key={i}
          d={d}
          fill="none"
          stroke={isGold ? WINTER.goldHot : WINTER.frost}
          strokeWidth={1.6}
          opacity={isGold ? 0.5 : 0.7}
          style={{
            filter: isGold
              ? "drop-shadow(0 0 6px #FFE3B0)"
              : "drop-shadow(0 0 5px #CFEAF4)",
          }}
        />
      ))}
      {/* top cap brillante */}
      <rect
        x={x + 4}
        y={yTop - 2}
        width={w - 8}
        height={14}
        rx={7}
        fill={isGold ? WINTER.goldHot : WINTER.frost}
        opacity={0.85}
        style={{
          filter: isGold
            ? "drop-shadow(0 -4px 16px #FFE3B0)"
            : "drop-shadow(0 -3px 14px #CFEAF4)",
        }}
      />

      {/* rime de escarcha (solo hielo) o brasas subiendo (oro) */}
      {!isGold &&
        [...leftFrost, ...rightFrost].map((c, i) => (
          <path key={i} d={c.d} fill={WINTER.icePale} opacity={c.o * 0.85} />
        ))}

      {isGold &&
        Array.from({ length: 9 }).map((_, i) => {
          const ex = x + w * (0.15 + r() * 0.7);
          const ey = yBot - (yBot - yTop) * r();
          const er = 3 + r() * 6;
          return (
            <circle
              key={i}
              cx={ex}
              cy={ey}
              r={er}
              fill={WINTER.goldHot}
              opacity={0.7}
              style={{ filter: "url(#w-blur-sm)" }}
            />
          );
        })}

      {/* hielo desprendiendose (transmutacion ice->gold) */}
      {shedIce &&
        Array.from({ length: 6 }).map((_, i) => {
          const side = i % 2 === 0 ? -1 : 1;
          const sx = (side < 0 ? x : x + w) + side * (10 + r() * 36);
          const sy = yTop + (yBot - yTop) * (0.1 + r() * 0.55);
          const s = 14 + r() * 22;
          const rot = (r() - 0.5) * 60;
          return (
            <g key={i} transform={`translate(${sx},${sy}) rotate(${rot})`}>
              <polygon
                points={`0,${-s} ${s * 0.7},0 ${s * 0.2},${s} ${-s * 0.5},${s * 0.4}`}
                fill="url(#w-ice)"
                stroke={WINTER.icePale}
                strokeWidth={1.4}
                strokeOpacity={0.7}
                opacity={0.85}
              />
            </g>
          );
        })}
    </g>
  );
};

// IceShards — añicos radiando desde un centro (el hielo que se rompe). t 0..1 =
// distancia recorrida + desvanecimiento. Para still: t ~0.55 (anicos en vuelo).
export const IceShards: React.FC<{
  cx: number;
  cy: number;
  count?: number;
  spread: number;
  t?: number;
  seed?: number;
}> = ({ cx, cy, count = 22, spread, t = 0.55, seed = 5 }) => {
  const r = rng(seed * 17 + 3);
  return (
    <g>
      {Array.from({ length: count }).map((_, i) => {
        const ang = (i / count) * Math.PI * 2 + (r() - 0.5) * 0.5;
        const dist = spread * t * (0.4 + r() * 0.6);
        const px = cx + Math.cos(ang) * dist;
        const py = cy + Math.sin(ang) * dist * 0.92;
        const s = (10 + r() * 26) * (1.1 - t * 0.4);
        const rot = (r() * 360).toFixed(0);
        const op = Math.max(0, (1 - t) * 0.9 + 0.1);
        return (
          <g key={i} transform={`translate(${px},${py}) rotate(${rot})`} opacity={op}>
            <polygon
              points={`0,${-s} ${s * 0.62},${s * 0.2} ${-s * 0.3},${s * 0.9} ${-s * 0.7},${-s * 0.1}`}
              fill="url(#w-ice)"
              stroke={WINTER.frost}
              strokeWidth={1.4}
              strokeOpacity={0.8}
            />
          </g>
        );
      })}
    </g>
  );
};

// FrostEdges — capa HTML: escarcha que invade desde los bordes (el frio
// cerrando el cuadro). amount 0..1. Va sobre el contenido, bajo la vineta.
export const FrostEdges: React.FC<{ amount?: number }> = ({ amount = 0.6 }) => (
  <div
    style={{
      position: "absolute",
      inset: 0,
      pointerEvents: "none",
      background: `radial-gradient(120% 90% at 50% 46%, transparent ${58 - amount * 26}%, rgba(111,183,216,${0.16 * amount}) ${88 - amount * 10}%, rgba(22,52,74,${0.42 * amount}) 100%)`,
      mixBlendMode: "screen",
    }}
  />
);
