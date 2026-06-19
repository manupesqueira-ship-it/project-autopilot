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

// Set-piece "ticket/recibo" (motion print_out): para microgastos / comisiones /
// efecto latte. El recibo es el OBJETO (foto gpt-image con la cara EN BLANCO) y
// los conceptos + el TOTAL van en capa CONTROLADA (Remotion) que "imprime" la
// tira de arriba a abajo y resalta el total. Sin foto cae a un recibo PROCEDURAL
// ($0, render-testable): tira termica + perforados + corte zigzag, mono.
//
// El total = dinero -> acento DORADO por defecto (rojo SOLO si es perdida real,
// decision de Manuel). Cifras en el overlay (la IA las escribe mal). Copy -> Manuel.

export type TicketItem = { label?: string; price?: string };
export type TicketSetPieceProps = {
  ticket?: string; // slug en public/setpieces/<slug>.png ("" -> procedural)
  store?: string; // encabezado del recibo
  items?: TicketItem[]; // conceptos del ticket
  totalLabel?: string;
  total?: string; // total resaltado (slot)
  accentColor?: string;
  startFrame?: number;
  printFrames?: number; // cuanto tarda en "imprimirse" la tira
};

const ZigZag: React.FC<{ color: string }> = ({ color }) => (
  <svg width="100%" height="22" viewBox="0 0 100 22" preserveAspectRatio="none" style={{ display: "block" }}>
    <polygon
      points="0,0 100,0 100,8 95,18 90,8 85,18 80,8 75,18 70,8 65,18 60,8 55,18 50,8 45,18 40,8 35,18 30,8 25,18 20,8 15,18 10,8 5,18 0,8"
      fill={color}
    />
  </svg>
);

export const TicketSetPiece: React.FC<TicketSetPieceProps> = ({
  ticket = "",
  store = "TICKET",
  items = [
    { label: "concepto", price: "$0" },
    { label: "concepto", price: "$0" },
  ],
  totalLabel = "TOTAL",
  total = "$0",
  accentColor = theme.gold,
  startFrame = 8,
  printFrames = 44,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const rows = Array.isArray(items) ? items : [];

  const push = interpolate(frame, [0, durationInFrames], [1.0, 1.05], {
    easing: Easing.bezier(0.33, 0, 0.67, 1),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const drift = Math.sin(frame / 105) * 0.3 + 0.8;

  // print_out: la tira se revela de arriba hacia abajo (alimentacion de papel)
  const print = interpolate(frame, [startFrame, startFrame + printFrames], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.4, 0, 0.2, 1),
  });
  const hiddenPct = (1 - print) * 100;

  // total: resalta cuando termina de imprimir
  const tStart = startFrame + printFrames + 4;
  const hi = interpolate(frame, [tStart, tStart + 16], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  const paper = "#f6f2e8";
  const ink = "#1c1a17";

  return (
    <AbsoluteFill style={{ backgroundColor: "#0a0d12" }}>
      <AbsoluteFill
        style={{
          transform: `scale(${push}) rotate(${drift}deg)`,
          transformOrigin: "50% 42%",
        }}
      >
        <div
          style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            width: 540,
            transform: "translate(-50%, -50%)",
            filter: "drop-shadow(0 36px 70px rgba(0,0,0,0.55))",
            clipPath: `inset(0 0 ${hiddenPct}% 0)`,
            WebkitClipPath: `inset(0 0 ${hiddenPct}% 0)`,
          }}
        >
          <ZigZag color={ticket ? "transparent" : paper} />
          <div style={{ background: ticket ? "transparent" : paper, padding: "8px 46px 0" }}>
            {ticket ? (
              <Img
                src={staticFile(`setpieces/${ticket}.png`)}
                style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover" }}
              />
            ) : null}

            {/* ---- capa controlada (mono, como impresion termica) ---- */}
            <div style={{ position: "relative", fontFamily: theme.mono, color: ink }}>
              <div
                style={{
                  textAlign: "center",
                  fontWeight: 800,
                  fontSize: 38,
                  letterSpacing: "0.22em",
                  paddingTop: 14,
                }}
              >
                {store}
              </div>
              <div style={{ textAlign: "center", fontSize: 20, opacity: 0.6, marginTop: 8 }}>
                * * * * * * * * * * * *
              </div>

              <div style={{ borderTop: `2px dashed ${ink}55`, margin: "22px 0 18px" }} />

              {rows.map((it, i) => (
                <div
                  key={i}
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    fontSize: 28,
                    padding: "9px 0",
                  }}
                >
                  <span style={{ opacity: 0.9, maxWidth: "66%", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                    {it.label}
                  </span>
                  <span style={{ fontWeight: 700 }}>{it.price}</span>
                </div>
              ))}

              <div style={{ borderTop: `2px dashed ${ink}55`, margin: "18px 0 16px" }} />

              {/* TOTAL resaltado */}
              <div style={{ position: "relative", display: "flex", justifyContent: "space-between", alignItems: "center", padding: "8px 4px 26px" }}>
                <span style={{ fontWeight: 800, fontSize: 34, letterSpacing: "0.06em" }}>{totalLabel}</span>
                <div style={{ position: "relative", display: "inline-block" }}>
                  <div
                    style={{
                      position: "absolute",
                      left: -10,
                      right: -10,
                      top: "12%",
                      bottom: "10%",
                      background: accentColor,
                      opacity: 0.92,
                      transform: `scaleX(${hi})`,
                      transformOrigin: "right center",
                      borderRadius: 4,
                    }}
                  />
                  <span style={{ position: "relative", fontWeight: 900, fontSize: 46, color: hi > 0.6 ? "#1a160d" : ink }}>
                    {total}
                  </span>
                </div>
              </div>
            </div>
          </div>
          <ZigZag color={ticket ? "transparent" : paper} />
        </div>
      </AbsoluteFill>

      <AbsoluteFill
        style={{
          background:
            "radial-gradient(ellipse 72% 70% at 50% 46%, transparent 56%, rgba(0,0,0,0.6) 100%)",
          pointerEvents: "none",
        }}
      />
    </AbsoluteFill>
  );
};
