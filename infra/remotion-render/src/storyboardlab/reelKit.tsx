import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { theme } from "../theme";

// ── reelKit — UNA sola fuente de verdad visual del Reel C completo. ──────────────
// El <Stage> (fondo + luces + viñeta + grano) envuelve TODO el reel y persiste
// entre escenas (no parpadea en los cortes). Las primitivas (columna vidrio/líquido,
// odómetro premium, partículas) se comparten entre las 6 escenas. Mejorar el look
// = tocar AQUÍ, no en cada escena. (Animatic de dirección, $0.)

export const W = 1080;
export const H = 1920;
export const FLOOR = 1320; // baseline de las pilas
export const BAR_W = 250;
export const COL_CASH_X = 290; // centro columna izquierda (efectivo)
export const COL_INV_X = 790; // centro columna derecha (invertir)
export const VMAX = 120000;
export const MAXH = 470;
export const vToH = (v: number) => (Math.max(0, v) / VMAX) * MAXH;
export const LOSS_RED = "#EA3D4C"; // rojo de pérdida (más profundo que el coral del theme)

// rand determinista (sin estado, mismo resultado cada render)
export const rnd = (i: number) => {
  const x = Math.sin(i * 127.1 + 11.7) * 43758.5453;
  return x - Math.floor(x);
};

// ── Stage: fondo + luces detrás, hijos en medio, viñeta + grano encima. ─────────
export const Stage: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const frame = useCurrentFrame();
  const glowX = 50 + Math.sin(frame / 40) * 8; // deriva constante del glow
  return (
    <AbsoluteFill style={{ background: theme.bg.gradient }}>
      <AbsoluteFill
        style={{
          background: `radial-gradient(58% 40% at ${glowX}% 28%, rgba(91,192,190,0.10), rgba(0,0,0,0) 60%)`,
        }}
      />
      {/* Luz cenital suave (da volumen al fondo) */}
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(70% 32% at 50% 0%, rgba(255,255,255,0.06), rgba(0,0,0,0) 70%)",
        }}
      />
      {/* Piso luminoso bajo las columnas */}
      <AbsoluteFill
        style={{
          background: `radial-gradient(46% 18% at 50% ${(FLOOR / H) * 100}%, rgba(91,192,190,0.10), rgba(0,0,0,0) 70%)`,
        }}
      />
      {children}
      {/* Viñeta (enmarca, foco al centro) */}
      <AbsoluteFill
        style={{
          pointerEvents: "none",
          background:
            "radial-gradient(120% 80% at 50% 42%, rgba(0,0,0,0) 56%, rgba(0,0,0,0.55) 100%)",
        }}
      />
      {/* Grano de película (mata el look 'plano digital') */}
      <AbsoluteFill style={{ pointerEvents: "none", opacity: 0.05, mixBlendMode: "overlay" }}>
        <svg width={W} height={H}>
          <filter id="filmgrain">
            <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves={2} stitchTiles="stitch" />
          </filter>
          <rect width={W} height={H} filter="url(#filmgrain)" />
        </svg>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

export const barFloat = (frame: number, phase: number) => Math.sin(frame / 14 + phase) * 3;

