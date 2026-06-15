import React from "react";
import {
  AbsoluteFill,
  Audio,
  Sequence,
  OffthreadVideo,
  Loop,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
} from "remotion";

const BG = "#0D1117";
const BG_DEEP = "#06080B";
const PANEL = "#161B22";
const PANEL_BORDER = "rgba(255,255,255,0.08)";
const GOLD = "#D4A574";
const CYAN = "#00D9A5";
const RED = "#FF6B6B";
const TEXT = "#F5F1E8";
const MUTED = "#8B949E";

const DEFAULT_TITLE_FRAMES = 90;
const OUTRO_FRAMES = 120;
const BEAT_FADE_FRAMES = 12;
const FADE_END_BUFFER = 6;

const SOFT_SPRING = { damping: 22, stiffness: 140, mass: 0.85 };
const SOFT_SPRING_FAST = { damping: 20, stiffness: 180, mass: 0.7 };
// Overshoot: damping below critical so the value passes the target and settles — reads as physical/crafted.
const OVERSHOOT_SPRING = { damping: 12, stiffness: 130, mass: 0.9 };
const OVERSHOOT_SOFT = { damping: 14, stiffness: 110, mass: 1 };
// Pro entrance easing (ease-out, no ease-in-out). Matches easeOutQuint/easeOutExpo feel.
const easeOutQuint = (t: number) => 1 - Math.pow(1 - t, 5);
const easeOutExpo = (t: number) => (t >= 1 ? 1 : 1 - Math.pow(2, -10 * t));

type CurrencyFormat = "currency_mxn" | "currency_usd" | "currency_ars" | "percent" | "number";

export type CounterSpec = {
  label?: string;
  from?: number;
  to: number;
  format?: CurrencyFormat;
  suffix?: string;
};

export type BarSpec = {
  label: string;
  value: number;
  color?: string;
};

export type BarChartSpec = {
  title?: string;
  bars: BarSpec[];
  format?: CurrencyFormat;
};

export type PieSliceSpec = {
  label: string;
  value: number;
  color?: string;
};

export type PieChartSpec = {
  slices: PieSliceSpec[];
  center_label?: string;
  format?: CurrencyFormat;
};

export type ComparisonSpec = {
  before: { label: string; value: string };
  after: { label: string; value: string };
  delta?: string;
};

export type UIMockupSpec = {
  question: string;
  answer: string;
  model_name?: string;
};

export type LinePoint = { x: string | number; y: number };

export type LineSeries = {
  points: LinePoint[];
  color?: string;
  label?: string;
};

export type LineChartSpec = {
  title?: string;
  subtitle?: string;
  points: LinePoint[];
  series?: LineSeries[];
  format?: CurrencyFormat;
};

export type IconName =
  | "bank"
  | "ai"
  | "growth"
  | "money"
  | "chart"
  | "warning"
  | "target"
  | "clock"
  | "shield"
  | "spark";

export type Hero3DSpec = {
  video_url: string;
  kicker?: string;
  scale?: number;
};

export type ScriptBeat = {
  kind?: "text" | "counter" | "bar_chart" | "comparison" | "ui_mockup" | "line_chart" | "pie_chart" | "hero_3d";
  text?: string;
  counter?: CounterSpec;
  chart?: BarChartSpec;
  line_chart?: LineChartSpec;
  pie?: PieChartSpec;
  comparison?: ComparisonSpec;
  mockup?: UIMockupSpec;
  hero?: Hero3DSpec;
  icon?: IconName;
  start_frame?: number;
  duration_frames?: number;
};

export type DineroIAReelProps = {
  title: string;
  title_frames?: number;
  script_beats: ScriptBeat[];
  voice_audio_url: string;
  music_audio_url?: string | null;
  music_volume?: number;
  accent_color?: string;
};

type BeatTiming = ScriptBeat & { from: number; duration: number };

const formatValue = (v: number, format?: CurrencyFormat, suffix?: string): string => {
  let str: string;
  if (format === "currency_mxn") str = "$" + Math.round(v).toLocaleString("es-MX") + " MXN";
  else if (format === "currency_usd") str = "$" + Math.round(v).toLocaleString("en-US") + " USD";
  else if (format === "currency_ars") str = "$" + Math.round(v).toLocaleString("es-AR") + " ARS";
  else if (format === "percent") str = (Math.round(v * 10) / 10).toFixed(1) + "%";
  else str = Math.round(v).toLocaleString("es-MX");
  if (suffix) str += " " + suffix;
  return str;
};

const hexBlend = (a: string, b: string, t: number): string => {
  const pa = [1, 3, 5].map((o) => parseInt(a.slice(o, o + 2), 16));
  const pb = [1, 3, 5].map((o) => parseInt(b.slice(o, o + 2), 16));
  const m = pa.map((v, i) => Math.round(v + (pb[i] - v) * t));
  return "#" + m.map((v) => v.toString(16).padStart(2, "0")).join("");
};

const easeOutCubic = (t: number) => 1 - Math.pow(1 - t, 3);
const easeInOutCubic = (t: number) =>
  t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;

export const DineroIAReel: React.FC<DineroIAReelProps> = ({
  title,
  title_frames,
  script_beats,
  voice_audio_url,
  music_audio_url,
  music_volume,
  accent_color = CYAN,
}) => {
  const { durationInFrames } = useVideoConfig();
  const titleFrames = title_frames ?? DEFAULT_TITLE_FRAMES;

  const allHaveStartFrame = script_beats.every((b) => typeof b.start_frame === "number");
  const allHaveDuration = script_beats.every((b) => typeof b.duration_frames === "number");

  let beatTimings: BeatTiming[];
  if (allHaveStartFrame) {
    beatTimings = script_beats.map((b, i) => {
      const from = b.start_frame as number;
      const nextStart =
        script_beats[i + 1]?.start_frame ?? durationInFrames - OUTRO_FRAMES;
      const duration = b.duration_frames ?? Math.max(1, (nextStart as number) - from);
      return { ...b, from, duration };
    });
  } else if (allHaveDuration) {
    let cursor = titleFrames;
    beatTimings = script_beats.map((b) => {
      const dur = b.duration_frames as number;
      const t = { ...b, from: cursor, duration: dur };
      cursor += dur;
      return t;
    });
  } else {
    const beatsAvailable = Math.max(1, durationInFrames - titleFrames - OUTRO_FRAMES);
    const perBeat = Math.floor(beatsAvailable / Math.max(1, script_beats.length));
    beatTimings = script_beats.map((b, i) => ({
      ...b,
      from: titleFrames + i * perBeat,
      duration:
        i === script_beats.length - 1
          ? beatsAvailable - i * perBeat
          : perBeat,
    }));
  }

  const lastBeat = beatTimings[beatTimings.length - 1];
  const lastBeatEnd = lastBeat ? lastBeat.from + lastBeat.duration : titleFrames;
  const outroStart = Math.min(lastBeatEnd + 8, durationInFrames - 30);
  const outroDuration = Math.max(30, durationInFrames - outroStart);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: BG,
        fontFamily: "Inter, system-ui, sans-serif",
        overflow: "hidden",
      }}
    >
      <DeepGradient />
      <Spotlight accent={accent_color} />

      {voice_audio_url && <Audio src={voice_audio_url} volume={1} />}
      {music_audio_url && (
        <Audio src={music_audio_url} volume={music_volume ?? 0.13} />
      )}

      <CameraMotion>
        <Sequence from={0} durationInFrames={titleFrames}>
          <TitleHook title={title} accent={accent_color} totalFrames={titleFrames} />
        </Sequence>

        {beatTimings.map((beat, i) => (
          <Sequence
            key={i}
            from={beat.from}
            durationInFrames={Math.max(1, beat.duration)}
          >
            {renderBeat(beat, accent_color, i)}
          </Sequence>
        ))}

        <Sequence from={outroStart} durationInFrames={outroDuration}>
          <Outro accent={accent_color} />
        </Sequence>
      </CameraMotion>

      <BrandWatermark />
      <GradeOverlay />
      <AnimatedGrain />
      <VignetteOverlay />
    </AbsoluteFill>
  );
};

const SlowZoom: React.FC<{ duration: number; children: React.ReactNode }> = ({
  duration,
  children,
}) => {
  const frame = useCurrentFrame();
  const scale = interpolate(frame, [0, duration], [1, 1.04], {
    extrapolateRight: "clamp",
  });
  return (
    <AbsoluteFill style={{ transform: `scale(${scale})`, transformOrigin: "center" }}>
      {children}
    </AbsoluteFill>
  );
};

// Directional slide/push transition (replaces the dip-to-background fade "AI tell").
// Outgoing scene slides out while incoming slides in from the opposite edge, with motion blur.
const SceneTransition: React.FC<{
  duration: number;
  index: number;
  children: React.ReactNode;
}> = ({ duration, index, children }) => {
  const frame = useCurrentFrame();
  const W = 12;
  const horizontal = index % 2 === 0;
  const sign = index % 4 < 2 ? 1 : -1;
  const enterP = easeOutQuint(
    interpolate(frame, [0, W], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })
  );
  const exitP = easeOutQuint(
    interpolate(frame, [duration - W, duration], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    })
  );
  const offIn = (1 - enterP) * 80 * sign;
  const offOut = exitP * -80 * sign;
  const off = offIn + offOut;
  const tx = horizontal ? off : 0;
  const ty = horizontal ? 0 : off;
  const blur = (Math.max(0, 1 - enterP) + exitP) * 4;
  return (
    <AbsoluteFill
      style={{
        transform: `translate(${tx}px, ${ty}px)`,
        filter: blur > 0.05 ? `blur(${blur}px)` : undefined,
      }}
    >
      {children}
    </AbsoluteFill>
  );
};

