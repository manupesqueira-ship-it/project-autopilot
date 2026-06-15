import React from "react";
import { AbsoluteFill } from "remotion";
import { theme } from "./theme";

import { LineChartSemantic } from "./beats/LineChartSemantic";
import { PictogramPersons } from "./beats/PictogramPersons";
import { BigNumberCounter } from "./beats/BigNumberCounter";
import { BarsValue } from "./beats/BarsValue";
import { TrendBreak } from "./beats/TrendBreak";
import { RecoveryChart } from "./beats/RecoveryChart";
import { DonutChart } from "./beats/DonutChart";
import { WaterfallChart } from "./beats/WaterfallChart";
import { BubbleChart } from "./beats/BubbleChart";
import { CandlestickChart } from "./beats/CandlestickChart";
import { BarRace } from "./beats/BarRace";
import { StackedAreaChart } from "./beats/StackedAreaChart";
import { DialGauge } from "./beats/DialGauge";
import { SlopeChart } from "./beats/SlopeChart";
import { ProgressRing } from "./beats/ProgressRing";
import { LollipopChart } from "./beats/LollipopChart";
import { FunnelChart } from "./beats/FunnelChart";
import { Histogram } from "./beats/Histogram";
import { ScaledIcon } from "./beats/ScaledIcon";
import { Heatmap } from "./beats/Heatmap";
import { TickerTape } from "./beats/TickerTape";
import { Treemap } from "./beats/Treemap";
import { RadarChart } from "./beats/RadarChart";
import { Scoreboard } from "./beats/Scoreboard";
import { SankeyFlow } from "./beats/SankeyFlow";

// Contact-sheet: TODOS los beats de graficas en una rejilla. Cada celda renderiza
// el beat real a 1080x1920 y lo escala. Datos financieros representativos reales.
type Entry = { id: string; node: React.ReactNode };

