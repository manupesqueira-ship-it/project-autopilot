import React from "react";
import { AbsoluteFill } from "remotion";
import { theme } from "../theme";
import { Thumb } from "./Thumb";
import { StyleframeSpec } from "./types";

// El storyboard: 8-12 frames vistos juntos (aquí las 6 escenas del Reel C).
// Resolver el ARCO y la COMPOSICIÓN antes de animar nada.
export const ContactSheet: React.FC<{
  frames: StyleframeSpec[];
  thumbW?: number;
  title?: string;
}> = ({ frames, thumbW = 300, title = "Storyboard" }) => {
  return (
    <AbsoluteFill style={{ background: theme.bg.gradient, fontFamily: theme.font }}>
      <div style={{ position: "absolute", top: 30, left: 0, width: "100%", textAlign: "center", color: theme.text, fontSize: 40, fontWeight: 800 }}>
        {title}
      </div>
      <div style={{ position: "absolute", inset: 0, display: "flex", flexWrap: "wrap", gap: 30, alignContent: "center", justifyContent: "center", padding: "120px 40px 40px" }}>
        {frames.map((f, i) => (
          <Thumb key={f.id} spec={f} w={thumbW} caption={`${i}. ${f.title ?? f.id}`} />
        ))}
      </div>
    </AbsoluteFill>
  );
};
