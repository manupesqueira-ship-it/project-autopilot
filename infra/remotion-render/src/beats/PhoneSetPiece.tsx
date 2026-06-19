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

// Set-piece "telefono" (motion notification_in): el telefono es el OBJETO (foto
// gpt-image en public/setpieces/<slug>.png con la PANTALLA EN BLANCO) y la UI /
// CIFRA van en capa CONTROLADA (Remotion): una notificacion ENTRA deslizando y
// el monto aparece. Sin foto cae a un telefono PROCEDURAL ($0, render-testable):
// cuerpo redondeado + isla dinamica + barra de estado + pantalla de marca.
//
// Alto reuso para fintech/ahorro (saldo, transferencia, alerta). El monto va en
// el overlay (la IA escribe mal las cifras). Copy/dato EXACTO -> Manuel.

export type PhoneSetPieceProps = {
  phone?: string; // slug en public/setpieces/<slug>.png ("" -> procedural)
  appName?: string; // emisor de la notificacion (banner)
  screenLabel?: string; // que muestra la pantalla (slot)
  amount?: string; // el monto / cifra (slot, acento)
  accentColor?: string;
  statusTime?: string;
  startFrame?: number;
};

export const PhoneSetPiece: React.FC<PhoneSetPieceProps> = ({
  phone = "",
  appName = "Tu banco",
  screenLabel = "saldo disponible",
  amount = "$0",
  accentColor = theme.green,
  statusTime = "9:41",
  startFrame = 10,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const push = interpolate(frame, [0, durationInFrames], [1.0, 1.05], {
    easing: Easing.bezier(0.33, 0, 0.67, 1),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const drift = Math.sin(frame / 110) * 0.3;

  // notificacion: entra deslizando desde arriba con micro-overshoot
  const nin = interpolate(frame, [startFrame, startFrame + 14], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.2, 1.2, 0.4, 1),
  });
  const notifY = interpolate(nin, [0, 1], [-130, 0]);

  // monto: pop-in despues del banner (escala + fade)
  const aStart = startFrame + 26;
  const ap = interpolate(frame, [aStart, aStart + 16], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.2, 1.25, 0.4, 1),
  });

  return (
    <AbsoluteFill style={{ backgroundColor: "#0a0d12" }}>
      <AbsoluteFill
        style={{
          transform: `scale(${push}) rotate(${drift}deg)`,
          transformOrigin: "50% 48%",
        }}
      >
        <div
          style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            width: 540,
            height: 1120,
            transform: "translate(-50%, -50%)",
          }}
        >
          {phone ? (
            <Img
              src={staticFile(`setpieces/${phone}.png`)}
              style={{ width: "100%", height: "100%", objectFit: "contain" }}
            />
          ) : (
            // cuerpo del telefono procedural
            <div
              style={{
                position: "absolute",
                inset: 0,
                background: "#0e1116",
                borderRadius: 68,
                boxShadow:
                  "0 50px 120px rgba(0,0,0,0.6), inset 0 0 0 3px rgba(255,255,255,0.06)",
                padding: 14,
                boxSizing: "border-box",
              }}
            >
              <div
                style={{
                  position: "absolute",
                  inset: 14,
                  borderRadius: 56,
                  background: theme.bg.gradient,
                  overflow: "hidden",
                }}
              />
              {/* isla dinamica */}
              <div
                style={{
                  position: "absolute",
                  top: 30,
                  left: "50%",
                  transform: "translateX(-50%)",
                  width: 132,
                  height: 34,
                  background: "#000",
                  borderRadius: 18,
                  zIndex: 3,
                }}
              />
            </div>
          )}

          {/* ---- capa controlada (UI). Vive en la pantalla, sobre el objeto ---- */}
          <div
            style={{
              position: "absolute",
              inset: phone ? "8% 12%" : 28,
              borderRadius: 52,
              overflow: "hidden",
              display: "flex",
              flexDirection: "column",
            }}
          >
            {/* barra de estado */}
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                padding: "26px 40px 0",
                fontFamily: theme.font,
                color: theme.text,
                fontSize: 26,
                fontWeight: 700,
              }}
            >
              <span>{statusTime}</span>
              <div style={{ display: "flex", gap: 8, alignItems: "center", opacity: 0.9 }}>
                {[10, 14, 18, 22].map((h, i) => (
                  <div key={i} style={{ width: 6, height: h, background: theme.text, borderRadius: 2 }} />
                ))}
                <div
                  style={{
                    width: 34,
                    height: 18,
                    marginLeft: 6,
                    borderRadius: 4,
                    border: `2px solid ${theme.text}`,
                    position: "relative",
                  }}
                >
                  <div style={{ position: "absolute", inset: 2, width: "70%", background: theme.green, borderRadius: 2 }} />
                </div>
              </div>
            </div>

            {/* notificacion que ENTRA deslizando */}
            <div
              style={{
                margin: "40px 30px 0",
                padding: "20px 22px",
                borderRadius: 26,
                background: "rgba(20,26,38,0.82)",
                backdropFilter: "blur(8px)",
                border: "1px solid rgba(255,255,255,0.10)",
                display: "flex",
                alignItems: "center",
                gap: 16,
                transform: `translateY(${notifY}px)`,
                opacity: interpolate(nin, [0, 0.4], [0, 1]),
                boxShadow: "0 18px 40px rgba(0,0,0,0.4)",
              }}
            >
              <div
                style={{
                  width: 52,
                  height: 52,
                  borderRadius: 14,
                  background: `linear-gradient(135deg, ${accentColor}, ${theme.teal})`,
                  flexShrink: 0,
                }}
              />
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontFamily: theme.font, fontWeight: 800, fontSize: 28, color: theme.text }}>
                  {appName}
                </div>
                <div style={{ fontFamily: theme.font, fontSize: 24, color: theme.textDim, marginTop: 2 }}>
                  {screenLabel}
                </div>
              </div>
              <span style={{ fontFamily: theme.font, fontSize: 20, color: theme.textDim }}>ahora</span>
            </div>

            {/* el monto, protagonista al centro de la pantalla */}
            <div
              style={{
                flex: 1,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                gap: 14,
                padding: "0 30px 80px",
              }}
            >
              <div
                style={{
                  fontFamily: theme.font,
                  fontSize: 30,
                  letterSpacing: "0.04em",
                  textTransform: "uppercase",
                  color: theme.textDim,
                  opacity: interpolate(ap, [0, 0.5], [0, 1]),
                }}
              >
                {screenLabel}
              </div>
              <div
                style={{
                  fontFamily: theme.font,
                  fontWeight: 900,
                  fontSize: 112,
                  lineHeight: 1,
                  color: accentColor,
                  transform: `scale(${interpolate(ap, [0, 1], [0.8, 1])})`,
                  opacity: interpolate(ap, [0, 0.4], [0, 1]),
                  textShadow: `0 0 40px ${accentColor}40`,
                }}
              >
                {amount}
              </div>
            </div>
          </div>
        </div>
      </AbsoluteFill>

      <AbsoluteFill
        style={{
          background:
            "radial-gradient(ellipse 70% 64% at 50% 50%, transparent 56%, rgba(0,0,0,0.62) 100%)",
          pointerEvents: "none",
        }}
      />
    </AbsoluteFill>
  );
};
