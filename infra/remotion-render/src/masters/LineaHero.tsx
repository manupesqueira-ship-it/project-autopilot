import { evolvePath, getLength, getPointAtLength } from "@remotion/paths";
import { curveMonotoneX, line as d3line } from "d3-shape";
import React, { useMemo } from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { inkFlash, lprog, PAL, TOK, tprog } from "../kit2/tokens";
import { Grain, MassCamera, MONO, PageBg, SANS } from "../kit2/world";

// ============================================================================
// MASTER #2 — LÍNEA HÉROE (mundo de la página).
// EL FIX DEL "TRABADO": el path se genera UNA vez completo (d3-shape,
// curveMonotoneX = sin overshoot en datos financieros) y se revela por
// LONGITUD DE TRAZO con evolvePath (stroke-dashoffset) — velocidad uniforme,
// geometría congelada, cero serpenteo. Nunca más revelado por vértices.
// Coreografía (refs aprobadas): build en 2 etapas tipo Apple (ejes/labels
// primero, el dato después) · tracer esmeralda cabalga la cabeza (el acento
// vive en la transición) · endTag aterriza en `land` (la palabra del VO) ·
// cámara con masa · jerarquía por luminancia. Props = SOLO datos.
// ============================================================================

export type LineaHeroProps = {
  kicker?: string;
  points?: number[];        // serie completa (la geometría se congela una vez)
  xLabels?: string[];       // etiquetas de eje x (años/meses)
  endTag?: string;          // valor/cierre que aterriza ("×3.4", "+622%")
  sub?: string;
  foot?: string;
  land?: number;            // frame donde aterriza el endTag (ancla del VO)
  durF?: number;
};

const D = TOK.dur;
const MX = 120;
const CHART_TOP = 820;
const CHART_H = 560;
const BASE_Y = CHART_TOP + CHART_H;

