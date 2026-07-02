import React from "react";
import {
  AbsoluteFill,
  Sequence,
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
  interpolateColors,
  Easing,
} from "remotion";
import { theme } from "../theme";
import {
  Stage,
  Bar,
  GhostShell,
  ErosionDust,
  Counter,
  RollingNumber,
  settle,
  W,
  H,
  FLOOR,
  COL_CASH_X,
  COL_INV_X,
  vToH,
  LOSS_RED,
} from "./reelKit";

// ── REEL C COMPLETO — "$100,000 en 12 meses: efectivo vs. invertir" ─────────────
// 6 escenas en UN solo <Stage> persistente (el fondo no parpadea entre cortes).
// Sincronizado a la VO Asgard (reelc_full_vo, 56.88s). Datos REALES lockeados por
// Manuel 2026-06-28: tasa 7.17% · inflación 3.94% · ISR 0.90% ($900).
//   efectivo real $96,209 · invertido nominal $107,170 · invertido real $102,242
//   diferencia real ≈ $6,033  (la lección honesta: ~6%, no un número gigante).
// Animatic de DIRECCIÓN ($0). Juzgar en VIDEO con audio, no en still.
//
//   npx remotion render src/index.ts Lab-ReelC-Full out/lab_reelc_full.mp4 --crf=18 --timeout=600000

const clampOpts = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const EASE = Easing.inOut(Easing.cubic);
const eOpts = { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE } as const;

// Transición de escena: el Stage persiste detrás. La escena ENTRA con un leve push
// (escala 1.045→1.0 + deriva hacia arriba) y SALE recediendo (escala→0.97, sube y
// se desvanece) → se siente como movimiento de cámara, no un dissolve plano.
const sceneStyle = (local: number, dur: number): React.CSSProperties => {
  const opacity = interpolate(local, [0, 9, dur - 9, dur], [0, 1, 1, 0], clampOpts);
  const enter = interpolate(local, [0, 16], [1, 0], eOpts); // 1→0 en la entrada
  const exit = interpolate(local, [dur - 13, dur], [0, 1], eOpts); // 0→1 en la salida
  const scale = 1 + enter * 0.045 - exit * 0.03;
  const ty = enter * 20 - exit * 14;
  return { opacity, transform: `translateY(${ty}px) scale(${scale})`, transformOrigin: "50% 50%" };
};

const EFECTIVO_LABEL = "Efectivo";
const INVERTIR_LABEL = "Invertir";

// Etiqueta de columna bajo el piso.
const FloorLabel: React.FC<{ cx: number; text: string; opacity: number }> = ({ cx, text, opacity }) => (
  <div
    style={{
      position: "absolute",
      left: cx - 160,
      top: FLOOR + 18,
      width: 320,
      textAlign: "center",
      fontFamily: theme.font,
      fontSize: 36,
      fontWeight: 600,
      letterSpacing: 2,
      textTransform: "uppercase",
      color: theme.textDim,
      opacity,
    }}
  >
    {text}
  </div>
);

const FloorLine: React.FC<{ opacity: number }> = ({ opacity }) => (
  <div
    style={{
      position: "absolute",
      left: 120,
      top: FLOOR + 2,
      width: W - 240,
      height: 2,
      background: "rgba(255,255,255,0.12)",
      opacity,
    }}
  />
);

