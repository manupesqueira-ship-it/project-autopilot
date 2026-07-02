import React from "react";
import { Styleframe, LAB_W, LAB_H } from "./Styleframe";
import { StyleframeSpec } from "./types";

// Miniatura de un styleframe a 1080x1920 escalado a un ancho dado.
export const Thumb: React.FC<{
  spec: StyleframeSpec;
  w: number;
  showSafe?: boolean;
  showUI?: boolean;
  showGrid?: boolean;
  caption?: string;
}> = ({ spec, w, showSafe = false, showUI = false, showGrid = false, caption }) => {
  const scale = w / LAB_W;
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 8, fontFamily: "Inter, sans-serif" }}>
      <div style={{ width: w, height: LAB_H * scale, position: "relative", borderRadius: 10, overflow: "hidden", outline: "1px solid rgba(255,255,255,0.12)" }}>
        <div style={{ position: "absolute", top: 0, left: 0, width: LAB_W, height: LAB_H, transform: `scale(${scale})`, transformOrigin: "top left" }}>
          <Styleframe spec={spec} showSafe={showSafe} showUI={showUI} showGrid={showGrid} />
        </div>
      </div>
      {caption ? <div style={{ width: w, textAlign: "center", fontSize: 20, color: "rgba(255,255,255,0.7)" }}>{caption}</div> : null}
    </div>
  );
};
