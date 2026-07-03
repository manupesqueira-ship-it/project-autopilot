import { linearTiming, TransitionSeries } from "@remotion/transitions";
import React from "react";
import { AbsoluteFill, CalculateMetadataFunction } from "remotion";
import { Camera, Grade } from "../kit/cinema";
import { dipToBlack, whipPan, zoomThrough } from "../kit/transitions";
import { Bars2, Donut2, Gauge2, Lines2, Race2, TrendPro2 } from "./ChartBeats2";
import { Close2, NewsHook2, Reveal2, Scale2, Shock2, Trend2 } from "./NewsBeats2";

// NEWSREEL — el reel ENTERO como UNA composición: beats en TransitionSeries con
// gramática de edición real (zoom-through / whip / dip / hard cut) + cámara por beat
// + Grade global. El ensamblador (assemble_news.py) le pasa el treatment compilado.

export type BeatSpec = {
  type:
    | "hook" | "reveal" | "shock" | "scale" | "trend" | "close"
    | "bars" | "trendpro" | "lines" | "gauge" | "donut" | "race";
  props: Record<string, unknown>;
  durF: number;
  trans?: "cut" | "zoom" | "whip" | "whipL" | "dip";  // transición HACIA el siguiente beat
  transF?: number;
};
export type NewsReelProps = { beats: BeatSpec[] };

const MAP: Record<BeatSpec["type"], React.FC<Record<string, unknown>>> = {
  hook: NewsHook2 as never,
  reveal: Reveal2 as never,
  shock: Shock2 as never,
  scale: Scale2 as never,
  trend: Trend2 as never,
  close: Close2 as never,
  // gráficas ECharts premium (kit/charts.tsx)
  bars: Bars2 as never,
  trendpro: TrendPro2 as never,
  lines: Lines2 as never,
  gauge: Gauge2 as never,
  donut: Donut2 as never,
  race: Race2 as never,
};

const pres = (t?: string) =>
  t === "zoom" ? zoomThrough() : t === "whip" ? whipPan(1) : t === "whipL" ? whipPan(-1) : t === "dip" ? dipToBlack() : null;

export const NewsReel: React.FC<NewsReelProps> = ({ beats = [] }) => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#08090B" }}>
      <TransitionSeries>
        {beats.flatMap((b, i) => {
          const Comp = MAP[b.type];
          const out: React.ReactNode[] = [
            <TransitionSeries.Sequence key={`s${i}`} durationInFrames={b.durF}>
              <Camera durF={b.durF} seed={i + 1} push={0.05} drift={2.5}>
                <Comp {...b.props} durF={b.durF} />
              </Camera>
            </TransitionSeries.Sequence>,
          ];
          const p = pres(b.trans);
          if (i < beats.length - 1 && p) {
            out.push(
              <TransitionSeries.Transition
                key={`t${i}`}
                presentation={p as never}
                timing={linearTiming({ durationInFrames: b.transF ?? 10 })}
              />,
            );
          }
          return out;
        })}
      </TransitionSeries>
      <Grade grain={0.05} vignette={0.30} />
    </AbsoluteFill>
  );
};

export const calcNewsReel: CalculateMetadataFunction<NewsReelProps> = ({ props }) => {
  const beats = props.beats || [];
  let total = 0;
  beats.forEach((b, i) => {
    total += b.durF;
    if (i < beats.length - 1 && b.trans && b.trans !== "cut") total -= b.transF ?? 10;
  });
  return { durationInFrames: Math.max(60, total) };
};
