import React from "react";
import {
  AbsoluteFill,
  Easing,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { loadFont } from "@remotion/fonts";
import { theme } from "../theme";

// Set-piece "servilleta write-on": la servilleta es una FOTO (gpt-image, en
// public/setpieces/<slug>.png, superficie EN BLANCO a proposito). Remotion le da
// vida: push-in lento de camara + la formula se ESCRIBE sola sobre la servilleta
// (clip-path izquierda->derecha, letra manuscrita, tinta marcador) con un nib de
// tinta "humeda" en la punta del trazo. Los numeros van SIEMPRE en esta capa
// controlada (la IA los escribe mal); por eso la servilleta sale en blanco.
//
// Arquitectura (2026-06-19): OBJETO = imagen IA (un tiro) · DATOS = overlay
// controlado aqui · MOVIMIENTO = camara $0 (img2vid de paga solo para objetos
// iconicos en movimiento real). El copy exacto lo decide Manuel.
loadFont({ family: "Inkfree", url: staticFile("fonts/Inkfree.ttf"), weight: "400" });

export type NapkinWriteOnProps = {
  napkin?: string; // slug en public/setpieces/<slug>.png
  promise?: string; // linea 1: la PROMESA (lo que el numero responde)
  formula?: string; // linea 2: la formula / el dato (acento)
  inkColor?: string; // tinta marcador
  accentColor?: string; // color del dato/formula
  // posicion del texto SOBRE la servilleta (se afina contra la foto)
  textTop?: number; // % vertical del centro del bloque
  textLeft?: number; // % horizontal del centro del bloque
  textWidth?: number; // px del bloque de escritura
  textRotate?: number; // grados, para acostar el texto sobre el plano de la servilleta
  promiseSize?: number;
  formulaSize?: number;
  // timing de escritura (frames). Si llega wordFrames se podra atar a la voz.
  startFrame?: number;
  writePromise?: number; // frames que tarda en escribirse la promesa
  gap?: number; // frames entre lineas
  writeFormula?: number; // frames que tarda la formula
};

// trazo "a mano": revela el texto de izquierda a derecha recortando por la derecha
const reveal = (frame: number, from: number, dur: number) =>
  interpolate(frame, [from, from + dur], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.25, 0.1, 0.3, 1),
  });

const Handwritten: React.FC<{
  text: string;
  p: number; // 0..1 progreso de escritura
  size: number;
  color: string;
  weight: number;
  glow?: string;
}> = ({ text, p, size, color, weight, glow }) => {
  // ancho aproximado del texto para colocar el nib en la punta del trazo
  const approxW = text.length * size * 0.46;
  return (
    <div style={{ position: "relative", display: "inline-block" }}>
      <div
        style={{
          clipPath: `inset(-18% ${(1 - p) * 100}% -18% 0%)`,
          WebkitClipPath: `inset(-18% ${(1 - p) * 100}% -18% 0%)`,
        }}
      >
        <span
          style={{
            fontFamily: "Inkfree, 'Segoe Print', cursive",
            fontSize: size,
            fontWeight: weight,
            color,
            letterSpacing: "0.01em",
            whiteSpace: "nowrap",
            textShadow: glow ? `0 0 18px ${glow}` : "0 1px 0 rgba(0,0,0,0.22)",
          }}
        >
          {text}
        </span>
      </div>
      {/* nib de tinta humeda en la punta del trazo */}
      {p > 0.01 && p < 0.99 && (
        <div
          style={{
            position: "absolute",
            top: "50%",
            left: p * approxW,
            width: 16,
            height: 16,
            marginTop: -8,
            marginLeft: -8,
            borderRadius: "50%",
            background: `radial-gradient(circle, ${color} 0%, ${color}88 40%, transparent 72%)`,
            filter: "blur(1.5px)",
          }}
        />
      )}
    </div>
  );
};

