import React, { useEffect, useRef, useState } from "react";
import { AbsoluteFill, cancelRender, continueRender, delayRender, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import RiveCanvas from "@rive-app/canvas-advanced";

// RiveHero — POC: renderiza una animación RIVE (.riv) dentro de Remotion, con tiempo
// controlado por frame (time absoluto, seguro con cualquier orden de render).

export type RiveHeroProps = { src?: string };

// runtime cargado una sola vez por proceso
let RUNTIME: Awaited<ReturnType<typeof RiveCanvas>> | null = null;

export const RiveHero: React.FC<RiveHeroProps> = ({ src = "rive/vehicles.riv" }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const stateRef = useRef<{ rive: any; artboard: any; anim: any; renderer: any } | null>(null);
  const [handle] = useState(() => delayRender("rive load", { timeoutInMilliseconds: 60000 }));

  useEffect(() => {
    let active = true;
    (async () => {
      try {
        if (!RUNTIME) RUNTIME = await RiveCanvas({ locateFile: () => staticFile("rive/rive.wasm") });
        const rive: any = RUNTIME;
        const bytes = await fetch(staticFile(src)).then((r) => r.arrayBuffer());
        const file = await rive.load(new Uint8Array(bytes));
        const artboard = file.artboardByIndex(0);
        const anim = new rive.LinearAnimationInstance(artboard.animationByIndex(0), artboard);
        const renderer = rive.makeRenderer(canvasRef.current);
        if (!active) return;
        stateRef.current = { rive, artboard, anim, renderer };
        continueRender(handle);
      } catch (e) {
        cancelRender(e as Error);
      }
    })();
    return () => { active = false; };
  }, [handle, src]);

  useEffect(() => {
    const st = stateRef.current;
    const canvas = canvasRef.current;
    if (!st || !canvas) return;
    const { rive, artboard, anim, renderer } = st;
    const dur = anim.duration || 3;
    const t = (frame / fps) % dur;
    anim.time = t;
    anim.apply(1);
    artboard.advance(0);
    renderer.clear();
    renderer.save();
    renderer.align(
      rive.Fit.contain,
      rive.Alignment.center,
      { minX: 0, minY: 0, maxX: canvas.width, maxY: canvas.height },
      artboard.bounds,
    );
    artboard.draw(renderer);
    renderer.restore();
    rive.resolveAnimationFrame();
  });

  return (
    <AbsoluteFill style={{ backgroundColor: "#0A0B0D" }}>
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
        <canvas ref={canvasRef} width={1000} height={1000} style={{ width: 1000, height: 1000 }} />
      </AbsoluteFill>
      <div style={{ position: "absolute", bottom: 120, left: 96, right: 96, fontSize: 30, fontWeight: 500, color: "#8A909B", fontFamily: "Inter, sans-serif" }}>Rive · renderizado en Remotion (demo .riv)</div>
    </AbsoluteFill>
  );
};
