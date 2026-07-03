import React from "react";
import { AbsoluteFill, spring, useCurrentFrame, useVideoConfig } from "remotion";
import {
  barsOption,
  donutOption,
  EChartCanvas,
  gaugeOption,
  lineHeroOption,
  multiLineOption,
  raceOption,
} from "../kit/charts";
import { LiveBg } from "../kit/cinema";
import { L, TYPE } from "../kit/look";
import { glowFilter, Masthead } from "../kit/material";
import { EASE, Odometer, prog, SPR, stag, useBeatDur } from "../kit/motion";

// CHART BEATS v2 — gráficas ECharts premium en el look A. Mismo contrato que
// NewsBeats2: revela temprano, SOSTIENE legible, nunca quieto (LiveBg + Camera
// del NewsReel). El chart es el protagonista: NO va título encima (regla locked);
// kicker arriba en su carril, caption abajo en el suyo.

const semC = (v?: string) => (v === "gain" ? L.green : v === "loss" ? L.red : L.gold);

const Scaffold: React.FC<{
  kicker?: string;
  label?: string;
  caption?: string;
  accent: string;
  kO: number;
  cO: number;
  children: React.ReactNode;
}> = ({ kicker, label, caption, accent, kO, cO, children }) => (
  <AbsoluteFill style={{ fontFamily: L.font }}>
    <LiveBg accent={accent} energy={0.09} />
    <Masthead />
    {kicker ? (
      <div style={{ position: "absolute", top: 250, left: L.mx, right: L.mx, textAlign: "center", ...TYPE.kicker, color: accent, opacity: kO }}>
        {kicker}
      </div>
    ) : null}
    {label ? (
      <div style={{ position: "absolute", top: 318, left: L.mx, right: L.mx, textAlign: "center", fontSize: 34, fontWeight: 500, color: L.mute, opacity: kO }}>
        {label}
      </div>
    ) : null}
    {children}
    {caption ? (
      <div style={{ position: "absolute", bottom: 250, left: L.mx, right: L.mx, textAlign: "center", fontSize: 44, fontWeight: 600, color: L.ink, opacity: cO }}>
        {caption}
      </div>
    ) : null}
  </AbsoluteFill>
);

// formatter con moneda/sufijo del treatment (el director manda strings ya resueltos
// donde puede; aquí solo formatea el número vivo del draw-on)
const mkFmt = (prefix = "", suffix = "", decimals = 0) => (v: number) =>
  `${prefix}${v.toLocaleString("es-MX", { maximumFractionDigits: decimals })}${suffix}`;

// ── BARRAS — comparación con UN acento (sujeto de la noticia) ───────────────
export const Bars2: React.FC<{
  kicker?: string; label?: string; caption?: string;
  cats?: string[]; values?: number[]; accentIndex?: number;
  valence?: "gain" | "loss" | "gold";
  prefix?: string; suffix?: string; durF?: number;
}> = ({ kicker = "", label = "", caption = "", cats = [], values = [], accentIndex = 0, valence = "gain", prefix = "", suffix = "", durF }) => {
  const frame = useCurrentFrame();
  const D = useBeatDur(durF);
  const accent = semC(valence);
  // stagger: cada barra crece 8 frames después de la anterior, todas legibles pronto
  const progress = values.map((_, i) => prog(frame, 16 + stag(i, 8), 52 + stag(i, 8), EASE.enter));
  return (
    <Scaffold kicker={kicker} label={label} caption={caption} accent={accent} kO={prog(frame, 4, 18)} cO={prog(frame, Math.min(D - 40, 78), Math.min(D - 26, 92))}>
      <EChartCanvas
        option={barsOption({ cats, values, progress, accentIndex, accent, labelFmt: mkFmt(prefix, suffix) })}
        width={1080}
        height={1000}
        style={{ position: "absolute", top: 430, left: 0 }}
      />
    </Scaffold>
  );
};

// ── TRENDPRO — línea héroe ECharts con área y umbral semántico opcional ─────
export const TrendPro2: React.FC<{
  kicker?: string; label?: string; caption?: string; endTag?: string;
  points?: number[]; xLabels?: string[]; threshold?: number;
  valence?: "gain" | "loss" | "gold"; durF?: number;
}> = ({ kicker = "", label = "", caption = "", endTag = "", points = [], xLabels, threshold, valence = "gain", durF }) => {
  const frame = useCurrentFrame();
  const D = useBeatDur(durF);
  const accent = semC(valence);
  const draw = prog(frame, 18, D - 46, EASE.update);
  const tagO = prog(frame, D - 52, D - 38);
  return (
    <Scaffold kicker={kicker} label={label} caption={caption} accent={accent} kO={prog(frame, 4, 18)} cO={tagO}>
      <EChartCanvas
        option={lineHeroOption({ data: points, progress: draw, color: accent, xLabels, threshold, area: true, showAxis: Boolean(xLabels) })}
        width={1080}
        height={1000}
        style={{ position: "absolute", top: 430, left: 0 }}
      />
      {endTag ? (
        <div style={{ position: "absolute", top: 470, right: 90, fontSize: 92, fontWeight: 800, color: accent, opacity: tagO, filter: glowFilter(accent, 0.6) }}>
          {endTag}
        </div>
      ) : null}
    </Scaffold>
  );
};

