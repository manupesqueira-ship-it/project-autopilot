import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import {
  ComposableMap,
  Geographies,
  Geography,
  Sphere,
  Graticule,
} from "react-simple-maps";
import * as Flags from "country-flag-icons/react/3x2";
import { feature } from "topojson-client";
import topo from "../data/countries-50m.json";

// FeatureCollection una sola vez (modulo).
const COUNTRIES: any = feature(topo as any, (topo as any).objects.countries);

const W = 1080;
const H = 1920;
const CX = W / 2; // 540
const GLOBE_CY = 820; // globo un poco arriba del centro -> aire abajo para la etiqueta

// LOOK & FEEL biblia igloo.inc: negro mate, UN elemento, azules frios + 1 acento
// calido (fuego naranja), restriccion extrema, tipo grotesca finisima MAYUS.
const VOID = "#070707"; // negro mate
const EMBER = "#FF7A1A"; // unico acento calido (foco = El Salvador)
const ATMO = "#5C82A6"; // azul frio (atmosfera/rim del globo)
const LAND = "#1A222D"; // tierra casi-negra (un pelo mas visible -> lee America)
const LAND_STROKE = "#2A3744"; // borde tenue

export type GlobeHeroProps = {
  countryName?: string;
  iso2?: string;
  label?: string;
  // coords del pais a centrar [lon, lat]
  lon?: number;
  lat?: number;
  scale?: number;
};

