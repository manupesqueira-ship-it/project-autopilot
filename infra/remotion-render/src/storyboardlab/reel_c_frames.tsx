// Styleframes del Golden Reel C (composición ANTES de animar; cifras como <<verify>>).
// Brief: infra/grammar/reel_c/brief.md. Color semántico: oro=dinero, rojo=pérdida real,
// verde=sube/gana, teal=neutral/real-atenuado. Moneda explícita (MXN).
import { StyleframeSpec } from "./types";

const GOLD = "#D4A574";
const GREEN = "#00D9A5";
const RED = "#FF6B6B";
const TEAL = "#5BC0BE";
const TEXT = "#FFFFFF";
const DIM = "#A0A0B0";

// ---- Escena 0 — PrincipalCounter (HOOK): 3 styleframes ----------------------
export const s0_inicial: StyleframeSpec = {
  id: "C0-inicial",
  title: "PrincipalCounter · entrada",
  note: "Entra el capital ancla. Aún sin subline; la cifra manda.",
  blocks: [
    { type: "label", text: "Tienes", x: 0, y: 600, w: 1080, align: "center", size: 46, color: DIM },
    { type: "number", text: "$100,000", x: 0, y: 712, w: 1080, align: "center", size: 168, color: GOLD },
    { type: "label", text: "MXN", x: 0, y: 936, w: 1080, align: "center", size: 54, color: GOLD },
  ],
};

export const s0_maxinfo: StyleframeSpec = {
  id: "C0-maxinfo",
  title: "PrincipalCounter · máxima info",
  note: "Cifra + open loop. La voz redondea; el visual es exacto.",
  blocks: [
    { type: "label", text: "Tienes", x: 0, y: 560, w: 1080, align: "center", size: 44, color: DIM },
    { type: "number", text: "$100,000", x: 0, y: 668, w: 1080, align: "center", size: 168, color: GOLD },
    { type: "label", text: "MXN", x: 0, y: 892, w: 1080, align: "center", size: 52, color: GOLD },
    { type: "text", text: "En 12 meses, dos caminos.", x: 130, y: 1030, w: 820, align: "center", size: 52, color: TEXT },
    { type: "text", text: "Uno te deja con menos de lo que crees.", x: 130, y: 1118, w: 820, align: "center", size: 34, color: DIM, weight: 600 },
  ],
};

export const s0_salida: StyleframeSpec = {
  id: "C0-salida",
  title: "PrincipalCounter · salida",
  note: "La cifra sube y aparecen los dos carriles (puente a ComparisonSplit).",
  blocks: [
    { type: "number", text: "$100,000", x: 0, y: 470, w: 1080, align: "center", size: 116, color: GOLD },
    { type: "label", text: "MXN", x: 0, y: 610, w: 1080, align: "center", size: 36, color: GOLD },
    { type: "rect", x: 120, y: 760, w: 380, h: 560, stroke: "rgba(91,192,190,0.5)", fill: "rgba(91,192,190,0.05)" },
    { type: "rect", x: 580, y: 760, w: 380, h: 560, stroke: "rgba(212,165,116,0.5)", fill: "rgba(212,165,116,0.05)" },
    { type: "label", text: "Efectivo", x: 120, y: 800, w: 380, align: "center", size: 34, color: TEAL },
    { type: "label", text: "Invertir", x: 580, y: 800, w: 380, align: "center", size: 34, color: GOLD },
  ],
};

// ---- Escenas 1-5 — un styleframe representativo por escena (storyboard) ------
export const s1_comparison: StyleframeSpec = {
  id: "C1",
  title: "ComparisonSplit",
  note: "Dos escenarios coexisten; mismo punto de partida.",
  blocks: [
    { type: "rect", x: 108, y: 540, w: 372, h: 840, stroke: "rgba(91,192,190,0.45)", fill: "rgba(91,192,190,0.05)" },
    { type: "rect", x: 600, y: 540, w: 372, h: 840, stroke: "rgba(212,165,116,0.45)", fill: "rgba(212,165,116,0.05)" },
    { type: "rect", x: 538, y: 560, w: 4, h: 800, fill: "rgba(255,255,255,0.12)" },
    { type: "label", text: "Efectivo", x: 108, y: 590, w: 372, align: "center", size: 38, color: TEAL },
    { type: "number", text: "$100,000", x: 108, y: 760, w: 372, align: "center", size: 64, color: TEXT },
    { type: "label", text: "MXN", x: 108, y: 858, w: 372, align: "center", size: 30, color: DIM },
    { type: "label", text: "Invertir", x: 600, y: 590, w: 372, align: "center", size: 38, color: GOLD },
    { type: "number", text: "$100,000", x: 600, y: 760, w: 372, align: "center", size: 64, color: TEXT },
    { type: "label", text: "tasa  <<verify>>", x: 600, y: 980, w: 372, align: "center", size: 34, color: GREEN },
    { type: "text", text: "Mismo punto de partida.", x: 130, y: 1430, w: 820, align: "center", size: 40, color: DIM },
  ],
};

