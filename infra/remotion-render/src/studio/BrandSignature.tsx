import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../theme";
import { popIn } from "../anim";

// FIRMA DE MARCA recurrente (Style Bible §5.8): UN activo de marca propio,
// reconocible en ~0.5s, presente en CADA video. Es un "bug" sutil de esquina
// que respeta las safe-areas del 9:16 (la UI de IG tapa abajo/derecha) y entra
// con el easing LOCKED (§5.4) sin competir con el contenido.
//
// Arquitectura (igual que los set-pieces): el OBJETO de marca = una FOTO/asset
// ($0 tras un tiro) que vive en public/brand/<slug>.png; el slug llega por prop.
//   - mascot vacio  -> MARCA PROCEDURAL $0 (chip neutro + wordmark): render-testable
//     HOY sin gastar nada, para validar tamaño/posicion/sutileza en R1.
//   - mascot = slug -> se compone el asset real (la mascota que Manuel defina).
// La MASCOTA en si (§5.8: "el primer asset 3D organico") la DEFINE Manuel: este
// componente es el SLOT + el sistema de firma, no decide la identidad de marca.
// gpt-image (PNG) o un frame hero del modelo 3D caen en el mismo slot PNG (mismo
// patron que HeroCoin). Gasto gpt-image GATEADO -> avisar costo.

export type Corner = "tl" | "tr" | "bl" | "br";

export type BrandSignatureProps = {
  mascot?: string; // slug en public/brand/<slug>.png ("" -> placeholder procedural $0)
  wordmark?: string; // texto de la firma (marca/handle ya decidido por Manuel)
  placement?: Corner; // esquina; default arriba-izq (la mas segura vs UI de IG)
  accentColor?: string;
  size?: number; // px del glifo/mascota
  restOpacity?: number; // opacidad de reposo (sutil, no domina)
  enterFrame?: number; // frame en que entra la firma
  preview?: boolean; // true -> dibuja un backdrop oscuro detras (solo para QC standalone)
};

// margenes de safe-area por esquina (la UI de IG come abajo y la derecha)
const SAFE = { x: 64, top: 120, bottom: 300 };

const cornerStyle = (c: Corner): React.CSSProperties => {
  switch (c) {
    case "tr":
      return { top: SAFE.top, right: SAFE.x, flexDirection: "row-reverse", textAlign: "right" };
    case "bl":
      return { bottom: SAFE.bottom, left: SAFE.x };
    case "br":
      return { bottom: SAFE.bottom, right: SAFE.x, flexDirection: "row-reverse", textAlign: "right" };
    case "tl":
    default:
      return { top: SAFE.top, left: SAFE.x };
  }
};

// Glifo PROCEDURAL neutro ($0): chip redondeado con una marca geometrica de
// "dinero que sube" (semantica: dorado=dinero). NO es una mascota inventada — es
// el placeholder que el asset real reemplaza cuando Manuel defina la mascota.
const PlaceholderGlyph: React.FC<{ size: number; accent: string }> = ({ size, accent }) => (
  <div
    style={{
      width: size,
      height: size,
      borderRadius: size * 0.28,
      background: `linear-gradient(145deg, ${accent}2e 0%, ${accent}12 100%)`,
      border: `1.5px solid ${accent}66`,
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      boxShadow: `0 0 ${size * 0.4}px ${accent}22`,
    }}
  >
    <svg width={size * 0.56} height={size * 0.56} viewBox="0 0 24 24" fill="none">
      {/* tres barras crecientes + flecha = "dinero sube", puramente geometrico */}
      <rect x="3" y="14" width="4" height="7" rx="1.2" fill={accent} opacity="0.7" />
      <rect x="10" y="10" width="4" height="11" rx="1.2" fill={accent} opacity="0.85" />
      <rect x="17" y="5" width="4" height="16" rx="1.2" fill={accent} />
      <path d="M3 11 L11 7 L19 3" stroke={accent} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  </div>
);

export const BrandSignature: React.FC<BrandSignatureProps> = ({
  mascot = "",
  wordmark = "DINERO LATAM",
  placement = "tl",
  accentColor = theme.gold,
  size = 76,
  restOpacity = 0.92,
  enterFrame = 6,
  preview = false,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // entra en ~0.5s con el easing LOCKED (pop sutil), luego se queda quieta.
  const enter = popIn({ frame, fps, delay: enterFrame, from: 0.8, fadeFrames: 8 });
  const breath = 0.97 + Math.sin(frame / 26) * 0.03; // micro-vida calmada, casi imperceptible

  return (
    <AbsoluteFill
      style={{
        background: preview ? theme.bg.gradient : "transparent",
        fontFamily: theme.font,
      }}
    >
      <div
        style={{
          position: "absolute",
          display: "flex",
          alignItems: "center",
          gap: size * 0.26,
          opacity: (enter.opacity as number) * restOpacity * breath,
          transform: enter.transform,
          ...cornerStyle(placement),
        }}
      >
        {mascot ? (
          <Img
            src={staticFile(`brand/${mascot}.png`)}
            style={{
              width: size,
              height: size,
              objectFit: "contain",
              filter: "drop-shadow(0 4px 12px rgba(0,0,0,0.45))",
            }}
          />
        ) : (
          <PlaceholderGlyph size={size} accent={accentColor} />
        )}
        <span
          style={{
            fontSize: size * 0.38,
            fontWeight: 800,
            letterSpacing: "0.02em",
            color: theme.text,
            textShadow: "0 1px 8px rgba(0,0,0,0.55)",
            whiteSpace: "nowrap",
          }}
        >
          {wordmark}
        </span>
      </div>

      {preview && (
        <div
          style={{
            position: "absolute",
            bottom: 70,
            width: "100%",
            textAlign: "center",
            fontSize: 26,
            color: theme.textDim,
            opacity: interpolate(frame, [10, 24], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          }}
        >
          firma de marca · placeholder $0 (la mascota la define Manuel)
        </div>
      )}
    </AbsoluteFill>
  );
};
