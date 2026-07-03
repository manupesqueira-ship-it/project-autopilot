import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { holdF, inkFlash, lprog, PAL, TOK, tprog } from "../kit2/tokens";
import { Grain, MassCamera, MONO, PageBg, SANS } from "../kit2/world";

// ============================================================================
// MASTER #1 — CIFRA HÉROE / ODÓMETRO (mundo de la página).
// Coreografía congelada; las props son SOLO datos. Referencias aprobadas
// (tablero 2026-07-03): Apple M3 (una cosa a la vez, número aterriza con la
// voz) · Territory (jerarquía por LUMINANCIA, mono legible) · DIA (el texto
// entra siempre con la misma regla) · Tendril (cámara con masa) · Terminal
// (la línea se dibuja ANTES del contenido; el esmeralda vive en la transición).
// Cero glow, cero springs de caricatura: la jerarquía es luz, no tamaño.
// ============================================================================

export type CifraHeroProps = {
  kicker?: string;        // mono MAYÚS tracking ancho ("INFLACIÓN ANUAL")
  value?: string;         // cifra YA formateada ("$96,209")
  unit?: string;          // unidad chica junto a la cifra ("MXN")
  sub?: string;           // frase de contexto (grotesca fina)
  foot?: string;          // pie mono chiquito (fuente/fecha o marca demo)
  land?: number;          // frame donde ATERRIZA la cifra (el assembler lo ancla a la palabra del VO)
  durF?: number;
};

const D = TOK.dur;