// ── Columna "vidrio/líquido" 2.5D: color sólido + sheen + sombra + reflejo. ──────
export const Bar: React.FC<{
  cx: number;
  h: number;
  color: string;
  frame: number;
  phase: number;
  eroding?: boolean;
}> = ({ cx, h, color, frame, phase, eroding }) => {
  const float = barFloat(frame, phase);
  const hh = Math.max(0, h);
  const left = cx - BAR_W / 2;
  const top = FLOOR - hh + float;

  const topWhite = eroding ? 0.18 : 0.34;
  const fill = `linear-gradient(180deg, rgba(255,255,255,${topWhite}) 0%, rgba(255,255,255,0.05) 20%, rgba(0,0,0,0) 52%, rgba(0,0,0,0.42) 100%), ${color}`;

  const inner = (
    <>
      <div
        style={{
          position: "absolute",
          left: "11%",
          top: 0,
          width: "20%",
          height: "100%",
          background:
            "linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.42) 50%, rgba(255,255,255,0) 100%)",
          filter: "blur(4px)",
          borderRadius: 40,
        }}
      />
      <div
        style={{
          position: "absolute",
          top: -1,
          left: 7,
          width: BAR_W - 14,
          height: 8,
          borderRadius: 8,
          background: "#fff",
          opacity: eroding ? 0.5 : 0.85,
          filter: "blur(1.4px)",
        }}
      />
    </>
  );

  const boxBase: React.CSSProperties = {
    position: "absolute",
    left,
    width: BAR_W,
    height: hh,
    borderRadius: "16px 16px 5px 5px",
    background: fill,
    overflow: "hidden",
  };

  return (
    <>
      {/* sombra de contacto */}
      <div
        style={{
          position: "absolute",
          left: left - 20,
          top: FLOOR - 16 + float,
          width: BAR_W + 40,
          height: 36,
          borderRadius: "50%",
          background: "rgba(0,0,0,0.55)",
          filter: "blur(17px)",
        }}
      />
      {/* reflejo bajo el piso */}
      <div
        style={{
          ...boxBase,
          top: FLOOR + float,
          transform: "scaleY(-1)",
          transformOrigin: "50% 0%",
          opacity: 0.17,
          WebkitMaskImage: "linear-gradient(180deg, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0) 68%)",
          maskImage: "linear-gradient(180deg, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0) 68%)",
        }}
      >
        {inner}
      </div>
      {/* columna principal */}
      <div
        style={{
          ...boxBase,
          top,
          boxShadow: `0 0 24px ${color}33, 0 26px 50px rgba(0,0,0,0.45), inset 0 2px 0 rgba(255,255,255,0.32), inset 0 -18px 32px rgba(0,0,0,0.26)`,
        }}
      >
        {inner}
      </div>
    </>
  );
};

// ── GhostShell: "vaso" del valor NOMINAL. El líquido (Bar) baja con el valor REAL;
// el hueco superior = poder de compra perdido (impuestos + inflación). ──────────
export const GhostShell: React.FC<{ cx: number; hNominal: number; color: string; frame: number; phase: number }> = ({
  cx,
  hNominal,
  color,
  frame,
  phase,
}) => {
  const float = barFloat(frame, phase);
  const hh = Math.max(0, hNominal);
  const left = cx - BAR_W / 2;
  const top = FLOOR - hh + float;
  return (
    <div
      style={{
        position: "absolute",
        left,
        top,
        width: BAR_W,
        height: hh,
        borderRadius: "16px 16px 5px 5px",
        border: `2px solid ${color}55`,
        background: `linear-gradient(180deg, ${color}14 0%, ${color}06 100%)`,
        boxShadow: `inset 0 2px 0 ${color}33`,
        boxSizing: "border-box",
      }}
    >
      {/* rim superior (boca del vaso) */}
      <div
        style={{
          position: "absolute",
          top: -2,
          left: 6,
          width: BAR_W - 16,
          height: 4,
          borderRadius: 4,
          background: color,
          opacity: 0.5,
          filter: "blur(0.6px)",
        }}
      />
    </div>
  );
};

// ── Partículas de erosión (chispas que caen del nivel del líquido). ─────────────
export const ErosionDust: React.FC<{ frame: number; topY: number; cx: number; t0: number; count?: number }> = ({
  frame,
  topY,
  cx,
  t0,
  count = 26,
}) => {
  const out: React.ReactNode[] = [];
  for (let i = 0; i < count; i++) {
    const start = t0 + i * 2.4;
    const life = 46;
    const t = (frame - start) / life;
    if (t < 0 || t > 1) continue;
    const drift = (rnd(i) - 0.5) * 90 * t;
    const x = cx - BAR_W / 2 + rnd(i) * BAR_W + drift;
    const y = topY - t * 40 + t * t * 260;
    const size = 4 + rnd(i + 9) * 8;
    const hot = rnd(i + 3) > 0.55;
    const c = hot ? theme.gold : theme.red;
    const op = Math.sin(Math.min(t, 1) * Math.PI) * 0.9;
    out.push(
      <div
        key={i}
        style={{
          position: "absolute",
          left: x,
          top: y,
          width: size,
          height: size,
          borderRadius: "50%",
          background: c,
          opacity: op,
          boxShadow: `0 0 ${size * 1.6}px ${c}, 0 0 ${size * 0.7}px #fff8`,
        }}
      />
    );
  }
  return <>{out}</>;
};

