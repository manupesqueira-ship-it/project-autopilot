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

// Set-piece "pizarron" (motion write_on, multilinea): HERMANO de la servilleta
// para lecciones paso a paso. El pizarron es el OBJETO (foto gpt-image con la
// SUPERFICIE EN BLANCO) y el titulo + los PASOS se ESCRIBEN con gis en capa
// controlada (Remotion, revelado izq->der). Sin foto cae a un pizarron PROCEDURAL
// ($0, render-testable): pizarra oscura + marco de madera + polvo de gis.
//
// Para contenido didactico/mas largo (varias lineas). Los numeros van en el gis
// controlado (la IA escribe mal cifras). Copy/dato EXACTO -> Manuel.
loadFont({ family: "Inkfree", url: staticFile("fonts/Inkfree.ttf"), weight: "400" });

export type ChalkboardSetPieceProps = {
  board?: string; // slug en public/setpieces/<slug>.png ("" -> procedural)
  title?: string; // titulo de la leccion
  steps?: string[]; // lineas / pasos del calculo
  accentColor?: string; // gis de color para el paso clave
  accentStep?: number; // indice del paso a resaltar (-1 = ninguno)
  chalk?: string;
  startFrame?: number;
  writeTitle?: number;
  writeStep?: number;
  gap?: number;
};

const reveal = (frame: number, from: number, dur: number) =>
  interpolate(frame, [from, from + dur], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.25, 0.1, 0.3, 1),
  });

const ChalkLine: React.FC<{
  text: string;
  p: number;
  size: number;
  color: string;
  weight?: number;
}> = ({ text, p, size, color, weight = 400 }) => (
  <div style={{ position: "relative", display: "inline-block" }}>
    <div
      style={{
        clipPath: `inset(-20% ${(1 - p) * 100}% -20% 0%)`,
        WebkitClipPath: `inset(-20% ${(1 - p) * 100}% -20% 0%)`,
      }}
    >
      <span
        style={{
          fontFamily: "Inkfree, 'Segoe Print', cursive",
          fontSize: size,
          fontWeight: weight,
          color,
          whiteSpace: "nowrap",
          letterSpacing: "0.01em",
          // textura de gis: doble sombra suave = trazo "polvoso"
          textShadow: `0 0 1px ${color}aa, 0 1px 6px rgba(255,255,255,0.18)`,
        }}
      >
        {text}
      </span>
    </div>
    {/* puntita de gis (polvo) en la punta del trazo */}
    {p > 0.01 && p < 0.99 && (
      <div
        style={{
          position: "absolute",
          top: "50%",
          left: p * text.length * size * 0.44,
          width: 14,
          height: 14,
          marginTop: -7,
          marginLeft: -7,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${color} 0%, transparent 70%)`,
          filter: "blur(2px)",
          opacity: 0.8,
        }}
      />
    )}
  </div>
);

export const ChalkboardSetPiece: React.FC<ChalkboardSetPieceProps> = ({
  board = "",
  title = "como funciona",
  steps = ["primer paso", "segundo paso", "resultado"],
  accentColor = theme.green,
  accentStep = -1,
  chalk = "#eef2ec",
  startFrame = 10,
  writeTitle = 26,
  writeStep = 22,
  gap = 8,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const list = Array.isArray(steps) ? steps : [];

  const push = interpolate(frame, [0, durationInFrames], [1.0, 1.055], {
    easing: Easing.bezier(0.33, 0, 0.67, 1),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const drift = Math.sin(frame / 95) * 0.3;

  const pTitle = reveal(frame, startFrame, writeTitle);

  return (
    <AbsoluteFill style={{ backgroundColor: "#0a0d12" }}>
      <AbsoluteFill
        style={{
          transform: `scale(${push}) rotate(${drift}deg)`,
          transformOrigin: "50% 46%",
        }}
      >
        <div
          style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            width: 940,
            height: 1140,
            transform: "translate(-50%, -50%)",
          }}
        >
          {board ? (
            <Img
              src={staticFile(`setpieces/${board}.png`)}
              style={{ width: "100%", height: "100%", objectFit: "cover", borderRadius: 10 }}
            />
          ) : (
            // pizarron procedural: marco de madera + pizarra + polvo
            <div
              style={{
                position: "absolute",
                inset: 0,
                borderRadius: 14,
                padding: 26,
                boxSizing: "border-box",
                background: "linear-gradient(160deg, #6b4a2b 0%, #4e3520 50%, #3d2a18 100%)",
                boxShadow: "0 40px 90px rgba(0,0,0,0.55)",
              }}
            >
              <div
                style={{
                  position: "absolute",
                  inset: 26,
                  borderRadius: 6,
                  background:
                    "radial-gradient(ellipse 80% 70% at 50% 38%, #20302b 0%, #16221e 70%, #101a16 100%)",
                  boxShadow: "inset 0 0 80px rgba(0,0,0,0.55)",
                }}
              />
              {/* veladuras de gis borrado */}
              <div
                style={{
                  position: "absolute",
                  inset: 26,
                  borderRadius: 6,
                  background:
                    "radial-gradient(ellipse 30% 16% at 30% 70%, rgba(255,255,255,0.05), transparent 70%), radial-gradient(ellipse 26% 14% at 70% 30%, rgba(255,255,255,0.04), transparent 70%)",
                  pointerEvents: "none",
                }}
              />
            </div>
          )}

          {/* ---- capa controlada: titulo + pasos escritos con gis ---- */}
          <div
            style={{
              position: "absolute",
              top: 120,
              left: 90,
              right: 90,
              bottom: 120,
              display: "flex",
              flexDirection: "column",
            }}
          >
            <div style={{ opacity: interpolate(pTitle, [0, 0.05], [0, 1]) }}>
              <ChalkLine text={title} p={pTitle} size={70} color={chalk} weight={400} />
            </div>
            {/* subrayado de gis bajo el titulo */}
            <div
              style={{
                height: 5,
                width: `${interpolate(pTitle, [0.5, 1], [0, 62], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}%`,
                background: chalk,
                opacity: 0.5,
                borderRadius: 3,
                margin: "14px 0 38px",
              }}
            />

            <div style={{ display: "flex", flexDirection: "column", gap: 30 }}>
              {list.map((s, i) => {
                const from = startFrame + writeTitle + gap + i * (writeStep + gap);
                const p = reveal(frame, from, writeStep);
                const col = i === accentStep ? accentColor : chalk;
                return (
                  <div
                    key={i}
                    style={{
                      display: "flex",
                      alignItems: "baseline",
                      gap: 22,
                      opacity: interpolate(p, [0, 0.05], [0, 1]),
                    }}
                  >
                    <span
                      style={{
                        fontFamily: "Inkfree, cursive",
                        fontSize: 38,
                        color: col,
                        opacity: 0.85,
                        minWidth: 46,
                      }}
                    >
                      {i + 1}.
                    </span>
                    <ChalkLine text={s} p={p} size={52} color={col} />
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </AbsoluteFill>

      <AbsoluteFill
        style={{
          background:
            "radial-gradient(ellipse 84% 72% at 50% 47%, transparent 60%, rgba(0,0,0,0.58) 100%)",
          pointerEvents: "none",
        }}
      />
    </AbsoluteFill>
  );
};