export const s2_erosion: StyleframeSpec = {
  id: "C2",
  title: "InflationErosion",
  note: "El tercer jugador: la inflación erosiona el poder de compra del efectivo.",
  blocks: [
    { type: "label", text: "El tercer jugador: inflación", x: 0, y: 500, w: 1080, align: "center", size: 40, color: RED },
    { type: "chartph", x: 140, y: 600, w: 800, h: 560, trend: "down", label: "valor real del efectivo  ↓  12 meses" },
    { type: "label", text: "$100,000 MXN  →  <<verify>> MXN", x: 0, y: 1200, w: 1080, align: "center", size: 40, color: TEXT },
    { type: "label", text: "−<<verify>>  inflación", x: 0, y: 1270, w: 1080, align: "center", size: 34, color: RED },
  ],
};

export const s3_nominal_real: StyleframeSpec = {
  id: "C3",
  title: "NominalVsReal",
  note: "No te engañe el nominal: real = − impuestos − inflación.",
  blocks: [
    { type: "label", text: "No te engañe el nominal", x: 0, y: 500, w: 1080, align: "center", size: 40, color: TEXT },
    { type: "number", text: "<<verify>>", x: 0, y: 620, w: 1080, align: "center", size: 104, color: GREEN },
    { type: "label", text: "nominal", x: 0, y: 760, w: 1080, align: "center", size: 34, color: GREEN },
    { type: "number", text: "<<verify>>", x: 0, y: 940, w: 1080, align: "center", size: 104, color: TEAL },
    { type: "label", text: "real  (− impuestos − inflación)", x: 0, y: 1080, w: 1080, align: "center", size: 34, color: TEAL },
    { type: "label", text: "supuesto fiscal: <<verify>>", x: 0, y: 1320, w: 1080, align: "center", size: 26, color: DIM },
  ],
};

export const s4_outcome: StyleframeSpec = {
  id: "C4",
  title: "OutcomeReveal · PAYOFF",
  note: "Cifra clímax: la diferencia REAL entre los caminos.",
  blocks: [
    { type: "label", text: "La diferencia real", x: 0, y: 540, w: 1080, align: "center", size: 44, color: GOLD },
    { type: "number", text: "<<verify>>", x: 0, y: 660, w: 1080, align: "center", size: 150, color: GREEN },
    { type: "label", text: "efectivo  <<verify>>", x: 108, y: 1040, w: 380, align: "center", size: 34, color: RED },
    { type: "label", text: "invertir  <<verify>>", x: 592, y: 1040, w: 380, align: "center", size: 34, color: GREEN },
    { type: "text", text: "Lo que la inflación te cobra por no decidir.", x: 130, y: 1220, w: 820, align: "center", size: 38, color: DIM },
  ],
};

export const s5_close: StyleframeSpec = {
  id: "C5",
  title: "DecisionClose · CTA",
  note: "Conclusión educativa (no recomendación) + CTA + loop.",
  blocks: [
    { type: "text", text: "Entiende la tasa real.", x: 0, y: 620, w: 1080, align: "center", size: 64, color: TEXT, weight: 800 },
    { type: "text", text: "Si no le gana a la inflación, pierdes — aunque el número suba.", x: 130, y: 740, w: 820, align: "center", size: 38, color: DIM },
    { type: "label", text: "Guarda esto", x: 0, y: 940, w: 1080, align: "center", size: 44, color: GOLD },
    { type: "divider", x: 290, y: 1050, w: 500, color: "rgba(255,255,255,0.14)" },
    { type: "label", text: "mañana: una tasa que sí le gane a la inflación", x: 0, y: 1090, w: 1080, align: "center", size: 32, color: GREEN },
    { type: "text", text: "Contenido educativo, no recomendación individualizada.", x: 130, y: 1500, w: 820, align: "center", size: 22, color: DIM },
  ],
};

// Escena 0 = 3 styleframes (la PRIMERA escena se trabaja a fondo).
export const reelC_scene0 = [s0_inicial, s0_maxinfo, s0_salida];

// Storyboard completo (1 frame por escena) — el arco de 6.
export const reelC_storyboard: StyleframeSpec[] = [
  s0_maxinfo,
  s1_comparison,
  s2_erosion,
  s3_nominal_real,
  s4_outcome,
  s5_close,
];
