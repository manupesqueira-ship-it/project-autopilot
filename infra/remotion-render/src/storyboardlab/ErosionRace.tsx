import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
  interpolateColors,
} from "remotion";
import { theme } from "../theme";

// ── Prototipo #1: 2D cinemático coreografiado (animatic de DIRECCIÓN, $0). ──────
// Mecánica memorable del Reel C: dos pilas de $100,000 MXN parten iguales; la de
// EFECTIVO se erosiona con la inflación (teal→rojo, se desmorona en partículas) y
// la de INVERTIR trepa con overshoot físico (verde). El dato no "aparece": se revela.
//
// ⚠ Cifras de fin = ILUSTRATIVAS (la tasa/inflación reales son <<verify>>). Esto es
// una prueba de MOVIMIENTO, no contenido publicable. Disclaimer horneado en pantalla.
//
// Render (juzgar en VIDEO, no en still):
//   npx remotion render src/index.ts Lab-ReelC-ErosionRace out/lab_reelc_erosion.mp4 --crf=18

const W = 1080;
const H = 1920;
const FLOOR = 1320; // baseline de las pilas
const BAR_W = 250;
const COL_CASH_X = 290; // centro columna izquierda (efectivo)
const COL_INV_X = 790; // centro columna derecha (invertir)
const VMAX = 120000;
const MAXH = 470;
const vToH = (v: number) => (v / VMAX) * MAXH;

// Cifras ILUSTRATIVAS (reales = <<verify>>): solo para mover la pieza.
const START = 100000;
const CASH_END = 94000; // efectivo pierde poder de compra
const INV_END = 110000; // invertir gana (nominal ilustrativo)

// rand determinista (sin estado, mismo resultado cada render)
const rnd = (i: number) => {
  const x = Math.sin(i * 127.1 + 11.7) * 43758.5453;
  return x - Math.floor(x);
};

// Columna "vidrio/líquido" 2.5D: color sólido + sheen (luz) + sombra de contacto
// + reflejo bajo el piso. Da MATERIAL y PROFUNDIDAD sin 3D (premium, no neón).
const Bar: React.FC<{
  cx: number;
  h: number;
  color: string;
  frame: number;
  phase: number;
  eroding?: boolean;
}> = ({ cx, h, color, frame, phase, eroding }) => {
  const float = Math.sin(frame / 14 + phase) * 3; // micro-float constante
  const hh = Math.max(0, h);
  const left = cx - BAR_W / 2;
  const top = FLOOR - h + float;

  const topWhite = eroding ? 0.18 : 0.34; // menos lavado en el efectivo → el rojo lee profundo
  const fill = `linear-gradient(180deg, rgba(255,255,255,${topWhite}) 0%, rgba(255,255,255,0.05) 20%, rgba(0,0,0,0) 52%, rgba(0,0,0,0.42) 100%), ${color}`;

  const inner = (
    <>
      {/* sheen vertical (reflejo de softbox) */}
      <div
        style={{
          position: "absolute",
          left: "11%",
          top: 0,
          width: "20%",
          height: "100%",
          background:
            "linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.42) 50%, rgba(255,255,255,0) 100%)",
          filter: "blur(4px)",
          borderRadius: 40,
        }}
      />
      {/* canto superior brillante */}
      <div
        style={{
          position: "absolute",
          top: -1,
          left: 7,
          width: BAR_W - 14,
          height: 8,
          borderRadius: 8,
          background: "#fff",
          opacity: eroding ? 0.5 : 0.85,
          filter: "blur(1.4px)",
        }}
      />
    </>
  );

  const boxBase: React.CSSProperties = {
    position: "absolute",
    left,
    width: BAR_W,
    height: hh,
    borderRadius: "16px 16px 5px 5px",
    background: fill,
    overflow: "hidden",
  };

  return (
    <>
      {/* sombra de contacto (asienta la columna en el piso) */}
      <div
        style={{
          position: "absolute",
          left: left - 20,
          top: FLOOR - 16 + float,
          width: BAR_W + 40,
          height: 36,
          borderRadius: "50%",
          background: "rgba(0,0,0,0.55)",
          filter: "blur(17px)",
        }}
      />
      {/* reflejo bajo el piso */}
      <div
        style={{
          ...boxBase,
          top: FLOOR + float,
          transform: "scaleY(-1)",
          transformOrigin: "50% 0%",
          opacity: 0.17,
          WebkitMaskImage:
            "linear-gradient(180deg, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0) 68%)",
          maskImage:
            "linear-gradient(180deg, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0) 68%)",
        }}
      >
        {inner}
      </div>
      {/* columna principal */}
      <div
        style={{
          ...boxBase,
          top,
          boxShadow: `0 0 24px ${color}33, 0 26px 50px rgba(0,0,0,0.45), inset 0 2px 0 rgba(255,255,255,0.32), inset 0 -18px 32px rgba(0,0,0,0.26)`,
        }}
      >
        {inner}
      </div>
    </>
  );
};