const renderBeat = (beat: BeatTiming, accent: string, index = 0) => {
  const kind = beat.kind ?? "text";
  let content: React.ReactNode;
  if (kind === "counter" && beat.counter) {
    content = (
      <CounterBeat
        counter={beat.counter}
        accent={accent}
        durationFrames={beat.duration}
        icon={beat.icon}
      />
    );
  } else if (kind === "bar_chart" && beat.chart) {
    content = (
      <BarChartBeat
        chart={beat.chart}
        accent={accent}
        durationFrames={beat.duration}
        icon={beat.icon}
      />
    );
  } else if (kind === "line_chart" && beat.line_chart) {
    content = (
      <LineChartBeat
        chart={beat.line_chart}
        accent={accent}
        durationFrames={beat.duration}
        icon={beat.icon}
      />
    );
  } else if (kind === "pie_chart" && beat.pie) {
    content = (
      <PieChartBeat
        chart={beat.pie}
        accent={accent}
        durationFrames={beat.duration}
        icon={beat.icon}
      />
    );
  } else if (kind === "comparison" && beat.comparison) {
    content = (
      <ComparisonBeat
        comparison={beat.comparison}
        accent={accent}
        durationFrames={beat.duration}
      />
    );
  } else if (kind === "ui_mockup" && beat.mockup) {
    content = (
      <UIMockupBeat
        mockup={beat.mockup}
        accent={accent}
        durationFrames={beat.duration}
      />
    );
  } else if (kind === "hero_3d" && beat.hero) {
    content = (
      <HeroBeat hero={beat.hero} accent={accent} durationFrames={beat.duration} />
    );
  } else {
    content = (
      <BeatText
        text={beat.text || ""}
        accent={accent}
        durationFrames={beat.duration}
        icon={beat.icon}
      />
    );
  }
  return (
    <SceneTransition duration={beat.duration} index={index}>
      <SlowZoom duration={beat.duration}>{content}</SlowZoom>
    </SceneTransition>
  );
};

const HeroBeat: React.FC<{
  hero: Hero3DSpec;
  accent: string;
  durationFrames: number;
}> = ({ hero, accent, durationFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = spring({ frame, fps, config: SOFT_SPRING });
  const scale = (hero.scale ?? 1) * interpolate(enter, [0, 1], [0.82, 1]);
  const opacity = interpolate(frame, [0, 12], [0, 1], { extrapolateRight: "clamp" });
  const out = interpolate(frame, [durationFrames - 12, durationFrames], [1, 0], {
    extrapolateLeft: "clamp",
  });
  const floatY = Math.sin((frame / fps) * 1.1) * 10;
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity: opacity * out }}>
      <div
        style={{
          position: "relative",
          width: 760,
          height: 760,
          transform: `translateY(${floatY}px) scale(${scale})`,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <div
          style={{
            position: "absolute",
            width: 560,
            height: 560,
            borderRadius: "50%",
            background: `radial-gradient(circle, ${accent}33 0%, ${accent}10 38%, transparent 66%)`,
            filter: "blur(28px)",
          }}
        />
        <Loop durationInFrames={60} style={{ width: 760, height: 760 }}>
          <OffthreadVideo
            src={hero.video_url}
            transparent
            muted
            style={{ width: 760, height: 760, objectFit: "contain" }}
          />
        </Loop>
      </div>
      {hero.kicker && (
        <div
          style={{
            marginTop: 8,
            fontSize: 54,
            fontWeight: 800,
            letterSpacing: -1,
            color: TEXT,
            textAlign: "center",
            maxWidth: 880,
            lineHeight: 1.1,
            textShadow: "0 4px 24px rgba(0,0,0,0.5)",
          }}
        >
          {hero.kicker}
        </div>
      )}
    </AbsoluteFill>
  );
};

const DeepGradient: React.FC = () => (
  <AbsoluteFill
    style={{
      background: `linear-gradient(165deg, #1B2433 0%, #141C28 48%, #0D131C 100%)`,
    }}
  />
);

// Single soft overhead spotlight — the only background light. Replaces the old
// clutter (mesh + bokeh + grid + particles + leak) for a clean 0x100x-style stage.
const Spotlight: React.FC<{ accent: string }> = ({ accent }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const breathe = 1 + 0.04 * Math.sin((frame / fps) * 0.7);
  return (
    <>
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(ellipse 64% 50% at 50% 32%, rgba(255,255,255,0.13) 0%, rgba(255,255,255,0.04) 38%, transparent 64%)",
          transform: `scale(${breathe})`,
          transformOrigin: "50% 32%",
        }}
      />
      <AbsoluteFill
        style={{
          background: `radial-gradient(ellipse 72% 58% at 50% 58%, ${accent}1F 0%, transparent 64%)`,
          mixBlendMode: "screen",
        }}
      />
    </>
  );
};

// Gradient-mesh: 4 large radial blobs drifting on sine, heavily blurred → soft "painted" depth.
const GradientMesh: React.FC<{ color: string }> = ({ color }) => {
  const frame = useCurrentFrame();
  const { width, height, fps } = useVideoConfig();
  const t = frame / fps;
  const blobs = [
    { c: color, a: "30", fx: 0.20, fy: 0.16, ox: 0.0, oy: 0.0, r: 0.55, sx: [0.12, 0.6], sy: [0.10, 0.55] },
    { c: GOLD, a: "22", fx: 0.15, fy: 0.13, ox: 1.4, oy: 0.7, r: 0.5, sx: [0.45, 0.92], sy: [0.30, 0.8] },
    { c: color, a: "1C", fx: 0.11, fy: 0.18, ox: 2.6, oy: 1.9, r: 0.6, sx: [0.30, 0.78], sy: [0.55, 0.95] },
    { c: "#5BC0BE", a: "18", fx: 0.18, fy: 0.10, ox: 0.6, oy: 3.1, r: 0.48, sx: [0.10, 0.5], sy: [0.45, 0.9] },
  ];
  const layers = blobs.map((b) => {
    const x = interpolate(Math.sin(t * b.fx + b.ox), [-1, 1], [width * b.sx[0], width * b.sx[1]]);
    const y = interpolate(Math.cos(t * b.fy + b.oy), [-1, 1], [height * b.sy[0], height * b.sy[1]]);
    return `radial-gradient(circle at ${x}px ${y}px, ${b.c}${b.a} 0%, transparent ${b.r * 100}%)`;
  });
  // No blur filter: radial gradients with transparent falloff are already soft.
  // (A full-screen blur() in headless Chromium is software-rasterized and ~3-4x's render time.)
  return (
    <AbsoluteFill
      style={{
        background: layers.join(",\n"),
        transform: "scale(1.12)",
        opacity: 0.95,
      }}
    />
  );
};

// Bokeh depth: soft blurred circles with slow parallax — foreground feel without busy.
const BokehLayer: React.FC<{ accent: string; count?: number }> = ({ accent, count = 9 }) => {
  const frame = useCurrentFrame();
  const { width, height, fps } = useVideoConfig();
  const t = frame / fps;
  const circles = Array.from({ length: count }, (_, i) => {
    const seed = i * 2.39 + 0.7;
    const depth = 0.3 + (i % 3) * 0.32; // parallax speed by depth
    const baseX = (Math.sin(seed * 4.1) * 0.5 + 0.5) * width;
    const baseY = (Math.cos(seed * 2.7) * 0.5 + 0.5) * height;
    const driftX = Math.sin(t * 0.06 * depth + seed) * 90 * depth;
    const driftY = Math.cos(t * 0.05 * depth + seed * 1.3) * 70 * depth;
    const size = 90 + (i % 4) * 110 + depth * 60;
    const op = (0.05 + 0.05 * (1 - depth)) * (0.7 + 0.3 * Math.sin(t * 0.3 + seed));
    const tone = i % 3;
    const color = tone === 0 ? accent : tone === 1 ? GOLD : "#5BC0BE";
    return { x: baseX + driftX, y: baseY + driftY, size, op: Math.max(0, op), color };
  });
  // Radial-gradient circles are already soft → no blur filter needed (perf).
  return (
    <AbsoluteFill style={{ pointerEvents: "none", mixBlendMode: "screen" }}>
      {circles.map((c, i) => (
        <div
          key={i}
          style={{
            position: "absolute",
            left: c.x - c.size / 2,
            top: c.y - c.size / 2,
            width: c.size,
            height: c.size,
            borderRadius: "50%",
            background: `radial-gradient(circle, ${c.color} 0%, transparent 72%)`,
            opacity: c.op,
          }}
        />
      ))}
    </AbsoluteFill>
  );
};

// Light leak: 1-2 warm diagonal streaks that slowly breathe, screen blend.
const LightLeak: React.FC = () => {
  const frame = useCurrentFrame();
  const { width, height, fps } = useVideoConfig();
  const t = frame / fps;
  const drift1 = interpolate(Math.sin(t * 0.08), [-1, 1], [-width * 0.1, width * 0.15]);
  const op1 = 0.10 + 0.05 * Math.sin(t * 0.25);
  const drift2 = interpolate(Math.cos(t * 0.06 + 1.5), [-1, 1], [width * 0.7, width * 0.95]);
  const op2 = 0.07 + 0.04 * Math.cos(t * 0.2 + 0.8);
  return (
    <AbsoluteFill style={{ pointerEvents: "none", mixBlendMode: "screen" }}>
      <div
        style={{
          position: "absolute",
          left: drift1,
          top: -height * 0.2,
          width: width * 0.6,
          height: height * 1.4,
          background: `linear-gradient(115deg, transparent 0%, ${GOLD}55 38%, #FFE0A088 50%, ${GOLD}55 62%, transparent 100%)`,
          opacity: Math.max(0, op1),
          transform: "rotate(18deg)",
        }}
      />
      <div
        style={{
          position: "absolute",
          left: drift2,
          top: -height * 0.1,
          width: width * 0.45,
          height: height * 1.2,
          background: `linear-gradient(100deg, transparent 0%, #FF9E6B55 50%, transparent 100%)`,
          opacity: Math.max(0, op2),
          transform: "rotate(-14deg)",
        }}
      />
    </AbsoluteFill>
  );
};

