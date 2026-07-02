import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  useCurrentFrame,
} from "remotion";
import { IglooStage } from "../studio/IglooStage";
import { WINTER, WinterDefs, IceColumn, Ember, FrostEdges } from "../studio/winter";

// SF-1 / beat b4 (v2) — EL PISO DEL DESPLOME. Reemplaza la "linea-V triste" de
// RecoveryChart. El precio es un PILAR volumetrico: arriba sangra rojo (cae
// desde ~$69k), abajo congela en "$16,000 USD" encerrado en hielo, y la brasa ₿
// resiste en la base sin apagarse. Historia visual con garra, no grafica plana.

const W = 1080;
const H = 1920;
const PX = 465; // x del pilar
const PW = 150; // ancho
const PTOP = 520;
const PBOT = 1330;

export const IcePillarCrash: React.FC<{
  troughLabel?: string;
  fromLabel?: string;
}> = ({ troughLabel = "$16,000 USD", fromLabel = "$69,000" }) => {
  const frame = useCurrentFrame();
  const cx = PX + PW / 2;

  // el rojo cae desde arriba hasta el fondo (el desplome)
  const bleed = interpolate(frame, [0, 46], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.5, 0, 0.85, 1),
  });
  const redY = PTOP + (PBOT - PTOP) * (0.16 + 0.84 * bleed); // nivel rojo desciende
  // el hielo congela tras tocar fondo
  const freeze = interpolate(frame, [40, 74], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.cubic),
  });
  // la cifra del fondo + la brasa aparecen al congelar
  const stamp = interpolate(frame, [62, 80], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <IglooStage accent={WINTER.iceMid} glowY={0.74} grainSeed={11}>
      <AbsoluteFill style={{ fontFamily: "InterVar, Inter, sans-serif" }}>
        {/* kicker de contexto (carril propio arriba, NO encima del chart) */}
        <div
          style={{
            position: "absolute",
            top: 250,
            width: "100%",
            textAlign: "center",
            color: "#7FA8BD",
            fontFamily: "InterVar, Inter, sans-serif",
            fontSize: 30,
            fontWeight: 300,
            letterSpacing: "0.42em",
            textTransform: "uppercase",
            opacity: 0.8,
          }}
        >
          Bitcoin · invierno cripto
        </div>

        <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{ position: "absolute", inset: 0 }}>
          <WinterDefs />
          <defs>
            <clipPath id="pillarClip">
              <rect x={PX} y={PTOP} width={PW} height={PBOT - PTOP} rx={22} />
            </clipPath>
          </defs>

          {/* marca de la altura de la que cayo (~$69k) */}
          <line
            x1={PX - 40}
            y1={PTOP + 18}
            x2={PX + PW + 40}
            y2={PTOP + 18}
            stroke="#5E7B8C"
            strokeWidth={2}
            strokeDasharray="4 10"
            opacity={0.6}
          />

          {/* pilar de hielo (cuerpo + rime + grietas) */}
          <IceColumn x={PX} w={PW} yTop={PTOP} yBot={PBOT} variant="ice" seed={4} />

          {/* sangre roja: el precio que cayo, pooled abajo, clip al pilar */}
          <g clipPath="url(#pillarClip)">
            <rect
              x={PX}
              y={redY}
              width={PW}
              height={PBOT - redY + 10}
              fill="url(#w-redbleed)"
              opacity={0.92}
            />
            {/* menisco brillante del nivel rojo */}
            <rect x={PX} y={redY - 3} width={PW} height={6} fill={WINTER.redPale} opacity={0.85 * (1 - freeze * 0.5)} />
          </g>

          {/* flecha de plomada a la izquierda (la caida) */}
          <g opacity={0.9}>
            <line
              x1={PX - 70}
              y1={PTOP + 30}
              x2={PX - 70}
              y2={redY}
              stroke={WINTER.red}
              strokeWidth={4}
              strokeLinecap="round"
              style={{ filter: `drop-shadow(0 0 10px ${WINTER.red})` }}
            />
            <polygon
              points={`${PX - 70},${redY + 16} ${PX - 86},${redY - 12} ${PX - 54},${redY - 12}`}
              fill={WINTER.red}
              style={{ filter: `drop-shadow(0 0 10px ${WINTER.red})` }}
            />
          </g>

          {/* bloque de hielo encerrando la base (congelado) */}
          <g opacity={freeze}>
            <rect
              x={PX - 34}
              y={PBOT - 150}
              width={PW + 68}
              height={196}
              rx={26}
              fill="url(#w-ice)"
              stroke={WINTER.icePale}
              strokeWidth={2}
              strokeOpacity={0.7}
              opacity={0.5}
            />
          </g>

          {/* la brasa ₿ resiste en la base (no se apaga) */}
          <g opacity={stamp}>
            <Ember cx={cx} cy={PBOT - 8} r={50} intensity={0.55 + 0.45 * stamp} />
          </g>
        </svg>

        {/* $69,000 — de donde cayo (tenue) */}
        <div
          style={{
            position: "absolute",
            left: PX + PW + 56,
            top: PTOP - 4,
            color: "#6F8DA0",
            fontFamily: "InterVar, Inter, sans-serif",
            fontSize: 34,
            fontWeight: 400,
            letterSpacing: "0.02em",
            opacity: 0.7,
          }}
        >
          {fromLabel}
        </div>

        {/* $16,000 USD — el fondo congelado (dato, con garra) */}
        <div
          style={{
            position: "absolute",
            top: PBOT + 70,
            width: "100%",
            textAlign: "center",
            color: "#EAF4F8",
            fontFamily: "InterVar, Inter, sans-serif",
            fontSize: 84,
            fontWeight: 800,
            letterSpacing: "-0.01em",
            opacity: stamp,
            transform: `translateY(${(1 - stamp) * 16}px)`,
            textShadow: "0 0 30px rgba(111,183,216,0.55)",
          }}
        >
          {troughLabel}
        </div>
        <div
          style={{
            position: "absolute",
            top: PBOT + 168,
            width: "100%",
            textAlign: "center",
            color: WINTER.red,
            fontFamily: "InterVar, Inter, sans-serif",
            fontSize: 38,
            fontWeight: 700,
            letterSpacing: "0.04em",
            opacity: stamp * 0.95,
          }}
        >
          −77% DESDE SU PICO
        </div>

        <FrostEdges amount={0.5 + 0.4 * freeze} />
      </AbsoluteFill>
    </IglooStage>
  );
};