const ErosionDust: React.FC<{ frame: number; topY: number; cx: number }> = ({
  frame,
  topY,
  cx,
}) => {
  const N = 26;
  const out: React.ReactNode[] = [];
  for (let i = 0; i < N; i++) {
    const start = 63 + i * 2.4; // arranca con la divergencia (VO "En efectivo", f63)
    const life = 46;
    const t = (frame - start) / life;
    if (t < 0 || t > 1) continue;
    // sube un poco y luego cae (chispa), con deriva lateral
    const drift = (rnd(i) - 0.5) * 90 * t;
    const x = cx - BAR_W / 2 + rnd(i) * BAR_W + drift;
    const y = topY - t * 40 + t * t * 260; // pequeño impulso arriba → gravedad
    const size = 4 + rnd(i + 9) * 8;
    const hot = rnd(i + 3) > 0.55; // unas brasas más calientes (ámbar)
    const c = hot ? theme.gold : theme.red;
    const op = Math.sin(Math.min(t, 1) * Math.PI) * 0.9; // fade-in/out suave
    out.push(
      <div
        key={i}
        style={{
          position: "absolute",
          left: x,
          top: y,
          width: size,
          height: size,
          borderRadius: "50%",
          background: c,
          opacity: op,
          boxShadow: `0 0 ${size * 1.6}px ${c}, 0 0 ${size * 0.7}px #fff8`,
        }}
      />
    );
  }
  return <>{out}</>;
};

// Reel de un dígito (odómetro): el offset es el valor CONTINUO de esa posición,
// así las unidades giran rápido y los dígitos altos lento (mecánico real, no swap).
const REEL_MASK =
  "linear-gradient(180deg, transparent 0%, #000 30%, #000 70%, transparent 100%)";

const DigitReel: React.FC<{ place: number; value: number; size: number; h: number; dim: boolean }> = ({
  place,
  value,
  size,
  h,
  dim,
}) => {
  // Posiciones bajas (≤2) quedan en 0: el contador rueda en MILES (legible, premium) y
  // aterriza EXACTO (los finales terminan en 000). La rueda de los MILES gira suave
  // (umbral 0.82, featured); las ruedas ALTAS sólo giran en el acarreo real (umbral 0.95)
  // para no "arrastrarse" en valores estáticos — p.ej. 94,000 debe leer un 0 nítido, no
  // medio 1. Un umbral único eager dejaba la rueda alta a media vuelta en endpoints.
  let dv: number;
  if (place <= 2) {
    dv = 0;
  } else {
    const raw = value / Math.pow(10, place);
    const D = Math.floor(raw) % 10;
    const frac = raw - Math.floor(raw);
    const thr = place >= 4 ? 0.95 : 0.82;
    const roll = frac < thr ? 0 : (frac - thr) / (1 - thr); // 0→1 giro veloz en el acarreo
    dv = D + roll;
  }
  const winH = h * 1.7; // ventana más alta: el dígito centrado queda nítido, los vecinos asoman
  const offset = (winH - h) / 2 - dv * h;
  return (
    <div
      style={{
        position: "relative",
        width: size * 0.6,
        height: winH,
        overflow: "hidden",
        opacity: dim ? 0.26 : 1, // ceros a la izquierda atenuados (look odómetro premium)
        WebkitMaskImage: REEL_MASK,
        maskImage: REEL_MASK,
      }}
    >
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          transform: `translateY(${offset}px)`,
        }}
      >
        {[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0].map((n, k) => (
          <div key={k} style={{ height: h, lineHeight: `${h}px`, textAlign: "center" }}>
            {n}
          </div>
        ))}
      </div>
    </div>
  );
};

