import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { theme } from "../theme";
import { PremiumStage } from "../studio/PremiumStage";

// Gráfica explicativa PREMIUM — tenencias de El Salvador en Bitcoin.
// Dos columnas de "vidrio" sobre el mismo piso (mismo lenguaje que el animatic
// aprobado ErosionRace + la ref bars_label_5090 de 0x100x): lo INVERTIDO ($270M,
// teal neutro) vs el VALOR ACTUAL ($479M). La GANANCIA (+$209M) no es un número
// suelto: es un BLOQUE DORADO que crece SOBRE el nivel de lo invertido — el
// espectador LEE "esto puse, esto de más vale hoy". Color semántico: teal=costo
// (no pérdida), verde=capital que aguantó, dorado=dinero ganado.

const W = 1080;
const FLOOR = 1300;
const BAR_W = 210;
const XL = 290; // centro columna invertido
const XR = 790; // centro columna valor actual

const INVESTED = 270_000_000;
const VALUE = 479_000_000;
const GAIN = VALUE - INVESTED; // 209M
const PCT = Math.round((GAIN / INVESTED) * 100); // 77

const VMAX = VALUE;
const MAXH = 560;
const vToH = (v: number) => (v / VMAX) * MAXH;
const INVESTED_LEVEL = FLOOR - vToH(INVESTED); // y donde termina lo invertido

const fmt = (v: number) => "$" + Math.round(v).toLocaleString("en-US");

// Segmento de columna "vidrio/líquido": gradiente vertical (luz arriba → sombra
// abajo) + sheen + canto brillante. Da MATERIAL y volumen sin 3D (premium).
const GlassSegment: React.FC<{
  x: number;
  yTop: number;
  yBot: number;
  color: string;
  topEdge?: boolean;
}> = ({ x, yTop, yBot, color, topEdge = true }) => {
  const h = Math.max(0, yBot - yTop);
  if (h < 1) return null;
  const left = x - BAR_W / 2;
  const fill = `linear-gradient(180deg, rgba(255,255,255,0.30) 0%, rgba(255,255,255,0.06) 22%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.40) 100%), ${color}`;
  return (
    <div
      style={{
        position: "absolute",
        left,
        top: yTop,
        width: BAR_W,
        height: h,
        background: fill,
        borderRadius: 6,
        overflow: "hidden",
        boxShadow: `0 0 30px ${color}33, inset 0 2px 0 rgba(255,255,255,0.34), inset 0 -16px 30px rgba(0,0,0,0.22)`,
      }}
    >
      {/* sheen vertical (reflejo de softbox) */}
      <div
        style={{
          position: "absolute",
          left: "12%",
          top: 0,
          width: "18%",
          height: "100%",
          background:
            "linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.40) 50%, rgba(255,255,255,0) 100%)",
          filter: "blur(4px)",
        }}
      />
      {/* canto superior brillante */}
      {topEdge && (
        <div
          style={{
            position: "absolute",
            top: -1,
            left: 7,
            width: BAR_W - 14,
            height: 7,
            borderRadius: 8,
            background: "#fff",
            opacity: 0.8,
            filter: "blur(1.2px)",
          }}
        />
      )}
    </div>
  );
};

// Columna completa: sombra de contacto + reflejo bajo el piso + segmentos.
const GlassColumn: React.FC<{
  x: number;
  topY: number; // tope actual de la columna
  segments: { yTop: number; yBot: number; color: string }[];
  glow: string;
  float: number;
}> = ({ x, topY, segments, glow, float }) => {
  const left = x - BAR_W / 2;
  const h = FLOOR - topY;
  if (h < 1) return null;
  return (
    <>
      {/* sombra de contacto (asienta en el piso) */}
      <div
        style={{
          position: "absolute",
          left: left - 24,
          top: FLOOR - 14 + float,
          width: BAR_W + 48,
          height: 34,
          borderRadius: "50%",
          background: "rgba(0,0,0,0.5)",
          filter: "blur(16px)",
        }}
      />
      {/* reflejo bajo el piso */}
      <div
        style={{
          position: "absolute",
          left,
          top: FLOOR + float,
          width: BAR_W,
          height: h,
          transform: "scaleY(-1)",
          transformOrigin: "50% 0%",
          opacity: 0.16,
          background: `linear-gradient(180deg, ${glow} 0%, transparent 70%)`,
          borderRadius: 6,
          WebkitMaskImage:
            "linear-gradient(180deg, rgba(0,0,0,0.8) 0%, rgba(0,0,0,0) 66%)",
          maskImage:
            "linear-gradient(180deg, rgba(0,0,0,0.8) 0%, rgba(0,0,0,0) 66%)",
        }}
      />
      {/* segmentos de vidrio (con micro-float) */}
      <div style={{ transform: `translateY(${float}px)` }}>
        {segments.map((s, i) => (
          <GlassSegment
            key={i}
            x={x}
            yTop={s.yTop}
            yBot={s.yBot}
            color={s.color}
            topEdge={i === segments.length - 1}
          />
        ))}
      </div>
    </>
  );
};

