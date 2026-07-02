import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { theme } from "../theme";

// PremiumStage — el "mundo vivo" (salto 2026-06-26): el StudioScene plano (push
// de escala + grid estático) hacía sentir las gráficas BÁSICAS. Aquí el escenario
// RESPIRA como 0x100x: cámara siempre a la deriva (parallax por capas), piso en
// PERSPECTIVA que avanza hacia el espectador, atmósfera con profundidad y un
// sheen reflejante. El color lo pone el CONTENIDO (luz neutra), no el cuarto.
// Es un escenario NUEVO (no toca StudioScene ni los beats ya aprobados): solo lo
// usan los beats premium nuevos hasta que Manuel apruebe el look.

const W = 1080;
const H = 1920;
const HORIZON = 1180;

const PerspectiveFloor: React.FC<{ frame: number; tint: string }> = ({
  frame,
  tint,
}) => {
  const VPX = 540;
  const floorH = H - HORIZON;

  // líneas de profundidad (convergen al punto de fuga)
  const verts: React.ReactNode[] = [];
  for (let bx = -480; bx <= 1560; bx += 120) {
    verts.push(
      <line
        key={`fv${bx}`}
        x1={VPX}
        y1={HORIZON}
        x2={bx}
        y2={H}
        stroke="white"
        strokeWidth={1.2}
      />,
    );
  }

  // líneas horizontales que SCROLLEAN hacia la cámara (sensación de avance)
  const N = 18;
  const t = ((frame * 0.16) / 30) % 1;
  const horis: React.ReactNode[] = [];
  for (let i = 0; i < N; i++) {
    let d = (i / N + t) % 1;
    if (d <= 0.0015) d = 0.0015;
    const y = HORIZON + floorH * Math.pow(d, 2.3);
    const op = Math.min(d * 1.5, 1) * 0.55;
    horis.push(
      <line
        key={`fh${i}`}
        x1={0}
        y1={y}
        x2={W}
        y2={y}
        stroke="white"
        strokeWidth={1.3}
        opacity={op}
      />,
    );
  }

  return (
    <svg width={W} height={H} style={{ position: "absolute" }}>
      <defs>
        <linearGradient id="floorfade" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="white" stopOpacity="0" />
          <stop offset="20%" stopColor="white" stopOpacity="0.12" />
          <stop offset="100%" stopColor="white" stopOpacity="0.015" />
        </linearGradient>
        <mask id="floormask">
          <rect x="0" y={HORIZON} width={W} height={floorH} fill="url(#floorfade)" />
        </mask>
      </defs>
      {/* tint del piso (glow de color de la marca, muy sutil) */}
      <rect
        x="0"
        y={HORIZON}
        width={W}
        height={floorH}
        fill={tint}
        opacity={0.06}
        mask="url(#floormask)"
      />
      <g mask="url(#floormask)">
        {verts}
        {horis}
      </g>
    </svg>
  );
};

export const PremiumStage: React.FC<{
  children: React.ReactNode;
  tint?: string;
  push?: boolean;
}> = ({ children, tint = theme.green, push = true }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  // deriva de cámara: parallax suave por capas (piso se mueve MÁS que el contenido)
  const driftX = Math.sin(frame / 88) * 11;
  const driftY = Math.cos(frame / 116) * 7;
  const scale = push
    ? interpolate(frame, [0, durationInFrames], [1.012, 1.05], {
        easing: Easing.bezier(0.33, 0, 0.67, 1),
      })
    : 1.012;

  return (
    <AbsoluteFill style={{ background: theme.bg.gradient, overflow: "hidden" }}>
      {/* atmósfera superior: spotlight neutro + halo de marca con profundidad */}
      <AbsoluteFill
        style={{
          background: `radial-gradient(ellipse 80% 50% at 50% 36%, rgba(255,255,255,0.12) 0%, rgba(255,255,255,0.05) 28%, ${tint}12 52%, transparent 78%)`,
          transform: `translate(${driftX * 0.4}px, ${driftY * 0.4}px)`,
        }}
      />
      {/* halo de horizonte: donde el contenido se asienta sobre el piso */}
      <AbsoluteFill
        style={{
          background: `radial-gradient(ellipse 70% 22% at 50% ${HORIZON}px, ${tint}22 0%, transparent 70%)`,
        }}
      />

      {/* piso en perspectiva (capa más cercana => más parallax) */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          transform: `translate(${driftX * 1.5}px, ${driftY * 1.1}px)`,
        }}
      >
        <PerspectiveFloor frame={frame} tint={tint} />
      </div>

      {/* sheen reflejante del piso (sutil, premium) */}
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(180deg, transparent 62%, rgba(150,170,200,0.05) 80%, rgba(170,190,215,0.11) 100%)",
          pointerEvents: "none",
        }}
      />

      {/* partículas flotantes — MUY escasas, premium (no confeti) */}
      <FloatMotes frame={frame} tint={tint} driftX={driftX} driftY={driftY} />

      {/* contenido (capa flotante => parallax menor) */}
      <AbsoluteFill
        style={{
          transform: `translate(${driftX * 0.55}px, ${driftY * 0.45}px) scale(${scale})`,
        }}
      >
        {children}
      </AbsoluteFill>

      {/* viñeta de profundidad de campo */}
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(ellipse 92% 70% at 50% 44%, transparent 58%, rgba(0,0,0,0.5) 100%)",
          pointerEvents: "none",
        }}
      />
      {/* grano */}
      <AbsoluteFill style={{ opacity: theme.grainOpacity, pointerEvents: "none" }}>
        <svg width={W} height={H}>
          <filter id="pgrain">
            <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed={11} />
            <feColorMatrix type="saturate" values="0" />
          </filter>
          <rect width={W} height={H} filter="url(#pgrain)" />
        </svg>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const MOTES = [
  { x: 180, y: 520, r: 3.5, ph: 0 },
  { x: 880, y: 360, r: 2.6, ph: 1.7 },
  { x: 760, y: 760, r: 3.0, ph: 3.1 },
  { x: 300, y: 900, r: 2.2, ph: 4.4 },
  { x: 560, y: 280, r: 2.8, ph: 5.6 },
  { x: 940, y: 640, r: 2.3, ph: 2.2 },
];

const FloatMotes: React.FC<{
  frame: number;
  tint: string;
  driftX: number;
  driftY: number;
}> = ({ frame, tint, driftX, driftY }) => (
  <svg
    width={W}
    height={H}
    style={{
      position: "absolute",
      transform: `translate(${driftX * 0.9}px, ${driftY * 0.7}px)`,
    }}
  >
    {MOTES.map((m, i) => {
      const fy = m.y + Math.sin(frame / 60 + m.ph) * 18;
      const op = 0.18 + 0.16 * (0.5 + 0.5 * Math.sin(frame / 45 + m.ph));
      return (
        <circle
          key={i}
          cx={m.x}
          cy={fy}
          r={m.r}
          fill={i % 2 === 0 ? tint : "#FFFFFF"}
          opacity={op}
          style={{ filter: `blur(0.6px) drop-shadow(0 0 6px ${tint}aa)` }}
        />
      );
    })}
  </svg>
);
