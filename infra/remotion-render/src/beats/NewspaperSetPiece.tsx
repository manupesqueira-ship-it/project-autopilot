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
import { theme } from "../theme";

// Set-piece "periodico" (motion headline_set): el periodico es el OBJETO (foto
// gpt-image en public/setpieces/<slug>.png, con la PORTADA EN BLANCO) y el
// TITULAR + la CIFRA van en capa CONTROLADA (Remotion) que "imprime" el texto y
// resalta el dato. Sin foto cae a un periodico PROCEDURAL ($0, render-testable
// ya): nameplate + reglas + columnas tenues + caja de foto. Misma arquitectura
// que la servilleta: objeto=IA / datos=overlay / movimiento=camara $0.
//
// Los numeros SIEMPRE en el overlay (la IA los escribe mal) -> portada en blanco.
// El copy/dato EXACTO lo decide Manuel (slots <<rellenar>>), nunca el director.

export type NewspaperSetPieceProps = {
  paper?: string; // slug en public/setpieces/<slug>.png ("" -> procedural)
  headline?: string; // el TITULAR (data overlay)
  stat?: string; // la CIFRA resaltada (acento dorado = dinero)
  kicker?: string; // antetitulo / seccion (pequeno)
  nameplate?: string; // nombre del diario (solo modo procedural)
  dateline?: string; // fecha / edicion (solo modo procedural)
  inkColor?: string;
  accentColor?: string;
  paperColor?: string;
  startFrame?: number;
};

// "set" tipografico: la prensa golpea el tipo -> entra con micro-overshoot.
const STAMP = Easing.bezier(0.18, 1.4, 0.36, 1);

// anchos deterministas (NO Math.random: parpadearia entre frames) para simular
// renglones de columna justificados.
const lineW = (i: number) => 62 + ((i * 37) % 38);

const ProceduralPaper: React.FC<{
  nameplate: string;
  dateline: string;
  paperColor: string;
  ink: string;
}> = ({ nameplate, dateline, paperColor, ink }) => (
  <div
    style={{
      position: "absolute",
      inset: 0,
      background: paperColor,
      borderRadius: 6,
      padding: "60px 64px",
      boxSizing: "border-box",
      display: "flex",
      flexDirection: "column",
    }}
  >
    {/* nameplate (cabecera del diario) */}
    <div
      style={{
        textAlign: "center",
        fontFamily: "Georgia, 'Times New Roman', serif",
        fontWeight: 800,
        fontSize: 66,
        letterSpacing: "0.02em",
        color: ink,
        lineHeight: 1,
      }}
    >
      {nameplate}
    </div>
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        borderTop: `2px solid ${ink}`,
        borderBottom: `2px solid ${ink}`,
        margin: "14px 0 0",
        padding: "6px 2px",
        fontFamily: "Georgia, serif",
        fontSize: 18,
        letterSpacing: "0.08em",
        textTransform: "uppercase",
        color: ink,
        opacity: 0.7,
      }}
    >
      <span>{dateline}</span>
      <span>Edicion especial</span>
    </div>

    {/* banda del titular: queda en blanco; el overlay escribe encima */}
    <div style={{ height: 250 }} />

    {/* cuerpo: caja de foto + columnas de texto tenue */}
    <div style={{ display: "flex", gap: 26, flex: 1, marginTop: 8 }}>
      <div
        style={{
          width: "42%",
          background: "rgba(0,0,0,0.10)",
          border: `1px solid ${ink}22`,
          borderRadius: 3,
        }}
      />
      <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 11 }}>
        {Array.from({ length: 14 }).map((_, i) => (
          <div
            key={i}
            style={{
              height: 9,
              width: `${lineW(i)}%`,
              background: ink,
              opacity: 0.16,
              borderRadius: 2,
            }}
          />
        ))}
      </div>
    </div>
  </div>
);