// ── Odómetro premium: reel por dígito; rueda en MILES, ceros a la izq atenuados. ─
const REEL_MASK = "linear-gradient(180deg, transparent 0%, #000 16%, #000 84%, transparent 100%)";
const REEL_WIN = 1.3; // alto de ventana / alto de dígito (ajustado para no revelar vecinos)

const DigitReel: React.FC<{ place: number; value: number; size: number; h: number; dim: boolean }> = ({
  place,
  value,
  size,
  h,
  dim,
}) => {
  // Cada rueda muestra su dígito EXACTO (dato locked = se ve exacto, no se redondea).
  // Umbral ALTO por posición: la rueda descansa CRISP en su dígito y sólo gira en el
  // último tramo del acarreo real → los endpoints no-redondos (96,209 · 107,170 ·
  // 102,242) leen nítidos, sin quedar a media vuelta. (Un umbral bajo dejaba ruedas
  // entre dígitos en valores estáticos; pinear los bajos a 0 ocultaba las unidades.)
  const raw = value / Math.pow(10, place);
  const D = Math.floor(raw) % 10;
  const frac = raw - Math.floor(raw);
  const thr = place >= 5 ? 0.97 : 0.92;
  const roll = frac < thr ? 0 : (frac - thr) / (1 - thr);
  const dv = D + roll;
  const winH = h * REEL_WIN;
  const offset = (winH - h) / 2 - dv * h;
  return (
    <div
      style={{
        position: "relative",
        width: size * 0.6,
        height: winH,
        overflow: "hidden",
        opacity: dim ? 0.26 : 1,
        WebkitMaskImage: REEL_MASK,
        maskImage: REEL_MASK,
      }}
    >
      <div style={{ position: "absolute", top: 0, left: 0, width: "100%", transform: `translateY(${offset}px)` }}>
        {[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0].map((n, k) => (
          <div key={k} style={{ height: h, lineHeight: `${h}px`, textAlign: "center" }}>
            {n}
          </div>
        ))}
      </div>
    </div>
  );
};

export const RollingNumber: React.FC<{ value: number; color: string; size: number }> = ({ value, color, size }) => {
  const v = Math.max(0, value);
  const d = Math.max(6, String(Math.floor(v)).length); // ancho FIJO 6 (escala 100k)
  const h = size * 1.16;
  const winH = h * REEL_WIN;
  const nodes: React.ReactNode[] = [];
  for (let i = 0; i < d; i++) {
    const place = d - 1 - i;
    const dim = v < Math.pow(10, place);
    nodes.push(<DigitReel key={`d${i}`} place={place} value={v} size={size} h={h} dim={dim} />);
    if (place > 0 && place % 3 === 0) {
      nodes.push(
        <span key={`c${i}`} style={{ height: winH, lineHeight: `${winH}px` }}>
          ,
        </span>
      );
    }
  }
  return (
    <div
      style={{
        display: "inline-flex",
        alignItems: "center",
        height: winH,
        fontFamily: theme.font,
        fontSize: size,
        fontWeight: 800,
        color,
        fontVariantNumeric: "tabular-nums",
      }}
    >
      <span style={{ height: winH, lineHeight: `${winH}px`, marginRight: size * 0.04 }}>$</span>
      {nodes}
    </div>
  );
};

export const Counter: React.FC<{
  cx: number;
  value: number;
  color: string;
  tick?: number;
  top?: number;
  size?: number;
  width?: number;
}> = ({ cx, value, color, tick = 1, top = 700, size = 76, width = 400 }) => (
  <div
    style={{
      position: "absolute",
      left: cx - width / 2,
      top,
      width,
      display: "flex",
      justifyContent: "center",
      transform: `scale(${tick})`,
      transformOrigin: "50% 50%",
      filter: `drop-shadow(0 0 22px ${color}55)`,
    }}
  >
    <RollingNumber value={value} color={color} size={size} />
  </div>
);

// Pulso de asiento: escala sutil cuando un número aterriza.
export const settle = (frame: number, f0: number) => {
  const t = (frame - f0) / 1;
  if (t < 0) return 0;
  const a = Math.max(0, Math.min(1, (frame - f0) / 4));
  const b = Math.max(0, Math.min(1, (frame - (f0 + 4)) / 9));
  return a * (1 - b);
};