export const GlobeHero: React.FC<GlobeHeroProps> = ({
  countryName = "El Salvador",
  iso2 = "SV",
  label = "EL SALVADOR",
  lon = -88.8965,
  lat = 13.7942,
  scale = 470,
}) => {
  const frame = useCurrentFrame();

  // entrada lenta y deliberada (estilo GSAP): el globo respira, la camara casi no
  // se mueve. Todo "aterrizado" hacia ~frame 40.
  const intro = interpolate(frame, [0, 40], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const haloPulse = 0.6 + Math.sin(frame / 16) * 0.4;

  const FlagCmp: React.FC<{ title?: string; style?: React.CSSProperties }> =
    (Flags as any)[iso2.toUpperCase()] || null;

  // orthographic centrado en el pais -> el pais cae en el centro del globo, de cara
  // al espectador. rotate = [-lon, -lat, 0].
  const projectionConfig = { rotate: [-lon, -lat, 0] as [number, number, number], scale };

  const geos = (
    <Geographies geography={COUNTRIES}>
      {({ geographies }: any) =>
        geographies.map((geo: any) => {
          const isTarget = geo.properties.name === countryName;
          return (
            <Geography
              key={geo.rsmKey}
              geography={geo}
              style={{
                default: {
                  fill: isTarget ? EMBER : LAND,
                  stroke: isTarget ? EMBER : LAND_STROKE,
                  strokeWidth: isTarget ? 0.6 : 0.4,
                  outline: "none",
                },
                hover: { fill: isTarget ? EMBER : LAND, outline: "none" },
                pressed: { outline: "none" },
              }}
            />
          );
        })
      }
    </Geographies>
  );

  return (
    <AbsoluteFill style={{ backgroundColor: VOID }}>
      {/* atmosfera fria (rim) detras del globo — azul frio, volumetrica y suave */}
      <div
        style={{
          position: "absolute",
          left: CX - 560,
          top: GLOBE_CY - 560,
          width: 1120,
          height: 1120,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${ATMO}26 0%, ${ATMO}10 38%, transparent 60%)`,
          opacity: intro,
          filter: "blur(4px)",
          pointerEvents: "none",
        }}
      />

      <ComposableMap
        width={W}
        height={H}
        projection="geoOrthographic"
        projectionConfig={projectionConfig}
        style={{ width: W, height: H }}
      >
        <defs>
          {/* volumen del globo: lado iluminado frio -> terminador a negro */}
          <radialGradient id="globeBody" cx="40%" cy="34%" r="74%">
            <stop offset="0%" stopColor="#27384A" />
            <stop offset="48%" stopColor="#101822" />
            <stop offset="100%" stopColor="#04070A" />
          </radialGradient>
          {/* rim de luz fria en el borde del globo */}
          <radialGradient id="globeRim" cx="50%" cy="50%" r="50%">
            <stop offset="86%" stopColor="transparent" />
            <stop offset="97%" stopColor={`${ATMO}55`} />
            <stop offset="100%" stopColor="transparent" />
          </radialGradient>
        </defs>

        <g transform={`translate(0 ${GLOBE_CY - H / 2})`} opacity={intro}>
          {/* cuerpo del globo (oceano) con gradiente de volumen */}
          <Sphere id="sph" fill="url(#globeBody)" stroke="transparent" strokeWidth={0} />
          {/* meridianos/paralelos finisimos -> lee como globo 3D */}
          <Graticule stroke="#2E3D4C" strokeWidth={0.4} opacity={0.55} />
          {geos}
          {/* rim de luz fria encima */}
          <Sphere id="rim" fill="url(#globeRim)" stroke="transparent" strokeWidth={0} />
        </g>
      </ComposableMap>

      {/* halo calido (ember) sobre El Salvador = centro del globo */}
      <div
        style={{
          position: "absolute",
          left: CX - 200,
          top: GLOBE_CY - 200,
          width: 400,
          height: 400,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${EMBER}66 0%, ${EMBER}22 34%, transparent 62%)`,
          opacity: intro * haloPulse,
          pointerEvents: "none",
        }}
      />
      {/* anillo lock-on finisimo sobre el pais */}
      <div
        style={{
          position: "absolute",
          left: CX - 42,
          top: GLOBE_CY - 42,
          width: 84,
          height: 84,
          borderRadius: "50%",
          border: `2px solid ${EMBER}`,
          boxShadow: `0 0 26px ${EMBER}, inset 0 0 10px ${EMBER}66`,
          opacity: interpolate(intro, [0.5, 1], [0, 0.95], { extrapolateLeft: "clamp" }),
          transform: `scale(${interpolate(intro, [0.5, 1], [1.6, 1], {
            extrapolateLeft: "clamp",
          })})`,
          pointerEvents: "none",
        }}
      />

      {/* conector finisimo: del pais (speck) a la etiqueta -> anota sin recargar */}
      <div
        style={{
          position: "absolute",
          left: CX,
          top: GLOBE_CY + 36,
          width: 1,
          height: 560,
          background: `linear-gradient(180deg, ${EMBER}aa 0%, ${EMBER}22 55%, transparent 100%)`,
          opacity: interpolate(intro, [0.6, 1], [0, 0.7], { extrapolateLeft: "clamp" }),
          transformOrigin: "top",
          transform: `scaleY(${interpolate(intro, [0.6, 1], [0, 1], {
            extrapolateLeft: "clamp",
          })})`,
          pointerEvents: "none",
        }}
      />

      {/* etiqueta: grotesca finisima, MAYUS, tracking ancho, baja opacidad, 1 linea */}
      <AbsoluteFill
        style={{
          justifyContent: "flex-end",
          alignItems: "center",
          paddingBottom: 250,
          fontFamily: "InterVar, Inter, Helvetica, Arial, sans-serif",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 22,
            opacity: interpolate(intro, [0.65, 1], [0, 1], { extrapolateLeft: "clamp" }),
            transform: `translateY(${interpolate(intro, [0.65, 1], [16, 0], {
              extrapolateLeft: "clamp",
            })}px)`,
          }}
        >
          {FlagCmp && (
            <div
              style={{
                width: 64,
                height: 43,
                borderRadius: 6,
                overflow: "hidden",
                boxShadow: `0 0 0 1px #ffffff14, 0 10px 30px rgba(0,0,0,0.6)`,
                opacity: 0.92,
                flexShrink: 0,
              }}
            >
              <FlagCmp title={countryName} style={{ width: "100%", height: "100%", display: "block" }} />
            </div>
          )}
          <div
            style={{
              color: "#EAEef2",
              fontSize: 54,
              fontWeight: 200,
              letterSpacing: "0.42em",
              textTransform: "uppercase",
              opacity: 0.82,
              paddingLeft: "0.42em",
            }}
          >
            {label}
          </div>
        </div>
      </AbsoluteFill>

      {/* vignette para fundir bordes al negro */}
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(120% 80% at 50% 42%, transparent 52%, rgba(0,0,0,0.55) 100%)",
          pointerEvents: "none",
        }}
      />
      {/* grano fino */}
      <svg style={{ position: "absolute", inset: 0, width: W, height: H, opacity: 0.05, mixBlendMode: "overlay", pointerEvents: "none" }}>
        <filter id="grain">
          <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" stitchTiles="stitch" />
        </filter>
        <rect width={W} height={H} filter="url(#grain)" />
      </svg>
    </AbsoluteFill>
  );
};
