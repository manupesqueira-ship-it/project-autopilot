import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  OffthreadVideo,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { theme } from "../theme";

// BeatMovingData — el beat de la ARQUITECTURA NUEVA (rechazo Manuel 2026-06-26):
// el clip i2v (un mundo caricatura-fino que SE MUEVE) va de LECHO a pantalla
// completa, y la DATA EXACTA se compone ENCIMA en codigo, integrada y en
// movimiento (nunca pantalla plana con numero quieto). Un solo ADN: el mismo
// mundo generado en cada beat + el dato exacto que la IA no sabe escribir.
//
// `kind` cambia el overlay segun el rol del beat:
//   build    — una cifra que ESCALA por hitos (15k->45k->90k) + meter segmentado
//   timeline — hitos temporales (Mes 1/3/6) que se encienden white->green->gold
//   climax   — la cifra meta que cuenta hasta el apice (sincronizable a la voz)

type Step = { label?: string; value: number };
type Node = { label: string; tone?: "white" | "green" | "gold" };

export type MovingDataProps = {
  clip: string; // stem del mp4 en public/i2v/<clip>.mp4
  kind: "build" | "timeline" | "climax";
  caption?: string; // kicker chico arriba (NO subtitulo de la voz)
  prefix?: string;
  suffix?: string;
  decimals?: number;
  accentColor?: string;
  // build
  steps?: Step[];
  meterLabel?: string;
  // timeline
  nodes?: Node[];
  // climax
  value?: number;
  subline?: string;
  countEndFrame?: number;
};

const toneColor = (t?: string) =>
  t === "green" ? theme.green : t === "gold" ? theme.gold : theme.text;

const fmt = (n: number, decimals = 0) =>
  n.toLocaleString("es-MX", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });

// veil para legibilidad de la data sobre el lecho en movimiento
const Veil: React.FC<{ from: string; op: number }> = ({ from, op }) => (
  <AbsoluteFill style={{ background: from, opacity: op }} />
);

const BigNumber: React.FC<{
  text: string;
  color: string;
  size?: number;
}> = ({ text, color, size = 132 }) => (
  <div
    style={{
      fontSize: size,
      fontWeight: 800,
      letterSpacing: "-0.02em",
      color,
      lineHeight: 1,
      textShadow: `0 6px 34px rgba(0,0,0,0.6), 0 0 26px ${color}55`,
      fontVariantNumeric: "tabular-nums",
    }}
  >
    {text}
  </div>
);

