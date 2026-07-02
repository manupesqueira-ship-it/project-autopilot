import React, { useMemo } from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import * as THREE from "three";
import { EffectComposer, Bloom } from "@react-three/postprocessing";
import { geoEquirectangular, geoPath, geoCentroid, geoGraticule10 } from "d3-geo";
import * as Flags from "country-flag-icons/react/3x2";
import { feature } from "topojson-client";
import topo from "../data/countries-50m.json";

const COUNTRIES: any = feature(topo as any, (topo as any).objects.countries);

const W = 1080;
const H = 1920;
const CX = W / 2; // 540
const GLOBE_CY = 820; // globo arriba del centro -> aire abajo para la etiqueta

// Biblia igloo.inc: negro mate, UN elemento, azules frios + 1 acento calido (brasa).
const VOID = "#070707";
const EMBER = "#FF7A1A"; // unico acento calido (foco = El Salvador)
const ATMO = "#5C82A6"; // azul frio (atmosfera/rim del globo)

// Ortho zoom=1 => 1 unidad de mundo = 1px. Registro 1:1 con el overlay 2D.
const R = 430; // radio del globo en px
const LIFT = H / 2 - GLOBE_CY; // +140 => centro del globo en y=820

const DEG = Math.PI / 180;

export type GlobeHero3DProps = {
  countryName?: string;
  iso2?: string;
  label?: string;
  lon?: number;
  lat?: number;
};

// Textura equirectangular (mundo) dibujada desde el GeoJSON real -> tierra obsidiana
// + graticula tenue (lee como globo 3D). El Salvador NO va aqui (va en el emissive).
function buildBaseTexture(): THREE.Texture {
  const w = 4096;
  const h = 2048;
  const canvas = document.createElement("canvas");
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext("2d")!;
  const projection = geoEquirectangular()
    .scale(w / (2 * Math.PI))
    .translate([w / 2, h / 2]);
  const path = geoPath(projection, ctx as any);

  // oceano casi-negro frio
  ctx.fillStyle = "#05080C";
  ctx.fillRect(0, 0, w, h);

  // graticula finisima
  ctx.beginPath();
  (path as any)(geoGraticule10());
  ctx.lineWidth = 1;
  ctx.strokeStyle = "#11202C";
  ctx.stroke();

  // tierra obsidiana
  ctx.fillStyle = "#141C26";
  ctx.strokeStyle = "#243240";
  ctx.lineWidth = 1.4;
  COUNTRIES.features.forEach((f: any) => {
    ctx.beginPath();
    (path as any)(f);
    ctx.fill();
    ctx.stroke();
  });

  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = 8;
  return tex;
}

// Emissive: negro salvo El Salvador = brasa (fill preciso + halo suave -> bloom limpio).
function buildEmberTexture(countryName: string): THREE.Texture {
  const w = 4096;
  const h = 2048;
  const canvas = document.createElement("canvas");
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext("2d")!;
  const projection = geoEquirectangular()
    .scale(w / (2 * Math.PI))
    .translate([w / 2, h / 2]);
  const path = geoPath(projection, ctx as any);

  ctx.fillStyle = "#000000";
  ctx.fillRect(0, 0, w, h);

  const target = COUNTRIES.features.find(
    (f: any) => f.properties.name === countryName
  );
  if (target) {
    const c = geoCentroid(target);
    const p = projection(c as [number, number]);
    if (p) {
      const g = ctx.createRadialGradient(p[0], p[1], 0, p[0], p[1], 90);
      g.addColorStop(0, "#FFB066");
      g.addColorStop(0.4, "#FF7A1A");
      g.addColorStop(1, "#00000000");
      ctx.fillStyle = g;
      ctx.beginPath();
      ctx.arc(p[0], p[1], 90, 0, Math.PI * 2);
      ctx.fill();
    }
    // pais preciso encendido encima del halo
    ctx.fillStyle = "#FFC27A";
    ctx.strokeStyle = "#FF7A1A";
    ctx.lineWidth = 6;
    ctx.beginPath();
    (path as any)(target);
    ctx.fill();
    ctx.stroke();
  }

  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = 8;
  return tex;
}