// ════════════════════════════ ESCENA 0 — HOOK ══════════════════════════════════
// "Tienes cien mil pesos. En doce meses, uno de dos caminos te deja con menos…"
const SceneHook: React.FC<{ dur: number }> = ({ dur }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const rise = spring({ frame, fps, config: { damping: 200 }, durationInFrames: 30 });
  const val = rise * 100000;
  const tick = 1 + settle(frame, 30) * 0.06;

  const eyebrowIn = interpolate(frame, [0, 16], [0, 1], eOpts);
  const subIn = interpolate(frame, [22, 42], [0, 1], eOpts);
  const forkIn = interpolate(frame, [88, 116], [0, 1], eOpts);
  const breatheY = interpolate(frame, [30, dur], [0, -10], clampOpts);

  return (
    <AbsoluteFill style={sceneStyle(frame, dur)}>
      <div style={{ transform: `translateY(${breatheY}px)` }}>
        {/* eyebrow */}
        <div
          style={{
            position: "absolute",
            top: 600,
            width: W,
            textAlign: "center",
            fontFamily: theme.font,
            fontSize: 38,
            fontWeight: 700,
            letterSpacing: 8,
            textTransform: "uppercase",
            color: theme.textDim,
            opacity: eyebrowIn,
            transform: `translateY(${(1 - eyebrowIn) * 16}px)`,
          }}
        >
          Tienes
        </div>
        {/* número ancla */}
        <Counter cx={540} value={val} color={theme.gold} tick={tick} top={720} size={132} width={820} />
        {/* sublabel */}
        <div
          style={{
            position: "absolute",
            top: 905,
            width: W,
            textAlign: "center",
            fontFamily: theme.font,
            fontSize: 34,
            fontWeight: 600,
            letterSpacing: 6,
            textTransform: "uppercase",
            color: theme.textDim,
            opacity: subIn,
            transform: `translateY(${(1 - subIn) * 12}px)`,
          }}
        >
          MXN · en 12 meses
        </div>
      </div>
      {/* fork: dos caminos */}
      <svg width={W} height={H} style={{ position: "absolute", left: 0, top: 0, opacity: forkIn }}>
        <line x1={540} y1={1060} x2={320} y2={1260} stroke={theme.teal} strokeWidth={4} strokeLinecap="round" />
        <line x1={540} y1={1060} x2={760} y2={1260} stroke={theme.green} strokeWidth={4} strokeLinecap="round" />
        <circle cx={320} cy={1260} r={10} fill={theme.teal} />
        <circle cx={760} cy={1260} r={10} fill={theme.green} />
        <circle cx={540} cy={1060} r={7} fill={theme.gold} />
      </svg>
    </AbsoluteFill>
  );
};

// ════════════════════════════ ESCENA 1 — SETUP ═════════════════════════════════
// "El primero: dejarlo quieto. El segundo: invertirlo a 7.17%. Mismo punto de partida."
const SceneSetup: React.FC<{ dur: number }> = ({ dur }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const leftRise = spring({ frame, fps, config: { damping: 16 }, durationInFrames: 30 });
  const rightRise = spring({ frame: Math.max(0, frame - 103), fps, config: { damping: 16 }, durationInFrames: 30 });
  const cashVal = leftRise * 100000;
  const invVal = rightRise * 100000;
  const cashH = vToH(cashVal);
  const invH = vToH(invVal);

  const tasaIn = interpolate(frame, [146, 170], [0, 1], eOpts);
  const tasaPulse = 1 + Math.sin(frame / 7) * 0.04;
  const mismoIn = interpolate(frame, [230, 252], [0, 1], eOpts);
  const cashTick = 1 + settle(frame, 30) * 0.05;
  const invTick = 1 + settle(frame, 133) * 0.05;

  return (
    <AbsoluteFill style={sceneStyle(frame, dur)}>
      {/* columnas */}
      <Bar cx={COL_CASH_X} h={cashH} color={theme.teal} frame={frame} phase={0} />
      <Bar cx={COL_INV_X} h={invH} color={theme.teal} frame={frame} phase={2.1} />

      {/* contadores */}
      <Counter cx={COL_CASH_X} value={cashVal} color={theme.teal} tick={cashTick} top={700} size={60} />
      <Counter cx={COL_INV_X} value={invVal} color={theme.teal} tick={invTick} top={700} size={60} />

      {/* badge tasa 7.17% sobre invertir */}
      <div
        style={{
          position: "absolute",
          left: COL_INV_X - 150,
          top: 612,
          width: 300,
          textAlign: "center",
          opacity: tasaIn,
          transform: `translateY(${(1 - tasaIn) * 14}px) scale(${tasaPulse})`,
        }}
      >
        <span
          style={{
            fontFamily: theme.font,
            fontSize: 32,
            fontWeight: 800,
            color: theme.green,
            padding: "8px 22px",
            borderRadius: 999,
            border: `2px solid ${theme.green}66`,
            background: "rgba(0,217,165,0.10)",
          }}
        >
          tasa 7.17%
        </span>
      </div>

      {/* conector "mismo inicio" */}
      <svg width={W} height={H} style={{ position: "absolute", left: 0, top: 0, opacity: mismoIn }}>
        <line
          x1={COL_CASH_X}
          y1={905}
          x2={COL_INV_X}
          y2={905}
          stroke="rgba(255,255,255,0.35)"
          strokeWidth={2}
          strokeDasharray="8 10"
        />
      </svg>
      <div
        style={{
          position: "absolute",
          left: 0,
          top: 880,
          width: W,
          textAlign: "center",
          opacity: mismoIn,
          transform: `translateY(${(1 - mismoIn) * 12}px)`,
        }}
      >
        <span
          style={{
            fontFamily: theme.font,
            fontSize: 28,
            fontWeight: 700,
            letterSpacing: 4,
            textTransform: "uppercase",
            color: theme.text,
            padding: "6px 20px",
            borderRadius: 999,
            background: "rgba(13,17,23,0.85)",
            border: "1px solid rgba(255,255,255,0.18)",
          }}
        >
          Mismo inicio
        </span>
      </div>

      <FloorLine opacity={1} />
      <FloorLabel cx={COL_CASH_X} text={EFECTIVO_LABEL} opacity={leftRise} />
      <FloorLabel cx={COL_INV_X} text={INVERTIR_LABEL} opacity={rightRise} />
    </AbsoluteFill>
  );
};