export const NapkinWriteOn: React.FC<NapkinWriteOnProps> = ({
  napkin = "napkin_2",
  promise = "tu dinero se duplica en…",
  formula = "72 ÷ %  =  años",
  inkColor = "#16181d",
  accentColor = "#181a1f",
  textTop = 47,
  textLeft = 45,
  textWidth = 540,
  textRotate = -3,
  promiseSize = 44,
  formulaSize = 72,
  startFrame = 10,
  writePromise = 34,
  gap = 10,
  writeFormula = 30,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  // push-in lento de camara sobre el plano servilleta+tinta (parallax correcto)
  const push = interpolate(frame, [0, durationInFrames], [1.0, 1.07], {
    easing: Easing.bezier(0.33, 0, 0.67, 1),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const driftRot = Math.sin(frame / 90) * 0.4; // micro vida de camara

  const p1 = reveal(frame, startFrame, writePromise);
  const f2start = startFrame + writePromise + gap;
  const p2 = reveal(frame, f2start, writeFormula);
  const settle = interpolate(frame, [f2start + writeFormula, f2start + writeFormula + 14], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const glowPulse = 0.7 + Math.sin(frame / 11) * 0.3;

  return (
    <AbsoluteFill style={{ backgroundColor: "#0a0d12" }}>
      {/* plano servilleta + tinta: escala junto = la tinta vive SOBRE el papel */}
      <AbsoluteFill
        style={{
          transform: `scale(${push}) rotate(${driftRot}deg)`,
          transformOrigin: "50% 42%",
        }}
      >
        <Img
          src={staticFile(`setpieces/${napkin}.png`)}
          style={{
            position: "absolute",
            width: "100%",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
          }}
        />

        {/* la formula escrita a mano, acostada sobre el plano de la servilleta */}
        <div
          style={{
            position: "absolute",
            top: `${textTop}%`,
            left: `${textLeft}%`,
            width: textWidth,
            transform: `translate(-50%, -50%) rotate(${textRotate}deg)`,
            textAlign: "center",
            lineHeight: 1.18,
          }}
        >
          <div style={{ opacity: interpolate(p1, [0, 0.05], [0, 1]) }}>
            <Handwritten
              text={promise}
              p={p1}
              size={promiseSize}
              color={inkColor}
              weight={400}
            />
          </div>
          <div style={{ marginTop: 18, opacity: interpolate(p2, [0, 0.05], [0, 1]) }}>
            <Handwritten
              text={formula}
              p={p2}
              size={formulaSize}
              color={accentColor}
              weight={400}
            />
          </div>
          {/* subrayado que se traza bajo la formula al terminar (cierre) */}
          <svg
            width={textWidth * 0.62}
            height="22"
            style={{ display: "block", margin: "10px auto 0", overflow: "visible" }}
          >
            <path
              d={`M 6 12 q ${textWidth * 0.15} -14 ${textWidth * 0.3} -2 q ${textWidth * 0.15} 10 ${textWidth * 0.28} -3`}
              fill="none"
              stroke={accentColor}
              strokeWidth={6}
              strokeLinecap="round"
              style={{
                strokeDasharray: textWidth,
                strokeDashoffset: textWidth * (1 - settle),
                opacity: 0.85,
              }}
            />
          </svg>
        </div>
      </AbsoluteFill>

      {/* viñeta para fundir cualquier borde de la foto con el fondo de marca */}
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(ellipse 78% 64% at 50% 44%, transparent 60%, rgba(0,0,0,0.55) 100%)",
          pointerEvents: "none",
        }}
      />
      {/* leve realce de luz sobre la zona escrita (foco premium) */}
      <AbsoluteFill
        style={{
          background: `radial-gradient(ellipse 40% 26% at ${textLeft}% ${textTop}%, ${theme.gold}0e 0%, transparent 70%)`,
          opacity: glowPulse,
          pointerEvents: "none",
          mixBlendMode: "screen",
        }}
      />
    </AbsoluteFill>
  );
};
