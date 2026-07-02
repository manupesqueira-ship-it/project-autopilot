import React from "react";
import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

// Ref0x100xOrb — PRUEBA DE CRAFT (2026-07-01). Reproduce fielmente UN momento
// icónico de 0x100x (orbe verde glossy sobre la línea, mundo negro, cámara en
// deriva) para comparar LADO A LADO contra el frame real. NO es marca final; su
// único trabajo es probar o descartar que el código puede llegar a la barra.
// Referencia: _0x100x_research/clips/DF5nBHoyYMq.mp4 @ ~9s.

const W = 1080;
const H = 1920;

// --- curva estilo 0x100x: borde derecho de un area oscura, con un DIP donde
// descansa el orbe. Catmull-Rom sobre anclas -> polilinea suave, determinista. ---
const ANCHORS: [number, number][] = [
  [150, -80],
  [178, 360],
  [470, 690],   // el orbe descansa cerca de aqui (el dip)
  [500, 980],
  [360, 1230],
  [720, 1560],
  [735, 2040],
];

function catmullRom(pts: [number, number][], perSeg = 40): [number, number][] {
  const p = [pts[0], ...pts, pts[pts.length - 1]];
  const out: [number, number][] = [];
  for (let i = 1; i < p.length - 2; i++) {
    const [p0, p1, p2, p3] = [p[i - 1], p[i], p[i + 1], p[i + 2]];
    for (let s = 0; s < perSeg; s++) {
      const t = s / perSeg;
      const t2 = t * t;
      const t3 = t2 * t;
      const x =
        0.5 * (2 * p1[0] + (-p0[0] + p2[0]) * t +
        (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 +
        (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3);
      const y =
        0.5 * (2 * p1[1] + (-p0[1] + p2[1]) * t +
        (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 +
        (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3);
      out.push([x, y]);
    }
  }
  return out;
}

const PTS = catmullRom(ANCHORS);
const LINE_D = "M " + PTS.map(([x, y]) => `${x.toFixed(1)} ${y.toFixed(1)}`).join(" L ");
// area oscura a la IZQUIERDA de la linea (cierra por el borde izquierdo/inferior)
const FILL_D =
  `M 0 -80 L ${PTS.map(([x, y]) => `${x.toFixed(1)} ${y.toFixed(1)}`).join(" L ")} L 0 2040 Z`;

const GREEN = "#4ade80";

export const Ref0x100xOrb: React.FC<{ caption: string }> = ({ caption }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  // orbe cabalga la curva (baja hacia el dip) — lento
  const t = interpolate(frame, [8, durationInFrames - 8], [0.16, 0.40], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const idx = Math.min(PTS.length - 1, Math.max(0, Math.round(t * (PTS.length - 1))));
  const [ox, oy] = PTS[idx];
  const ORB = 210;

  // camara en deriva lenta (0x100x NUNCA estatico): push + drift sutil
  const camScale = interpolate(frame, [0, durationInFrames], [1.0, 1.05]);
  const camY = interpolate(frame, [0, durationInFrames], [0, -22]);
  const camX = interpolate(frame, [0, durationInFrames], [0, 10]);

  const capO = interpolate(frame, [6, 20], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ backgroundColor: "#000000" }}>
      <AbsoluteFill
        style={{ transform: `translate(${camX}px, ${camY}px) scale(${camScale})`, transformOrigin: "50% 42%" }}
      >
        <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{ position: "absolute" }}>
          <defs>
            <filter id="lineglow" x="-40%" y="-40%" width="180%" height="180%">
              <feGaussianBlur stdDeviation="5" result="b" />
              <feMerge>
                <feMergeNode in="b" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
            {/* rejilla tenue del mundo (lado derecho) */}
            <pattern id="grid" width="64" height="64" patternUnits="userSpaceOnUse">
              <path d="M 64 0 L 0 0 0 64" fill="none" stroke="#1c1c1c" strokeWidth="1" />
            </pattern>
          </defs>

          {/* grid tenue a la derecha, muy sutil */}
          <rect x="640" y="0" width="440" height={H} fill="url(#grid)" opacity="0.5" />

          {/* area oscura (la "montaña") */}
          <path d={FILL_D} fill="#0b0b0b" />
          {/* borde verde glowing = la linea del chart */}
          <path d={LINE_D} fill="none" stroke={GREEN} strokeWidth="2.6" filter="url(#lineglow)" opacity="0.95" />
        </svg>

        {/* orbe glossy: glow externo + esfera con gradiente radial + highlight */}
        <div
          style={{
            position: "absolute",
            left: ox - ORB / 2,
            top: oy - ORB / 2,
            width: ORB,
            height: ORB,
            borderRadius: "50%",
            background:
              "radial-gradient(circle at 42% 33%, #eafff0 0%, #86f7a2 24%, #35d36b 54%, #0f8f40 82%, #0a6e33 100%)",
            boxShadow:
              "0 0 90px 16px rgba(74,222,128,0.28), 0 0 34px 4px rgba(74,222,128,0.35), inset -12px -16px 34px rgba(0,45,15,0.55), inset 8px 8px 22px rgba(230,255,240,0.28)",
          }}
        />
      </AbsoluteFill>

      {/* caption blanca chica, arriba-centro (no cambia con la camara) */}
      <div
        style={{
          position: "absolute",
          top: 250,
          width: "100%",
          textAlign: "center",
          fontFamily: "InterVar, Inter, Helvetica, Arial, sans-serif",
          fontSize: 46,
          fontWeight: 600,
          color: "#FFFFFF",
          letterSpacing: "-0.005em",
          opacity: capO,
        }}
      >
        {caption}
      </div>
    </AbsoluteFill>
  );
};
