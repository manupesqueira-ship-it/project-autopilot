import { staticFile } from "remotion";
import { loadFont } from "@remotion/fonts";

// Tokens LOCKED — fuente: docs/standards/DINERO_IA_STYLE_BIBLE.md §3-§4
export const theme = {
  bg: {
    base: "#0D1117",
    gradient: "linear-gradient(180deg, #1B2433 0%, #141C28 55%, #0D131C 100%)",
  },
  gold: "#D4A574",
  green: "#00D9A5",
  red: "#FF6B6B",
  teal: "#5BC0BE", // neutro / no-pérdida (asignación, gasto rutinario). El rojo queda RESERVADO a pérdida real.
  text: "#FFFFFF",
  textDim: "#A0A0B0",
  font: "InterVar, Inter, Helvetica, Arial, sans-serif",
  mono: "JetBrains Mono, Consolas, monospace",
  grainOpacity: 0.04,
};

// Fuente desde staticFile (servidor local de Remotion) via @remotion/fonts, el
// camino soportado/probado. El data-URI inline (1.16MB en el bundle JS) saturaba
// el parse de cada tab y su FontFace.load() se colgaba bajo carga, reventando el
// delayRender de la fuente en frames aleatorios.
loadFont({
  family: "InterVar",
  url: staticFile("Inter-Variable.ttf"),
  weight: "100 900",
});