const atmosphereVert = `
varying vec3 vNormalW;
varying vec3 vViewDir;
void main() {
  vec4 wp = modelMatrix * vec4(position, 1.0);
  vNormalW = normalize(mat3(modelMatrix) * normal);
  vViewDir = normalize(cameraPosition - wp.xyz);
  gl_Position = projectionMatrix * viewMatrix * wp;
}`;

const atmosphereFrag = `
varying vec3 vNormalW;
varying vec3 vViewDir;
uniform vec3 uColor;
uniform float uPower;
uniform float uIntensity;
uniform vec3 uLightDir;
void main() {
  float f = pow(1.0 - max(dot(vNormalW, vViewDir), 0.0), uPower);
  // crescente volumetrico: brilla en el limbo iluminado, se apaga en el lado oscuro
  float lit = clamp(dot(normalize(vNormalW), normalize(uLightDir)) * 0.5 + 0.5, 0.0, 1.0);
  float dir = mix(0.16, 1.0, pow(lit, 1.4));
  gl_FragColor = vec4(uColor * f * uIntensity * dir, f * dir);
}`;

const LIGHT_DIR = new THREE.Vector3(-520, 600, 720).normalize();

// Cascara de atmosfera (Fresnel, BackSide aditivo). Apilar 2 -> halo volumetrico.
const Atmo: React.FC<{ scale: number; power: number; intensity: number }> = ({
  scale,
  power,
  intensity,
}) => {
  const uniforms = useMemo(
    () => ({
      uColor: { value: new THREE.Color(ATMO) },
      uPower: { value: power },
      uIntensity: { value: intensity },
      uLightDir: { value: LIGHT_DIR },
    }),
    [power, intensity]
  );
  return (
    <mesh scale={scale}>
      <sphereGeometry args={[R, 96, 96]} />
      <shaderMaterial
        vertexShader={atmosphereVert}
        fragmentShader={atmosphereFrag}
        uniforms={uniforms}
        transparent
        side={THREE.BackSide}
        blending={THREE.AdditiveBlending}
        depthWrite={false}
      />
    </mesh>
  );
};

const Globe: React.FC<{
  countryName: string;
  lon: number;
  lat: number;
  zoom: number;
  settleRad: number;
}> = ({ countryName, lon, lat, zoom, settleRad }) => {
  const baseTex = useMemo(() => buildBaseTexture(), []);
  const emberTex = useMemo(() => buildEmberTexture(countryName), [countryName]);

  // Orientacion deterministica: lleva (lon,lat) al frente (+Z), de cara a la camara.
  // Derivado del mapeo UV de SphereGeometry: outer rot.x = latR, inner rot.y = -pi/2 - lonR.
  const latR = lat * DEG;
  const lonR = lon * DEG;

  // En ortho, escalar el grupo en su origen mantiene El Salvador (x=0,y=LIFT) fijo en
  // pantalla -> el zoom "cae" exactamente sobre el pais, sin deriva.
  return (
    <group position={[0, LIFT, 0]} scale={zoom}>
      {/* atmosfera fria volumetrica: rim fino en el limbo iluminado + halo al vacio */}
      <Atmo scale={1.015} power={2.8} intensity={0.85} />
      <Atmo scale={1.2} power={2.6} intensity={0.42} />

      {/* globo obsidiana mate (sin hotspot especular -> nada que lea como sol/luna) */}
      <group rotation-x={latR}>
        <group rotation-y={-Math.PI / 2 - lonR + settleRad}>
          <mesh>
            <sphereGeometry args={[R, 128, 128]} />
            <meshStandardMaterial
              map={baseTex}
              emissive={"#ffffff"}
              emissiveMap={emberTex}
              emissiveIntensity={3.4}
              roughness={0.88}
              metalness={0.0}
            />
          </mesh>
        </group>
      </group>
    </group>
  );
};

