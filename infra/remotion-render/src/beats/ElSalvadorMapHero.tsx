import React, { useMemo } from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  useCurrentFrame,
} from "remotion";
import { geoMercator, geoPath, geoCentroid } from "d3-geo";
import * as Flags from "country-flag-icons/react/3x2";
import { feature } from "topojson-client";
import topo from "../data/countries-50m.json";

const COUNTRIES: any = feature(topo as any, (topo as any).objects.countries);

const W = 1080;
const H = 1920;

// Biblia igloo.inc
const VOID = "#070707";
const OCEAN = "#0A1018"; // oceano frio, un punto mas claro para separar de la tierra
const LAND = "#273947"; // tierra obsidiana MAS iluminada (se ve bien, no vacio negro)
const LAND_STROKE = "#496074"; // bordes visibles para que los paises se lean
const ACCENT = "#00D9A5"; // verde de marca (igual que la web) — El Salvador protagonista
const ACCENT_HI = "#7CFFE0"; // realce mint para el degradado interno
const ACCENT_DEEP = "#007A5E"; // verde profundo (base del degradado)

const REGION = [
  "Guatemala",
  "Honduras",
  "Nicaragua",
  "Mexico",
  "Belize",
  "Costa Rica",
  "Panama",
];

// El Salvador se ancla SIEMPRE aqui en pantalla -> el zoom cae recto sobre el pais.
const ANCHOR: [number, number] = [W / 2, 835];

export type ElSalvadorMapHeroProps = {
  countryName?: string;
  iso2?: string;
  label?: string;
  sublabel?: string;
};

