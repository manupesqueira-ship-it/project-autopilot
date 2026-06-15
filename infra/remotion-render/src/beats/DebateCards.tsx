import React from "react";
import {
  AbsoluteFill,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { theme } from "../theme";
import { StudioScene } from "../studio/StudioScene";

// Debate de 2 caricaturas: dos personajes enfrentados (mirando al centro) con
// bocadillos que entran en secuencia (izq habla -> der responde) = ritmo de
// debate. Imagen via public/characters/<slug>.png; si falta el slug se dibuja
// una silueta placeholder (para validar layout sin generar caras nuevas $).
export type DebateSide = {
  imageSlug?: string;
  name: string;
  quote: string;
  // mirar al centro: por defecto izq no se voltea, der se voltea (mirror)
  flip?: boolean;
  color?: string;
};

export type DebateCardsProps = {
  topic?: string;
  left: DebateSide;
  right: DebateSide;
};

const Silhouette: React.FC<{ color: string }> = ({ color }) => (
  <svg width={420} height={560} viewBox="0 0 420 560">
    <defs>
      <linearGradient id="silg" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stopColor={color} stopOpacity="0.5" />
        <stop offset="100%" stopColor={color} stopOpacity="0.12" />
      </linearGradient>
    </defs>
    <circle cx="210" cy="160" r="120" fill="url(#silg)" />
    <path
      d="M50 560c0-110 72-200 160-200s160 90 160 200Z"
      fill="url(#silg)"
    />
  </svg>
);

const Character: React.FC<{
  side: DebateSide;
  pop: number;
  float: number;
  glow: number;
  baseColor: string;
}> = ({ side, pop, float, glow, baseColor }) => {
  const color = side.color ?? baseColor;
  return (
    <div
      style={{
        position: "relative",
        transform: `translateY(${float - (1 - pop) * 40}px) scale(${0.82 + pop * 0.18})`,
        opacity: pop,
      }}
    >
      {/* halo */}
      <div
        style={{
          position: "absolute",
          left: "50%",
          top: 80,
          width: 540,
          height: 540,
          marginLeft: -270,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${color}38 0%, ${color}10 44%, transparent 68%)`,
          filter: "blur(14px)",
          opacity: glow,
        }}
      />
      {/* sombra de piso */}
      <div
        style={{
          position: "absolute",
          left: "50%",
          bottom: -30,
          width: 380,
          height: 90,
          marginLeft: -190,
          borderRadius: "50%",
          background: "radial-gradient(ellipse, rgba(0,0,0,0.55) 0%, transparent 70%)",
          filter: "blur(18px)",
        }}
      />
      <div style={{ transform: side.flip ? "scaleX(-1)" : "none" }}>
        {side.imageSlug ? (
          <Img
            src={staticFile(`characters/${side.imageSlug}.png`)}
            style={{ width: 520, height: "auto", display: "block" }}
          />
        ) : (
          <Silhouette color={color} />
        )}
      </div>
    </div>
  );
};

const Bubble: React.FC<{
  side: "left" | "right";
  color: string;
  text: string;
  name: string;
  p: number;
}> = ({ side, color, text, name, p }) => {
  const isLeft = side === "left";
  return (
    <div
      style={{
        position: "relative",
        maxWidth: 470,
        opacity: p,
        transform: `translateY(${(1 - p) * 24}px) scale(${0.9 + p * 0.1})`,
        transformOrigin: isLeft ? "left bottom" : "right bottom",
      }}
    >
      <div
        style={{
          background:
            "linear-gradient(165deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.045) 100%)",
          border: `2px solid ${color}66`,
          borderRadius: 32,
          padding: "30px 34px",
          boxShadow: `0 24px 60px rgba(0,0,0,0.5), 0 0 40px ${color}1f`,
        }}
      >
        <div
          style={{
            fontSize: 25,
            fontWeight: 800,
            letterSpacing: "0.06em",
            textTransform: "uppercase",
            color,
            marginBottom: 12,
          }}
        >
          {name}
        </div>
        <div
          style={{
            fontSize: 44,
            fontWeight: 800,
            lineHeight: 1.2,
            letterSpacing: "-0.01em",
            color: theme.text,
          }}
        >
          {text}
        </div>
      </div>
      {/* tail apuntando hacia abajo al personaje */}
      <div
        style={{
          position: "absolute",
          bottom: -13,
          [isLeft ? "left" : "right"]: 60,
          width: 28,
          height: 28,
          background: "rgba(255,255,255,0.06)",
          borderRight: `2px solid ${color}66`,
          borderBottom: `2px solid ${color}66`,
          transform: "rotate(45deg)",
        }}
      />
    </div>
  );
};

export const DebateCards: React.FC<DebateCardsProps> = ({
  topic,
  left,
  right,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const clamp = {
    extrapolateLeft: "clamp" as const,
    extrapolateRight: "clamp" as const,
  };

  const leftColor = left.color ?? theme.green;
  const rightColor = right.color ?? theme.gold;

  const popL = spring({ frame: frame - 4, fps, config: { damping: 14, mass: 0.8 } });
  const popR = spring({ frame: frame - 12, fps, config: { damping: 14, mass: 0.8 } });
  const floatL = Math.sin(frame / 16) * 7;
  const floatR = Math.sin(frame / 16 + 1.6) * 7;
  const glow = 0.5 + Math.sin(frame / 12) * 0.4;

  // bocadillos en secuencia: izq habla primero, der responde
  const bubbleL = spring({ frame: frame - 26, fps, config: { damping: 16, mass: 0.7 } });
  const bubbleR = spring({ frame: frame - 70, fps, config: { damping: 16, mass: 0.7 } });

  return (
    <StudioScene spotlightColor={leftColor} grid={false}>
      <AbsoluteFill style={{ fontFamily: theme.font }}>
        {topic && (
          <div
            style={{
              position: "absolute",
              // top-211px (11%) = safe-area superior de filter_a; el topic se
              // baja a 220 para no invadirla (antes 130 -> reprobaba safe_areas).
              top: 220,
              width: "100%",
              textAlign: "center",
              fontSize: 40,
              fontWeight: 800,
              letterSpacing: "-0.01em",
              color: theme.text,
              opacity: interpolate(frame, [2, 12], [0, 1], clamp),
              padding: "0 90px",
              boxSizing: "border-box",
            }}
          >
            {topic}
          </div>
        )}

        {/* bocadillos */}
        <div
          style={{
            position: "absolute",
            top: 300,
            left: 80,
            width: 520,
            display: "flex",
            justifyContent: "flex-start",
          }}
        >
          <Bubble side="left" color={leftColor} text={left.quote} name={left.name} p={bubbleL} />
        </div>
        <div
          style={{
            position: "absolute",
            top: 560,
            right: 80,
            width: 520,
            display: "flex",
            justifyContent: "flex-end",
          }}
        >
          <Bubble side="right" color={rightColor} text={right.quote} name={right.name} p={bubbleR} />
        </div>

        {/* personajes enfrentados, abajo */}
        <div
          style={{
            position: "absolute",
            bottom: 200,
            left: 40,
          }}
        >
          <Character side={{ ...left, flip: left.flip ?? false }} pop={popL} float={floatL} glow={glow} baseColor={leftColor} />
        </div>
        <div
          style={{
            position: "absolute",
            bottom: 200,
            right: 40,
          }}
        >
          <Character side={{ ...right, flip: right.flip ?? true }} pop={popR} float={floatR} glow={glow} baseColor={rightColor} />
        </div>

        {/* badge VS al centro */}
        <div
          style={{
            position: "absolute",
            left: "50%",
            bottom: 470,
            marginLeft: -56,
            width: 112,
            height: 112,
            borderRadius: "50%",
            background: theme.bg.base,
            border: "3px solid rgba(255,255,255,0.5)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: 46,
            fontWeight: 900,
            color: theme.text,
            boxShadow: "0 14px 40px rgba(0,0,0,0.6)",
            opacity: interpolate(frame, [14, 26], [0, 1], clamp),
            transform: `scale(${0.7 + interpolate(frame, [14, 30], [0, 1], clamp) * 0.3})`,
          }}
        >
          VS
        </div>
      </AbsoluteFill>
    </StudioScene>
  );
};
