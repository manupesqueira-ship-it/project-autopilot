import React from "react";
import { AbsoluteFill, Easing, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";

// PhotoHero — momento creativo con una FOTO REAL (dominio público) de una figura pública:
// zoom-out cinematográfico (Ken Burns) sobre la foto tratada al look editorial oscuro +
// nuestro BTC vectorial real apareciendo enfrente. 100% automatizable y legal (foto PD).

const FONT = "InterVar, Inter, Georgia, serif";
const INK = "#F3EFE7", MUTE = "#9AA0AA", ACCENT = "#E45B4E";

export type PhotoHeroProps = {
  photo?: string;
  kicker?: string;
  headline?: string;
  sub?: string;
  btc?: string;
};

export const PhotoHero: React.FC<PhotoHeroProps> = ({
  photo = "photos/trump.jpg",
  kicker = "CRIPTO · LA NOTICIA",
  headline = "El poder entra al Bitcoin",
  sub = "20 BTC ≈ $1.24 M USD",
  btc = "logos/bitcoin.svg",
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  // zoom-out: arranca cerca de la cara, se aleja revelando (Ken Burns)
  const scale = interpolate(frame, [0, durationInFrames], [1.55, 1.08], { extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  const py = interpolate(frame, [0, durationInFrames], [-60, 20], { extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  const photoO = interpolate(frame, [0, 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  // el BTC se revela enfrente al alejarse la cámara
  const coin = Math.min(1, spring({ frame: frame - 34, fps, config: { damping: 12, stiffness: 120 } }));
  const kO = interpolate(frame, [8, 22], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const hO = interpolate(frame, [40, 56], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const coinFloat = Math.sin(frame / 22) * 8;

  return (
    <AbsoluteFill style={{ backgroundColor: "#0A0B0D", fontFamily: FONT }}>
      {/* foto real tratada al look editorial oscuro */}
      <AbsoluteFill style={{ overflow: "hidden", opacity: photoO }}>
        <Img src={staticFile(photo)} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: "50% 18%", transform: `scale(${scale}) translateY(${py}px)`, filter: "grayscale(0.55) contrast(1.08) brightness(0.72) sepia(0.12)" }} />
        <AbsoluteFill style={{ background: "radial-gradient(120% 90% at 50% 30%, transparent 30%, rgba(10,11,13,0.55) 72%, rgba(10,11,13,0.95) 100%)" }} />
        <AbsoluteFill style={{ background: "linear-gradient(to bottom, rgba(10,11,13,0.5) 0%, transparent 22%, transparent 52%, rgba(10,11,13,0.96) 100%)" }} />
      </AbsoluteFill>

      {/* BTC vectorial real (nuestro logo), revelado enfrente */}
      <div style={{ position: "absolute", left: 540 - 200, top: 1030 + coinFloat, width: 400, height: 400, transform: `scale(${coin})`, transformOrigin: "50% 50%" }}>
        <div style={{ position: "absolute", inset: -70, borderRadius: "50%", background: "radial-gradient(circle, rgba(247,147,26,0.45) 0%, transparent 66%)" }} />
        <Img src={staticFile(btc)} style={{ width: 400, height: 400, filter: "drop-shadow(0 24px 60px rgba(0,0,0,0.6))" }} />
      </div>

      {/* marco editorial */}
      <div style={{ position: "absolute", top: 78, left: 96, fontSize: 27, fontWeight: 700, letterSpacing: "0.28em", color: INK }}>DINERO&nbsp;IA</div>
      <div style={{ position: "absolute", top: 130, left: 96, width: 888, height: 1, background: "#2B2F38" }} />
      <div style={{ position: "absolute", top: 250, left: 96, fontSize: 30, fontWeight: 700, letterSpacing: "0.2em", color: ACCENT, opacity: kO }}>{kicker}</div>

      {/* titular + dato abajo */}
      <div style={{ position: "absolute", bottom: 250, left: 96, right: 96, fontSize: 82, fontWeight: 800, lineHeight: 1.04, letterSpacing: "-0.02em", color: INK, opacity: hO, transform: `translateY(${interpolate(hO, [0, 1], [22, 0])}px)` }}>{headline}</div>
      <div style={{ position: "absolute", bottom: 170, left: 96, right: 96, fontSize: 44, fontWeight: 600, color: MUTE, opacity: hO }}>{sub}</div>
    </AbsoluteFill>
  );
};
