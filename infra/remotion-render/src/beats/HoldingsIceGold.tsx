import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  useCurrentFrame,
} from "remotion";
import { IglooStage } from "../studio/IglooStage";
import { WINTER, WinterDefs, IceColumn, Ember } from "../studio/winter";

// SF-2 / beat b5 (v2) — TENENCIAS hielo->oro. Reemplaza las barras "meh". Dos
// columnas sobre un mismo piso: lo INVERTIDO ($270M) es hielo azul; el VALOR
// ACTUAL ($479M) es una columna mas alta de oro-esmeralda con hielo
// desprendiendose (transmuto) y la brasa ₿ coronandola. Cifras EXACTAS.

const W = 1080;
const H = 1920;
const YBOT = 1300;
const COL_W = 160;
const LX = 215; // invertido (hielo)
const RX = 705; // valor actual (oro)

const H_VALOR = 740; // px del valor actual ($479M)

export const HoldingsIceGold: React.FC<{
  investedLabel?: string;
  investedValue?: string;
  nowLabel?: string;
  nowValue?: string;
  ratio?: number; // invertido / valor
}> = ({
  investedLabel = "INVERTIDO",
  investedValue = "$270,000,000",
  nowLabel = "VALOR ACTUAL",
  nowValue = "$479,000,000",
  ratio = 270 / 479,
}) => {
  const frame = useCurrentFrame();

  const grow = interpolate(frame, [6, 64], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const reveal = interpolate(frame, [40, 70], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const hInvest = H_VALOR * ratio;
  const yTopInvest = YBOT - hInvest;
  const hValorNow = H_VALOR * grow;
  const yTopValor = YBOT - hValorNow;

  return (
    <IglooStage accent={WINTER.green} glowY={0.6} grainSeed={5}>
      <AbsoluteFill style={{ fontFamily: "InterVar, Inter, sans-serif" }}>
        {/* kicker contexto */}
        <div
          style={{
            position: "absolute",
            top: 250,
            width: "100%",
            textAlign: "center",
            color: "#7FA8BD",
            fontSize: 30,
            fontWeight: 300,
            letterSpacing: "0.42em",
            textTransform: "uppercase",
            opacity: 0.82,
          }}
        >
          La apuesta de El Salvador
        </div>

        <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{ position: "absolute", inset: 0 }}>
          <WinterDefs />

          {/* piso comun (reflejo tenue) */}
          <ellipse cx={W / 2} cy={YBOT + 30} rx={520} ry={30} fill="#0A1018" opacity={0.7} />
          <line x1={150} y1={YBOT + 2} x2={W - 150} y2={YBOT + 2} stroke="#2A4A5C" strokeWidth={2} opacity={0.5} />

          {/* INVERTIDO — hielo azul */}
          <IceColumn x={LX} w={COL_W} yTop={yTopInvest} yBot={YBOT} variant="ice" seed={6} />

          {/* VALOR ACTUAL — oro-esmeralda, crece, desprende hielo */}
          {grow > 0.02 && (
            <IceColumn x={RX} w={COL_W} yTop={yTopValor} yBot={YBOT} variant="gold" seed={9} shedIce={grow < 0.96} />
          )}

          {/* delta: arco tenue de crecimiento entre topes */}
          <path
            d={`M ${LX + COL_W / 2} ${yTopInvest - 26} Q ${W / 2} ${yTopValor - 120} ${RX + COL_W / 2} ${yTopValor - 26}`}
            fill="none"
            stroke={WINTER.green}
            strokeWidth={2.5}
            strokeDasharray="2 12"
            opacity={0.45 * reveal}
            style={{ filter: `drop-shadow(0 0 8px ${WINTER.green})` }}
          />

          {/* brasa ₿ coronando el valor actual */}
          {grow > 0.85 && <Ember cx={RX + COL_W / 2} cy={yTopValor - 6} r={34} intensity={reveal} />}
        </svg>

        {/* etiquetas INVERTIDO */}
        <Col label={investedLabel} value={investedValue} cx={LX + COL_W / 2} labelColor="#7FA8BD" valueColor="#D7E8F0" valueSize={44} appear={reveal} />
        {/* etiquetas VALOR ACTUAL (mas grande, dominante) */}
        <Col label={nowLabel} value={nowValue} cx={RX + COL_W / 2} labelColor="#5FD9BE" valueColor={WINTER.goldHot} valueSize={56} appear={reveal} bold />
      </AbsoluteFill>
    </IglooStage>
  );
};

const Col: React.FC<{
  label: string;
  value: string;
  cx: number;
  labelColor: string;
  valueColor: string;
  valueSize: number;
  appear: number;
  bold?: boolean;
}> = ({ label, value, cx, labelColor, valueColor, valueSize, appear, bold }) => (
  <div
    style={{
      position: "absolute",
      left: cx - 215,
      top: YBOT + 36,
      width: 430,
      textAlign: "center",
      opacity: appear,
      transform: `translateY(${(1 - appear) * 14}px)`,
    }}
  >
    <div
      style={{
        color: labelColor,
        fontSize: 30,
        fontWeight: 500,
        letterSpacing: "0.28em",
        textTransform: "uppercase",
      }}
    >
      {label}
    </div>
    <div
      style={{
        marginTop: 14,
        color: valueColor,
        fontSize: valueSize,
        fontWeight: bold ? 800 : 700,
        letterSpacing: "-0.01em",
        fontVariantNumeric: "tabular-nums",
        textShadow: bold ? `0 0 30px ${valueColor}55` : "none",
      }}
    >
      {value}
    </div>
  </div>
);