const RollingNumber: React.FC<{ value: number; color: string; size: number }> = ({
  value,
  color,
  size,
}) => {
  const v = Math.max(0, value);
  // Ancho FIJO (6 para escala 100k): evita el glitch de cambiar de nº de dígitos al cruzar
  // 100,000 (antes la rueda alta no tenía dónde mostrar el "1" entrante → "09,000").
  const d = Math.max(6, String(Math.floor(v)).length);
  const h = size * 1.16;
  const winH = h * 1.7;
  const nodes: React.ReactNode[] = [];
  for (let i = 0; i < d; i++) {
    const place = d - 1 - i;
    const dim = v < Math.pow(10, place); // cero a la izquierda → atenuado
    nodes.push(<DigitReel key={`d${i}`} place={place} value={v} size={size} h={h} dim={dim} />);
    if (place > 0 && place % 3 === 0) {
      nodes.push(
        <span key={`c${i}`} style={{ height: winH, lineHeight: `${winH}px` }}>
          ,
        </span>
      );
    }
  }
  return (
    <div
      style={{
        display: "inline-flex",
        alignItems: "center",
        height: winH,
        fontFamily: theme.font,
        fontSize: size,
        fontWeight: 800,
        color,
        fontVariantNumeric: "tabular-nums",
      }}
    >
      <span style={{ height: winH, lineHeight: `${winH}px`, marginRight: size * 0.04 }}>$</span>
      {nodes}
    </div>
  );
};

const Counter: React.FC<{ cx: number; value: number; color: string; tick: number }> = ({
  cx,
  value,
  color,
  tick,
}) => (
  <div
    style={{
      position: "absolute",
      left: cx - 200,
      top: 700,
      width: 400,
      display: "flex",
      justifyContent: "center",
      transform: `scale(${tick})`,
      transformOrigin: "50% 50%",
      filter: `drop-shadow(0 0 22px ${color}55)`,
    }}
  >
    <RollingNumber value={value} color={color} size={76} />
  </div>
);