export const GlobeHero3D: React.FC<GlobeHero3DProps> = ({
  countryName = "El Salvador",
  iso2 = "SV",
  label = "EL SALVADOR",
  lon = -88.8965,
  lat = 13.7942,
}) => {
  const frame = useCurrentFrame();

  // el globo gira para "presentar" El Salvador y ATERRIZA bajo el centro ~frame 30.
  const settleRad = interpolate(frame, [0, 30], [0.36, 0], {
    easing: Easing.out(Easing.cubic),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  // la brasa calida crece mientras El Salvador rota hacia el centro.
  const glow = interpolate(frame, [10, 32], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  // anillo/conector/etiqueta revelan DESPUES de que la brasa aterriza (sin desfase).
  const reveal = interpolate(frame, [32, 56], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const haloPulse = 0.6 + Math.sin(frame / 16) * 0.4;

  // zoom lento y deliberado hacia El Salvador (estilo GSAP, ease-out)
  const zoom = interpolate(frame, [0, 85], [1.0, 1.5], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  const FlagCmp: React.FC<{ title?: string; style?: React.CSSProperties }> =
    (Flags as any)[iso2.toUpperCase()] || null;

  return (
    <AbsoluteFill style={{ backgroundColor: VOID }}>
      <ThreeCanvas
        width={W}
        height={H}
        orthographic
        camera={{ position: [0, 0, 1600], zoom: 1, near: 1, far: 6000 }}
        gl={{ antialias: true }}
        style={{ width: W, height: H }}
      >
        <ambientLight intensity={0.12} color={"#1E2C3A"} />
        <hemisphereLight args={["#2B4258", "#04060A", 0.55]} />
        <directionalLight position={[-520, 600, 720]} intensity={1.5} color={"#AEC6E0"} />
        <Globe countryName={countryName} lon={lon} lat={lat} zoom={zoom} settleRad={settleRad} />
        <EffectComposer>
          <Bloom
            intensity={1.25}
            luminanceThreshold={0.16}
            luminanceSmoothing={0.9}
            mipmapBlur
            radius={0.72}
          />
        </EffectComposer>
      </ThreeCanvas>

      {/* halo calido (brasa) sobre El Salvador = centro del globo */}
      <div
        style={{
          position: "absolute",
          left: CX - 200,
          top: GLOBE_CY - 200,
          width: 400,
          height: 400,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${EMBER}55 0%, ${EMBER}1A 34%, transparent 62%)`,
          opacity: glow * haloPulse,
          mixBlendMode: "screen",
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
          opacity: interpolate(reveal, [0, 1], [0, 0.95], { extrapolateLeft: "clamp" }),
          transform: `scale(${interpolate(reveal, [0, 1], [1.6, 1], {
            extrapolateLeft: "clamp",
          })})`,
          pointerEvents: "none",
        }}
      />

      {/* conector finisimo: del pais a la etiqueta */}
      <div
        style={{
          position: "absolute",
          left: CX,
          top: GLOBE_CY + 36,
          width: 1,
          height: 560,
          background: `linear-gradient(180deg, ${EMBER}aa 0%, ${EMBER}22 55%, transparent 100%)`,
          opacity: interpolate(reveal, [0.15, 1], [0, 0.7], { extrapolateLeft: "clamp" }),
          transformOrigin: "top",
          transform: `scaleY(${interpolate(reveal, [0.15, 1], [0, 1], {
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
            opacity: interpolate(reveal, [0.35, 1], [0, 1], { extrapolateLeft: "clamp" }),
            transform: `translateY(${interpolate(reveal, [0.35, 1], [16, 0], {
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
        <filter id="grain3d">
          <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" stitchTiles="stitch" />
        </filter>
        <rect width={W} height={H} filter="url(#grain3d)" />
      </svg>
    </AbsoluteFill>
  );
};