export const GALLERY: Entry[] = [
  {
    id: "BeatLineChart",
    node: (
      <LineChartSemantic
        caption="el Bitcoin subió 8 meses seguidos"
        points={[18, 26, 23, 34, 31, 47, 44, 62, 78, 96, 71, 52, 38, 30]}
        peakIndex={9}
        labels={[
          { text: "$43,200", index: 3 },
          { text: "$69,000", index: 7 },
          { text: "-$38,000", index: 12, color: "#FF6B6B" },
        ]}
        peakLabel="+$108,000"
      />
    ),
  },
  {
    id: "BeatPictogram",
    node: (
      <PictogramPersons
        caption="¿cuántos mexicanos invierten su dinero?"
        count={21}
        total={100}
        statSuffix="de cada 100"
      />
    ),
  },
  {
    id: "BeatBigNumber",
    node: (
      <BigNumberCounter
        caption="la inflación se comió de tu sueldo"
        prefix="$"
        value={18400}
        suffix=" MXN"
        decimals={0}
        subline="en los últimos 12 meses"
      />
    ),
  },
  {
    id: "BeatBars",
    node: (
      <BarsValue
        caption="lo que paga $10,000 en un año"
        bars={[
          { label: "Débito", value: 12 },
          { label: "Pagaré banco", value: 480 },
          { label: "Fondo gub.", value: 980, highlight: true },
        ]}
        prefix="$"
        suffix=""
      />
    ),
  },
  {
    id: "BeatTrendBreak",
    node: (
      <TrendBreak
        caption="y entonces llegó 2022"
        points={[134.73, 144.7, 133.68, 148.05, 141.9, 144.85, 135.3, 135.06, 139.07, 114.11, 113.76, 108.96, 116.32, 108.22, 95.65, 94.51, 100.99, 88.23]}
        peakIndex={3}
        counterLabel="tu inversión"
        countFrom={10989}
        countTo={6549}
        countPrefix="$"
        pctLabel="−40%"
        peakLabel="$148"
        troughLabel="$88"
      />
    ),
  },
  {
    id: "BeatRecovery",
    node: (
      <RecoveryChart
        caption="Bitcoin: el desplome y la recuperación"
        points={[44739, 52000, 47000, 38000, 31000, 22000, 19000, 16000, 21000, 27000, 30000, 38000, 45000, 52000, 58000, 64089]}
        troughIndex={7}
        troughLabel="$16,000"
        endLabel="$64,000"
      />
    ),
  },
  {
    id: "BeatDonut",
    node: (
      <DonutChart
        caption="de cada dólar que factura Apple"
        segments={[
          { label: "iPhone", value: 52 },
          { label: "Servicios", value: 24 },
          { label: "Mac", value: 10 },
          { label: "iPad", value: 8 },
          { label: "Otros", value: 6 },
        ]}
        highlightIndex={1}
        centerLabel="Servicios"
      />
    ),
  },
  {
    id: "BeatWaterfall",
    node: (
      <WaterfallChart
        caption="a dónde se va tu sueldo de $30,000"
        startLabel="Sueldo"
        startValue={30000}
        steps={[
          { label: "Renta", delta: -9000 },
          { label: "Comida", delta: -6000 },
          { label: "Transporte", delta: -3000 },
          { label: "Deudas", delta: -4500 },
        ]}
        endLabel="Te queda"
        prefix="$"
      />
    ),
  },
  {
    id: "BeatBubble",
    node: (
      <BubbleChart
        caption="las empresas más valiosas del mundo"
        bubbles={[
          { label: "Apple", value: 3.4e12, logo: "apple" },
          { label: "Nvidia", value: 3.3e12, logo: "nvidia" },
          { label: "Microsoft", value: 3.1e12, logo: "microsoft" },
          { label: "Alphabet", value: 2.1e12, logo: "google" },
          { label: "Amazon", value: 2.0e12, logo: "amazon" },
        ]}
        prefix="$"
        valueScale={1e12}
        valueUnit="T"
      />
    ),
  },
  {
    id: "BeatCandlestick",
    node: (
      <CandlestickChart
        caption="el precio del Bitcoin en 2024"
        candles={[
          { o: 42000, h: 44000, l: 41500, c: 43500 },
          { o: 43500, h: 46000, l: 43000, c: 45500 },
          { o: 45500, h: 46500, l: 44000, c: 44200 },
          { o: 44200, h: 48000, l: 44000, c: 47500 },
          { o: 47500, h: 52000, l: 47000, c: 51000 },
          { o: 51000, h: 53000, l: 49000, c: 49500 },
          { o: 49500, h: 55000, l: 49000, c: 54000 },
          { o: 54000, h: 58000, l: 53500, c: 57500 },
          { o: 57500, h: 60000, l: 55000, c: 56000 },
          { o: 56000, h: 62000, l: 55500, c: 61500 },
          { o: 61500, h: 66000, l: 61000, c: 63000 },
          { o: 63000, h: 65000, l: 61500, c: 64089 },
        ]}
        prefix="$"
        readoutLabel="cierre"
        highlightLast
      />
    ),
  },
  {
    id: "BeatBarRace",
    node: (
      <BarRace
        caption="$250 USD al mes · 10% anual"
        monthly={250}
        rate={0.1}
        ageStart={25}
        ageEnd={65}
        racers={[
          { label: "empiezas a los 25", startAge: 25, tag: "40 años" },
          { label: "a los 35", startAge: 35, tag: "30 años" },
          { label: "a los 45", startAge: 45, tag: "20 años" },
        ]}
        prefix="$"
        winnerIndex={0}
        countEndFrame={120}
        pulseFrames={[130, 138]}
      />
    ),
  },
  {
    id: "BeatStackedArea",
    node: (
      <StackedAreaChart
        caption="de dónde sale el ahorro que acumulas"
        series={[
          { label: "Aportación", values: [200, 420, 660, 920, 1200, 1500] },
          { label: "Interés", values: [5, 22, 58, 120, 215, 350] },
          { label: "Patrón", values: [100, 210, 330, 460, 600, 750] },
        ]}
        xLabels={["Año 1", "Año 2", "Año 3", "Año 4", "Año 5", "Año 6"]}
        highlightIndex={1}
        prefix="$"
      />
    ),
  },
  {
    id: "BeatDialGauge",
    node: (
      <DialGauge
        caption="qué tan caro está el mercado hoy"
        value={38}
        min={0}
        max={100}
        label="índice miedo / codicia"
        suffix=""
        goodHigh={false}
      />
    ),
  },
  {
    id: "BeatSlope",
    node: (
      <SlopeChart
        caption="tu poder de compra en 4 años"
        leftLabel="2020"
        rightLabel="2024"
        items={[
          { label: "Salario", left: 100, right: 118, color: "#00D9A5" },
          { label: "Canasta básica", left: 100, right: 142, color: "#FF6B6B" },
        ]}
        prefix=""
        suffix=""
      />
    ),
  },
  {
    id: "BeatProgressRing",
    node: (
      <ProgressRing
        caption="cuánto de tu deuda ya pagaste"
        percent={64}
        label="de $85,000 MXN"
        color="#00D9A5"
      />
    ),
  },
  {
    id: "BeatLollipop",
    node: (
      <LollipopChart
        caption="brecha salarial entre hombres y mujeres"
        items={[
          { label: "Directivos", value: 58000, value2: 47000 },
          { label: "Ingeniería", value: 42000, value2: 36000 },
          { label: "Ventas", value: 28000, value2: 25000 },
        ]}
        prefix="$"
        legend1="Hombres"
        legend2="Mujeres"
      />
    ),
  },
  {
    id: "BeatFunnel",
    node: (
      <FunnelChart
        caption="de cada 100 que abren cuenta de inversión"
        stages={[
          { label: "Abren cuenta", value: 100 },
          { label: "Depositan", value: 62 },
          { label: "Invierten", value: 34 },
          { label: "Siguen al año", value: 11 },
        ]}
        suffix=""
      />
    ),
  },
  {
    id: "BeatHistogram",
    node: (
      <Histogram
        caption="cuánto gana la gente en México"
        bins={[8, 22, 41, 58, 47, 30, 18, 10, 6, 3]}
        xLabels={["5k", "10k", "15k", "20k", "25k", "30k", "40k", "50k", "70k", "+90k"]}
        markerIndex={3}
        markerLabel="tú"
        color="#00D9A5"
      />
    ),
  },
  {
    id: "BeatScaledIcon",
    node: (
      <ScaledIcon
        caption="una casa vs lo que ganas en un año"
        items={[
          { label: "Tu sueldo anual", value: 360000 },
          { label: "Casa promedio", value: 2880000 },
        ]}
        symbol="$"
        prefix="$"
        valueScale={1000}
        valueUnit="k"
      />
    ),
  },
  {
    id: "BeatHeatmap",
    node: (
      <Heatmap
        caption="rendimiento mes a mes de tu portafolio"
        rows={[
          { label: "2022", values: [-4, 2, -6, 3, -8, -11, 5, -3, -9, 7, 4, -5] },
          { label: "2023", values: [6, 3, -2, 5, 1, 4, 8, -1, -3, 2, 9, 6] },
          { label: "2024", values: [3, 5, 7, -2, 4, 6, 2, 5, 3, 8, 11, 7] },
        ]}
        colLabels={["E", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]}
        diverging
        suffix="%"
      />
    ),
  },
  {
    id: "BeatTickerTape",
    node: (
      <TickerTape
        caption="los mercados hoy"
        items={[
          { symbol: "AAPL", price: 229.87, changePct: 1.2, logo: "apple" },
          { symbol: "NVDA", price: 131.26, changePct: 3.4, logo: "nvidia" },
          { symbol: "TSLA", price: 248.5, changePct: -2.1, logo: "tesla" },
          { symbol: "BTC", price: 64089, changePct: 0.8, logo: "bitcoin" },
          { symbol: "GOOGL", price: 178.35, changePct: -0.6, logo: "google" },
          { symbol: "META", price: 563.27, changePct: 2.3, logo: "meta" },
        ]}
        prefix="$"
        decimals={2}
        speed={1}
      />
    ),
  },
  {
    id: "BeatTreemap",
    node: (
      <Treemap
        caption="cómo se reparte un portafolio de $100,000"
        items={[
          { label: "Acciones EU", value: 45000 },
          { label: "Bonos", value: 22000 },
          { label: "Cripto", value: 12000 },
          { label: "Bienes raíces", value: 11000 },
          { label: "Efectivo", value: 6000 },
          { label: "Oro", value: 4000 },
        ]}
        prefix="$"
        valueScale={1000}
        valueUnit="k"
      />
    ),
  },
  {
    id: "BeatRadar",
    node: (
      <RadarChart
        caption="dos formas de invertir, comparadas"
        axes={["Rendimiento", "Riesgo", "Liquidez", "Costo", "Simpleza"]}
        series={[
          { label: "Cetes", values: [4, 1, 5, 5, 5] },
          { label: "Acciones", values: [5, 5, 4, 3, 2] },
        ]}
        max={5}
      />
    ),
  },
  {
    id: "BeatScoreboard",
    node: (
      <Scoreboard
        caption="tus finanzas este mes"
        cards={[
          { label: "Ingresos", value: 32000, deltaPct: 4.2, prefix: "$", color: "#00D9A5" },
          { label: "Gastos", value: 23500, deltaPct: 6.8, prefix: "$", color: "#5BC0BE", higherIsBetter: false },
          { label: "Ahorro", value: 8500, deltaPct: -2.1, prefix: "$", color: "#F5B544" },
          { label: "Tasa ahorro", value: 27, deltaPct: 1.5, suffix: "%", color: "#5BC0BE" },
        ]}
      />
    ),
  },
  {
    id: "BeatSankey",
    node: (
      <SankeyFlow
        caption="a dónde se va tu sueldo de $30,000"
        source={{ label: "Sueldo", value: 30000 }}
        targets={[
          { label: "Renta", value: 9000 },
          { label: "Comida", value: 6000 },
          { label: "Transporte", value: 3000 },
          { label: "Deudas", value: 4500 },
          { label: "Ahorro", value: 7500 },
        ]}
        prefix="$"
      />
    ),
  },
];