const GridLines: React.FC<{ color: string }> = ({ color }) => {
  const frame = useCurrentFrame();
  const offset = (frame * 0.2) % 90;
  return (
    <AbsoluteFill
      style={{
        opacity: 0.025,
        backgroundImage: `linear-gradient(${color} 1px, transparent 1px),
                          linear-gradient(90deg, ${color} 1px, transparent 1px)`,
        backgroundSize: "90px 90px",
        backgroundPosition: `${offset}px ${offset}px`,
        mixBlendMode: "screen",
        maskImage: "radial-gradient(ellipse 80% 80% at center, black 30%, transparent 75%)",
        WebkitMaskImage: "radial-gradient(ellipse 80% 80% at center, black 30%, transparent 75%)",
      }}
    />
  );
};

const FloatingParticles: React.FC<{ accent: string; count?: number }> = ({
  accent,
  count = 28,
}) => {
  const frame = useCurrentFrame();
  const { width, height, fps } = useVideoConfig();
  const t = frame / fps;

  const particles = Array.from({ length: count }, (_, i) => {
    const seed = i * 1.71 + 0.3;
    const baseX = (Math.sin(seed * 3.7) * 0.5 + 0.5) * width;
    const baseY = (Math.cos(seed * 5.3) * 0.5 + 0.5) * height;
    const speed = 6 + (i % 7) * 3;
    const driftX = Math.sin(t * 0.25 + seed) * 60;
    const driftY = ((t * speed + baseY) % (height + 100)) - 50;
    const x = ((baseX + driftX) % width + width) % width;
    const y = driftY;
    const size = 2 + (i % 4);
    const baseOp = 0.18 + 0.28 * Math.sin(t * 0.6 + seed);
    return { x, y, size, opacity: Math.max(0, baseOp), tone: i % 3 };
  });

  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      {particles.map((p, i) => {
        const color = p.tone === 0 ? accent : p.tone === 1 ? GOLD : TEXT;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: p.x,
              top: p.y,
              width: p.size,
              height: p.size,
              borderRadius: "50%",
              background: color,
              opacity: p.opacity,
              boxShadow: `0 0 ${p.size * 5}px ${color}`,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

// Film grain: ONE static turbulence texture (decoded once → cached) shifted per frame so it "boils".
// Avoids regenerating the SVG filter each frame (that was ~4x'ing render time in headless Chromium).
const GRAIN_URL = `url("data:image/svg+xml,${encodeURIComponent(
  "<svg xmlns='http://www.w3.org/2000/svg' width='260' height='260'><filter id='g'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/><feColorMatrix type='saturate' values='0'/></filter><rect width='100%' height='100%' filter='url(%23g)'/></svg>"
)}")`;
const AnimatedGrain: React.FC = () => {
  const frame = useCurrentFrame();
  // pseudo-random per-frame jump → grain reads as boiling, not scrolling
  const px = ((frame * 73) % 260);
  const py = ((frame * 137) % 260);
  return (
    <AbsoluteFill
      style={{
        opacity: 0.045,
        backgroundImage: GRAIN_URL,
        backgroundSize: "260px 260px",
        backgroundPosition: `${px}px ${py}px`,
        mixBlendMode: "overlay",
        pointerEvents: "none",
      }}
    />
  );
};

const VignetteOverlay: React.FC = () => (
  <AbsoluteFill
    style={{
      background:
        "radial-gradient(ellipse 78% 90% at center 44%, transparent 42%, rgba(0,0,0,0.28) 72%, rgba(0,0,0,0.62) 100%)",
      pointerEvents: "none",
    }}
  />
);

// Global grade: subtle contrast/saturation lift + cool-shadow/warm-highlight split via blended overlays.
const GradeOverlay: React.FC = () => (
  <>
    <AbsoluteFill
      style={{
        background:
          "linear-gradient(180deg, rgba(255,225,180,0.05) 0%, transparent 35%, transparent 65%, rgba(10,20,40,0.10) 100%)",
        mixBlendMode: "soft-light",
        pointerEvents: "none",
      }}
    />
    <AbsoluteFill
      style={{
        background: "rgba(0,0,0,0.05)",
        mixBlendMode: "multiply",
        pointerEvents: "none",
      }}
    />
  </>
);

const ICON_PATHS: Record<IconName, React.ReactNode> = {
  bank: (
    <>
      <path d="M12 4 L22 10 L2 10 Z" />
      <rect x="4" y="11" width="2.5" height="8" />
      <rect x="9" y="11" width="2.5" height="8" />
      <rect x="14" y="11" width="2.5" height="8" />
      <rect x="19" y="11" width="2.5" height="8" />
      <rect x="2" y="20" width="20" height="2" rx="0.5" />
    </>
  ),
  ai: (
    <>
      <path d="M12 2 L13 8 L19 9 L13 10 L12 16 L11 10 L5 9 L11 8 Z" />
      <circle cx="19" cy="19" r="2" />
      <circle cx="5" cy="19" r="1.5" />
    </>
  ),
  growth: (
    <>
      <polyline points="3,18 9,12 13,15 21,5" fill="none" strokeWidth="2" stroke="currentColor" strokeLinejoin="round" strokeLinecap="round" />
      <polyline points="16,5 21,5 21,10" fill="none" strokeWidth="2" stroke="currentColor" strokeLinecap="round" />
    </>
  ),
  money: (
    <>
      <circle cx="12" cy="12" r="9" fill="none" strokeWidth="2" stroke="currentColor" />
      <text x="12" y="16.5" textAnchor="middle" fontSize="11" fontWeight="900" fill="currentColor" fontFamily="Inter">$</text>
    </>
  ),
  chart: (
    <>
      <rect x="3" y="14" width="4" height="7" />
      <rect x="10" y="9" width="4" height="12" />
      <rect x="17" y="4" width="4" height="17" />
    </>
  ),
  warning: (
    <>
      <path d="M12 3 L22 20 L2 20 Z" fill="none" strokeWidth="2" stroke="currentColor" strokeLinejoin="round" />
      <line x1="12" y1="10" x2="12" y2="15" strokeWidth="2" stroke="currentColor" strokeLinecap="round" />
      <circle cx="12" cy="17.5" r="0.8" />
    </>
  ),
  target: (
    <>
      <circle cx="12" cy="12" r="9" fill="none" strokeWidth="2" stroke="currentColor" />
      <circle cx="12" cy="12" r="5" fill="none" strokeWidth="2" stroke="currentColor" />
      <circle cx="12" cy="12" r="1.5" />
    </>
  ),
  clock: (
    <>
      <circle cx="12" cy="12" r="9" fill="none" strokeWidth="2" stroke="currentColor" />
      <line x1="12" y1="12" x2="12" y2="6" strokeWidth="2" stroke="currentColor" strokeLinecap="round" />
      <line x1="12" y1="12" x2="16" y2="14" strokeWidth="2" stroke="currentColor" strokeLinecap="round" />
    </>
  ),
  shield: (
    <>
      <path d="M12 2 L21 6 V13 C21 17 17 21 12 22 C7 21 3 17 3 13 V6 Z" fill="none" strokeWidth="2" stroke="currentColor" strokeLinejoin="round" />
      <polyline points="8,12 11,15 16,9" fill="none" strokeWidth="2" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" />
    </>
  ),
  spark: (
    <>
      <path d="M12 2 L13.5 9 L20 10.5 L13.5 12 L12 19 L10.5 12 L4 10.5 L10.5 9 Z" />
      <circle cx="20" cy="4" r="1.5" />
      <circle cx="4" cy="20" r="1" />
    </>
  ),
};

const Icon: React.FC<{ name: IconName; size?: number; color?: string; progress?: number }> = ({
  name,
  size = 80,
  color = CYAN,
  progress = 1,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;

  let microRotate = 0;
  let microScale = 1;
  let microTranslateY = 0;

  if (name === "ai" || name === "spark") {
    microRotate = Math.sin(t * 1.4) * 5;
    microScale = 1 + Math.sin(t * 2.2) * 0.05;
  } else if (name === "money") {
    microScale = 1 + Math.sin(t * 2.5) * 0.06;
  } else if (name === "growth") {
    microTranslateY = -Math.sin(t * 2) * 4;
    microRotate = Math.sin(t * 1.1) * 1.5;
  } else if (name === "target" || name === "shield") {
    microScale = 1 + Math.sin(t * 1.8) * 0.04;
  } else if (name === "clock") {
    microRotate = t * 8;
  } else if (name === "chart") {
    microTranslateY = -Math.abs(Math.sin(t * 1.6)) * 3;
  } else if (name === "bank") {
    microScale = 1 + Math.sin(t * 1.7) * 0.025;
  } else if (name === "warning") {
    microRotate = Math.sin(t * 6) * 2;
  }

  const entryScale = interpolate(progress, [0, 1], [0.6, 1]);
  const entryRotate = interpolate(progress, [0, 1], [-15, 0]);

  return (
    <div
      style={{
        width: size,
        height: size,
        color,
        opacity: progress,
        transform: `translateY(${microTranslateY}px) scale(${entryScale * microScale}) rotate(${entryRotate + microRotate}deg)`,
        filter: `drop-shadow(0 0 ${size * 0.35}px ${color}cc)`,
      }}
    >
      <svg viewBox="0 0 24 24" width={size} height={size}>
        {ICON_PATHS[name]}
      </svg>
    </div>
  );
};

const CameraMotion: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const panX = Math.sin(t * 0.13) * 18;
  const panY = Math.cos(t * 0.1) * 10;
  const zoom = 1.005 + Math.sin(t * 0.08) * 0.012;
  return (
    <AbsoluteFill
      style={{
        transform: `translate(${panX}px, ${panY}px) scale(${zoom})`,
        transformOrigin: "center",
      }}
    >
      {children}
    </AbsoluteFill>
  );
};

const polar = (cx: number, cy: number, r: number, deg: number) => ({
  x: cx + r * Math.cos((deg * Math.PI) / 180),
  y: cy + r * Math.sin((deg * Math.PI) / 180),
});

const PieChartBeat: React.FC<{
  chart: PieChartSpec;
  accent: string;
  durationFrames: number;
  icon?: IconName;
}> = ({ chart, accent, durationFrames, icon }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const exitProgress = interpolate(
    frame,
    [durationFrames - BEAT_FADE_FRAMES - FADE_END_BUFFER, durationFrames - FADE_END_BUFFER],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  const iconProgress = spring({ frame, fps, config: SOFT_SPRING_FAST });

  const total = chart.slices.reduce((s, sl) => s + sl.value, 0);
  const sortedColors = [accent, GOLD, `${accent}80`, `${GOLD}80`, MUTED];
  const slicesNorm = chart.slices.map((sl, i) => ({
    ...sl,
    percent: (sl.value / total) * 100,
    color: sl.color || sortedColors[i % sortedColors.length],
  }));

  const CX = 540;
  const CY = 540;
  const R_OUTER = 280;
  const R_INNER = 145;
  const SVG_W = 1080;
  const SVG_H = 1080;

  let cumulativeAngle = -90;

  const drawDuration = Math.min(Math.max(durationFrames - 30, 60), 100);
  const centerFade = interpolate(
    frame,
    [drawDuration + 6, drawDuration + 18],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        padding: 30,
        opacity: 1 - exitProgress,
        flexDirection: "column",
      }}
    >
      {icon && (
        <div style={{ marginBottom: 16 }}>
          <Icon name={icon} size={64} color={accent} progress={iconProgress} />
        </div>
      )}
      <svg width={SVG_W} height={SVG_H} viewBox={`0 0 ${SVG_W} ${SVG_H}`}>
        <defs>
          {slicesNorm.map((sl, i) => (
            <radialGradient key={i} id={`sliceGrad${i}`} cx="50%" cy="50%" r="50%">
              <stop offset="60%" stopColor={sl.color} stopOpacity="1" />
              <stop offset="100%" stopColor={sl.color} stopOpacity="0.7" />
            </radialGradient>
          ))}
        </defs>

        {slicesNorm.map((sl, i) => {
          const sliceStart = 10 + i * 14;
          const sliceProgress = spring({
            frame: frame - sliceStart,
            fps,
            config: { damping: 22, stiffness: 130, mass: 0.85 },
          });
          const sweepAngle = (sl.value / total) * 360;
          const currentSweep = sweepAngle * sliceProgress;
          const startAngle = cumulativeAngle;
          const endAngle = cumulativeAngle + currentSweep;
          cumulativeAngle += sweepAngle;

          if (currentSweep < 0.5) return null;

          const startOuter = polar(CX, CY, R_OUTER, startAngle);
          const endOuter = polar(CX, CY, R_OUTER, endAngle);
          const startInner = polar(CX, CY, R_INNER, endAngle);
          const endInner = polar(CX, CY, R_INNER, startAngle);
          const largeArc = currentSweep > 180 ? 1 : 0;

          const path = `M ${startOuter.x.toFixed(2)} ${startOuter.y.toFixed(2)}
                         A ${R_OUTER} ${R_OUTER} 0 ${largeArc} 1 ${endOuter.x.toFixed(2)} ${endOuter.y.toFixed(2)}
                         L ${startInner.x.toFixed(2)} ${startInner.y.toFixed(2)}
                         A ${R_INNER} ${R_INNER} 0 ${largeArc} 0 ${endInner.x.toFixed(2)} ${endInner.y.toFixed(2)}
                         Z`;

          const midAngle = startAngle + (sweepAngle * sliceProgress) / 2;
          const labelPos = polar(CX, CY, R_OUTER + 90, midAngle);
          const labelOpacity = interpolate(sliceProgress, [0.5, 1], [0, 1]);
          const isBiggest =
            sl.percent === Math.max(...slicesNorm.map((s) => s.percent));

          return (
            <g key={i}>
              <path
                d={path}
                fill={`url(#sliceGrad${i})`}
                stroke={BG}
                strokeWidth="3"
                opacity={interpolate(sliceProgress, [0, 0.3], [0, 1])}
                filter={`drop-shadow(0 0 ${isBiggest ? 24 : 12}px ${sl.color}cc)`}
              />
              <text
                x={labelPos.x}
                y={labelPos.y - 18}
                textAnchor="middle"
                fontSize="30"
                fontWeight="700"
                fill={TEXT}
                opacity={labelOpacity * 0.85}
                fontFamily="Inter"
                letterSpacing="0.5"
              >
                {sl.label}
              </text>
              <text
                x={labelPos.x}
                y={labelPos.y + 28}
                textAnchor="middle"
                fontSize={isBiggest ? 56 : 44}
                fontWeight="900"
                fill={sl.color}
                opacity={labelOpacity}
                fontFamily="Inter"
                style={{ fontVariantNumeric: "tabular-nums" }}
                filter={`drop-shadow(0 0 ${isBiggest ? 24 : 12}px ${sl.color})`}
              >
                {Math.round(sl.percent)}%
              </text>
            </g>
          );
        })}

        <text
          x={CX}
          y={CY - 12}
          textAnchor="middle"
          fontSize="28"
          fill={MUTED}
          letterSpacing="6"
          fontFamily="Inter"
          fontWeight="700"
          opacity={interpolate(centerFade, [0, 1], [0, 0.85])}
        >
          {(chart.center_label || "PORTAFOLIO").toUpperCase()}
        </text>
        <text
          x={CX}
          y={CY + 48}
          textAnchor="middle"
          fontSize="64"
          fontWeight="900"
          fill={accent}
          fontFamily="Inter"
          opacity={centerFade}
          filter={`drop-shadow(0 0 30px ${accent})`}
        >
          100%
        </text>
      </svg>
    </AbsoluteFill>
  );
};

const TitleHook: React.FC<{ title: string; accent: string; totalFrames: number }> = ({
  title,
  accent,
  totalFrames,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const words = title.split(" ");

  const exitProgress = interpolate(
    frame,
    [totalFrames - BEAT_FADE_FRAMES - FADE_END_BUFFER, totalFrames - FADE_END_BUFFER],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  const exitOpacity = 1 - exitProgress;
  const exitScale = interpolate(exitProgress, [0, 1], [1, 0.96]);

  const sheenStart = words.length * 6 + 20;
  const sheenDuration = 36;
  const sheenProgress = interpolate(
    frame,
    [sheenStart, sheenStart + sheenDuration],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        padding: 80,
        opacity: exitOpacity,
        transform: `scale(${exitScale})`,
      }}
    >
      <div
        style={{
          position: "relative",
          display: "block",
          textAlign: "center",
          maxWidth: 980,
          lineHeight: 1.05,
        }}
      >
        {words.map((word, i) => {
          const wordStart = i * 7;
          const progress = spring({
            frame: frame - wordStart,
            fps,
            config: SOFT_SPRING,
          });
          const opacity = interpolate(progress, [0, 1], [0, 1]);
          const scale = interpolate(progress, [0, 1], [0.7, 1]);
          const blur = interpolate(progress, [0, 1], [12, 0]);
          const isLast = i === words.length - 1;

          return (
            <span
              key={i}
              style={{
                display: "inline-block",
                fontSize: words.length > 3 ? 92 : 116,
                fontWeight: 900,
                color: isLast ? accent : TEXT,
                letterSpacing: -3,
                opacity,
                marginRight: i < words.length - 1 ? 18 : 0,
                transform: `scale(${scale})`,
                filter: `blur(${blur}px)`,
                textShadow: isLast
                  ? `0 0 60px ${accent}55, 0 4px 30px rgba(0,0,0,0.4)`
                  : "0 4px 30px rgba(0,0,0,0.4)",
              }}
            >
              {word}
            </span>
          );
        })}
        {sheenProgress > 0 && sheenProgress < 1 && (
          <div
            style={{
              position: "absolute",
              inset: -50,
              background: `linear-gradient(105deg,
                transparent 35%,
                ${accent}40 47%,
                rgba(255,255,255,0.55) 50%,
                ${accent}40 53%,
                transparent 65%)`,
              transform: `translateX(${interpolate(sheenProgress, [0, 1], [-120, 120])}%)`,
              mixBlendMode: "screen",
              pointerEvents: "none",
              borderRadius: 12,
            }}
          />
        )}
      </div>
      <div
        style={{
          marginTop: 56,
          width: interpolate(
            spring({
              frame: frame - words.length * 7,
              fps,
              config: SOFT_SPRING,
            }),
            [0, 1],
            [0, 200]
          ),
          height: 6,
          background: accent,
          borderRadius: 3,
          boxShadow: `0 0 40px ${accent}b0`,
        }}
      />
    </AbsoluteFill>
  );
};

const BeatText: React.FC<{
  text: string;
  accent: string;
  durationFrames: number;
  icon?: IconName;
}> = ({ text, accent, durationFrames, icon }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const enter = spring({ frame, fps, config: SOFT_SPRING });
  const exitProgress = interpolate(
    frame,
    [durationFrames - BEAT_FADE_FRAMES - FADE_END_BUFFER, durationFrames - FADE_END_BUFFER],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  const opacity = interpolate(enter, [0, 1], [0, 1]) * (1 - exitProgress);
  const translateY = interpolate(enter, [0, 1], [40, 0]);
  const scale = interpolate(enter, [0, 1], [0.94, 1]);

  const iconProgress = spring({ frame: frame - 4, fps, config: SOFT_SPRING_FAST });

  const accentPattern = /(\$[\d,\.]+\s?[A-Z]{0,4}|\+?\d+[\d,\.]*\s?%|\d+[\d,\.]*\s?(MXN|USD|ARS|COP|CLP))/g;
  const parts: { text: string; accent: boolean }[] = [];
  let lastIdx = 0;
  let match;
  while ((match = accentPattern.exec(text)) !== null) {
    if (match.index > lastIdx)
      parts.push({ text: text.slice(lastIdx, match.index), accent: false });
    parts.push({ text: match[0], accent: true });
    lastIdx = match.index + match[0].length;
  }
  if (lastIdx < text.length) parts.push({ text: text.slice(lastIdx), accent: false });

  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        padding: 80,
        flexDirection: "column",
        gap: 36,
      }}
    >
      {icon && <Icon name={icon} size={110} color={accent} progress={iconProgress} />}
      <div
        style={{
          fontSize: 84,
          fontWeight: 800,
          color: TEXT,
          letterSpacing: -1.8,
          lineHeight: 1.12,
          textAlign: "center",
          opacity,
          transform: `translateY(${translateY}px) scale(${scale})`,
          maxWidth: 940,
          textShadow: "0 4px 30px rgba(0,0,0,0.4)",
        }}
      >
        {parts.map((p, i) =>
          p.accent ? (
            <span
              key={i}
              style={{
                color: accent,
                fontWeight: 900,
                textShadow: `0 0 30px ${accent}40`,
                whiteSpace: "nowrap",
              }}
            >
              {p.text}
            </span>
          ) : (
            <span key={i}>{p.text}</span>
          )
        )}
      </div>
    </AbsoluteFill>
  );
};

// ── Odometer digit roll ────────────────────────────────────────────────
const DIGIT_STRIP = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0];