export const ElSalvadorMapHero: React.FC<ElSalvadorMapHeroProps> = ({
  countryName = "El Salvador",
  iso2 = "SV",
  label = "EL SALVADOR",
  sublabel = "",
}) => {
  const frame = useCurrentFrame();

  // Geometria fija (no depende del frame): features + centroide + escala destino.
  const { sv, neighbors, svLonLat, endK } = useMemo(() => {
    const sv = COUNTRIES.features.find(
      (f: any) => f.properties.name === countryName
    );
    const neighbors = COUNTRIES.features.filter(
      (f: any) =>
        REGION.includes(f.properties.name) &&
        f.properties.name !== countryName
    );
    const svLonLat = geoCentroid(sv) as [number, number];
    // Encuadre destino aprobado: El Salvador protagonista, vecinos de contexto.
    const endProj = geoMercator().fitExtent(
      [
        [330, 660],
        [750, 1010],
      ],
      sv
    );
    const endK = endProj.scale();
    return { sv, neighbors, svLonLat, endK };
  }, [countryName]);

  // Push-in deliberado (estilo igloo.inc): de la region al pais. ease-out.
  const startK = endK * 0.28;
  const zoomT = interpolate(frame, [0, 72], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const settledK = interpolate(zoomT, [0, 1], [startK, endK]);
  // vida en reposo: micro-push continuo tras aterrizar (NUNCA congelado durante
  // la narracion larga). Movimiento lento igloo.inc, re-proyectado por-frame =>
  // todo (pais + vecinos + etiquetas) sigue coherente.
  const idleCreep = interpolate(frame, [72, 270], [1, 1.04], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.sin),
  });
  const k = settledK * idleCreep;
  // respiracion de la brasa (halo + silueta) cuando ya esta encendido
  const emberBreath = 0.86 + 0.14 * Math.sin(frame / 26);

  // El Salvador se ENCIENDE al acercarnos (antes = obsidiana como sus vecinos).
  const ignite = interpolate(frame, [44, 78], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.cubic),
  });
  // Nombre + bandera + etiquetas de vecinos: revelan al aterrizar.
  const arrive = interpolate(frame, [74, 92], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Proyeccion por-frame: El Salvador clavado en ANCHOR, escala interpolada.
  const projection = geoMercator().center(svLonLat).scale(k).translate(ANCHOR);
  const pathGen = geoPath(projection);
  const svPath = pathGen(sv) || "";
  const neighborPaths = neighbors.map((n: any) => ({
    name: n.properties.name,
    d: pathGen(n) || "",
  }));
  const neighborLabels = neighbors
    .map((n: any) => {
      const p = projection(geoCentroid(n) as [number, number]);
      return { name: n.properties.name, x: p ? p[0] : -999, y: p ? p[1] : -999 };
    })
    .filter(
      (l: any) => l.x > 40 && l.x < W - 40 && l.y > 120 && l.y < H - 260
    );

  const FlagCmp: React.FC<{ title?: string; style?: React.CSSProperties }> =
    (Flags as any)[iso2.toUpperCase()] || null;

  return (
    <AbsoluteFill style={{ backgroundColor: VOID }}>
      {/* oceano frio */}
      <AbsoluteFill style={{ backgroundColor: OCEAN }} />

      {/* halo de brasa detras de El Salvador (crece con el encendido) */}
      <div
        style={{
          position: "absolute",
          left: ANCHOR[0] - 360,
          top: ANCHOR[1] - 360,
          width: 720,
          height: 720,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${ACCENT}33 0%, ${ACCENT}12 38%, transparent 64%)`,
          opacity: ignite * emberBreath,
          transform: `scale(${1 + 0.05 * Math.sin(frame / 30)})`,
          mixBlendMode: "screen",
          pointerEvents: "none",
        }}
      />

      <svg
        width={W}
        height={H}
        viewBox={`0 0 ${W} ${H}`}
        style={{ position: "absolute", inset: 0 }}
      >
        <defs>
          <radialGradient id="emberFill" cx="50%" cy="42%" r="62%">
            <stop offset="0%" stopColor={ACCENT_HI} />
            <stop offset="55%" stopColor={ACCENT} />
            <stop offset="100%" stopColor={ACCENT_DEEP} />
          </radialGradient>
          <filter id="svGlow" x="-120%" y="-120%" width="340%" height="340%">
            <feGaussianBlur stdDeviation="22" />
          </filter>
        </defs>

        {/* vecinos en obsidiana (contexto geografico) */}
        {neighborPaths.map((n: any) => (
          <path
            key={n.name}
            d={n.d}
            fill={LAND}
            stroke={LAND_STROKE}
            strokeWidth={1.4}
            strokeLinejoin="round"
          />
        ))}

        {/* El Salvador base obsidiana (visible desde el inicio del zoom) */}
        <path
          d={svPath}
          fill={LAND}
          stroke={LAND_STROKE}
          strokeWidth={1.4}
          strokeLinejoin="round"
        />
        {/* resplandor de la silueta al encender */}
        <path
          d={svPath}
          fill={ACCENT}
          opacity={0.85 * ignite * emberBreath}
          filter="url(#svGlow)"
        />
        {/* El Salvador encendido = protagonista */}
        <path
          d={svPath}
          fill="url(#emberFill)"
          stroke={ACCENT_HI}
          strokeWidth={3}
          strokeLinejoin="round"
          opacity={ignite}
        />
      </svg>

      {/* etiquetas tenues de vecinos (test del extraño) */}
      <AbsoluteFill
        style={{
          fontFamily: "InterVar, Inter, Helvetica, Arial, sans-serif",
          pointerEvents: "none",
        }}
      >
        {neighborLabels.map((l: any) => (
          <div
            key={l.name}
            style={{
              position: "absolute",
              left: l.x,
              top: l.y,
              transform: "translate(-50%,-50%)",
              color: "#8497A9",
              fontSize: 24,
              fontWeight: 300,
              letterSpacing: "0.32em",
              textTransform: "uppercase",
              opacity: 0.8 * arrive,
              whiteSpace: "nowrap",
            }}
          >
            {l.name}
          </div>
        ))}
      </AbsoluteFill>

      {/* nombre del pais protagonista + bandera */}
      <AbsoluteFill
        style={{
          justifyContent: "flex-end",
          alignItems: "center",
          paddingBottom: 300,
          fontFamily: "InterVar, Inter, Helvetica, Arial, sans-serif",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 24,
            opacity: arrive,
            transform: `translateY(${interpolate(arrive, [0, 1], [18, 0])}px)`,
          }}
        >
          {FlagCmp && (
            <div
              style={{
                width: 72,
                height: 48,
                borderRadius: 7,
                overflow: "hidden",
                boxShadow: `0 0 0 1px #ffffff1a, 0 12px 34px rgba(0,0,0,0.65)`,
                flexShrink: 0,
              }}
            >
              <FlagCmp
                title={countryName}
                style={{ width: "100%", height: "100%", display: "block" }}
              />
            </div>
          )}
          <div
            style={{
              color: "#EAEEF2",
              fontSize: 62,
              fontWeight: 200,
              letterSpacing: "0.4em",
              textTransform: "uppercase",
              paddingLeft: "0.4em",
            }}
          >
            {label}
          </div>
        </div>
        {sublabel && (
          <div
            style={{
              marginTop: 20,
              color: "#7E8C9A",
              fontSize: 25,
              fontWeight: 300,
              letterSpacing: "0.34em",
              textTransform: "uppercase",
              opacity: 0.9 * arrive,
            }}
          >
            {sublabel}
          </div>
        )}
      </AbsoluteFill>

      {/* vignette */}
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(120% 80% at 50% 44%, transparent 50%, rgba(0,0,0,0.6) 100%)",
          pointerEvents: "none",
        }}
      />
      {/* grano fino */}
      <svg
        style={{
          position: "absolute",
          inset: 0,
          width: W,
          height: H,
          opacity: 0.05,
          mixBlendMode: "overlay",
          pointerEvents: "none",
        }}
      >
        <filter id="grainMap">
          <feTurbulence
            type="fractalNoise"
            baseFrequency="0.9"
            numOctaves="2"
            stitchTiles="stitch"
          />
        </filter>
        <rect width={W} height={H} filter="url(#grainMap)" />
      </svg>
    </AbsoluteFill>
  );
};