// ── LINES — hasta 3 series con nombre+valor al final + umbral (meta Banxico) ─
export const Lines2: React.FC<{
  kicker?: string; label?: string; caption?: string;
  series?: { name: string; data: number[]; color?: string }[];
  xLabels?: string[]; threshold?: number; thresholdLabel?: string;
  valence?: "gain" | "loss" | "gold"; prefix?: string; suffix?: string; durF?: number;
}> = ({ kicker = "", label = "", caption = "", series = [], xLabels, threshold, thresholdLabel, valence = "gain", prefix = "", suffix = "", durF }) => {
  const frame = useCurrentFrame();
  const D = useBeatDur(durF);
  const accent = semC(valence);
  const draw = prog(frame, 18, D - 60, EASE.update);
  return (
    <Scaffold kicker={kicker} label={label} caption={caption} accent={accent} kO={prog(frame, 4, 18)} cO={prog(frame, D - 46, D - 32)}>
      <EChartCanvas
        option={multiLineOption({ series, progress: draw, xLabels, threshold, thresholdLabel, accent, endFmt: mkFmt(prefix, suffix, 2) })}
        width={1080}
        height={1000}
        style={{ position: "absolute", top: 430, left: 0 }}
      />
    </Scaffold>
  );
};

// ── GAUGE — un porcentaje protagonista en arco fino ─────────────────────────
export const Gauge2: React.FC<{
  kicker?: string; label?: string; caption?: string;
  value?: number; max?: number; suffix?: string;
  valence?: "gain" | "loss" | "gold"; land?: number; durF?: number;
}> = ({ kicker = "", label = "", caption = "", value = 0, max = 100, suffix = "%", valence = "gain", land = 46, durF }) => {
  const frame = useCurrentFrame();
  const D = useBeatDur(durF);
  const accent = semC(valence);
  const p = prog(frame, 12, land, EASE.dramatic);
  return (
    <Scaffold kicker={kicker} label={label} caption={caption} accent={accent} kO={prog(frame, 4, 18)} cO={prog(frame, land + 8, land + 22)}>
      <EChartCanvas
        option={gaugeOption({ value, max, progress: p, color: accent, fmt: (v) => `${Math.round(v)}${suffix}` })}
        width={1080}
        height={1050}
        style={{ position: "absolute", top: 420, left: 0 }}
      />
    </Scaffold>
  );
};

// ── DONUT — proporción ultrafina; cifra central como capa React (Odometer) ──
export const Donut2: React.FC<{
  kicker?: string; label?: string; caption?: string;
  parts?: { name: string; value: number }[];
  centerValue?: string; centerLabel?: string;
  valence?: "gain" | "loss" | "gold"; land?: number; durF?: number;
}> = ({ kicker = "", label = "", caption = "", parts = [], centerValue = "", centerLabel = "", valence = "gain", land = 48, durF }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const D = useBeatDur(durF);
  const accent = semC(valence);
  const sweep = prog(frame, 14, land, EASE.dramatic);
  const labelO = prog(frame, land + 4, land + 18);
  const pop = spring({ frame: frame - land, fps, config: SPR.SNAPPY, durationInFrames: 16 });
  return (
    <Scaffold kicker={kicker} label={label} caption={caption} accent={accent} kO={prog(frame, 4, 18)} cO={prog(frame, land + 12, land + 26)}>
      <EChartCanvas
        option={donutOption({ parts, progress: sweep, accent })}
        width={1080}
        height={1050}
        style={{ position: "absolute", top: 430, left: 0 }}
      />
      <div style={{ position: "absolute", top: 430, left: 0, width: 1080, height: 1050, display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", transform: `scale(${0.94 + 0.06 * pop})` }}>
        {centerValue ? (
          <Odometer value={centerValue} fontSize={128} color={frame >= land ? accent : L.dim} start={14} land={land} glow={accent} glowAt={land} />
        ) : null}
        {centerLabel ? (
          <div style={{ fontSize: 32, fontWeight: 600, color: L.mute, marginTop: 12, opacity: labelO }}>{centerLabel}</div>
        ) : null}
      </div>
    </Scaffold>
  );
};

// ── RACE — carrera de barras entre periodos (quién sube, quién cae) ─────────
export const Race2: React.FC<{
  kicker?: string; label?: string; caption?: string;
  steps?: { period: string; values: Record<string, number> }[];
  accentName?: string; prefix?: string; suffix?: string; durF?: number;
}> = ({ kicker = "", label = "", caption = "", steps = [], accentName = "", prefix = "", suffix = "", durF }) => {
  const frame = useCurrentFrame();
  const D = useBeatDur(durF);
  const t = prog(frame, 16, D - 50, EASE.update);
  if (!steps.length) return null;
  const { option, period } = raceOption({ steps, t, accentName, fmt: mkFmt(prefix, suffix) });
  return (
    <Scaffold kicker={kicker} label={label} caption={caption} accent={L.green} kO={prog(frame, 4, 18)} cO={prog(frame, D - 44, D - 30)}>
      <EChartCanvas option={option} width={1080} height={980} style={{ position: "absolute", top: 440, left: 0 }} />
      {/* periodo gigante como overlay React (patrón minado: año como capa) */}
      <div style={{ position: "absolute", top: 1330, left: 0, right: 0, textAlign: "center", fontSize: 96, fontWeight: 800, color: L.dim, letterSpacing: "-0.02em", opacity: 0.85 }}>
        {period}
      </div>
    </Scaffold>
  );
};
