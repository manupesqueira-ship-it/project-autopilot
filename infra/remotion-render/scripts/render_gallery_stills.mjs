// Render cada beat de grafica a un still full-res 1080x1920 en out/_stills/gallery/.
// Bundlea UNA sola vez (rapido) y usa renderStill por cada composicion.
import { bundle } from "@remotion/bundler";
import { selectComposition, renderStill } from "@remotion/renderer";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, "..");
const outDir = path.resolve(root, "../assembler/out/_stills/gallery");

// ids de beats de grafica (viejos + 14 nuevos) y el frame representativo.
const BEATS = [
  ["BeatLineChart", 130],
  ["BeatPictogram", 120],
  ["BeatBigNumber", 110],
  ["BeatBars", 120],
  ["BeatTrendBreak", 150],
  ["BeatRecovery", 140],
  ["BeatDonut", 130],
  ["BeatWaterfall", 150],
  ["BeatBubble", 140],
  ["BeatCandlestick", 150],
  ["BeatBarRace", 120],
  ["BeatStackedArea", 140],
  ["BeatDialGauge", 120],
  ["BeatSlope", 130],
  ["BeatProgressRing", 120],
  ["BeatLollipop", 140],
  ["BeatFunnel", 130],
  ["BeatHistogram", 130],
  ["BeatScaledIcon", 120],
  ["BeatHeatmap", 130],
  ["BeatTickerTape", 90],
  ["BeatTreemap", 120],
  ["BeatRadar", 120],
  ["BeatScoreboard", 110],
  ["BeatSankey", 130],
];

const main = async () => {
  console.log("Bundling once...");
  const serveUrl = await bundle({
    entryPoint: path.resolve(root, "src/index.ts"),
    onProgress: () => {},
  });
  console.log("Bundle ready.");

  for (const [id, frame] of BEATS) {
    const comp = await selectComposition({ serveUrl, id });
    const output = path.join(outDir, `${id}.png`);
    await renderStill({
      composition: comp,
      serveUrl,
      output,
      frame,
      overwrite: true,
    });
    console.log(`OK ${id} @${frame}`);
  }
  console.log("DONE");
};

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