export const LineaHero: React.FC<LineaHeroProps> = ({
  kicker = "INTERÉS COMPUESTO",
  points = [10, 10.8, 11.7, 12.6, 13.6, 14.7, 15.9, 17.2, 18.6, 20.1, 23.4, 27.2, 31.6, 34.0],
  xLabels = [],
  endTag = "×3.4",
  sub = "",
  foot = "",
  land,
  durF,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const total = durF ?? durationInFrames;

  // línea de tiempo (todo derivado de tokens)
  const ruleAt = 4;
  const kickerAt = ruleAt + Math.round(D.ruleDrawF * 0.6);
  const labelsAt = ruleAt + D.ruleDrawF;                    // etapa 1: ejes/labels (Apple)
  const drawAt = labelsAt + D.enterF + 2;                   // etapa 2: el dato
  const drawEnd = drawAt + D.lineDrawF;
  const landAt = land ?? drawEnd + 8;
  const subAt = landAt + 10;
  const exitAt = total - D.exitF - 2;

  // geometría CONGELADA: path completo una sola vez (nunca cambia por frame)
  const { d, len, areaD, xs } = useMemo(() => {
    const w = 1080 - 2 * MX;
    const min = Math.min(...points);
    const max = Math.max(...points);
    const span = Math.max(max - min, 1e-9);
    const px = points.map((_, i) => MX + (i / (points.length - 1)) * w);
    const py = points.map((v) => BASE_Y - ((v - min) / span) * (CHART_H - 60));
    const gen = d3line<number>()
      .x((_, i) => px[i])
      .y((_, i) => py[i])
      .curve(curveMonotoneX);
    const path = gen(points) ?? "";
    return { d: path, len: getLength(path), areaD: `${path} L ${px[px.length - 1]} ${BASE_Y} L ${px[0]} ${BASE_Y} Z`, xs: px };
  }, [points]);

  const rule = tprog(frame, ruleAt, ruleAt + D.ruleDrawF, "standard");
  const kickerT = tprog(frame, kickerAt, kickerAt + D.enterF);
  const draw = tprog(frame, drawAt, drawEnd, "standard");
  const evolved = evolvePath(draw, d);
  const head = getPointAtLength(d, Math.max(0.001, len * draw));
  const subT = tprog(frame, subAt, subAt + D.enterF);
  const flashT = lprog(frame, landAt, landAt + Math.round(D.accentFlashF / TOK.accent.flashWindowPct));
  const tagIn = tprog(frame, landAt, landAt + D.enterF);
  const exitO = 1 - tprog(frame, exitAt, exitAt + D.exitF, "exit");
  // el tracer vive SOLO durante el trazado y se apaga al aterrizar el tag
  const tracerO = draw <= 0.001 ? 0 : draw < 1 ? 1 : 1 - lprog(frame, drawEnd, landAt);

  return (
    <AbsoluteFill style={{ fontFamily: SANS }}>
      <PageBg energy={0.05} />
      <MassCamera durF={total} seed={3}>
        <div style={{ opacity: exitO }}>
          {/* regla del kicker — antes del contenido */}
          <div style={{ position: "absolute", top: 636, left: MX, width: (1080 - 2 * MX) * rule, height: 1, background: PAL.lineSoft }} />
          <div
            style={{
              position: "absolute", top: 668, left: MX, right: MX,
              fontFamily: MONO, fontWeight: 500, fontSize: 30, letterSpacing: "0.32em",
              textTransform: "uppercase", color: inkFlash(kickerT, PAL.dim),
              opacity: Math.min(1, kickerT * 1.4), transform: `translateY(${(1 - kickerT) * 10}px)`,
            }}
          >
            {kicker}
          </div>

          <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
            <defs>
              <linearGradient id="lh-area" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={PAL.ink} stopOpacity="0.10" />
                <stop offset="100%" stopColor={PAL.ink} stopOpacity="0" />
              </linearGradient>
              <clipPath id="lh-clip">
                <rect x={MX} y={CHART_TOP - 80} width={Math.max(0.001, head.x - MX)} height={CHART_H + 160} />
              </clipPath>
            </defs>
            {/* etapa 1: baseline (se dibuja) */}
            <line x1={MX} y1={BASE_Y} x2={MX + (1080 - 2 * MX) * rule} y2={BASE_Y} stroke={PAL.lineSoft} strokeWidth={1} />
            {/* etapa 2: área + trazo revelados por LONGITUD (evolvePath) */}
            <path d={areaD} fill="url(#lh-area)" clipPath="url(#lh-clip)" />
            <path
              d={d}
              fill="none"
              stroke={PAL.ink}
              strokeWidth={4}
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeDasharray={evolved.strokeDasharray}
              strokeDashoffset={evolved.strokeDashoffset}
            />
            {/* tracer esmeralda en la cabeza: el acento vive en la transición */}
            {tracerO > 0.01 ? (
              <circle cx={head.x} cy={head.y} r={9} fill={PAL.accent} opacity={tracerO} />
            ) : null}
          </svg>

          {/* etapa 1: labels de x (mono, tenues, stagger corto) */}
          {xLabels.map((lb, i) => {
            const at = labelsAt + Math.min(i * TOK.stagger.perItemF, TOK.stagger.maxTotalF);
            const t = tprog(frame, at, at + D.enterF);
            const x = xs[Math.round((i / Math.max(xLabels.length - 1, 1)) * (xs.length - 1))];
            return (
              <div
                key={i}
                style={{
                  position: "absolute", top: BASE_Y + 26, left: x - 60, width: 120, textAlign: "center",
                  fontFamily: MONO, fontWeight: 400, fontSize: 24, letterSpacing: "0.08em",
                  color: PAL.faint, opacity: t,
                }}
              >
                {lb}
              </div>
            );
          })}

          {/* endTag — aterriza con la palabra del VO, destello y reposo en hueso */}
          {endTag ? (
            <div
              style={{
                position: "absolute",
                top: Math.max(CHART_TOP - 150, head.y - 170),
                right: MX,
                fontFamily: MONO, fontWeight: 500, fontSize: 96, letterSpacing: "-0.01em",
                fontVariantNumeric: "tabular-nums",
                color: inkFlash(flashT, PAL.ink),
                opacity: tagIn, transform: `translateY(${(1 - tagIn) * 12}px)`,
              }}
            >
              {endTag}
            </div>
          ) : null}

          {sub ? (
            <div
              style={{
                position: "absolute", top: BASE_Y + 96, left: MX, right: MX,
                fontFamily: SANS, fontWeight: 350, fontSize: 44, lineHeight: 1.4,
                color: inkFlash(subT, PAL.dim), opacity: Math.min(1, subT * 1.4),
                transform: `translateY(${(1 - subT) * 10}px)`, maxWidth: 760,
              }}
            >
              {sub}
            </div>
          ) : null}

          {foot ? (
            <div
              style={{
                position: "absolute", top: 1720, left: MX, right: MX,
                fontFamily: MONO, fontWeight: 400, fontSize: 21, letterSpacing: "0.22em",
                textTransform: "uppercase", color: PAL.faint, opacity: Math.min(1, kickerT),
              }}
            >
              {foot}
            </div>
          ) : null}
        </div>
      </MassCamera>
      <Grain />
    </AbsoluteFill>
  );
};