export const ErosionRace: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Beats SINCRONIZADOS a la VO Asgard (reelc_vo, 6.72s @30fps):
  //   "Cien mil pesos…"             0.0–1.13s   → suben juntas + cuentan 0→100k
  //   "…el mismo arranque."         1.13–2.10s  → hold a 100k (mismo inicio)
  //   "En efectivo,…"               2.107s = f63 → arranca la divergencia
  //   "…la inflación los derrite."  4.64s = f139 → columnas asentadas
  //   "Invertir cambia el final."   4.83s = f145 → payoff
  const DIV_START = 63;
  const DIV_END = 139;
  const PAY_START = 145;

  // Fase A: suben juntas + cuentan 0→100k, luego hold hasta DIV_START.
  const rise = spring({ frame, fps, config: { damping: 200 }, durationInFrames: 30 });
  const startVal = rise * START;

  // Fase B (DIV_START→DIV_END): divergencia.
  const divActive = frame >= DIV_START;
  const cashProg = interpolate(frame, [DIV_START, DIV_END], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const invSp = spring({
    frame: Math.max(0, frame - DIV_START),
    fps,
    config: { damping: 11, stiffness: 80, mass: 1.2 }, // overshoot: rebasa y asienta
    durationInFrames: DIV_END - DIV_START,
  });
  const colorProg = interpolate(frame, [DIV_START, DIV_START + 57], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const cashV = divActive ? interpolate(cashProg, [0, 1], [START, CASH_END]) : startVal;
  const invV = divActive ? START + invSp * (INV_END - START) : startVal;

  const LOSS_RED = "#EA3D4C"; // rojo de pérdida más profundo que el coral del theme (lee mejor en columna)
  const cashColor = interpolateColors(colorProg, [0, 1], [theme.teal, LOSS_RED]);
  const invColor = interpolateColors(colorProg, [0, 1], [theme.teal, theme.green]);

  const cashH = vToH(cashV);
  const invH = vToH(invV);
  const cashTopY = FLOOR - cashH;

  // "↓ inflación" entra con la divergencia, se mantiene, sale antes del payoff.
  const inflOp = interpolate(
    frame,
    [DIV_START - 3, DIV_START + 9, DIV_END - 7, DIV_END + 3],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  const inflPulse = 1 + Math.sin(frame / 6) * 0.05;

  // Payoff (PAY_START→): card central con la diferencia real (<<verify>>).
  const pay = spring({
    frame: Math.max(0, frame - PAY_START),
    fps,
    config: { damping: 200 },
    durationInFrames: 26,
  });
  // Cámara: push-in lento (la pieza "respira") + focus-pull REAL en el payoff
  // (la escena escala hacia atrás y se desenfoca cuando entra la tarjeta).
  const breathe = interpolate(frame, [0, 200], [1.012, 1.05], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const breatheY = interpolate(frame, [0, 200], [6, -8], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const stageScale = breathe * interpolate(pay, [0, 1], [1, 0.92]);
  const stageBlur = pay * 4;
  const stageDim = interpolate(pay, [0, 1], [1, 0.6]);

  // Glow de fondo a la deriva (movimiento constante).
  const glowX = 50 + Math.sin(frame / 40) * 8;

  // Entrada del hook: el título sube + aparece (stagger título→subtítulo).
  const titleIn = spring({ frame, fps, config: { damping: 18 }, durationInFrames: 22 });
  const subIn = spring({
    frame: Math.max(0, frame - 6),
    fps,
    config: { damping: 18 },
    durationInFrames: 22,
  });

  // "Tick" de asiento: pulso de escala sutil cuando los números llegan (30=100k, PAY_START=final).
  const settle = (f0: number) =>
    interpolate(frame, [f0, f0 + 4, f0 + 13], [0, 1, 0], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
  const tick = 1 + (settle(30) + settle(PAY_START)) * 0.05;

  return (
    <AbsoluteFill style={{ background: theme.bg.gradient }}>
      <AbsoluteFill
        style={{
          background: `radial-gradient(58% 40% at ${glowX}% 28%, rgba(91,192,190,0.10), rgba(0,0,0,0) 60%)`,
        }}
      />
      {/* Luz cenital suave (da volumen al fondo, no plano) */}
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(70% 32% at 50% 0%, rgba(255,255,255,0.06), rgba(0,0,0,0) 70%)",
        }}
      />
      {/* Piso luminoso bajo las columnas (las asienta en un escenario) */}
      <AbsoluteFill
        style={{
          background: `radial-gradient(46% 18% at 50% ${(FLOOR / H) * 100}%, rgba(91,192,190,0.10), rgba(0,0,0,0) 70%)`,
        }}
      />

      <AbsoluteFill
        style={{
          opacity: stageDim,
          transform: `scale(${stageScale}) translateY(${breatheY}px)`,
          transformOrigin: "50% 54%",
          filter: stageBlur > 0.1 ? `blur(${stageBlur}px)` : undefined,
        }}
      >
      {/* Título */}
      <div
        style={{
          position: "absolute",
          top: 300,
          width: W,
          textAlign: "center",
          fontFamily: theme.font,
          fontSize: 58,
          fontWeight: 800,
          color: theme.text,
          opacity: titleIn,
          transform: `translateY(${(1 - titleIn) * 28}px)`,
        }}
      >
        Mismo inicio.
      </div>
      <div
        style={{
          position: "absolute",
          top: 384,
          width: W,
          textAlign: "center",
          fontFamily: theme.font,
          fontSize: 40,
          fontWeight: 600,
          color: theme.textDim,
          opacity: subIn,
          transform: `translateY(${(1 - subIn) * 24}px)`,
        }}
      >
        La <span style={{ color: theme.red }}>inflación</span> decide quién gana.
      </div>

      {/* Pilas */}
      <Bar cx={COL_CASH_X} h={cashH} color={cashColor} frame={frame} phase={0} eroding={frame >= DIV_START} />
      <Bar cx={COL_INV_X} h={invH} color={invColor} frame={frame} phase={2.1} />

      {/* Partículas de erosión (solo efectivo) */}
      <ErosionDust frame={frame} topY={cashTopY} cx={COL_CASH_X} />

      {/* Contadores */}
      <Counter cx={COL_CASH_X} value={cashV} color={cashColor} tick={tick} />
      <Counter cx={COL_INV_X} value={invV} color={invColor} tick={tick} />

      {/* Etiqueta inflación sobre el efectivo */}
      <div
        style={{
          position: "absolute",
          left: COL_CASH_X - 160,
          top: 560,
          width: 320,
          textAlign: "center",
          opacity: inflOp,
          transform: `scale(${inflPulse})`,
        }}
      >
        <span
          style={{
            fontFamily: theme.font,
            fontSize: 34,
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

      {/* Piso + etiquetas de columna */}
      <div
        style={{
          position: "absolute",
          left: 120,
          top: FLOOR + 2,
          width: W - 240,
          height: 2,
          background: "rgba(255,255,255,0.12)",
        }}
      />
      <div
        style={{
          position: "absolute",
          left: COL_CASH_X - 160,
          top: FLOOR + 18,
          width: 320,
          textAlign: "center",
          fontFamily: theme.font,
          fontSize: 36,
          fontWeight: 600,
          letterSpacing: 2,
          textTransform: "uppercase",
          color: theme.textDim,
        }}
      >
        Efectivo
      </div>
      <div
        style={{
          position: "absolute",
          left: COL_INV_X - 160,
          top: FLOOR + 18,
          width: 320,
          textAlign: "center",
          fontFamily: theme.font,
          fontSize: 36,
          fontWeight: 600,
          letterSpacing: 2,
          textTransform: "uppercase",
          color: theme.textDim,
        }}
      >
        Invertir
      </div>
      </AbsoluteFill>

      {/* Payoff: diferencia real (card con fondo propio para no chocar con las pilas) */}
      <AbsoluteFill style={{ background: "rgba(13,17,23,0.40)", opacity: pay * 0.5 }} />
      <div
        style={{
          position: "absolute",
          left: 165,
          top: 980,
          width: 750,
          opacity: pay,
          transform: `translateY(${(1 - pay) * 26}px)`,
          background: "rgba(13,17,23,0.90)",
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
            fontSize: 110,
            fontWeight: 800,
            color: theme.green,
            margin: "6px 0 2px",
          }}
        >
          {"<<verify>>"}
        </div>
        <div style={{ fontFamily: theme.font, fontSize: 32, color: theme.textDim }}>
          lo que la inflación cobra por no decidir
        </div>
      </div>

      {/* Disclaimer (meta, no contenido) */}
      <div
        style={{
          position: "absolute",
          top: 1700,
          width: W,
          textAlign: "center",
          fontFamily: theme.font,
          fontSize: 22,
          color: "rgba(160,160,176,0.7)",
        }}
      >
        Cifras ilustrativas — tasa/inflación reales pendientes de &lt;&lt;verify&gt;&gt;. Animatic de dirección.
      </div>

      {/* Viñeta (enmarca, da foco al centro) */}
      <AbsoluteFill
        style={{
          pointerEvents: "none",
          background:
            "radial-gradient(120% 80% at 50% 42%, rgba(0,0,0,0) 56%, rgba(0,0,0,0.55) 100%)",
        }}
      />
      {/* Grano de película (textura, mata el look 'plano digital') */}
      <AbsoluteFill style={{ pointerEvents: "none", opacity: 0.05, mixBlendMode: "overlay" }}>
        <svg width={W} height={H}>
          <filter id="filmgrain">
            <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves={2} stitchTiles="stitch" />
          </filter>
          <rect width={W} height={H} filter="url(#filmgrain)" />
        </svg>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