const Counter: React.FC<{
  x: number;
  value: number;
  color: string;
  appear: number;
}> = ({ x, value, color, appear }) => (
  <div
    style={{
      position: "absolute",
      left: x - 230,
      top: 596,
      width: 460,
      textAlign: "center",
      opacity: appear,
      transform: `translateY(${(1 - appear) * 14}px)`,
    }}
  >
    <div
      style={{
        fontFamily: theme.font,
        fontSize: 56,
        fontWeight: 800,
        color,
        fontVariantNumeric: "tabular-nums",
        letterSpacing: "-0.01em",
        textShadow: `0 0 26px ${color}55`,
      }}
    >
      {fmt(value)}
    </div>
  </div>
);

const ColLabel: React.FC<{ x: number; label: string }> = ({ x, label }) => (
  <div
    style={{
      position: "absolute",
      left: x - 230,
      top: FLOOR + 22,
      width: 460,
      textAlign: "center",
      fontFamily: theme.font,
      fontSize: 32,
      fontWeight: 600,
      letterSpacing: "0.16em",
      textTransform: "uppercase",
      color: theme.textDim,
    }}
  >
    {label}
  </div>
);

export const HoldingsGainBars: React.FC<{
  kicker?: string;
  investedLabel?: string;
  valueLabel?: string;
  // sync a la voz (el ensamblador los inyecta desde apply_cues): growFrames[0] =
  // arranca la columna invertido (palabra "Invirtieron"), growFrames[1] = arranca
  // la columna valor (palabra "supera"), gainFrame = revela la GANANCIA (palabra
  // "Ganancia"). Sin cues, caen a la coreografía fija original (preview $0).
  growFrames?: number[];
  gainFrame?: number;
}> = ({
  kicker = "El Salvador · su reserva en Bitcoin",
  investedLabel = "Invertido",
  valueLabel = "Valor actual",
  growFrames,
  gainFrame,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // anclas de la coreografía: atadas a la voz si hay cues, si no la fija original.
  const g0 = growFrames?.[0] ?? 4;
  const g1 = growFrames?.[1] ?? 44;
  const gf = gainFrame ?? 104;

  // ── Coreografía por fases (monótona: la cifra crece y aterriza EXACTA, sin
  // overshoot que muestre un número falso intermedio) ───────────────────────
  // Fase 1: sube la columna INVERTIDO + cuenta a $270M.
  const grow1 = interpolate(frame, [g0, g0 + 38], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  // Fase 2: sube VALOR ACTUAL + cuenta a $479M (el cap dorado emerge solo).
  const grow2 = interpolate(frame, [g1, g1 + 56], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  // Fase 3: revela la etiqueta de GANANCIA (pop con vida, no mueve cifras).
  const gainIn = spring({
    frame: Math.max(0, frame - gf),
    fps,
    config: { damping: 14, mass: 0.7 },
  });

  const investedH = vToH(INVESTED) * grow1;
  const investedTopY = FLOOR - investedH;
  const investedVal = INVESTED * grow1;

  const valueH = vToH(VALUE) * grow2;
  const valueTopY = FLOOR - valueH;
  const valueVal = VALUE * grow2;

  const float1 = Math.sin(frame / 16) * 2.5;
  const float2 = Math.sin(frame / 16 + 2.1) * 2.5;

  // micro-float aplicado al nivel de invertido para la dashed (sigue la columna der.)
  const splitY = INVESTED_LEVEL + float2;

  // segmentos columna VALOR: verde hasta el nivel invertido, dorado por encima
  const greenBot = FLOOR;
  const greenTop = Math.max(valueTopY, INVESTED_LEVEL);
  const valueSegs: { yTop: number; yBot: number; color: string }[] = [
    { yTop: greenTop, yBot: greenBot, color: theme.green },
  ];
  const goldShown = valueTopY < INVESTED_LEVEL - 1;
  if (goldShown) {
    valueSegs.push({ yTop: valueTopY, yBot: INVESTED_LEVEL, color: theme.gold });
  }

  return (
    <PremiumStage tint={theme.green}>
      <AbsoluteFill style={{ fontFamily: theme.font }}>
        {/* kicker de contexto (carril propio arriba, NO sobre el chart) */}
        <div
          style={{
            position: "absolute",
            top: 250,
            width: "100%",
            textAlign: "center",
            color: theme.textDim,
            fontSize: 30,
            fontWeight: 300,
            letterSpacing: "0.36em",
            textTransform: "uppercase",
            opacity: 0.85,
          }}
        >
          {kicker}
        </div>

        {/* piso (línea base común bajo las columnas) */}
        <div
          style={{
            position: "absolute",
            left: 120,
            top: FLOOR + 1,
            width: W - 240,
            height: 2,
            background:
              "linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.18) 50%, transparent 100%)",
          }}
        />

        {/* línea punteada del NIVEL INVERTIDO: cruza SOLO el hueco, del tope de la
            columna invertido al punto donde el cap dorado arranca (la ganancia) */}
        {grow2 > 0.4 && (
          <div
            style={{
              position: "absolute",
              left: XL + BAR_W / 2,
              top: splitY,
              width: XR - XL - BAR_W,
              height: 0,
              borderTop: `2px dashed ${theme.gold}80`,
              opacity: interpolate(grow2, [0.4, 0.85], [0, 1], {
                extrapolateLeft: "clamp",
                extrapolateRight: "clamp",
              }),
            }}
          />
        )}

        {/* COLUMNA INVERTIDO (teal neutro) */}
        <GlassColumn
          x={XL}
          topY={investedTopY}
          glow={theme.teal}
          float={float1}
          segments={[{ yTop: investedTopY, yBot: FLOOR, color: theme.teal }]}
        />

        {/* COLUMNA VALOR ACTUAL (verde base + cap dorado = ganancia) */}
        {grow2 > 0.01 && (
          <GlassColumn x={XR} topY={valueTopY} glow={theme.green} float={float2} segments={valueSegs} />
        )}

        {/* ── PAYOFF HERO: la GANANCIA es el número GRANDE y legible (el porqué del
            video). Zona baja libre, centrada a todo el ancho (NUNCA se recorta). El
            eyebrow nombra el cap dorado; el color liga el cap con esta cifra. ── */}
        <div
          style={{
            position: "absolute",
            top: 1436,
            width: "100%",
            textAlign: "center",
            opacity: gainIn,
            transform: `translateY(${(1 - gainIn) * 26}px)`,
          }}
        >
          <div
            style={{
              fontSize: 30,
              fontWeight: 600,
              letterSpacing: "0.34em",
              textTransform: "uppercase",
              color: theme.gold,
              opacity: 0.82,
            }}
          >
            Ganancia
          </div>
          <div
            style={{
              marginTop: 8,
              fontSize: 104,
              fontWeight: 800,
              color: theme.gold,
              fontVariantNumeric: "tabular-nums",
              letterSpacing: "-0.02em",
              lineHeight: 1,
              textShadow: `0 0 48px ${theme.gold}66, 0 0 100px ${theme.gold}33`,
            }}
          >
            +{fmt(GAIN)}
          </div>
          <div
            style={{
              marginTop: 20,
              fontSize: 40,
              fontWeight: 700,
              letterSpacing: "0.05em",
              color: theme.green,
            }}
          >
            +{PCT}% sobre lo invertido
          </div>
        </div>

        {/* contadores sobre cada columna */}
        <Counter x={XL} value={investedVal} color={theme.teal} appear={Math.min(grow1 * 1.3, 1)} />
        <Counter
          x={XR}
          value={valueVal}
          color={theme.text}
          appear={Math.min(grow2 * 1.3, 1)}
        />

        {/* etiquetas de columna */}
        <ColLabel x={XL} label={investedLabel} />
        <ColLabel x={XR} label={valueLabel} />
      </AbsoluteFill>
    </PremiumStage>
  );
};
