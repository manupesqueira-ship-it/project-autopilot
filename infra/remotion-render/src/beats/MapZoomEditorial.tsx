import React, { useMemo } from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { geoMercator, geoPath, geoCentroid } from "d3-geo";
import * as Flags from "country-flag-icons/react/3x2";
import { feature } from "topojson-client";
import topo from "../data/countries-50m.json";

// MapZoomEditorial — escena DINÁMICA reusable: mapa editorial (paper) con un país
// resaltado en oxblood, cámara que hace ZOOM de la región al país + micro-push
// continuo (nunca congelado). Data-driven (cualquier país vía d3-geo, no dibujado).
// Estilo de la casa: papel = océano (se funde con la página), tierra gris, país = acento.

const COUNTRIES: any = feature(topo as any, (topo as any).objects.countries);
const W = 1080;
const H = 1920;

const PAPER = "#F1ECE1";       // océano = papel (se funde con la página)
const LAND = "#DED6C6";        // tierra vecina
const LAND_STROKE = "#C4B9A4";
const ACCENT = "#9E2B22";      // país protagonista (oxblood editorial)
const ACCENT_HI = "#C24A3F";
const INK = "#1B1712";
const MUTE = "#8A806F";
const FONT = "InterVar, Inter, Georgia, serif";

// Rect SEGURO donde vive el país protagonista (grande = protagonista grande). Tunable.
// Deja banda arriba para el kicker y abajo (~1120) para nombre+bandera, sin chocar con el frame.
const RECT: [[number, number], [number, number]] = [[130, 470], [950, 1040]];
const RECT_CENTER: [number, number] = [(RECT[0][0] + RECT[1][0]) / 2, (RECT[0][1] + RECT[1][1]) / 2]; // [540, 755]

export type MapZoomEditorialProps = {
  countryName?: string;
  iso2?: string;
  label?: string;
  region?: string[];
};

export const MapZoomEditorial: React.FC<MapZoomEditorialProps> = ({
  countryName = "El Salvador",
  iso2 = "SV",
  label = "EL SALVADOR",
  region = ["Guatemala", "Honduras", "Nicaragua", "Mexico", "Belize", "Costa Rica", "Panama"],
}) => {
  const frame = useCurrentFrame();

  const { target, neighbors, centerLonLat, endK } = useMemo(() => {
    const target = COUNTRIES.features.find((f: any) => f.properties.name === countryName);
    const neighbors = COUNTRIES.features.filter(
      (f: any) => region.includes(f.properties.name) && f.properties.name !== countryName,
    );
    // UN solo fitExtent al rect SEGURO grande; leemos su scale Y centramos por el centro del rect
    // (centro-de-bbox vía invert) → el protagonista queda GRANDE y centrado para cualquier país.
    const endProj = geoMercator().fitExtent(RECT, target);
    const centerLonLat = endProj.invert!(RECT_CENTER) as [number, number];
    return { target, neighbors, centerLonLat, endK: endProj.scale() };
  }, [countryName, region]);

  // zoom región -> país (ease-out) + micro-push continuo (movimiento constante)
  const zoomT = interpolate(frame, [0, 74], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  const settledK = interpolate(zoomT, [0, 1], [endK * 0.3, endK]);
  const idle = interpolate(frame, [74, 320], [1, 1.05], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.sin) });
  const k = settledK * idle;

  const ignite = interpolate(frame, [46, 80], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.cubic) });
  const arrive = interpolate(frame, [76, 96], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const glowBreath = 0.82 + 0.18 * Math.sin(frame / 24);

  const projection = geoMercator().center(centerLonLat).scale(k).translate(RECT_CENTER);
  const pathGen = geoPath(projection);
  const cPath = pathGen(target) || "";
  const neighborPaths = neighbors.map((n: any) => ({ name: n.properties.name, d: pathGen(n) || "" }));
  const neighborLabels = neighbors
    .map((n: any) => {
      const p = projection(geoCentroid(n) as [number, number]);
      return { name: n.properties.name, x: p ? p[0] : -999, y: p ? p[1] : -999 };
    })
    .filter((l: any) => l.x > 40 && l.x < W - 40 && l.y > 220 && l.y < 1440);

  const FlagCmp: React.FC<{ style?: React.CSSProperties }> = (Flags as any)[iso2.toUpperCase()] || null;
  const cPt = projection(centerLonLat) || RECT_CENTER;

  return (
    <AbsoluteFill style={{ backgroundColor: PAPER, fontFamily: FONT }}>
      {/* halo del país protagonista */}
      <div style={{ position: "absolute", left: cPt[0] - 300, top: cPt[1] - 300, width: 600, height: 600, borderRadius: "50%", background: `radial-gradient(circle, ${ACCENT}26 0%, ${ACCENT}0D 40%, transparent 66%)`, opacity: ignite * glowBreath, transform: `scale(${1 + 0.06 * Math.sin(frame / 28)})`, pointerEvents: "none" }} />

      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{ position: "absolute", inset: 0 }}>
        <defs>
          <filter id="cglow" x="-120%" y="-120%" width="340%" height="340%"><feGaussianBlur stdDeviation="14" /></filter>
        </defs>
        {/* vecinos (contexto) */}
        {neighborPaths.map((n: any) => (
          <path key={n.name} d={n.d} fill={LAND} stroke={LAND_STROKE} strokeWidth={1.2} strokeLinejoin="round" />
        ))}
        {/* país protagonista: glow + silueta oxblood que se enciende */}
        <path d={cPath} fill={ACCENT} opacity={0.5 * ignite} filter="url(#cglow)" />
        <path d={cPath} fill={ACCENT} stroke={ACCENT_HI} strokeWidth={2} strokeLinejoin="round" opacity={interpolate(ignite, [0, 1], [0.25, 1])} />

        {/* etiquetas de vecinos (tenues) */}
        {neighborLabels.map((l: any) => (
          <text key={l.name} x={l.x} y={l.y} textAnchor="middle" fill={MUTE} fontSize={26} fontWeight={600} letterSpacing={1.5} opacity={0.5 * arrive} style={{ textTransform: "uppercase" }}>
            {l.name}
          </text>
        ))}
      </svg>

      {/* nombre del país + bandera (aterrizaje) */}
      <div style={{ position: "absolute", top: 1150, left: 0, width: "100%", textAlign: "center", opacity: arrive, transform: `translateY(${interpolate(arrive, [0, 1], [16, 0])}px)` }}>
        <div style={{ display: "inline-flex", alignItems: "center", gap: 20 }}>
          {FlagCmp && <div style={{ width: 66, height: 44, borderRadius: 5, overflow: "hidden", boxShadow: "0 2px 10px rgba(0,0,0,0.2)" }}><FlagCmp style={{ width: "100%", height: "100%", objectFit: "cover" }} /></div>}
          <div style={{ fontSize: 62, fontWeight: 800, letterSpacing: "0.02em", color: INK }}>{label}</div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
