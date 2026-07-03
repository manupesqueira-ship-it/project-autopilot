import React, { useEffect, useState } from "react";
import { AbsoluteFill, cancelRender, continueRender, delayRender, staticFile, useCurrentFrame } from "remotion";
import { Lottie, LottieAnimationData } from "@remotion/lottie";

// LottieHero — POC: renderiza una animación LOTTIE profesional (hecha por motion designer)
// dentro de Remotion, con nuestro marco editorial. Prueba de que el craft PRO pre-hecho
// se ve mucho mejor que animación codeada a mano — sin salir del pipeline.

const FONT = "InterVar, Inter, Georgia, serif";

export type LottieHeroProps = {
  src?: string;
  kicker?: string;
  label?: string;
  caption?: string;
  bg?: "paper" | "dark";
};

export const LottieHero: React.FC<LottieHeroProps> = ({
  src = "lottie/lf20_5n8yfkac.json",
  kicker = "ANIMACIÓN PROFESIONAL",
  label = "Hecha por motion designer",
  caption = "Renderizada en Remotion · Lottie",
  bg = "paper",
}) => {
  const frame = useCurrentFrame();
  const dark = bg === "dark";
  const INK = dark ? "#F3EFE7" : "#1B1712";
  const PAPER = dark ? "#0A0B0D" : "#F1ECE1";
  const ACCENT = "#9E2B22";
  const MUTE = dark ? "#8A909B" : "#7A7264";
  const [data, setData] = useState<LottieAnimationData | null>(null);
  const [handle] = useState(() => delayRender("cargando lottie"));

  useEffect(() => {
    fetch(staticFile(src))
      .then((r) => r.json())
      .then((json) => { setData(json); continueRender(handle); })
      .catch((e) => cancelRender(e));
  }, [handle, src]);

  return (
    <AbsoluteFill style={{ backgroundColor: PAPER, fontFamily: FONT, color: INK }}>
      {dark && <div style={{ position: "absolute", left: 540 - 540, top: 400, width: 1080, height: 1080, borderRadius: "50%", background: "radial-gradient(circle, #34507E44 0%, transparent 66%)" }} />}
      <div style={{ position: "absolute", top: 78, left: 96, fontSize: 27, fontWeight: 700, letterSpacing: "0.28em", color: INK }}>DINERO&nbsp;IA</div>
      <div style={{ position: "absolute", top: 130, left: 96, width: 888, height: dark ? 1 : 2, background: dark ? "#2B2F38" : INK }} />
      {kicker && <div style={{ position: "absolute", top: 250, left: 96, fontSize: 30, fontWeight: 700, letterSpacing: "0.2em", color: ACCENT }}>{kicker}</div>}
      {label && <div style={{ position: "absolute", top: 320, left: 96, right: 96, fontSize: 64, fontWeight: 800, lineHeight: 1.04, letterSpacing: "-0.02em", color: INK }}>{label}</div>}
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
        {data && <Lottie animationData={data} loop style={{ width: 900, height: 900 }} />}
      </AbsoluteFill>
      {caption && <div style={{ position: "absolute", bottom: 150, left: 96, right: 96, fontSize: 34, fontWeight: 400, color: MUTE }}>{caption}</div>}
    </AbsoluteFill>
  );
};
