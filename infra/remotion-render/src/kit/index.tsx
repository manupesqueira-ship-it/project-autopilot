import React from "react";
import { theme } from "../theme";

// ============================================================================
// Dinero IA — KIT visual compartido (la "vocabulario" del look de las graficas).
// UNA fuente de verdad: mejorar un primitivo AQUI mejora TODOS los beats que lo
// importan (coherencia ESTRUCTURAL, no coordinada). Se compone sobre
// PremiumStage (el mundo vivo). Regla: ningun beat re-inventa glow/orb/labels;
// los toma de aqui. v1 cubre la grafica de linea semantica (verde->rojo); se
// extiende a otros charts conforme se necesiten (no antes).
// ============================================================================

// Defs compartidos (gradientes + filtros de bloom volumetrico). Incluir UNA vez
// dentro del <svg> del beat, antes de usar cualquier primitivo.
export const KitDefs: React.FC = () => (
  <defs>
    <linearGradient id="kit-fill-green" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stopColor={theme.green} stopOpacity="0.34" />
      <stop offset="46%" stopColor={theme.green} stopOpacity="0.12" />
      <stop offset="100%" stopColor={theme.green} stopOpacity="0" />
    </linearGradient>
    <linearGradient id="kit-fill-red" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stopColor={theme.red} stopOpacity="0.36" />
      <stop offset="46%" stopColor={theme.red} stopOpacity="0.12" />
      <stop offset="100%" stopColor={theme.red} stopOpacity="0" />
    </linearGradient>
    <radialGradient id="kit-orb-green" cx="34%" cy="28%" r="78%">
      <stop offset="0%" stopColor="#FFFFFF" />
      <stop offset="28%" stopColor="#9BFFE6" />
      <stop offset="60%" stopColor={theme.green} />
      <stop offset="100%" stopColor="#00563F" />
    </radialGradient>
    <radialGradient id="kit-orb-red" cx="34%" cy="28%" r="78%">
      <stop offset="0%" stopColor="#FFFFFF" />
      <stop offset="28%" stopColor="#FFC9C9" />
      <stop offset="60%" stopColor={theme.red} />
      <stop offset="100%" stopColor="#6E1717" />
    </radialGradient>
    <filter id="kit-bloom" x="-80%" y="-80%" width="260%" height="260%">
      <feGaussianBlur stdDeviation="8" />
    </filter>
    <filter id="kit-bloom-lg" x="-160%" y="-160%" width="420%" height="420%">
      <feGaussianBlur stdDeviation="24" />
    </filter>
  </defs>
);

// GlowLine — el trazo heroe: 3 capas (bloom volumetrico + cuerpo de color +
// nucleo blanco-caliente) reveladas progresivamente por dash. El glow es del
// FILTRO gaussiano (lee volumetrico), no solo drop-shadow plano.
export const GlowLine: React.FC<{
  d: string;
  length: number;
  drawn: number; // px de longitud ya dibujados (0..length)
  color: string;
  width?: number;
  visible?: boolean;
}> = ({ d, length, drawn, color, width = 7, visible = true }) => {
  if (!visible || length <= 0) return null;
  const offset = length - Math.min(Math.max(drawn, 0), length);
  const base = {
    d,
    fill: "none" as const,
    strokeLinecap: "round" as const,
    strokeLinejoin: "round" as const,
    strokeDasharray: length,
    strokeDashoffset: offset,
  };
  return (
    <g>
      <path
        {...base}
        stroke={color}
        strokeWidth={width * 3.4}
        opacity={0.28}
        style={{ filter: "url(#kit-bloom)" }}
      />
      <path
        {...base}
        stroke={color}
        strokeWidth={width}
        style={{ filter: `drop-shadow(0 0 9px ${color})` }}
      />
      <path {...base} stroke="#FFFFFF" strokeWidth={width * 0.34} opacity={0.92} />
    </g>
  );
};

// AreaFill — cuerpo bajo la curva (gradiente rico, NO el wireframe invisible de
// antes). fillId = "kit-fill-green" | "kit-fill-red". clipPathId revela el area
// junto con el trazo.
export const AreaFill: React.FC<{
  d: string;
  fillId: string;
  clipPathId?: string;
}> = ({ d, fillId, clipPathId }) => (
  <path d={d} fill={`url(#${fillId})`} clipPath={clipPathId ? `url(#${clipPathId})` : undefined} />
);

