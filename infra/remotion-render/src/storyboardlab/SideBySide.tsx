import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { theme } from "../theme";
import { Thumb } from "./Thumb";
import { LAB_W, LAB_H } from "./Styleframe";
import { StyleframeSpec } from "./types";

// Comparación referencia | nuestro DENTRO del lab (para styleframes).
// Para comparar VIDEO renderizado vs. referencia se usa infra/grammar/sidebyside/compare.py.
// Si aún no hay referencia (MP4 no entregado), el lado izq. muestra el hueco explícito.
export const SideBySide: React.FC<{
  ours: StyleframeSpec;
  refImageSrc?: string | null;
  refSpec?: StyleframeSpec | null;
  colW?: number;
}> = ({ ours, refImageSrc = null, refSpec = null, colW = 520 }) => {
  const h = LAB_H * (colW / LAB_W);
  return (
    <AbsoluteFill style={{ background: theme.bg.base, fontFamily: theme.font }}>
      <div style={{ position: "absolute", inset: 0, display: "flex", gap: 28, alignItems: "center", justifyContent: "center" }}>
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          <div style={{ color: theme.textDim, fontSize: 22, textAlign: "center", textTransform: "uppercase", letterSpacing: 2 }}>Referencia</div>
          {refImageSrc ? (
            <div style={{ width: colW, height: h, borderRadius: 10, overflow: "hidden", outline: "1px solid rgba(255,255,255,0.12)" }}>
              <Img src={staticFile(refImageSrc)} style={{ width: colW, height: h, objectFit: "cover" }} />
            </div>
          ) : refSpec ? (
            <Thumb spec={refSpec} w={colW} />
          ) : (
            <div style={{ width: colW, height: h, borderRadius: 10, border: `2px dashed ${theme.red}`, display: "flex", alignItems: "center", justifyContent: "center", textAlign: "center", color: theme.textDim, padding: 24 }}>
              referencia pendiente<br />(MP4 no entregado)
            </div>
          )}
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          <div style={{ color: theme.green, fontSize: 22, textAlign: "center", textTransform: "uppercase", letterSpacing: 2 }}>Nuestro</div>
          <Thumb spec={ours} w={colW} showSafe />
        </div>
      </div>
    </AbsoluteFill>
  );
};
