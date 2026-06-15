import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { ComposableMap, Geographies, Geography } from "react-simple-maps";
import { geoCentroid } from "d3-geo";
import { feature } from "topojson-client";
import * as Flags from "country-flag-icons/react/3x2";
import { theme } from "../theme";
import { StudioScene } from "../studio/StudioScene";
import topo from "../data/countries-50m.json";

// FeatureCollection una sola vez (modulo) — evita recomputar por frame.
// 50m = bordes con muchos mas vertices que 110m -> el pais no se ve poligonal
// al hacer fly-in cerrado.
const COUNTRIES: any = feature(topo as any, (topo as any).objects.countries);
const FEATURES: any[] = COUNTRIES.features;

const W = 1080;
const H = 1920;
const CX = W / 2; // 540
const CY = H / 2; // 960

export type MapZoomProps = {
  // nombre EXACTO como aparece en el topojson (properties.name): "El Salvador"
  countryName: string;
  // ISO-3166 alpha-2 para la bandera: "SV"
  iso2: string;
  caption?: string;
  // etiqueta grande; default = countryName
  label?: string;
  sublabel?: string;
  accentColor?: string;
  zoomStartFrame?: number;
};

export const MapZoom: React.FC<MapZoomProps> = ({
  countryName,
  iso2,
  caption,
  label,
  sublabel,
  accentColor = theme.green,
  zoomStartFrame = 6,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const target = React.useMemo(
    () => FEATURES.find((f) => f.properties.name === countryName),
    [countryName],
  );
  const centroid = React.useMemo<[number, number]>(
    () => (target ? (geoCentroid(target) as [number, number]) : [0, 0]),
    [target],
  );

  // PROYECCION FIJA, centrada en el pais: al escalar 1x se ve el continente y el
  // pais queda exactamente en (540,960). scale base ~700 => ~88 grados de lon
  // visibles a zoom 1 (todo Centroamerica + Mexico + Caribe). El centroide cae
  // en el centro de pantalla por definicion (center -> translate del proyector).
  const BASE_SCALE = 720;
  const projectionConfig = React.useMemo(
    () => ({ scale: BASE_SCALE, center: centroid }),
    [centroid],
  );

  // fly-in: zoom VECTORIAL via <g transform> SVG (no rasteriza -> nitido a todo
  // nivel, a diferencia del transform CSS sobre HTML que se difuminaba). Reproyectar
  // por frame satura el event loop a 2x; aqui la geometria se proyecta UNA vez
  // (Geographies memoizado) y solo cambia el atributo transform del <g>.
  const z = spring({
    frame: frame - zoomStartFrame,
    fps,
    config: { damping: 200, mass: 1.4, stiffness: 55 },
  });
  const zoom = interpolate(z, [0, 1], [1, 11]);
  // escala alrededor de (540,960) = centro del pais -> "zoom hacia El Salvador".
  const mapTransform = `translate(${CX} ${CY}) scale(${zoom}) translate(${-CX} ${-CY})`;

  // halo + tarjeta aterrizan cuando el zoom casi termina
  const land = spring({
    frame: frame - (zoomStartFrame + 28),
    fps,
    config: { damping: 16, mass: 0.7 },
  });
  const haloPulse = 0.5 + Math.sin(frame / 12) * 0.5;
  const ring = spring({
    frame: frame - (zoomStartFrame + 30),
    fps,
    config: { damping: 12, mass: 0.6 },
  });

  const FlagCmp: React.FC<{ title?: string; style?: React.CSSProperties }> =
    (Flags as any)[iso2.toUpperCase()] || null;

  // geografias proyectadas UNA sola vez y memoizadas (referencia estable). El <g>
  // de zoom se aplica afuera para no invalidar este memo cada frame. Sin filtros
  // SVG sobre el pais (drop-shadow re-rasteriza al escalar y mata el event loop);
  // el brillo se hace con un halo HTML estatico afuera (truco de CharacterCard).
  const geos = React.useMemo(
    () => (
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
                    fill: isTarget ? accentColor : "#202B3B",
                    stroke: isTarget ? accentColor : "#33415A",
                    strokeWidth: isTarget ? 0.5 : 0.35,
                    outline: "none",
                    opacity: isTarget ? 1 : 0.5,
                  },
                  hover: { fill: isTarget ? accentColor : "#202B3B", outline: "none" },
                  pressed: { outline: "none" },
                }}
              />
            );
          })
        }
      </Geographies>
    ),
    [countryName, accentColor],
  );

  return (
    <StudioScene spotlightColor={accentColor} grid={false}>
      <AbsoluteFill style={{ fontFamily: theme.font }}>
        {/* MAPA: SVG fijo; el zoom es un transform vectorial del grupo interior */}
        <ComposableMap
          width={W}
          height={H}
          projection="geoMercator"
          projectionConfig={projectionConfig}
          style={{ width: W, height: H }}
        >
          <g transform={mapTransform}>{geos}</g>
        </ComposableMap>

        {/* halo HTML estatico centrado en el pais (pulsa por opacidad, barato GPU) */}
        <div
          style={{
            position: "absolute",
            left: CX - 320,
            top: CY - 320,
            width: 640,
            height: 640,
            borderRadius: "50%",
            background: `radial-gradient(circle, ${accentColor}3a 0%, ${accentColor}12 40%, transparent 66%)`,
            opacity: land * haloPulse,
            pointerEvents: "none",
          }}
        />
        {/* anillo "lock-on" que aparece al aterrizar el zoom */}
        <div
          style={{
            position: "absolute",
            left: CX - 70,
            top: CY - 70,
            width: 140,
            height: 140,
            borderRadius: "50%",
            border: `3px solid ${accentColor}`,
            boxShadow: `0 0 22px ${accentColor}aa`,
            opacity: interpolate(ring, [0, 0.6, 1], [0, 0.9, 0.35], {
              extrapolateRight: "clamp",
            }),
            transform: `scale(${interpolate(ring, [0, 1], [1.6, 1], {
              extrapolateRight: "clamp",
            })})`,
            pointerEvents: "none",
          }}
        />

        {/* tarjeta bandera + nombre (10/10 — sin cambios) */}
        <AbsoluteFill
          style={{
            justifyContent: "flex-end",
            alignItems: "center",
            paddingBottom: 300,
          }}
        >
          {caption && (
            <div
              style={{
                color: theme.textDim,
                fontSize: 30,
                fontWeight: 600,
                letterSpacing: "0.04em",
                textTransform: "uppercase",
                marginBottom: 22,
                opacity: interpolate(frame, [zoomStartFrame, zoomStartFrame + 8], [0, 1], {
                  extrapolateLeft: "clamp",
                  extrapolateRight: "clamp",
                }),
              }}
            >
              {caption}
            </div>
          )}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 26,
              opacity: land,
              transform: `translateY(${(1 - land) * 30}px) scale(${0.9 + land * 0.1})`,
            }}
          >
            {FlagCmp && (
              <div
                style={{
                  width: 116,
                  height: 78,
                  borderRadius: 10,
                  overflow: "hidden",
                  boxShadow: `0 0 0 2px #ffffff22, 0 14px 40px rgba(0,0,0,0.5)`,
                  flexShrink: 0,
                }}
              >
                <FlagCmp title={countryName} style={{ width: "100%", height: "100%", display: "block" }} />
              </div>
            )}
            <div style={{ textAlign: "left" }}>
              <div
                style={{
                  color: theme.text,
                  fontSize: 76,
                  fontWeight: 900,
                  letterSpacing: "-0.02em",
                  lineHeight: 1,
                }}
              >
                {label ?? countryName}
              </div>
              {sublabel && (
                <div
                  style={{
                    color: accentColor,
                    fontSize: 34,
                    fontWeight: 700,
                    marginTop: 10,
                  }}
                >
                  {sublabel}
                </div>
              )}
            </div>
          </div>
        </AbsoluteFill>
      </AbsoluteFill>
    </StudioScene>
  );
};
