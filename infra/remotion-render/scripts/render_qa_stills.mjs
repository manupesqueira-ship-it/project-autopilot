// Pase de calidad: rinde un still full-res 1080x1920 de LOS 39 beats registrados
// (no solo los 25 de grafica de la galeria) a out/_stills/qa_pass/.
// Bundlea UNA sola vez y usa renderStill por composicion. El frame de cada beat
// se elige en estado "asentado" (~70% de su duracion) para auditar la composicion
// final, no un fotograma de transicion.
import { bundle } from "@remotion/bundler";
import { selectComposition, renderStill } from "@remotion/renderer";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, "..");
const outDir = path.resolve(root, "../assembler/out/_stills/qa_pass");

// [CompId, frame representativo]. Los 25 de grafica reusan los frames de la
// galeria; los 14 narrativos/texto van a ~0.7x de su durationInFrames.
const BEATS = [
  ["BeatLineChart", 130],
  ["BeatPictogram", 120],
  ["BeatBigNumber", 110],
  ["BeatBars", 120],
  ["BeatAssetCard", 110],
  ["BeatTrendBreak", 150],
  ["BeatVersus", 130],
  ["BeatTimeline", 200],
  ["BeatBarRace", 120],
  ["BeatKinetic", 70],
  ["BeatMapZoom", 110],
  ["BeatRecovery", 140],
  ["BeatDonut", 130],
  ["BeatWaterfall", 150],
  ["BeatBubble", 140],
  ["BeatCandlestick", 150],
  ["BeatCharacter", 110],
  ["BeatNewsCard", 120],
  ["BeatMultiMap", 120],
  ["BeatLogoWall", 110],
  ["BeatDebate", 140],
  ["BeatHeroCoin", 110],
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
  ["BeatTestimonial", 130],
  ["BeatStatCallout", 110],
  ["BeatCta", 90],
];

const main = async () => {
  console.log(`Bundling once... (${BEATS.length} beats)`);
  const serveUrl = await bundle({
    entryPoint: path.resolve(root, "src/index.ts"),
    onProgress: () => {},
  });
  console.log("Bundle ready.");

  let okN = 0;
  for (const [id, frame] of BEATS) {
    try {
      const comp = await selectComposition({ serveUrl, id });
      const output = path.join(outDir, `${id}.png`);
      await renderStill({ composition: comp, serveUrl, output, frame, overwrite: true });
      okN += 1;
      console.log(`OK ${id} @${frame}`);
    } catch (e) {
      console.error(`FAIL ${id} @${frame}: ${e.message}`);
    }
  }
  console.log(`DONE ${okN}/${BEATS.length}`);
};

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
