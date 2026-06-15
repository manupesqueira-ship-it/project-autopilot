import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { ComposableMap, Geographies, Geography, Marker } from "react-simple-maps";
import { geoCentroid } from "d3-geo";
import { feature } from "topojson-client";
import * as Flags from "country-flag-icons/react/3x2";
import { theme } from "../theme";
import { StudioScene } from "../studio/StudioScene";
import topo from "../data/countries-50m.json";

// Mapa multi-pais: varios paises resaltados a la vez (region), cada uno se
// "enciende" con marcador pulsante + fila de leyenda con bandera, escalonado.
// A diferencia de MapZoom NO hace fly-in; muestra el conjunto. El fill de los
// paises es estatico (Geographies memoizado) -> barato; el storytelling vive en
// los markers + la lista lateral que aparecen con stagger.
const COUNTRIES: any = feature(topo as any, (topo as any).objects.countries);
const FEATURES: any[] = COUNTRIES.features;

const W = 1080;
const H = 1920;

export type MultiMapCountry = {
  // properties.name exacto del topojson: "El Salvador", "Argentina"
  name: string;
  iso2: string;
  label?: string;
};

export type MultiMapProps = {
  caption?: string;
  title?: string;
  sublabel?: string;
  countries: MultiMapCountry[];
  // centro de proyeccion [lon,lat]; default = promedio de centroides
  center?: [number, number];
  // escala base geoMercator; mas grande = mas cerca. default 380 (region)
  scale?: number;
  accentColor?: string;
};