// ═══════════════════ ESCENA 2-3-4 — CARRERA (erosión → nominal/real → payoff) ════
// La mecánica memorable: cada columna es un VASO (nominal) con LÍQUIDO (real). La
// inflación/impuestos hacen que el líquido NO llegue al borde = poder de compra perdido.
const SceneRace: React.FC<{ dur: number }> = ({ dur }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // ── valores (frames locales; ver mapa de palabras VO) ──
  const cashReal = interpolate(frame, [95, 317], [100000, 96209], { ...clampOpts, easing: EASE });
  const invGrow = spring({
    frame: Math.max(0, frame - 360),
    fps,
    config: { damping: 12, stiffness: 80, mass: 1.1 },
    durationInFrames: 76,
  });
  const investNominal = 100000 + invGrow * (107170 - 100000);
  const realDrain = interpolate(frame, [500, 575], [0, 1], { ...clampOpts, easing: EASE });
  const investReal = investNominal - realDrain * (107170 - 102242);

  const cashShellH = vToH(100000);
  const cashFillH = vToH(cashReal);
  const invShellH = vToH(investNominal);
  const invFillH = vToH(investReal);

  const cashColorProg = interpolate(frame, [95, 260], [0, 1], clampOpts);
  const cashFillColor = interpolateColors(cashColorProg, [0, 1], [theme.teal, LOSS_RED]);
  const invColorProg = interpolate(frame, [360, 420], [0, 1], clampOpts);
  const invColor = interpolateColors(invColorProg, [0, 1], [theme.teal, theme.green]);

  // ── pills / deltas ──
  const inflOp = interpolate(frame, [75, 95, 300, 330], [0, 1, 1, 0], clampOpts);
  const inflPulse = 1 + Math.sin(frame / 6) * 0.05;
  const cashDeltaOp = interpolate(frame, [205, 235], [0, 1], eOpts);
  const invDeltaOp = interpolate(frame, [388, 412], [0, 1], eOpts);
  const invReal = frame >= 500;

  // ── payoff (focus-pull) ──
  const pay = spring({ frame: Math.max(0, frame - 575), fps, config: { damping: 200 }, durationInFrames: 30 });
  // entrada con leve overshoot (la tarjeta "aterriza", no sólo aparece)
  const payIn = spring({ frame: Math.max(0, frame - 575), fps, config: { damping: 15, stiffness: 110, mass: 0.9 }, durationInFrames: 36 });
  // bloom del número en el golpe (sincronizado con el impact SFX ~frame 1031 global)
  const payFlash = interpolate(frame, [575, 585, 655], [0, 1, 0], { ...clampOpts, easing: EASE });
  const colsDim = interpolate(pay, [0, 1], [1, 0.5]);
  const colsScale = interpolate(pay, [0, 1], [1, 0.94]);
  const colsBlur = pay * 3.5;
  const payPulse = 1 + Math.sin(Math.max(0, frame - 620) / 9) * 0.02;
  const cardScale = (0.92 + payIn * 0.08) * payPulse;

  const cashTick = 1 + settle(frame, 317) * 0.05;
  const invTickUp = settle(frame, 408) * 0.05;
  const invTickDn = settle(frame, 560) * 0.05;
  const invTick = 1 + invTickUp + invTickDn;

  return (
    <AbsoluteFill style={sceneStyle(frame, dur)}>
      {/* ── capa columnas (se atenúa/desenfoca en el payoff) ── */}
      <AbsoluteFill
        style={{
          opacity: colsDim,
          transform: `scale(${colsScale})`,
          transformOrigin: "50% 56%",
          filter: colsBlur > 0.1 ? `blur(${colsBlur}px)` : undefined,
        }}
      >
        {/* EFECTIVO: vaso nominal 100k + líquido real */}
        <GhostShell cx={COL_CASH_X} hNominal={cashShellH} color={theme.teal} frame={frame} phase={0} />
        <Bar cx={COL_CASH_X} h={cashFillH} color={cashFillColor} frame={frame} phase={0} eroding={frame >= 95} />
        <ErosionDust frame={frame} topY={FLOOR - cashFillH} cx={COL_CASH_X} t0={100} />

        {/* INVERTIR: vaso nominal (crece) + líquido real (se corrige) */}
        <GhostShell cx={COL_INV_X} hNominal={invShellH} color={invColor} frame={frame} phase={2.1} />
        <Bar cx={COL_INV_X} h={invFillH} color={invColor} frame={frame} phase={2.1} />

        {/* contadores */}
        <Counter cx={COL_CASH_X} value={cashReal} color={cashFillColor} tick={cashTick} top={690} size={60} />
        <Counter cx={COL_INV_X} value={investReal} color={invColor} tick={invTick} top={690} size={60} />

        {/* delta efectivo */}
        <div
          style={{
            position: "absolute",
            left: COL_CASH_X - 200,
            top: 840,
            width: 400,
            textAlign: "center",
            fontFamily: theme.font,
            fontSize: 27,
            fontWeight: 700,
            color: theme.red,
            opacity: cashDeltaOp,
          }}
        >
          −3.94% poder de compra
        </div>

        {/* delta invertir (nominal → real) */}
        <div
          style={{
            position: "absolute",
            left: COL_INV_X - 200,
            top: 840,
            width: 400,
            textAlign: "center",
            fontFamily: theme.font,
            fontSize: 27,
            fontWeight: 700,
            color: invReal ? theme.gold : theme.green,
            opacity: invDeltaOp,
          }}
        >
          {invReal ? "− ISR − inflación = real" : "+7.17% nominal"}
        </div>

        {/* pill inflación */}
        <div
          style={{
            position: "absolute",
            left: COL_CASH_X - 160,
            top: 576,
            width: 320,
            textAlign: "center",
            opacity: inflOp,
            transform: `scale(${inflPulse})`,
          }}
        >
          <span
            style={{
              fontFamily: theme.font,
              fontSize: 32,
              fontWeight: 700,
              color: theme.red,
              padding: "8px 22px",
              borderRadius: 999,
              border: `2px solid ${theme.red}66`,
              background: "rgba(255,107,107,0.10)",
            }}
          >
            ↓ inflación
          </span>
        </div>

        <FloorLine opacity={1} />
        <FloorLabel cx={COL_CASH_X} text={EFECTIVO_LABEL} opacity={1} />
        <FloorLabel cx={COL_INV_X} text={INVERTIR_LABEL} opacity={1} />
      </AbsoluteFill>

      {/* ── payoff: la diferencia real (nítido sobre las columnas atenuadas) ── */}
      <AbsoluteFill style={{ background: "rgba(13,17,23,0.40)", opacity: pay * 0.5 }} />
      <div
        style={{
          position: "absolute",
          left: 165,
          top: 980,
          width: 750,
          opacity: pay,
          transform: `translateY(${(1 - pay) * 26}px) scale(${cardScale})`,
          transformOrigin: "50% 50%",
          background: "rgba(13,17,23,0.92)",
          border: `1px solid ${theme.gold}55`,
          borderRadius: 22,
          padding: "30px 28px 36px",
          textAlign: "center",
          boxShadow: "0 24px 60px rgba(0,0,0,0.45)",
        }}
      >
        <div
          style={{
            fontFamily: theme.font,
            fontSize: 34,
            fontWeight: 700,
            letterSpacing: 3,
            textTransform: "uppercase",
            color: theme.gold,
          }}
        >
          La diferencia real
        </div>
        <div
          style={{
            fontFamily: theme.font,
            fontSize: 120,
            fontWeight: 800,
            color: theme.green,
            margin: "6px 0 2px",
            textShadow: `0 0 ${22 + payFlash * 80}px rgba(0,217,165,${0.30 + payFlash * 0.55})`,
            transform: `scale(${1 + payFlash * 0.05})`,
          }}
        >
          $6,033
        </div>
        <div style={{ fontFamily: theme.font, fontSize: 31, color: theme.textDim }}>
          lo que la inflación cobra por no decidir
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ════════════════════════════ ESCENA 5 — CIERRE / CTA ══════════════════════════
// "No es invierte siempre. Es la tasa real. Guarda esto. Mañana: una tasa que le gane."
const SceneCTA: React.FC<{ dur: number }> = ({ dur }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const eyebrowIn = interpolate(frame, [0, 18], [0, 1], eOpts);
  const line1In = interpolate(frame, [10, 34], [0, 1], eOpts);
  const line2In = interpolate(frame, [40, 66], [0, 1], eOpts);
  const chip = spring({ frame: Math.max(0, frame - 80), fps, config: { damping: 16 }, durationInFrames: 30 });
  const saveIn = interpolate(frame, [261, 285], [0, 1], eOpts);
  const savePulse = 1 + Math.sin(frame / 7) * 0.05;
  const tomorrow = spring({ frame: Math.max(0, frame - 311), fps, config: { damping: 16 }, durationInFrames: 30 });
  const discIn = interpolate(frame, [120, 150], [0, 1], eOpts);

  return (
    <AbsoluteFill style={sceneStyle(frame, dur)}>
      {/* eyebrow */}
      <div
        style={{
          position: "absolute",
          top: 360,
          width: W,
          textAlign: "center",
          fontFamily: theme.font,
          fontSize: 32,
          fontWeight: 800,
          letterSpacing: 8,
          textTransform: "uppercase",
          color: theme.gold,
          opacity: eyebrowIn,
        }}
      >
        La regla
      </div>
      {/* headline 2 líneas */}
      <div
        style={{
          position: "absolute",
          top: 432,
          width: W,
          textAlign: "center",
          fontFamily: theme.font,
          fontSize: 56,
          fontWeight: 800,
          color: theme.text,
          opacity: line1In,
          transform: `translateY(${(1 - line1In) * 18}px)`,
        }}
      >
        No es invertir por invertir.
      </div>
      <div
        style={{
          position: "absolute",
          top: 512,
          width: W,
          textAlign: "center",
          fontFamily: theme.font,
          fontSize: 56,
          fontWeight: 800,
          color: theme.text,
          opacity: line2In,
          transform: `translateY(${(1 - line2In) * 18}px)`,
        }}
      >
        Es la <span style={{ color: theme.green }}>tasa real</span>.
      </div>

      {/* chip comparación tasa vs inflación */}
      <div
        style={{
          position: "absolute",
          left: 90,
          top: 760,
          width: W - 180,
          opacity: chip,
          transform: `translateY(${(1 - chip) * 24}px)`,
          background: "rgba(13,17,23,0.9)",
          border: "1px solid rgba(255,255,255,0.14)",
          borderRadius: 24,
          padding: "34px 24px 30px",
          textAlign: "center",
          boxShadow: "0 24px 60px rgba(0,0,0,0.45)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 22 }}>
          <span style={{ fontFamily: theme.font, fontSize: 52, fontWeight: 800, color: theme.green }}>7.17%</span>
          <span style={{ fontFamily: theme.font, fontSize: 46, fontWeight: 800, color: theme.text }}>&gt;</span>
          <span style={{ fontFamily: theme.font, fontSize: 52, fontWeight: 800, color: theme.red }}>3.94%</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 60, marginTop: 8 }}>
          <span style={{ fontFamily: theme.font, fontSize: 24, fontWeight: 600, letterSpacing: 2, textTransform: "uppercase", color: theme.textDim }}>
            tu tasa
          </span>
          <span style={{ fontFamily: theme.font, fontSize: 24, fontWeight: 600, letterSpacing: 2, textTransform: "uppercase", color: theme.textDim }}>
            inflación
          </span>
        </div>
        <div style={{ fontFamily: theme.font, fontSize: 30, fontWeight: 700, color: theme.green, marginTop: 18 }}>
          ✓ ganas en términos reales
        </div>
      </div>

      {/* guarda esto */}
      <div
        style={{
          position: "absolute",
          top: 1110,
          width: W,
          textAlign: "center",
          fontFamily: theme.font,
          fontSize: 30,
          fontWeight: 700,
          color: theme.textDim,
          opacity: saveIn,
          transform: `scale(${savePulse})`,
        }}
      >
        ⤓ Guarda esto
      </div>

      {/* mañana (loop) */}
      <div
        style={{
          position: "absolute",
          left: 120,
          top: 1210,
          width: W - 240,
          opacity: tomorrow,
          transform: `translateY(${(1 - tomorrow) * 22}px)`,
          textAlign: "center",
        }}
      >
        <span
          style={{
            display: "inline-block",
            fontFamily: theme.font,
            fontSize: 26,
            fontWeight: 800,
            letterSpacing: 4,
            textTransform: "uppercase",
            color: theme.bg.base,
            background: theme.gold,
            padding: "8px 22px",
            borderRadius: 999,
            marginBottom: 18,
          }}
        >
          Mañana
        </span>
        <div style={{ fontFamily: theme.font, fontSize: 40, fontWeight: 700, color: theme.text, lineHeight: 1.25 }}>
          Cómo encontrar una tasa que <span style={{ color: theme.green }}>sí</span> le gane a la inflación
        </div>
      </div>

      {/* disclaimer real */}
      <div
        style={{
          position: "absolute",
          top: 1720,
          width: W,
          textAlign: "center",
          fontFamily: theme.font,
          fontSize: 21,
          lineHeight: 1.4,
          color: "rgba(160,160,176,0.72)",
          opacity: discIn,
          padding: "0 80px",
          boxSizing: "border-box",
        }}
      >
        Contenido educativo, no recomendación. Cifras ilustrativas, corte may 2026.
        <br />
        Fuentes: Banxico · INEGI · LIF 2026.
      </div>
    </AbsoluteFill>
  );
};

// ════════════════════════════ MASTER ═══════════════════════════════════════════
const S0 = 170; // hook
const S1 = 286; // setup   (ends 456)
const S2 = 850; // carrera (ends 1306)
const S3 = 444; // cierre  (ends 1750)
export const FULL_REEL_C_DURATION = S0 + S1 + S2 + S3;

export const FullReelC: React.FC = () => (
  <Stage>
    <Sequence from={0} durationInFrames={S0}>
      <SceneHook dur={S0} />
    </Sequence>
    <Sequence from={S0} durationInFrames={S1}>
      <SceneSetup dur={S1} />
    </Sequence>
    <Sequence from={S0 + S1} durationInFrames={S2}>
      <SceneRace dur={S2} />
    </Sequence>
    <Sequence from={S0 + S1 + S2} durationInFrames={S3}>
      <SceneCTA dur={S3} />
    </Sequence>
  </Stage>
);