const RollDigit: React.FC<{
  cont: number;
  h: number;
  w: number;
  fontSize: number;
  color: string;
  dim?: boolean;
}> = ({ cont, h, w, fontSize, color, dim }) => {
  const v = ((cont % 10) + 10) % 10;
  return (
    <div
      style={{
        height: h,
        width: w,
        overflow: "hidden",
        display: "inline-block",
        position: "relative",
        opacity: dim ? 0.14 : 1,
      }}
    >
      <div style={{ transform: `translateY(${(-v * h).toFixed(3)}px)` }}>
        {DIGIT_STRIP.map((d, i) => (
          <div
            key={i}
            style={{
              height: h,
              lineHeight: `${h}px`,
              textAlign: "center",
              fontSize,
              fontWeight: 900,
              color,
              fontVariantNumeric: "tabular-nums",
            }}
          >
            {d}
          </div>
        ))}
      </div>
    </div>
  );
};

const RollingNumber: React.FC<{
  value: number;
  maxValue: number;
  decimals?: number;
  group?: boolean;
  prefix?: string;
  suffixCode?: string;
  percent?: boolean;
  fontSize: number;
  color: string;
  accent: string;
}> = ({
  value,
  maxValue,
  decimals = 0,
  group = true,
  prefix,
  suffixCode,
  percent,
  fontSize,
  color,
  accent,
}) => {
  const h = fontSize * 0.98;
  const w = fontSize * 0.56;
  const intDigits = Math.max(
    1,
    Math.floor(Math.log10(Math.max(1, Math.abs(maxValue)))) + 1
  );
  // Proper odometer: only the least-significant displayed place rolls continuously;
  // higher places stay snapped to whole digits and only roll during the carry window.
  const smallestP = decimals > 0 ? -decimals : 0;
  const contFor = (p: number) => {
    const q = value / Math.pow(10, p);
    if (p === smallestP) return q;
    const base = Math.floor(q);
    const frac = q - base;
    const carry = frac > 0.9 ? (frac - 0.9) * 10 : 0;
    return base + carry;
  };

  const cells: React.ReactNode[] = [];
  for (let p = intDigits - 1; p >= 0; p--) {
    const cont = contFor(p);
    const active = Math.abs(value) >= Math.pow(10, p) || p === 0;
    cells.push(
      <RollDigit
        key={`i${p}`}
        cont={cont}
        h={h}
        w={w}
        fontSize={fontSize}
        color={color}
        dim={!active}
      />
    );
    if (group && p > 0 && p % 3 === 0) {
      cells.push(
        <span
          key={`g${p}`}
          style={{
            fontSize,
            fontWeight: 900,
            color,
            lineHeight: `${h}px`,
            width: fontSize * 0.3,
            textAlign: "center",
          }}
        >
          ,
        </span>
      );
    }
  }
  if (decimals > 0) {
    cells.push(
      <span
        key="dot"
        style={{
          fontSize,
          fontWeight: 900,
          color,
          lineHeight: `${h}px`,
          width: fontSize * 0.32,
          textAlign: "center",
        }}
      >
        .
      </span>
    );
    for (let d = 1; d <= decimals; d++) {
      cells.push(
        <RollDigit
          key={`d${d}`}
          cont={contFor(-d)}
          h={h}
          w={w}
          fontSize={fontSize}
          color={color}
        />
      );
    }
  }
  return (
    <div style={{ display: "flex", alignItems: "flex-end", justifyContent: "center" }}>
      {prefix && (
        <span
          style={{
            fontSize: fontSize * 0.6,
            fontWeight: 900,
            color,
            lineHeight: 1,
            marginRight: fontSize * 0.03,
            alignSelf: "flex-start",
            marginTop: fontSize * 0.06,
          }}
        >
          {prefix}
        </span>
      )}
      <div style={{ display: "flex", alignItems: "flex-end" }}>{cells}</div>
      {percent && (
        <span
          style={{
            fontSize: fontSize * 0.62,
            fontWeight: 900,
            color: accent,
            lineHeight: 1,
            marginLeft: fontSize * 0.02,
          }}
        >
          %
        </span>
      )}
      {suffixCode && (
        <span
          style={{
            fontSize: fontSize * 0.3,
            fontWeight: 800,
            color: MUTED,
            letterSpacing: 1.5,
            marginLeft: fontSize * 0.09,
            marginBottom: fontSize * 0.14,
            alignSelf: "flex-end",
          }}
        >
          {suffixCode}
        </span>
      )}
    </div>
  );
};