export const MovingData: React.FC<MovingDataProps> = ({
  clip,
  kind,
  caption,
  prefix = "",
  suffix = "",
  decimals = 0,
  accentColor = theme.gold,
  steps = [],
  meterLabel,
  nodes = [],
  value = 0,
  subline,
  countEndFrame,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const D = durationInFrames;

  // caption entra suave en el primer medio segundo
  const capIn = spring({ frame: frame - 8, fps, config: { damping: 16, mass: 0.8 } });

  return (
    <AbsoluteFill style={{ backgroundColor: theme.bg.base, fontFamily: theme.font }}>
      <OffthreadVideo
        src={staticFile(`i2v/${clip}.mp4`)}
        style={{ width: "100%", height: "100%", objectFit: "cover" }}
        muted
      />

      {/* caption-kicker arriba, sobre velo superior */}
      {caption && (
        <>
          <Veil
            from="linear-gradient(180deg, rgba(7,10,15,0.82) 0%, rgba(7,10,15,0.35) 60%, transparent 100%)"
            op={capIn}
          />
          <div
            style={{
              position: "absolute",
              top: 120,
              left: 84,
              right: 84,
              textAlign: "center",
              opacity: capIn,
              transform: `translateY(${(1 - capIn) * -18}px)`,
            }}
          >
            <div
              style={{
                fontSize: 38,
                fontWeight: 700,
                color: theme.textDim,
                letterSpacing: "0.01em",
              }}
            >
              {caption}
            </div>
          </div>
        </>
      )}

      {kind === "build" && (
        <BuildOverlay
          frame={frame}
          D={D}
          steps={steps}
          prefix={prefix}
          suffix={suffix}
          decimals={decimals}
          accent={accentColor}
          meterLabel={meterLabel}
        />
      )}
      {kind === "timeline" && (
        <TimelineOverlay frame={frame} D={D} nodes={nodes} />
      )}
      {kind === "climax" && (
        <ClimaxOverlay
          frame={frame}
          fps={fps}
          D={D}
          value={value}
          prefix={prefix}
          suffix={suffix}
          decimals={decimals}
          accent={accentColor}
          subline={subline}
          countEndFrame={countEndFrame}
        />
      )}
    </AbsoluteFill>
  );
};

// --- build: una cifra que escala por hitos + meter segmentado ---------------
const BuildOverlay: React.FC<{
  frame: number;
  D: number;
  steps: Step[];
  prefix: string;
  suffix: string;
  decimals: number;
  accent: string;
  meterLabel?: string;
}> = ({ frame, D, steps, prefix, suffix, decimals, accent, meterLabel }) => {
  const n = Math.max(steps.length, 1);
  // hitos repartidos en el beat: reveal i en (0.12 + i*gap)
  const gap = 0.62 / n;
  const reveals = steps.map((_, i) => Math.round(D * (0.14 + i * gap)));
  // indice del hito activo y valor "contado" hacia el (cuenta suave entre hitos)
  let active = 0;
  for (let i = 0; i < n; i++) if (frame >= reveals[i]) active = i;
  const prev = active > 0 ? steps[active - 1].value : 0;
  const cur = steps[active]?.value ?? 0;
  const segStart = reveals[active];
  const segEnd = active < n - 1 ? reveals[active + 1] : D;
  const t = interpolate(frame, [segStart, Math.min(segStart + 18, segEnd)], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const shown = prev + (cur - prev) * t;

  return (
    <>
      <Veil
        from="linear-gradient(0deg, rgba(7,10,15,0.9) 0%, rgba(7,10,15,0.45) 40%, transparent 72%)"
        op={1}
      />
      <div
        style={{
          position: "absolute",
          bottom: 300,
          left: 84,
          right: 84,
          textAlign: "center",
        }}
      >
        <BigNumber text={`${prefix}${fmt(shown, decimals)}${suffix}`} color={accent} />
        {/* meter segmentado: un segmento por hito, se llena hasta el activo */}
        <div style={{ display: "flex", gap: 12, marginTop: 40 }}>
          {steps.map((s, i) => {
            const on = i <= active;
            return (
              <div key={i} style={{ flex: 1 }}>
                <div
                  style={{
                    height: 12,
                    borderRadius: 8,
                    background: on ? accent : "rgba(255,255,255,0.14)",
                    boxShadow: on ? `0 0 16px ${accent}88` : "none",
                    transition: "none",
                  }}
                />
                {s.label && (
                  <div
                    style={{
                      marginTop: 14,
                      fontSize: 26,
                      fontWeight: 700,
                      color: on ? theme.text : theme.textDim,
                    }}
                  >
                    {s.label}
                  </div>
                )}
              </div>
            );
          })}
        </div>
        {meterLabel && (
          <div style={{ marginTop: 26, fontSize: 30, color: theme.textDim, fontWeight: 600 }}>
            {meterLabel}
          </div>
        )}
      </div>
    </>
  );
};

// --- timeline: hitos temporales que se encienden ----------------------------
const TimelineOverlay: React.FC<{ frame: number; D: number; nodes: Node[] }> = ({
  frame,
  D,
  nodes,
}) => {
  const n = Math.max(nodes.length, 1);
  const gap = 0.6 / n;
  const reveals = nodes.map((_, i) => Math.round(D * (0.16 + i * gap)));
  return (
    <>
      <Veil
        from="linear-gradient(180deg, rgba(7,10,15,0.82) 0%, rgba(7,10,15,0.3) 55%, transparent 100%)"
        op={1}
      />
      <div
        style={{
          position: "absolute",
          top: 210,
          left: 70,
          right: 70,
          display: "flex",
          alignItems: "flex-start",
          justifyContent: "space-between",
        }}
      >
        {nodes.map((node, i) => {
          const on = frame >= reveals[i];
          const pop = interpolate(frame, [reveals[i], reveals[i] + 12], [0.6, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.out(Easing.back(1.6)),
          });
          const col = toneColor(node.tone);
          return (
            <React.Fragment key={i}>
              <div style={{ width: 200, textAlign: "center", opacity: on ? 1 : 0.28 }}>
                <div
                  style={{
                    width: 34,
                    height: 34,
                    borderRadius: 20,
                    margin: "0 auto",
                    background: on ? col : "rgba(255,255,255,0.18)",
                    boxShadow: on ? `0 0 22px ${col}aa` : "none",
                    transform: `scale(${on ? pop : 0.6})`,
                  }}
                />
                <div
                  style={{
                    marginTop: 18,
                    fontSize: 32,
                    fontWeight: 800,
                    color: on ? theme.text : theme.textDim,
                  }}
                >
                  {node.label}
                </div>
              </div>
              {i < nodes.length - 1 && (
                <div
                  style={{
                    flex: 1,
                    height: 4,
                    marginTop: 15,
                    borderRadius: 3,
                    background: frame >= reveals[i + 1] ? toneColor(nodes[i + 1].tone) : "rgba(255,255,255,0.16)",
                  }}
                />
              )}
            </React.Fragment>
          );
        })}
      </div>
    </>
  );
};

// --- climax: la cifra meta que cuenta hasta el apice ------------------------
const ClimaxOverlay: React.FC<{
  frame: number;
  fps: number;
  D: number;
  value: number;
  prefix: string;
  suffix: string;
  decimals: number;
  accent: string;
  subline?: string;
  countEndFrame?: number;
}> = ({ frame, fps, D, value, prefix, suffix, decimals, accent, subline, countEndFrame }) => {
  const start = Math.round(D * 0.14);
  const end = countEndFrame ?? Math.round(D * 0.72);
  const shown = interpolate(frame, [start, end], [0, value], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  // sub aparece al aterrizar la cifra
  const subIn = spring({ frame: frame - end, fps, config: { damping: 18, mass: 0.9 } });
  return (
    <>
      <Veil
        from="radial-gradient(120% 60% at 50% 32%, rgba(7,10,15,0.78) 0%, rgba(7,10,15,0.28) 55%, transparent 80%)"
        op={1}
      />
      <div
        style={{
          position: "absolute",
          top: 300,
          left: 70,
          right: 70,
          textAlign: "center",
        }}
      >
        <BigNumber text={`${prefix}${fmt(shown, decimals)}${suffix}`} color={accent} size={130} />
        {subline && (
          <div
            style={{
              marginTop: 34,
              fontSize: 34,
              fontWeight: 600,
              color: theme.text,
              opacity: subIn,
              transform: `translateY(${(1 - subIn) * 16}px)`,
            }}
          >
            {subline}
          </div>
        )}
      </div>
    </>
  );
};