// GlossyOrb — esfera especular premium que cabalga la punta del trazo (firma
// 0x100x). Halo de bloom + esfera con gradiente + brillo especular.
export const GlossyOrb: React.FC<{
  x: number;
  y: number;
  variant: "green" | "red";
  r?: number;
}> = ({ x, y, variant, r = 22 }) => {
  const c = variant === "red" ? theme.red : theme.green;
  return (
    <g>
      <circle cx={x} cy={y} r={r * 2.1} fill={c} opacity={0.34} style={{ filter: "url(#kit-bloom-lg)" }} />
      <circle cx={x} cy={y} r={r} fill={`url(#kit-orb-${variant})`} style={{ filter: `drop-shadow(0 0 14px ${c})` }} />
      <ellipse cx={x - r * 0.3} cy={y - r * 0.4} rx={r * 0.3} ry={r * 0.2} fill="white" opacity={0.9} />
    </g>
  );
};

// BloomFlash — el destello blanco UNICO del video (motion_grammar: 1x antes del
// climax). t es una envolvente 0..1 que el beat calcula (sube y baja una vez).
export const BloomFlash: React.FC<{ x: number; y: number; t: number }> = ({ x, y, t }) => {
  if (t <= 0.001) return null;
  const grow = 50 + t * 240;
  const op = Math.sin(Math.min(t, 1) * Math.PI) * 0.6;
  return <circle cx={x} cy={y} r={grow} fill="#FFFFFF" opacity={op} style={{ filter: "url(#kit-bloom-lg)" }} />;
};

// SemanticDivider — divisor vertical blanco glowing en el punto de quiebre
// (verde->rojo). progress 0..1 lo extiende de arriba hacia abajo.
export const SemanticDivider: React.FC<{
  x: number;
  yTop: number;
  yBot: number;
  progress: number;
}> = ({ x, yTop, yBot, progress }) => {
  if (progress <= 0) return null;
  return (
    <line
      x1={x}
      y1={yTop}
      x2={x}
      y2={yTop + progress * (yBot - yTop)}
      stroke="#FFFFFF"
      strokeWidth={2.5}
      opacity={0.85}
      style={{ filter: "drop-shadow(0 0 10px rgba(255,255,255,0.9)) drop-shadow(0 0 26px rgba(255,255,255,0.5))" }}
    />
  );
};

// FloorReflection — reflejo tenue del trazo sobre el piso reflejante (profundidad
// premium, 0x100x). Espeja sobre mirrorY, muy bajo en opacidad + blur. La
// vineta inferior de PremiumStage termina de fundirlo.
export const FloorReflection: React.FC<{
  d: string;
  length: number;
  drawn: number;
  color: string;
  mirrorY: number;
  width?: number;
}> = ({ d, length, drawn, color, mirrorY, width = 7 }) => {
  if (length <= 0) return null;
  const offset = length - Math.min(Math.max(drawn, 0), length);
  return (
    <g transform={`translate(0 ${2 * mirrorY}) scale(1 -1)`} opacity={0.13} style={{ filter: "blur(7px)" }}>
      <path
        d={d}
        fill="none"
        stroke={color}
        strokeWidth={width}
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeDasharray={length}
        strokeDashoffset={offset}
      />
    </g>
  );
};

// FloatLabel — etiqueta de dato pequena y tenue, en espacio negativo limpio
// (NUNCA encima del trazo). El beat calcula left/top ya clampeados al safe-area.
export const FloatLabel: React.FC<{
  left: number;
  top: number;
  width: number;
  text: string;
  appear: number; // 0..1
  color?: string;
  size?: number;
  weight?: number;
}> = ({ left, top, width, text, appear, color = theme.textDim, size = 32, weight = 600 }) => (
  <div
    style={{
      position: "absolute",
      left,
      top,
      width,
      textAlign: "center",
      fontFamily: theme.font,
      fontSize: size,
      fontWeight: weight,
      color,
      opacity: Math.min(appear * 1.3, 1),
      transform: `translateY(${(1 - appear) * 14}px)`,
      letterSpacing: "0.01em",
    }}
  >
    {text}
  </div>
);

// Caption — linea de contexto chica arriba, revelada palabra por palabra. NO es
// titulo sobre el chart (regla locked): es contexto, va arriba en su carril.
export const Caption: React.FC<{
  text: string;
  frame: number;
  top?: number;
}> = ({ text, frame, top = 212 }) => {
  const words = text.split(" ");
  return (
    <div
      style={{
        position: "absolute",
        top,
        width: "100%",
        textAlign: "center",
        fontFamily: theme.font,
        fontSize: 34,
        fontWeight: 500,
        color: theme.textDim,
        opacity: 0.92,
        letterSpacing: "0.01em",
      }}
    >
      {words.map((w, i) => {
        const interp = (a: number, b: number) =>
          Math.min(Math.max((frame - a) / (b - a), 0), 1);
        const o = interp(2 + i * 3, 9 + i * 3);
        return (
          <span key={i} style={{ opacity: o }}>
            {w}{" "}
          </span>
        );
      })}
    </div>
  );
};