const CounterBeat: React.FC<{
  counter: CounterSpec;
  accent: string;
  durationFrames: number;
  icon?: IconName;
}> = ({ counter, accent, durationFrames, icon }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const enter = spring({ frame, fps, config: SOFT_SPRING });
  const exitProgress = interpolate(
    frame,
    [durationFrames - BEAT_FADE_FRAMES - FADE_END_BUFFER, durationFrames - FADE_END_BUFFER],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  const opacity = interpolate(enter, [0, 1], [0, 1]) * (1 - exitProgress);

  const countStart = 14;
  const countDuration = Math.min(Math.max(durationFrames - countStart - 28, 36), 70);
  const countProgress = interpolate(
    frame,
    [countStart, countStart + countDuration],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  const eased = easeOutCubic(countProgress);
  const from = counter.from ?? 0;
  const currentValue = from + (counter.to - from) * eased;

  const fmt = counter.format;
  let prefix: string | undefined;
  let suffixCode: string | undefined;
  let decimals = 0;
  let group = true;
  let percent = false;
  if (fmt === "currency_mxn") {
    prefix = "$";
    suffixCode = "MXN";
  } else if (fmt === "currency_usd") {
    prefix = "$";
    suffixCode = "USD";
  } else if (fmt === "currency_ars") {
    prefix = "$";
    suffixCode = "ARS";
  } else if (fmt === "percent") {
    decimals = 1;
    group = false;
    percent = true;
  }
  if (counter.suffix) suffixCode = counter.suffix;
  const maxValue = Math.max(Math.abs(counter.to), Math.abs(from), 1);

  const finalPunch = interpolate(
    frame,
    [countStart + countDuration - 4, countStart + countDuration + 12],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  const punchScale = 1 + 0.08 * Math.sin(finalPunch * Math.PI);
  const breathingScale = 1 + 0.012 * Math.sin((frame / fps) * 2);

  const iconProgress = spring({ frame: frame - 2, fps, config: OVERSHOOT_SOFT });
  // Staggered ease-out/overshoot entrances (icon → label → number).
  const labelEnter = spring({ frame: frame - 5, fps, config: OVERSHOOT_SOFT });
  const numberEnter = spring({ frame: frame - 9, fps, config: OVERSHOOT_SPRING });
  const numberScaleIn = interpolate(numberEnter, [0, 1], [0.82, 1]);

  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        padding: 60,
        opacity,
        flexDirection: "column",
        gap: 28,
      }}
    >
      {icon && <Icon name={icon} size={100} color={accent} progress={iconProgress} />}
      {counter.label && (
        <div
          style={{
            fontSize: 30,
            color: MUTED,
            letterSpacing: 5,
            textTransform: "uppercase",
            fontWeight: 700,
            opacity: interpolate(labelEnter, [0, 0.6], [0, 1], { extrapolateRight: "clamp" }),
            transform: `translateY(${interpolate(labelEnter, [0, 1], [26, 0])}px)`,
          }}
        >
          {counter.label}
        </div>
      )}
      <div
        style={{
          position: "relative",
          transform: `scale(${punchScale * breathingScale * numberScaleIn})`,
          opacity: interpolate(numberEnter, [0, 0.5], [0, 1], { extrapolateRight: "clamp" }),
          fontFamily: "'Inter', 'SF Pro Display', system-ui, sans-serif",
          letterSpacing: -3,
        }}
      >
        {/* Bloom/halation: blurred screen-blend duplicate that swells on the final punch. */}
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            filter: "blur(24px)",
            mixBlendMode: "screen",
            opacity: 0.55 + 0.35 * Math.sin(finalPunch * Math.PI),
            pointerEvents: "none",
          }}
          aria-hidden
        >
          <RollingNumber
            value={currentValue}
            maxValue={maxValue}
            decimals={decimals}
            group={group}
            prefix={prefix}
            suffixCode={suffixCode}
            percent={percent}
            fontSize={128}
            color={accent}
            accent={accent}
          />
        </div>
        <div
          style={{
            position: "relative",
            filter: `blur(${Math.max(0, 1 - numberEnter) * 5}px) drop-shadow(0 0 70px ${accent}55) drop-shadow(0 8px 40px rgba(0,0,0,0.5))`,
          }}
        >
          <RollingNumber
            value={currentValue}
            maxValue={maxValue}
            decimals={decimals}
            group={group}
            prefix={prefix}
            suffixCode={suffixCode}
            percent={percent}
            fontSize={128}
            color={accent}
            accent={accent}
          />
        </div>
      </div>
      <div
        style={{
          width: interpolate(eased, [0, 1], [40, 240]),
          height: 6,
          background: accent,
          borderRadius: 3,
          boxShadow: `0 0 30px ${accent}90`,
        }}
      />
    </AbsoluteFill>
  );
};