export const MultiMap: React.FC<MultiMapProps> = ({
  caption,
  title,
  sublabel,
  countries,
  center,
  scale = 380,
  accentColor = theme.green,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const clamp = {
    extrapolateLeft: "clamp" as const,
    extrapolateRight: "clamp" as const,
  };

  const nameSet = React.useMemo(
    () => new Set(countries.map((c) => c.name)),
    [countries],
  );

  // centroide de cada pais objetivo (para markers) + centro de la region
  const targets = React.useMemo(
    () =>
      countries.map((c) => {
        const f = FEATURES.find((g) => g.properties.name === c.name);
        const cen = f ? (geoCentroid(f) as [number, number]) : [0, 0];
        return { ...c, centroid: cen as [number, number] };
      }),
    [countries],
  );

  const autoCenter = React.useMemo<[number, number]>(() => {
    if (center) return center;
    const lon = targets.reduce((s, t) => s + t.centroid[0], 0) / targets.length;
    const lat = targets.reduce((s, t) => s + t.centroid[1], 0) / targets.length;
    return [lon, lat];
  }, [center, targets]);

  const projectionConfig = React.useMemo(
    () => ({ scale, center: autoCenter }),
    [scale, autoCenter],
  );

  // fill estatico -> memoizable (no recomputar geografias por frame)
  const geos = React.useMemo(
    () => (
      <Geographies geography={COUNTRIES}>
        {({ geographies }: any) =>
          geographies.map((geo: any) => {
            const isHi = nameSet.has(geo.properties.name);
            return (
              <Geography
                key={geo.rsmKey}
                geography={geo}
                style={{
                  default: {
                    fill: isHi ? accentColor : "#1C2636",
                    stroke: isHi ? accentColor : "#33415A",
                    strokeWidth: isHi ? 0.6 : 0.3,
                    outline: "none",
                    opacity: isHi ? 0.92 : 0.42,
                  },
                  hover: {
                    fill: isHi ? accentColor : "#1C2636",
                    outline: "none",
                  },
                  pressed: { outline: "none" },
                }}
              />
            );
          })
        }
      </Geographies>
    ),
    [nameSet, accentColor],
  );

  const REVEAL_START = 14;
  const REVEAL_STEP = 14;

  return (
    <StudioScene spotlightColor={accentColor} grid={false}>
      <AbsoluteFill style={{ fontFamily: theme.font }}>
        {caption && (
          <div
            style={{
              position: "absolute",
              // caption + title bajan en bloque (150->220, 230->300) para librar
              // la safe-area superior (top-211px) sin chocar entre si (80px aparte).
              top: 220,
              width: "100%",
              textAlign: "center",
              fontSize: 32,
              fontWeight: 600,
              letterSpacing: "0.05em",
              textTransform: "uppercase",
              color: theme.textDim,
              opacity: interpolate(frame, [2, 12], [0, 1], clamp),
              zIndex: 5,
            }}
          >
            {caption}
          </div>
        )}

        <ComposableMap
          width={W}
          height={H}
          projection="geoMercator"
          projectionConfig={projectionConfig}
          style={{ width: W, height: H }}
        >
          {geos}
          {targets.map((t, i) => {
            const p = spring({
              frame: frame - (REVEAL_START + i * REVEAL_STEP),
              fps,
              config: { damping: 13, mass: 0.6 },
            });
            const pulse = 0.6 + Math.sin((frame - i * 5) / 9) * 0.4;
            return (
              <Marker key={t.name} coordinates={t.centroid}>
                <circle
                  r={26}
                  fill={accentColor}
                  opacity={0.22 * p * pulse}
                  style={{ filter: "blur(6px)" }}
                />
                <circle
                  r={11 * p}
                  fill={accentColor}
                  stroke="#fff"
                  strokeWidth={1.4}
                  style={{ filter: `drop-shadow(0 0 8px ${accentColor})` }}
                />
                <circle r={3.5 * p} fill="#fff" opacity={0.9} />
              </Marker>
            );
          })}
        </ComposableMap>

        {/* titulo + contador */}
        {title && (
          <div
            style={{
              position: "absolute",
              top: 300,
              width: "100%",
              textAlign: "center",
              opacity: interpolate(frame, [6, 18], [0, 1], clamp),
            }}
          >
            <div
              style={{
                fontSize: 64,
                fontWeight: 900,
                letterSpacing: "-0.02em",
                color: theme.text,
                textShadow: "0 4px 24px rgba(0,0,0,0.5)",
              }}
            >
              {title}
            </div>
            {sublabel && (
              <div
                style={{
                  marginTop: 10,
                  fontSize: 38,
                  fontWeight: 700,
                  color: accentColor,
                  textShadow: `0 0 24px ${accentColor}44`,
                }}
              >
                {sublabel}
              </div>
            )}
          </div>
        )}

        {/* leyenda: lista de paises encendiendose con stagger */}
        <div
          style={{
            position: "absolute",
            left: 90,
            right: 90,
            // bottom-17% (y>1594) = safe-area inferior; bajar el borde a 340 deja
            // la fila de pills terminando en y~1580 (antes 230 -> reprobaba).
            bottom: 340,
            display: "flex",
            flexWrap: "wrap",
            justifyContent: "center",
            gap: 18,
          }}
        >
          {targets.map((t, i) => {
            const p = spring({
              frame: frame - (REVEAL_START + i * REVEAL_STEP),
              fps,
              config: { damping: 16, mass: 0.7 },
            });
            const FlagCmp: React.FC<{ style?: React.CSSProperties }> =
              (Flags as any)[t.iso2.toUpperCase()] || null;
            return (
              <div
                key={t.name}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 16,
                  background: "rgba(255,255,255,0.06)",
                  border: `1.5px solid ${accentColor}44`,
                  borderRadius: 999,
                  padding: "12px 24px 12px 14px",
                  opacity: p,
                  transform: `translateY(${(1 - p) * 18}px) scale(${0.92 + p * 0.08})`,
                }}
              >
                {FlagCmp && (
                  <div
                    style={{
                      width: 50,
                      height: 34,
                      borderRadius: 6,
                      overflow: "hidden",
                      boxShadow: "0 0 0 1.5px #ffffff22",
                      flexShrink: 0,
                    }}
                  >
                    <FlagCmp style={{ width: "100%", height: "100%", display: "block" }} />
                  </div>
                )}
                <span
                  style={{
                    fontSize: 36,
                    fontWeight: 700,
                    color: theme.text,
                    whiteSpace: "nowrap",
                  }}
                >
                  {t.label ?? t.name}
                </span>
              </div>
            );
          })}
        </div>
      </AbsoluteFill>
    </StudioScene>
  );
};
