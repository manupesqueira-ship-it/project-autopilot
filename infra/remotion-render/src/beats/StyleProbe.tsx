import React from "react";
import { AbsoluteFill } from "remotion";

// StyleProbe — COMPÁS DE ESTILOS (2026-07-01). NO es diseño final; es un
// direction-finder: la MISMA info en mundos visuales MUY distintos para que
// Manuel señale "este mundo sí / este no". Nos alejamos del dark-minimal-abstracto
// (rechazado). Cada variante = una dirección deliberadamente diferente.

export type Variant = "editorial" | "bold" | "fintech";

const FONT = "InterVar, Inter, Helvetica, Arial, sans-serif";

export const StyleProbe: React.FC<{ variant: Variant }> = ({ variant }) => {
  if (variant === "editorial") {
    // Editorial claro y serio (tipo revista financiera premium: Monocle/Economist)
    return (
      <AbsoluteFill style={{ backgroundColor: "#F3EFE6", fontFamily: FONT, color: "#17130D" }}>
        <div style={{ position: "absolute", top: 150, left: 90, right: 90, height: 3, background: "#17130D" }} />
        <div style={{ position: "absolute", top: 180, left: 90, fontSize: 30, fontWeight: 600, letterSpacing: "0.24em", textTransform: "uppercase", color: "#8A2B1E" }}>
          El costo de no mover tu dinero
        </div>
        <div style={{ position: "absolute", top: 470, left: 90, fontSize: 34, fontWeight: 500, color: "#6B6357" }}>
          Dejas en efectivo
        </div>
        <div style={{ position: "absolute", top: 520, left: 84, fontSize: 190, fontWeight: 800, letterSpacing: "-0.03em", lineHeight: 1 }}>
          $100,000
        </div>
        <div style={{ position: "absolute", top: 980, left: 90, right: 90, height: 1, background: "#C9C0AE" }} />
        <div style={{ position: "absolute", top: 1040, left: 90, fontSize: 34, fontWeight: 500, color: "#6B6357" }}>
          Un año después, en poder de compra
        </div>
        <div style={{ position: "absolute", top: 1090, left: 84, fontSize: 190, fontWeight: 800, letterSpacing: "-0.03em", lineHeight: 1, color: "#8A2B1E" }}>
          $96,209
        </div>
        <div style={{ position: "absolute", bottom: 150, left: 90, fontSize: 40, fontWeight: 600 }}>
          <span style={{ color: "#8A2B1E" }}>−$3,791</span> se los comió la inflación
        </div>
        <div style={{ position: "absolute", bottom: 96, left: 90, fontSize: 24, fontWeight: 500, letterSpacing: "0.2em", textTransform: "uppercase", color: "#9A9488" }}>
          DINERO IA · INFLACIÓN 3.94%
        </div>
      </AbsoluteFill>
    );
  }

  if (variant === "bold") {
    // Bold moderno: alto contraste, tipografía enorme, un acento vivo, energético
    return (
      <AbsoluteFill style={{ backgroundColor: "#0E0E10", fontFamily: FONT, color: "#FFFFFF" }}>
        <div style={{ position: "absolute", top: 150, left: 80, right: 80, fontSize: 64, fontWeight: 800, lineHeight: 1.02, letterSpacing: "-0.02em" }}>
          TU DINERO<br />PIERDE<br /><span style={{ color: "#FF5A3C" }}>SIN QUE LO VEAS</span>
        </div>
        {/* bloque de acento */}
        <div style={{ position: "absolute", top: 720, left: 80, width: 920, background: "#FF5A3C", borderRadius: 28, padding: "44px 48px" }}>
          <div style={{ fontSize: 34, fontWeight: 700, color: "#2A0A02", letterSpacing: "0.02em" }}>EN EFECTIVO, 1 AÑO</div>
          <div style={{ fontSize: 150, fontWeight: 900, color: "#140400", letterSpacing: "-0.03em", lineHeight: 1.05 }}>
            $100,000
          </div>
          <div style={{ fontSize: 96, fontWeight: 900, color: "#140400", letterSpacing: "-0.03em", lineHeight: 1.1 }}>
            → $96,209
          </div>
        </div>
        <div style={{ position: "absolute", bottom: 150, left: 80, fontSize: 100, fontWeight: 900, color: "#FF5A3C", letterSpacing: "-0.03em" }}>
          −$3,791
        </div>
        <div style={{ position: "absolute", bottom: 96, left: 82, fontSize: 34, fontWeight: 700, color: "#B9B9C2" }}>
          se lo comió la inflación · 3.94%
        </div>
      </AbsoluteFill>
    );
  }

  // fintech: claro, limpio, amable, con una gráfica simple y clara
  return (
    <AbsoluteFill style={{ backgroundColor: "#0B1020", fontFamily: FONT, color: "#0B1020" }}>
      {/* tarjeta clara flotante sobre fondo azul profundo */}
      <div style={{ position: "absolute", top: 210, left: 70, right: 70, bottom: 210, background: "#FFFFFF", borderRadius: 44, boxShadow: "0 40px 90px rgba(0,0,0,0.45)" }} />
      <div style={{ position: "absolute", top: 300, left: 130, fontSize: 34, fontWeight: 600, color: "#5B667E" }}>
        $100,000 en efectivo, 12 meses
      </div>
      <div style={{ position: "absolute", top: 360, left: 126, fontSize: 150, fontWeight: 800, letterSpacing: "-0.03em", color: "#0B1020" }}>
        $96,209
      </div>
      <div style={{ position: "absolute", top: 560, left: 130, display: "flex", alignItems: "center", gap: 14 }}>
        <span style={{ fontSize: 40, fontWeight: 800, color: "#E5484D" }}>−$3,791</span>
        <span style={{ fontSize: 30, fontWeight: 600, color: "#5B667E" }}>poder de compra</span>
      </div>
      {/* barras simples: 100 vs 96.2 */}
      <div style={{ position: "absolute", left: 130, right: 130, top: 720, bottom: 360, display: "flex", alignItems: "flex-end", gap: 60 }}>
        <div style={{ flex: 1, height: "100%", background: "#0B1020", borderRadius: "16px 16px 0 0" }} />
        <div style={{ flex: 1, height: "96.2%", background: "#E5484D", borderRadius: "16px 16px 0 0" }} />
      </div>
      <div style={{ position: "absolute", left: 130, right: 130, bottom: 300, display: "flex", gap: 60 }}>
        <div style={{ flex: 1, textAlign: "center", fontSize: 28, fontWeight: 700, color: "#0B1020" }}>hoy</div>
        <div style={{ flex: 1, textAlign: "center", fontSize: 28, fontWeight: 700, color: "#E5484D" }}>en un año</div>
      </div>
    </AbsoluteFill>
  );
};