const SCALE = 0.2;
const COLS = 5;
const TW = 1080 * SCALE; // 216
const TH = 1920 * SCALE; // 384
const GAP = 30;
const LABEL_H = 44;
const PAD = 40;
const HEADER = 90;

const ROWS = Math.ceil(GALLERY.length / COLS);

export const GALLERY_W = PAD * 2 + COLS * TW + (COLS - 1) * GAP;
export const GALLERY_H =
  PAD * 2 + HEADER + ROWS * (TH + LABEL_H) + (ROWS - 1) * GAP;

export const CatalogGallery: React.FC = () => {
  return (
    <AbsoluteFill style={{ background: "#0B0F14", fontFamily: theme.font }}>
      <div
        style={{
          position: "absolute",
          top: PAD,
          left: PAD,
          fontSize: 44,
          fontWeight: 800,
          color: theme.text,
        }}
      >
        Dinero IA — catálogo de gráficas{" "}
        <span style={{ color: theme.green }}>({GALLERY.length})</span>
      </div>

      {GALLERY.map((e, i) => {
        const col = i % COLS;
        const row = Math.floor(i / COLS);
        const left = PAD + col * (TW + GAP);
        const top = PAD + HEADER + row * (TH + LABEL_H + GAP);
        return (
          <div key={e.id} style={{ position: "absolute", left, top, width: TW }}>
            <div
              style={{
                width: TW,
                height: TH,
                position: "relative",
                overflow: "hidden",
                borderRadius: 14,
                border: "1px solid rgba(255,255,255,0.10)",
                background: theme.bg.base,
              }}
            >
              <div
                style={{
                  width: 1080,
                  height: 1920,
                  position: "absolute",
                  top: 0,
                  left: 0,
                  transform: `scale(${SCALE})`,
                  transformOrigin: "top left",
                }}
              >
                {e.node}
              </div>
            </div>
            <div
              style={{
                height: LABEL_H,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 20,
                fontWeight: 600,
                color: theme.textDim,
              }}
            >
              {e.id}
            </div>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};