export const CifraHero: React.FC<CifraHeroProps> = ({
  kicker = "INFLACIÓN ANUAL",
  value = "$96,209",
  unit = "",
  sub = "",
  foot = "",
  land,
  durF,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const total = durF ?? durationInFrames;

  // línea de tiempo del master (derivada de tokens, no números sueltos)
  const ruleAt = 4;
  const kickerAt = ruleAt + Math.round(D.ruleDrawF * 0.6);
  const rollStart = kickerAt + D.enterF + 4;
  const landAt = land ?? rollStart + D.countupF;
  const subAt = landAt + 10;
  const exitAt = total - D.exitF - 2;

  // etapa 1: la regla se dibuja ANTES del contenido (Terminal)
  const rule = tprog(frame, ruleAt, ruleAt + D.ruleDrawF, "standard");
  // kicker: entra con LA regla de entrada (DIA: siempre la misma) + destello
  const kickerT = tprog(frame, kickerAt, kickerAt + D.enterF);
  // sub: misma regla de entrada
  const subT = tprog(frame, subAt, subAt + D.enterF);
  // destello del aterrizaje: la tinta corre en tiempo LINEAL (esmeralda visible
  // ~accentFlashF frames, patrón Terminal 200-400ms); la curva es del movimiento
  const flashT = lprog(frame, landAt, landAt + Math.round(D.accentFlashF / TOK.accent.flashWindowPct));
  // salida: más corta que la entrada, acelerada
  const exitO = 1 - tprog(frame, exitAt, exitAt + D.exitF, "exit");

  const MX = 120; // margen del mundo (aire)

  // ── odómetro: cada dígito rueda en su columna; el DE LA DERECHA asienta al final
  const digits = value.split("");
  const rights: number[] = [];
  {
    let r = 0;
    for (let i = digits.length - 1; i >= 0; i--) {
      rights[i] = /\d/.test(digits[i]) ? r++ : -1;
    }
  }
  const numColor = frame < landAt ? PAL.faint : inkFlash(flashT, PAL.ink);
  const numSize = Math.min(210, Math.floor((1080 - 2 * MX) / (value.length * 0.62)));
  const H = Math.round(numSize * 1.08);

  return (
    <AbsoluteFill style={{ fontFamily: SANS }}>
      <PageBg energy={0.05} />
      <MassCamera durF={total} seed={2}>
        <div style={{ opacity: exitO }}>
          {/* regla fina — se dibuja antes que todo */}
          <div style={{ position: "absolute", top: 636, left: MX, width: (1080 - 2 * MX) * rule, height: 1, background: PAL.lineSoft }} />

          {/* kicker mono MAYÚS */}
          <div
            style={{
              position: "absolute",
              top: 668,
              left: MX,
              right: MX,
              fontFamily: MONO,
              fontWeight: 500,
              fontSize: 30,
              letterSpacing: "0.32em",
              textTransform: "uppercase",
              color: inkFlash(kickerT, PAL.dim),
              opacity: Math.min(1, kickerT * 1.4),
              transform: `translateY(${(1 - kickerT) * 10}px)`,
            }}
          >
            {kicker}
          </div>

          {/* cifra héroe — odómetro mono, jerarquía por LUMINANCIA */}
          <div style={{ position: "absolute", top: 790, left: MX, right: MX, display: "flex", alignItems: "flex-end", gap: 18 }}>
            <div style={{ display: "flex", fontVariantNumeric: "tabular-nums" }}>
              {digits.map((ch, i) => {
                if (!/\d/.test(ch)) {
                  return (
                    <span key={i} style={{ fontFamily: MONO, fontWeight: 500, fontSize: numSize, lineHeight: `${H}px`, color: numColor }}>
                      {ch}
                    </span>
                  );
                }
                const d = parseInt(ch, 10);
                // el dígito de la derecha (r=0) asienta AL FINAL (CountUp/Odometer)
                const end = landAt - 3 * rights[i];
                const t = tprog(frame, rollStart, end, "countLand");
                // UNA sola pasada por la rueda (Territory: legible, nunca slot-machine)
                const pos = t * (10 + d);
                const off = (pos % 10) * H;
                return (
                  <span key={i} style={{ display: "inline-block", height: H, overflow: "hidden", verticalAlign: "top" }}>
                    <span style={{ display: "block", transform: `translateY(${-off}px)` }}>
                      {Array.from({ length: 11 }).map((_, k) => (
                        <span
                          key={k}
                          style={{ display: "block", fontFamily: MONO, fontWeight: 500, fontSize: numSize, lineHeight: `${H}px`, textAlign: "center", color: numColor }}
                        >
                          {k % 10}
                        </span>
                      ))}
                    </span>
                  </span>
                );
              })}
            </div>
            {unit ? (
              <div style={{ fontFamily: MONO, fontWeight: 400, fontSize: 34, letterSpacing: "0.14em", color: PAL.faint, paddingBottom: Math.round(H * 0.16) }}>
                {unit}
              </div>
            ) : null}
          </div>

          {/* contexto — grotesca fina, misma regla de entrada */}
          {sub ? (
            <div
              style={{
                position: "absolute",
                top: 790 + H + 46,
                left: MX,
                right: MX,
                fontFamily: SANS,
                fontWeight: 350,
                fontSize: 44,
                lineHeight: 1.4,
                color: inkFlash(subT, PAL.dim),
                opacity: Math.min(1, subT * 1.4),
                transform: `translateY(${(1 - subT) * 10}px)`,
                maxWidth: 720,
              }}
            >
              {sub}
            </div>
          ) : null}

          {/* pie mono (fuente / marca demo) */}
          {foot ? (
            <div
              style={{
                position: "absolute",
                top: 1720,
                left: MX,
                right: MX,
                fontFamily: MONO,
                fontWeight: 400,
                fontSize: 21,
                letterSpacing: "0.22em",
                textTransform: "uppercase",
                color: PAL.faint,
                opacity: Math.min(1, kickerT),
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

// duración natural del motion test: entrada + aterrizaje + hold de lectura + salida
export const cifraHeroTestDur = (sub: string) =>
  4 + 10 + 14 + 4 + TOK.dur.countupF + 10 + TOK.dur.enterF + Math.max(holdF(sub.length), TOK.hold.chartPostMotionF) + TOK.dur.exitF + 4;