export const NewspaperSetPiece: React.FC<NewspaperSetPieceProps> = ({
  paper = "",
  headline = "el titular de la noticia",
  stat = "",
  kicker = "",
  nameplate = "LATAM TIMES",
  dateline = "Hoy",
  inkColor = "#15140f",
  accentColor = theme.gold,
  paperColor = "#ece6d6",
  startFrame = 8,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  // camara: push-in lento + micro drift (premium, $0). Igual que la servilleta.
  const push = interpolate(frame, [0, durationInFrames], [1.0, 1.06], {
    easing: Easing.bezier(0.33, 0, 0.67, 1),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const driftRot = Math.sin(frame / 100) * 0.35 - 1.2; // periodico ligeramente acostado

  const words = String(headline).split(" ");
  const stagger = 3;
  const stampDur = 11;

  // la cifra se resalta DESPUES de que el titular asienta
  const statStart = startFrame + words.length * stagger + stampDur + 8;
  const hi = interpolate(frame, [statStart, statStart + 16], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  return (
    <AbsoluteFill style={{ backgroundColor: "#0a0d12" }}>
      <AbsoluteFill
        style={{
          transform: `scale(${push}) rotate(${driftRot}deg)`,
          transformOrigin: "50% 44%",
        }}
      >
        {/* el OBJETO periodico, centrado vertical */}
        <div
          style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            width: 860,
            height: 1180,
            transform: "translate(-50%, -50%)",
            boxShadow: "0 40px 90px rgba(0,0,0,0.55)",
          }}
        >
          {paper ? (
            <Img
              src={staticFile(`setpieces/${paper}.png`)}
              style={{ width: "100%", height: "100%", objectFit: "cover", borderRadius: 6 }}
            />
          ) : (
            <ProceduralPaper
              nameplate={nameplate}
              dateline={dateline}
              paperColor={paperColor}
              ink={inkColor}
            />
          )}

          {/* ---- capa controlada: titular + cifra (sobre la banda en blanco) ---- */}
          <div
            style={{
              position: "absolute",
              top: 230,
              left: 64,
              right: 64,
              textAlign: "center",
            }}
          >
            {kicker ? (
              <div
                style={{
                  fontFamily: "Georgia, serif",
                  textTransform: "uppercase",
                  letterSpacing: "0.16em",
                  fontSize: 22,
                  fontWeight: 700,
                  color: accentColor,
                  opacity: interpolate(frame, [startFrame, startFrame + 8], [0, 1], {
                    extrapolateLeft: "clamp",
                    extrapolateRight: "clamp",
                  }),
                  marginBottom: 12,
                }}
              >
                {kicker}
              </div>
            ) : null}

            {/* titular: cada palabra "se imprime" con golpe de prensa */}
            <div
              style={{
                fontFamily: "Georgia, 'Times New Roman', serif",
                fontWeight: 800,
                fontSize: 84,
                lineHeight: 1.02,
                color: inkColor,
                letterSpacing: "-0.01em",
              }}
            >
              {words.map((w, i) => {
                const t0 = startFrame + i * stagger;
                const p = interpolate(frame, [t0, t0 + stampDur], [0, 1], {
                  extrapolateLeft: "clamp",
                  extrapolateRight: "clamp",
                  easing: STAMP,
                });
                return (
                  <span
                    key={i}
                    style={{
                      display: "inline-block",
                      marginRight: "0.26em",
                      opacity: interpolate(p, [0, 0.18], [0, 1]),
                      transform: `scale(${interpolate(p, [0, 1], [1.16, 1])})`,
                    }}
                  >
                    {w}
                  </span>
                );
              })}
            </div>

            {/* cifra resaltada: barrido de marcador dorado por detras */}
            {stat ? (
              <div style={{ position: "relative", display: "inline-block", marginTop: 26 }}>
                <div
                  style={{
                    position: "absolute",
                    left: -10,
                    right: -10,
                    top: "14%",
                    bottom: "12%",
                    background: accentColor,
                    opacity: 0.92,
                    transform: `scaleX(${hi})`,
                    transformOrigin: "left center",
                    borderRadius: 4,
                  }}
                />
                <span
                  style={{
                    position: "relative",
                    fontFamily: theme.font,
                    fontWeight: 900,
                    fontSize: 76,
                    color: hi > 0.6 ? "#1a160d" : inkColor,
                    padding: "0 8px",
                  }}
                >
                  {stat}
                </span>
              </div>
            ) : null}
          </div>
        </div>
      </AbsoluteFill>

      {/* vineta de marca: funde el borde del periodico con el fondo */}
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(ellipse 82% 70% at 50% 47%, transparent 58%, rgba(0,0,0,0.6) 100%)",
          pointerEvents: "none",
        }}
      />
    </AbsoluteFill>
  );
};