const BarChartBeat: React.FC<{
  chart: BarChartSpec;
  accent: string;
  durationFrames: number;
  icon?: IconName;
}> = ({ chart, accent, durationFrames, icon }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const exitProgress = interpolate(
    frame,
    [durationFrames - BEAT_FADE_FRAMES - FADE_END_BUFFER, durationFrames - FADE_END_BUFFER],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  const maxValue = Math.max(...chart.bars.map((b) => b.value));

  const iconProgress = spring({ frame, fps, config: SOFT_SPRING_FAST });

  const ranked = chart.bars
    .map((b, i) => ({ i, value: b.value }))
    .sort((a, b) => b.value - a.value);
  const rankOf = (idx: number) => ranked.findIndex((r) => r.i === idx) + 1;
  const mutedBar = hexBlend(accent, BG, 0.5);

  return (
    <AbsoluteFill
      style={{
        padding: "80px 60px 140px 60px",
        flexDirection: "column",
        justifyContent: "center",
        opacity: 1 - exitProgress,
      }}
    >
      {icon && (
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            marginBottom: 40,
          }}
        >
          <Icon name={icon} size={70} color={accent} progress={iconProgress} />
        </div>
      )}
      <div style={{ display: "flex", flexDirection: "column", gap: 36 }}>
        {chart.bars.map((bar, i) => {
          const barStart = 12 + i * 10;
          const barEnter = spring({
            frame: frame - barStart,
            fps,
            config: OVERSHOOT_SOFT,
          });
          const barProgress = Math.min(1, Math.max(0, barEnter));
          const enterX = interpolate(barEnter, [0, 1], [-44, 0]);
          const rawPct = (bar.value / maxValue) * 100;
          const widthPercent = Math.max(rawPct, 3.5) * barProgress;
          const isWinner = rankOf(i) === 1;
          const color = bar.color || (isWinner ? accent : mutedBar);
          const valueFormatted = formatValue(bar.value * barProgress, chart.format);
          const valuePunch = interpolate(
            frame,
            [barStart + 42, barStart + 56],
            [1, isWinner ? 1.1 : 1.04],
            { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
          );
          const rank = rankOf(i);
          const isTop = rank === 1;
          const shimmerCycle = 95;
          const sp = (((frame - barStart) % shimmerCycle) + shimmerCycle) % shimmerCycle / shimmerCycle;
          const shimmerX = interpolate(sp, [0, 1], [-70, 180]);
          const shimmerOn = barProgress > 0.65;

          return (
            <div
              key={i}
              style={{
                width: "100%",
                opacity: interpolate(barEnter, [0, 0.6], [0, 1], { extrapolateRight: "clamp" }),
                transform: `translateX(${enterX}px)`,
                filter: `blur(${Math.max(0, 1 - barProgress) * 3}px)`,
              }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: 14,
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
                  <div
                    style={{
                      width: 34,
                      height: 34,
                      borderRadius: 10,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontSize: 20,
                      fontWeight: 900,
                      color: isTop ? BG : MUTED,
                      background: isTop ? color : "rgba(255,255,255,0.06)",
                      border: isTop ? "none" : "1px solid rgba(255,255,255,0.1)",
                      boxShadow: isTop ? `0 0 18px ${color}aa` : "none",
                      fontVariantNumeric: "tabular-nums",
                    }}
                  >
                    {rank}
                  </div>
                  <div
                    style={{
                      fontSize: 34,
                      color: TEXT,
                      fontWeight: isWinner ? 900 : 700,
                      letterSpacing: -0.5,
                    }}
                  >
                    {bar.label}
                  </div>
                </div>
                <div
                  style={{
                    fontSize: isWinner ? 38 : 34,
                    color,
                    fontWeight: 900,
                    fontVariantNumeric: "tabular-nums",
                    textShadow: `0 0 24px ${color}80`,
                    transform: `scale(${valuePunch})`,
                    padding: "6px 18px",
                    borderRadius: 12,
                    background: `${color}14`,
                    border: `1px solid ${color}40`,
                  }}
                >
                  {valueFormatted}
                </div>
              </div>
              <div
                style={{
                  height: 52,
                  background: "rgba(255,255,255,0.04)",
                  borderRadius: 10,
                  overflow: "hidden",
                  boxShadow: "inset 0 2px 14px rgba(0,0,0,0.55)",
                  border: "1px solid rgba(255,255,255,0.04)",
                }}
              >
                <div
                  style={{
                    position: "relative",
                    height: "100%",
                    width: `${widthPercent}%`,
                    background: `linear-gradient(90deg, ${color}cc 0%, ${color} 50%, ${color}ee 100%)`,
                    borderRadius: 10,
                    overflow: "hidden",
                    boxShadow: `0 0 32px ${color}b0, inset 0 1px 0 rgba(255,255,255,0.15)`,
                  }}
                >
                  {shimmerOn && (
                    <div
                      style={{
                        position: "absolute",
                        top: 0,
                        left: 0,
                        height: "100%",
                        width: "45%",
                        background:
                          "linear-gradient(105deg, transparent 0%, rgba(255,255,255,0.45) 50%, transparent 100%)",
                        transform: `translateX(${shimmerX}%)`,
                        mixBlendMode: "screen",
                      }}
                    />
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

const LineChartBeat: React.FC<{
  chart: LineChartSpec;
  accent: string;
  durationFrames: number;
  icon?: IconName;
}> = ({ chart, accent, durationFrames, icon }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const exitProgress = interpolate(
    frame,
    [durationFrames - BEAT_FADE_FRAMES - FADE_END_BUFFER, durationFrames - FADE_END_BUFFER],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const iconProgress = spring({ frame, fps, config: SOFT_SPRING_FAST });

  const PAD_L = 100;
  const PAD_R = 100;
  const PAD_T = 60;
  const PAD_B = 100;
  const CHART_W = 980;
  const CHART_H = 820;
  const innerW = CHART_W - PAD_L - PAD_R;
  const innerH = CHART_H - PAD_T - PAD_B;

  const seriesList: LineSeries[] =
    chart.series && chart.series.length > 0
      ? chart.series
      : [{ points: chart.points, color: accent }];

  const allY = seriesList.flatMap((s) => s.points.map((p) => p.y));
  const rawMax = Math.max(...allY);
  const rawMin = Math.min(...allY);
  const span = rawMax - rawMin || 1;
  const yMax = rawMax + span * 0.1;
  const yMin = rawMin - span * 0.12;
  const yRange = yMax - yMin || 1;

  const projectX = (i: number, n: number) =>
    PAD_L + (i / Math.max(1, n - 1)) * innerW;
  const projectY = (v: number) => PAD_T + innerH - ((v - yMin) / yRange) * innerH;

  const drawStart = 12;
  const drawDuration = Math.min(Math.max(durationFrames - drawStart - 40, 50), 90);
  const pathLength = 2200;

  const maxDrawEased = easeInOutCubic(
    interpolate(frame, [drawStart, drawStart + drawDuration], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    })
  );

  const gridLineCount = 4;
  const gridLines = Array.from({ length: gridLineCount + 1 }, (_, i) => {
    const yRatio = i / gridLineCount;
    return {
      y: PAD_T + innerH - yRatio * innerH,
      value: yMin + yRatio * yRange,
    };
  });

  const axisSeries = seriesList.reduce((a, b) =>
    b.points.length > a.points.length ? b : a
  );

  const compact = (v: number): string => {
    if (chart.format === "percent") return formatValue(v, chart.format);
    const a = Math.abs(v);
    const pre = chart.format && chart.format.startsWith("currency") ? "$" : "";
    let s: string;
    if (a >= 1_000_000) s = (a / 1_000_000).toFixed(a >= 10_000_000 ? 0 : 1) + "M";
    else if (a >= 1000) s = (a / 1000).toFixed(a >= 10_000 ? 0 : 1) + "k";
    else s = String(Math.round(a));
    return (v < 0 ? "-" : "") + pre + s;
  };

  const pillFont = 40;
  const pillH = 58;

  const renderSeries = (s: LineSeries, si: number) => {
    const color = s.color ?? accent;
    const n = s.points.length;
    const sp = s.points.map((p, i) => ({
      x: projectX(i, n),
      y: projectY(p.y),
      raw: p,
    }));

    let pathD = "";
    for (let i = 0; i < sp.length; i++) {
      const p = sp[i];
      if (i === 0) {
        pathD += `M ${p.x.toFixed(2)} ${p.y.toFixed(2)}`;
      } else {
        const prev = sp[i - 1];
        const cx = prev.x + (p.x - prev.x) * 0.5;
        pathD += ` C ${cx.toFixed(2)} ${prev.y.toFixed(2)} ${cx.toFixed(2)} ${p.y.toFixed(2)} ${p.x.toFixed(2)} ${p.y.toFixed(2)}`;
      }
    }
    const lastP = sp[sp.length - 1];
    const firstP = sp[0];
    const areaD = `${pathD} L ${lastP.x.toFixed(2)} ${PAD_T + innerH} L ${firstP.x.toFixed(2)} ${PAD_T + innerH} Z`;

    const sStart = drawStart + si * 6;
    const drawEased = easeInOutCubic(
      interpolate(frame, [sStart, sStart + drawDuration], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      })
    );
    const dashOffset = pathLength * (1 - drawEased);

    const segLens: number[] = [];
    let totalLen = 0;
    for (let i = 1; i < sp.length; i++) {
      segLens.push(Math.hypot(sp[i].x - sp[i - 1].x, sp[i].y - sp[i - 1].y));
      totalLen += segLens[segLens.length - 1];
    }
    let tgt = drawEased * totalLen;
    let lead = { x: sp[0].x, y: sp[0].y };
    for (let i = 0; i < segLens.length; i++) {
      if (tgt <= segLens[i] || i === segLens.length - 1) {
        const t = segLens[i] ? Math.min(1, tgt / segLens[i]) : 0;
        lead = {
          x: sp[i].x + (sp[i + 1].x - sp[i].x) * t,
          y: sp[i].y + (sp[i + 1].y - sp[i].y) * t,
        };
        break;
      }
      tgt -= segLens[i];
    }
    const leadVisible = drawEased > 0.015 && drawEased < 0.992;
    const leadPulse = 1 + 0.12 * Math.sin((frame / fps) * 6);
    const lastPulse = 1 + 0.08 * Math.sin((frame / fps) * 3.5);

    const lastValStr = formatValue(lastP.raw.y, chart.format).replace(
      / (MXN|USD|ARS)$/,
      ""
    );
    const pillW = Math.max(120, lastValStr.length * (pillFont * 0.6) + 40);
    const pillCy = Math.min(
      CHART_H - pillH / 2 - 4,
      Math.max(pillH / 2 + 4, lastP.y)
    );
    const pillCx = Math.max(pillW / 2 + 12, lastP.x - 22 - pillW / 2);
    const pillOpacity = interpolate(drawEased, [0.62, 0.95], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });

    return (
      <g key={si}>
        <defs>
          <linearGradient id={`lineFill${si}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity="0.4" />
            <stop offset="100%" stopColor={color} stopOpacity="0" />
          </linearGradient>
        </defs>

        <path d={areaD} fill={`url(#lineFill${si})`} opacity={drawEased * 0.7} />

        <path
          d={pathD}
          fill="none"
          stroke={color}
          strokeWidth="20"
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeDasharray={pathLength}
          strokeDashoffset={dashOffset}
          opacity={0.2}
          style={{ filter: "blur(10px)" }}
        />
        <path
          d={pathD}
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeDasharray={pathLength}
          strokeDashoffset={dashOffset}
          filter={`drop-shadow(0 0 18px ${color})`}
        />

        {leadVisible && (
          <g>
            <circle cx={lead.x} cy={lead.y} r={24 * leadPulse} fill={color} opacity={0.18} />
            <circle
              cx={lead.x}
              cy={lead.y}
              r={9 * leadPulse}
              fill="#FFFFFF"
              filter={`drop-shadow(0 0 20px ${color})`}
            />
          </g>
        )}

        {sp.map((p, i) => {
          const appearAt = sStart + drawDuration * (i / Math.max(1, sp.length - 1));
          const prog = spring({ frame: frame - appearAt, fps, config: SOFT_SPRING_FAST });
          const sc = interpolate(prog, [0, 1], [0, 1]);
          const isLast = i === sp.length - 1;
          const r = isLast ? 16 : 8;
          return (
            <g key={i}>
              {isLast && (
                <circle
                  cx={p.x}
                  cy={p.y}
                  r={r * sc * 2.2 * lastPulse}
                  fill="none"
                  stroke={color}
                  strokeWidth="2"
                  opacity={sc * 0.35}
                />
              )}
              <circle
                cx={p.x}
                cy={p.y}
                r={r * sc * (isLast ? lastPulse : 1)}
                fill={isLast ? color : BG}
                stroke={color}
                strokeWidth="4"
                filter={`drop-shadow(0 0 ${isLast ? 30 : 10}px ${color}dd)`}
              />
            </g>
          );
        })}

        {pillOpacity > 0.01 && (
          <g opacity={pillOpacity}>
            <rect
              x={pillCx - pillW / 2}
              y={pillCy - pillH / 2}
              width={pillW}
              height={pillH}
              rx={pillH / 2}
              fill={`${color}1A`}
              stroke={`${color}66`}
              strokeWidth="2"
            />
            <text
              x={pillCx}
              y={pillCy + pillFont * 0.34}
              textAnchor="middle"
              fontSize={pillFont}
              fontWeight="900"
              fill={color}
              fontFamily="Inter"
              style={{ fontVariantNumeric: "tabular-nums" }}
              filter={`drop-shadow(0 0 22px ${color}80)`}
            >
              {lastValStr}
            </text>
          </g>
        )}
      </g>
    );
  };

  const hasLegend = seriesList.some((s) => s.label);

  return (
    <AbsoluteFill
      style={{
        padding: 40,
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        opacity: 1 - exitProgress,
      }}
    >
      {icon && (
        <div style={{ marginBottom: 20 }}>
          <Icon name={icon} size={64} color={accent} progress={iconProgress} />
        </div>
      )}

      {hasLegend && (
        <div
          style={{
            display: "flex",
            gap: 40,
            marginBottom: 14,
            opacity: interpolate(maxDrawEased, [0, 0.22], [0, 1], {
              extrapolateRight: "clamp",
            }),
          }}
        >
          {seriesList.map((s, i) =>
            s.label ? (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <span
                  style={{
                    width: 28,
                    height: 6,
                    borderRadius: 3,
                    background: s.color ?? accent,
                    boxShadow: `0 0 14px ${s.color ?? accent}`,
                  }}
                />
                <span style={{ fontSize: 27, fontWeight: 700, color: TEXT, letterSpacing: -0.5 }}>
                  {s.label}
                </span>
              </div>
            ) : null
          )}
        </div>
      )}

      <svg width={CHART_W} height={CHART_H} viewBox={`0 0 ${CHART_W} ${CHART_H}`}>
        {gridLines.map((g, i) => (
          <g key={i}>
            <line
              x1={PAD_L}
              y1={g.y}
              x2={CHART_W - PAD_R}
              y2={g.y}
              stroke="rgba(255,255,255,0.06)"
              strokeWidth="1"
              strokeDasharray="4 8"
            />
            <text
              x={PAD_L - 16}
              y={g.y + 7}
              textAnchor="end"
              fontSize="20"
              fontWeight="600"
              fill={MUTED}
              opacity={maxDrawEased * 0.5}
              fontFamily="Inter"
              style={{ fontVariantNumeric: "tabular-nums" }}
            >
              {compact(g.value)}
            </text>
          </g>
        ))}

        {seriesList.map((s, si) => renderSeries(s, si))}

        {axisSeries.points.map((p, i) => {
          const n = axisSeries.points.length;
          const x = projectX(i, n);
          const appearAt = drawStart + drawDuration * (i / Math.max(1, n - 1));
          const op = interpolate(frame - appearAt, [0, 10], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });
          return (
            <text
              key={i}
              x={x}
              y={CHART_H - PAD_B + 40}
              textAnchor="middle"
              fontSize="22"
              fontWeight="600"
              fill={MUTED}
              opacity={op}
              fontFamily="Inter"
            >
              {String(p.x)}
            </text>
          );
        })}
      </svg>
    </AbsoluteFill>
  );
};

const ComparisonBeat: React.FC<{
  comparison: ComparisonSpec;
  accent: string;
  durationFrames: number;
}> = ({ comparison, accent, durationFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const exitProgress = interpolate(
    frame,
    [durationFrames - BEAT_FADE_FRAMES - FADE_END_BUFFER, durationFrames - FADE_END_BUFFER],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const enterA = spring({ frame, fps, config: SOFT_SPRING });
  const enterArrow = spring({ frame: frame - 18, fps, config: SOFT_SPRING });
  const enterB = spring({ frame: frame - 32, fps, config: SOFT_SPRING });
  const enterDelta = spring({ frame: frame - 50, fps, config: SOFT_SPRING });

  const arrowFloat = Math.sin((frame / fps) * 2.5) * 6;
  const deltaPulse = 1 + 0.035 * Math.sin((frame / fps) * 3);

  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        padding: 60,
        flexDirection: "column",
        opacity: 1 - exitProgress,
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 36,
          justifyContent: "center",
        }}
      >
        <ComparisonCard
          label={comparison.before.label}
          value={comparison.before.value}
          color={MUTED}
          progress={enterA}
        />
        <div
          style={{
            opacity: interpolate(enterArrow, [0, 1], [0, 1]),
            transform: `translateX(${arrowFloat}px)`,
          }}
        >
          <svg width="100" height="100" viewBox="0 0 100 100">
            <defs>
              <linearGradient id="arrowGrad" x1="0%" y1="50%" x2="100%" y2="50%">
                <stop offset="0%" stopColor={accent} stopOpacity="0.4" />
                <stop offset="100%" stopColor={accent} stopOpacity="1" />
              </linearGradient>
            </defs>
            <line x1="10" y1="50" x2="80" y2="50" stroke="url(#arrowGrad)" strokeWidth="6" strokeLinecap="round" />
            <polyline
              points="60,28 88,50 60,72"
              fill="none"
              stroke={accent}
              strokeWidth="6"
              strokeLinecap="round"
              strokeLinejoin="round"
              filter={`drop-shadow(0 0 12px ${accent})`}
            />
          </svg>
        </div>
        <ComparisonCard
          label={comparison.after.label}
          value={comparison.after.value}
          color={accent}
          highlight
          progress={enterB}
        />
      </div>
      {comparison.delta && (
        <div
          style={{
            marginTop: 64,
            fontSize: 68,
            color: accent,
            fontWeight: 900,
            letterSpacing: -1.5,
            opacity: interpolate(enterDelta, [0, 1], [0, 1]),
            transform: `scale(${interpolate(enterDelta, [0, 1], [0.6, 1]) * deltaPulse})`,
            textShadow: `0 0 60px ${accent}90`,
            padding: "14px 36px",
            border: `3px solid ${accent}`,
            borderRadius: 100,
            fontVariantNumeric: "tabular-nums",
            background: `${accent}10`,
          }}
        >
          {comparison.delta}
        </div>
      )}
    </AbsoluteFill>
  );
};

const ComparisonCard: React.FC<{
  label: string;
  value: string;
  color: string;
  highlight?: boolean;
  progress: number;
}> = ({ label, value, color, highlight, progress }) => {
  const opacity = interpolate(progress, [0, 1], [0, 1]);
  const translateY = interpolate(progress, [0, 1], [30, 0]);
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 16,
        opacity,
        transform: `translateY(${translateY}px)`,
        padding: highlight ? "36px 44px" : "32px 40px",
        background: highlight ? `${color}18` : "rgba(255,255,255,0.02)",
        border: highlight ? `2px solid ${color}80` : "2px solid rgba(255,255,255,0.06)",
        borderRadius: 28,
        boxShadow: highlight
          ? `0 0 60px ${color}35, 0 12px 40px rgba(0,0,0,0.4)`
          : "0 8px 24px rgba(0,0,0,0.3)",
      }}
    >
      <div
        style={{
          fontSize: 24,
          color: MUTED,
          letterSpacing: 3,
          textTransform: "uppercase",
          fontWeight: 700,
        }}
      >
        {label}
      </div>
      <div
        style={{
          fontSize: 80,
          fontWeight: 900,
          color,
          letterSpacing: -2,
          lineHeight: 1,
          textShadow: highlight ? `0 0 40px ${color}70` : "none",
          fontVariantNumeric: "tabular-nums",
        }}
      >
        {value}
      </div>
    </div>
  );
};

const UIMockupBeat: React.FC<{
  mockup: UIMockupSpec;
  accent: string;
  durationFrames: number;
}> = ({ mockup, accent, durationFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const modelName = mockup.model_name || "Claude";

  const exitProgress = interpolate(
    frame,
    [durationFrames - BEAT_FADE_FRAMES - FADE_END_BUFFER, durationFrames - FADE_END_BUFFER],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const windowEnter = spring({ frame, fps, config: SOFT_SPRING });
  const windowOpacity = interpolate(windowEnter, [0, 1], [0, 1]);
  const windowScale = interpolate(windowEnter, [0, 1], [0.92, 1]);
  const windowTranslateY = interpolate(windowEnter, [0, 1], [40, 0]);

  const questionStartFrame = 14;
  const questionCharsPerFrame = 0.55;
  const questionVisible = Math.min(
    mockup.question.length,
    Math.max(0, Math.floor((frame - questionStartFrame) * questionCharsPerFrame))
  );
  const visibleQuestion = mockup.question.slice(0, questionVisible);
  const questionDoneFrame =
    questionStartFrame + Math.ceil(mockup.question.length / questionCharsPerFrame);

  const typingStartFrame = questionDoneFrame + 8;
  const typingDuration = 30;
  const answerStartFrame = typingStartFrame + typingDuration;
  const typingActive = frame >= typingStartFrame && frame < answerStartFrame;

  const answerCharsPerFrame = 0.85;
  const answerVisible = Math.min(
    mockup.answer.length,
    Math.max(0, Math.floor((frame - answerStartFrame) * answerCharsPerFrame))
  );
  const visibleAnswer = mockup.answer.slice(0, answerVisible);

  const cursorBlink = (frame % 24) < 12;

  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        padding: "60px 40px",
        opacity: (1 - exitProgress) * windowOpacity,
      }}
    >
      <div
        style={{
          width: 920,
          background: PANEL,
          border: `1px solid ${PANEL_BORDER}`,
          borderRadius: 28,
          overflow: "hidden",
          boxShadow: `0 30px 100px rgba(0,0,0,0.7), 0 0 80px ${accent}18`,
          transform: `scale(${windowScale}) translateY(${windowTranslateY}px)`,
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            padding: "22px 28px",
            borderBottom: `1px solid ${PANEL_BORDER}`,
            background: BG,
          }}
        >
          <div style={{ display: "flex", gap: 9 }}>
            <div style={{ width: 14, height: 14, borderRadius: 7, background: RED }} />
            <div style={{ width: 14, height: 14, borderRadius: 7, background: GOLD }} />
            <div style={{ width: 14, height: 14, borderRadius: 7, background: CYAN }} />
          </div>
          <div
            style={{
              marginLeft: 28,
              fontSize: 22,
              color: MUTED,
              fontWeight: 600,
              letterSpacing: 0.5,
              display: "flex",
              alignItems: "center",
              gap: 10,
            }}
          >
            <div style={{ width: 22, height: 22, borderRadius: 5, background: GOLD, opacity: 0.8 }} />
            {modelName}
          </div>
        </div>

        <div style={{ padding: "36px 36px 24px 36px" }}>
          <div
            style={{
              fontSize: 18,
              color: accent,
              letterSpacing: 4,
              textTransform: "uppercase",
              fontWeight: 700,
              marginBottom: 16,
            }}
          >
            Tú
          </div>
          <div
            style={{
              fontSize: 36,
              color: TEXT,
              fontWeight: 600,
              lineHeight: 1.35,
              letterSpacing: -0.5,
              minHeight: 50,
            }}
          >
            {visibleQuestion}
            {questionVisible < mockup.question.length && cursorBlink && (
              <span style={{ color: accent, marginLeft: 2 }}>▎</span>
            )}
          </div>
        </div>

        {(typingActive || answerVisible > 0) && (
          <div
            style={{
              padding: "16px 36px 36px 36px",
              borderTop: `1px solid ${PANEL_BORDER}`,
              background: `${BG_DEEP}40`,
            }}
          >
            <div
              style={{
                fontSize: 18,
                color: GOLD,
                letterSpacing: 4,
                textTransform: "uppercase",
                fontWeight: 700,
                marginBottom: 16,
                display: "flex",
                alignItems: "center",
                gap: 8,
              }}
            >
              <div style={{ width: 12, height: 12, borderRadius: 3, background: GOLD }} />
              {modelName}
            </div>
            {answerVisible === 0 && typingActive ? (
              <div style={{ display: "flex", gap: 10, paddingTop: 8 }}>
                {[0, 1, 2].map((i) => {
                  const t = (frame - typingStartFrame) / 8 + i * 0.4;
                  const dotOpacity = 0.3 + 0.7 * (Math.sin(t * Math.PI) * 0.5 + 0.5);
                  return (
                    <div
                      key={i}
                      style={{
                        width: 16,
                        height: 16,
                        borderRadius: 8,
                        background: GOLD,
                        opacity: dotOpacity,
                        boxShadow: `0 0 12px ${GOLD}80`,
                      }}
                    />
                  );
                })}
              </div>
            ) : (
              <div
                style={{
                  fontSize: 38,
                  color: TEXT,
                  fontWeight: 600,
                  lineHeight: 1.35,
                  letterSpacing: -0.5,
                  minHeight: 50,
                }}
              >
                {visibleAnswer}
                {answerVisible < mockup.answer.length && cursorBlink && (
                  <span style={{ color: GOLD, marginLeft: 2 }}>▎</span>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </AbsoluteFill>
  );
};

const Outro: React.FC<{ accent: string }> = ({ accent }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = spring({ frame, fps, config: SOFT_SPRING });
  const opacity = interpolate(enter, [0, 1], [0, 1]);
  const translateY = interpolate(enter, [0, 1], [30, 0]);

  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        padding: 100,
        opacity,
        transform: `translateY(${translateY}px)`,
      }}
    >
      <div
        style={{
          fontSize: 24,
          color: MUTED,
          letterSpacing: 4,
          textTransform: "uppercase",
          marginBottom: 28,
          fontWeight: 600,
        }}
      >
        Contenido educativo
      </div>
      <div
        style={{
          fontSize: 52,
          fontWeight: 900,
          color: TEXT,
          letterSpacing: -1.2,
          textAlign: "center",
          maxWidth: 820,
          lineHeight: 1.1,
        }}
      >
        No es asesoría
        <br />
        financiera
      </div>
      <div
        style={{
          marginTop: 48,
          padding: "16px 36px",
          border: `2px solid ${accent}`,
          borderRadius: 100,
          fontSize: 30,
          color: accent,
          fontWeight: 800,
          letterSpacing: 1.5,
          boxShadow: `0 0 40px ${accent}30`,
        }}
      >
        @dinero.ia
      </div>
    </AbsoluteFill>
  );
};

const BrandWatermark: React.FC = () => (
  <div
    style={{
      position: "absolute",
      top: 80,
      right: 80,
      fontSize: 18,
      color: GOLD,
      letterSpacing: 4,
      textTransform: "uppercase",
      fontWeight: 700,
      opacity: 0.5,
      padding: "8px 16px",
      border: `1px solid ${GOLD}40`,
      borderRadius: 6,
    }}
  >
    Dinero · IA
  </div>
);
