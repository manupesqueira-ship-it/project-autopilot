import { CalculateMetadataFunction, Composition } from "remotion";
import { DineroIAReel } from "./Composition";
import { StoryboardLabCompositions } from "./storyboardlab/labCompositions";
import { TestReel, TEST_REEL_DURATION } from "./TestReel";
import { LineChartSemantic } from "./beats/LineChartSemantic";
import { LineChartPremium } from "./beats/LineChartPremium";
import { PictogramPersons } from "./beats/PictogramPersons";
import { BigNumberCounter } from "./beats/BigNumberCounter";
import { SigErosion } from "./beats/SigErosion";
import { SigErosionHero } from "./beats/SigErosionHero";
import { Ref0x100xOrb } from "./beats/Ref0x100xOrb";
import { StyleProbe } from "./beats/StyleProbe";
import { EditorialHouse } from "./beats/EditorialHouse";
import { EditorialHouseMotion } from "./beats/EditorialHouseMotion";
import { EditorialReel } from "./beats/EditorialReel";
import { StyleHero } from "./beats/StyleHero";
import { LottieHero } from "./beats/LottieHero";
import { EChartsHero } from "./beats/EChartsHero";
import { RiveHero } from "./beats/RiveHero";
import { PhotoHero } from "./beats/PhotoHero";
import { WaffleReveal } from "./beats/WaffleReveal";
import { ShockNumber } from "./beats/ShockNumber";
import { ScaleReveal } from "./beats/ScaleReveal";
import { ReelClose } from "./beats/ReelClose";
import { CardHook, MinPayFeel, DebtTimeline, CompareBars } from "./beats/CreditBeats";
import { NewsHook, Reveal, TrendLine } from "./beats/NewsBeats";
import { TypeAB } from "./beats/TypeAB";
import { Logo } from "./beats/Logo";
import { BtcShowcase } from "./beats/BtcShowcase";
import { MapZoomEditorial } from "./beats/MapZoomEditorial";
import { BarsValue } from "./beats/BarsValue";
import { KineticText } from "./beats/KineticText";
import { KineticTextPremium } from "./beats/KineticTextPremium";
import { CtaClose } from "./beats/CtaClose";
import { CtaClosePremium } from "./beats/CtaClosePremium";
import { AssetCard } from "./beats/AssetCard";
import { TrendBreak } from "./beats/TrendBreak";
import { VersusCards } from "./beats/VersusCards";
import { BarRace } from "./beats/BarRace";
import { Timeline } from "./beats/Timeline";
import { MapZoom } from "./beats/MapZoom";
import { GlobeHero } from "./beats/GlobeHero";
import { GlobeHero3D } from "./beats/GlobeHero3D";
import { ElSalvadorMapHero } from "./beats/ElSalvadorMapHero";
import { CharacterCard } from "./beats/CharacterCard";
import { RecoveryChart } from "./beats/RecoveryChart";
import { RecoveryChartPremium } from "./beats/RecoveryChartPremium";
import { IcePillarCrash } from "./beats/IcePillarCrash";
import { HoldingsIceGold } from "./beats/HoldingsIceGold";
import { HoldingsGainBars } from "./beats/HoldingsGainBars";
import { ThawClimax } from "./beats/ThawClimax";
import { DonutChart } from "./beats/DonutChart";
import { WaterfallChart } from "./beats/WaterfallChart";
import { BubbleChart } from "./beats/BubbleChart";
import { CandlestickChart } from "./beats/CandlestickChart";
import { NewsCard } from "./beats/NewsCard";
import { MultiMap } from "./beats/MultiMap";
import { LogoWall } from "./beats/LogoWall";
import { DebateCards } from "./beats/DebateCards";
import { HeroCoin } from "./beats/HeroCoin";
import { MovingHero } from "./beats/MovingHero";
import { MovingData } from "./beats/MovingData";
import { MovingDataPremium } from "./beats/MovingDataPremium";
import { RealValueMelt } from "./beats/RealValueMelt";
import { HeroCoin3D } from "./HeroCoin3D";
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
import { Testimonial } from "./beats/Testimonial";
import { StatCallout } from "./beats/StatCallout";
import { StoryHook } from "./beats/StoryHook";
import { NapkinWriteOn } from "./beats/NapkinWriteOn";
import { NewspaperSetPiece } from "./beats/NewspaperSetPiece";
import { PhoneSetPiece } from "./beats/PhoneSetPiece";
import { ChalkboardSetPiece } from "./beats/ChalkboardSetPiece";
import { TicketSetPiece } from "./beats/TicketSetPiece";
import { BrandSignature } from "./studio/BrandSignature";
import { CatalogGallery, GALLERY_W, GALLERY_H } from "./CatalogGallery";
import { ReelCoherencePreview, COHERENCE_TOTAL } from "./ReelCoherencePreview";
import { withSeams } from "./studio/SeamFx";
import "./theme";

const LineChartFx = withSeams(LineChartSemantic);
const PictogramFx = withSeams(PictogramPersons);
const BigNumberFx = withSeams(BigNumberCounter);
const BarsFx = withSeams(BarsValue);
const KineticFx = withSeams(KineticText);
const CtaFx = withSeams(CtaClose);
const AssetCardFx = withSeams(AssetCard);
const TrendBreakFx = withSeams(TrendBreak);
const VersusFx = withSeams(VersusCards);
const BarRaceFx = withSeams(BarRace);
const TimelineFx = withSeams(Timeline);
const MapZoomFx = withSeams(MapZoom);
const CharacterFx = withSeams(CharacterCard);
const RecoveryFx = withSeams(RecoveryChart);
const DonutFx = withSeams(DonutChart);
const WaterfallFx = withSeams(WaterfallChart);
const BubbleFx = withSeams(BubbleChart);
const CandlestickFx = withSeams(CandlestickChart);
const NewsCardFx = withSeams(NewsCard);
const MultiMapFx = withSeams(MultiMap);
const LogoWallFx = withSeams(LogoWall);
const DebateFx = withSeams(DebateCards);
const HeroCoinFx = withSeams(HeroCoin);
const MovingHeroFx = withSeams(MovingHero);
const MovingDataFx = withSeams(MovingData);
const StackedAreaFx = withSeams(StackedAreaChart);
const DialGaugeFx = withSeams(DialGauge);
const SlopeFx = withSeams(SlopeChart);
const ProgressRingFx = withSeams(ProgressRing);
const LollipopFx = withSeams(LollipopChart);
const FunnelFx = withSeams(FunnelChart);
const HistogramFx = withSeams(Histogram);
const ScaledIconFx = withSeams(ScaledIcon);
const HeatmapFx = withSeams(Heatmap);
const TickerTapeFx = withSeams(TickerTape);
const TreemapFx = withSeams(Treemap);
const RadarFx = withSeams(RadarChart);
const ScoreboardFx = withSeams(Scoreboard);
const SankeyFx = withSeams(SankeyFlow);
const TestimonialFx = withSeams(Testimonial);
const StatCalloutFx = withSeams(StatCallout);
const NapkinFx = withSeams(NapkinWriteOn);
const NewspaperFx = withSeams(NewspaperSetPiece);
const PhoneFx = withSeams(PhoneSetPiece);
const ChalkboardFx = withSeams(ChalkboardSetPiece);
const TicketFx = withSeams(TicketSetPiece);

// duracion dinamica: el ensamblador pasa durationInFrames en --props
const dyn =
  (fallback: number): CalculateMetadataFunction<Record<string, unknown>> =>
  ({ props }) => ({
    durationInFrames:
      typeof props.durationInFrames === "number"
        ? props.durationInFrames
        : fallback,
  });

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="TestReel"
        component={TestReel}
        durationInFrames={TEST_REEL_DURATION}
        fps={30}
        width={1080}
        height={1920}
      />
      <Composition
        id="CatalogGallery"
        component={CatalogGallery}
        durationInFrames={150}
        fps={30}
        width={GALLERY_W}
        height={GALLERY_H}
      />
      {/* SF v2 (concepto brasa / invierno cripto) — styleframes $0 para gate de look */}
      <Composition
        id="SF-Crash"
        component={IcePillarCrash}
        durationInFrames={90}
        fps={30}
        width={1080}
        height={1920}
      />
      <Composition
        id="SF-Holdings"
        component={HoldingsIceGold}
        durationInFrames={90}
        fps={30}
        width={1080}
        height={1920}
      />
      <Composition
        id="SF-Thaw"
        component={ThawClimax}
        durationInFrames={90}
        fps={30}
        width={1080}
        height={1920}
      />
      {/* Holdings como GRÁFICA explicativa premium (reset 2026-06-29: "no elementos,
          haz gráficas de alta calidad explicativas"). Columnas de vidrio (craft
          aprobado ErosionRace + ref 0x100x bars_label_5090): invertido vs valor,
          la ganancia = cap dorado sobre el nivel invertido. Juzgar en VIDEO. */}
      <Composition
        id="HoldingsGainBars"
        component={HoldingsGainBars}
        calculateMetadata={dyn(150) as never}
        durationInFrames={150}
        fps={30}
        width={1080}
        height={1920}
      />
      {/* b4 recuperación en el MISMO mundo premium (PremiumStage glass), reemplaza
          la versión IglooStage. Línea roja (caída $44,739->$16,000) -> verde
          (recuperación ->$64,000). Datos exactos del guion. Juzgar en VIDEO. */}
      <Composition
        id="RecoveryChartPremium"
        component={RecoveryChartPremium}
        calculateMetadata={dyn(150) as never}
        durationInFrames={150}
        fps={30}
        width={1080}
        height={1920}
      />
      {/* b1 hook en el MISMO mundo premium (PremiumStage) que las graficas
          aprobadas: texto cinetico sincronizado a la voz, acento esmeralda en las
          palabras clave. Un solo plano coherente para todo el reel. */}
      <Composition
        id="KineticTextPremium"
        component={KineticTextPremium}
        calculateMetadata={dyn(100) as never}
        durationInFrames={100}
        fps={30}
        width={1080}
        height={1920}
      />
      {/* b7 cierre/CTA en el MISMO mundo premium (PremiumStage). Reemplaza la
          version IglooStage (CtaClose). bookmark dorado que late + "El que
          AGUANTA, gana." + sub gancho del siguiente video. */}
      <Composition
        id="CtaClosePremium"
        component={CtaClosePremium}
        calculateMetadata={dyn(120) as never}
        durationInFrames={120}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          text: "El que aguanta, gana.",
          boldWord: "aguanta",
          sub: "mañana: cuánto pierde tu aguinaldo guardado en el banco",
          accent: "#00D9A5",
        }}
      />
      {/* Stitch MUDO de coherencia (juzgar EN VIDEO): hook -> mapa -> recovery ->
          holdings. Prueba si el plano establishing full-bleed (mapa) corta
          coherente con los beats sobre el piso iluminado. NO es el corte final
          (sin voz/xfade; eso vive en build916.py). */}
      <Composition
        id="ReelCoherencePreview"
        component={ReelCoherencePreview}
        durationInFrames={COHERENCE_TOTAL}
        fps={30}
        width={1080}
        height={1920}
      />
      {/* Showcase del hero 3D bespoke (Blender -> WebM alpha) sobre la StudioScene.
          NO es un beat (sin prefijo "Beat" => el validador no lo castea); es la
          evidencia R1 del lane hero custom in-script para el gate de Manuel. */}
      <Composition
        id="HeroCoin3D"
        component={HeroCoin3D}
        durationInFrames={90}
        fps={30}
        width={1080}
        height={1920}
      />
      {/* GlobeHero — opener "globo terrAqueo" (look biblia igloo.inc, negro mate)
          que ANCLA el lugar antes de los nUmeros. Reusa la geografIa 50m + bandera
          real de MapZoom. NO es un beat (sin prefijo "Beat" => el validador no lo
          castea); es el prototipo $0 de direcciOn del hero El Salvador. */}
      <Composition
        id="GlobeHero"
        component={GlobeHero}
        durationInFrames={90}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          countryName: "El Salvador",
          iso2: "SV",
          label: "EL SALVADOR",
          lon: -88.8965,
          lat: 13.7942,
          scale: 470,
        }}
      />
      {/* GlobeHero3D — el MISMO opener pero en 3D-CG real (R3F via @remotion/three):
          esfera obsidiana/vidrio, atmOsfera Fresnel azul fria, El Salvador encendido
          en brasa con bloom. Geografia 50m real horneada en textura equirectangular.
          Tier igloo.inc "wow". $0 (render local). */}
      <Composition
        id="GlobeHero3D"
        component={GlobeHero3D}
        durationInFrames={90}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          countryName: "El Salvador",
          iso2: "SV",
          label: "EL SALVADOR",
          lon: -88.8965,
          lat: 13.7942,
        }}
      />
      {/* ElSalvadorMapHero — DESTINO real: mapa vectorial a escala de pais.
          El Salvador = silueta protagonista encendida en brasa, vecinos en
          obsidiana para contexto, bandera + nombre. "mapa = codigo". $0. */}
      <Composition
        id="ElSalvadorMapHero"
        component={ElSalvadorMapHero}
        calculateMetadata={dyn(100) as never}
        durationInFrames={100}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          countryName: "El Salvador",
          iso2: "SV",
          label: "EL SALVADOR",
        }}
      />
      {/* Firma de marca (§5.8) — OVERLAY, NO un beat (sin prefijo "Beat" => el
          validador no lo castea). preview:true dibuja un backdrop oscuro para
          juzgar tamaño/posicion/sutileza en R1. mascot:"" => placeholder $0. */}
      <Composition
        id="BrandSignature"
        component={BrandSignature}
        durationInFrames={120}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          mascot: "",
          wordmark: "DINERO LATAM",
          placement: "tl" as const,
          preview: true,
        }}
      />
      <Composition
        id="StoryHook"
        component={StoryHook}
        calculateMetadata={dyn(180) as never}
        durationInFrames={180}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          kicker: "DINERO LATAM",
          question: "¿Cada cuánto se duplica tu dinero?",
          accentWords: ["duplica"],
          punch: "×2",
          cta: "la fórmula, en el post de hoy",
        }}
      />
      <Composition
        id="BeatLineChart"
        component={LineChartFx}
        calculateMetadata={dyn(160) as never}
        durationInFrames={160}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          caption: "el Bitcoin subió 8 meses seguidos",
          points: [18, 26, 23, 34, 31, 47, 44, 62, 78, 96, 71, 52, 38, 30],
          peakIndex: 9,
          labels: [
            { text: "$43,200", index: 3 },
            { text: "$69,000", index: 7 },
            { text: "-$38,000", index: 12, color: "#FF6B6B" },
          ],
          peakLabel: "+$108,000",
        }}
      />
      {/* BeatLineChartPremium — la MISMA grafica/data (BTC) reconstruida sobre el
          KIT compartido + PremiumStage. Antes/despues honesto vs BeatLineChart
          para el gate de Manuel del nuevo look. Sin withSeams (beat limpio). */}
      <Composition
        id="BeatLineChartPremium"
        component={LineChartPremium}
        calculateMetadata={dyn(160) as never}
        durationInFrames={160}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          caption: "el Bitcoin subió 8 meses seguidos",
          points: [18, 26, 23, 34, 31, 47, 44, 62, 78, 96, 71, 52, 38, 30],
          peakIndex: 9,
          labels: [
            { text: "$43,200", index: 3 },
            { text: "$69,000", index: 7 },
            { text: "-$38,000", index: 12, color: "#FF6B6B" },
          ],
          peakLabel: "+$108,000",
        }}
      />
      {/* BeatRealValueMelt — centerpiece data-viz PREMIUM (look-test 2026-06-26):
          el "efecto tijera" del plazo fijo argentino sobre el escenario VIVO
          (PremiumStage). Datos EXACTOS jun 2026 (verificar a la fecha de lanzar).
          Sin withSeams para juzgar el beat limpio. */}
      <Composition
        id="BeatRealValueMelt"
        component={RealValueMelt}
        calculateMetadata={dyn(150) as never}
        durationInFrames={150}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          caption: "pusiste un millón en un plazo fijo a un año",
          currency: "$",
          principal: 1000000,
          nominalEnd: 1211300,
          realEnd: 909400,
          teaTag: "plazo fijo +21%",
          inflTag: "el plazo fijo no le ganó a la inflación del 33%",
          nominalLabel: "te devuelve el banco",
          realLabel: "te alcanza en el súper",
          punch: "−9,1% de poder de compra",
        }}
      />
      <Composition
        id="BeatPictogram"
        component={PictogramFx}
        calculateMetadata={dyn(150) as never}
        durationInFrames={150}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          caption: "¿cuántos mexicanos invierten su dinero?",
          count: 21,
          total: 100,
          statSuffix: "de cada 100",
        }}
      />
      <Composition id="MapZoomEditorial" component={MapZoomEditorial as never} durationInFrames={130} fps={30} width={1080} height={1920} defaultProps={{} as never} />
      <Composition id="BtcShowcase" component={BtcShowcase as never} durationInFrames={150} fps={30} width={1080} height={1920} defaultProps={{} as never} />
      <Composition id="Logo" component={Logo as never} durationInFrames={1} fps={30} width={1080} height={1920} defaultProps={{ variant: "sheet", bg: "paper" } as never} />
      <Composition id="LogoWordmark" component={Logo as never} durationInFrames={1} fps={30} width={1500} height={420} defaultProps={{ variant: "wordmark", bg: "transparent" } as never} />
      <Composition id="StyleHero" component={StyleHero as never} durationInFrames={130} fps={30} width={1080} height={1920} defaultProps={{ variant: "a" } as never} />
      <Composition id="LottieHero" component={LottieHero as never} durationInFrames={120} fps={30} width={1080} height={1920} defaultProps={{ src: "lottie/lf20_5n8yfkac.json" } as never} />
      <Composition id="TypeAB" component={TypeAB as never} durationInFrames={110} fps={30} width={1080} height={1920} defaultProps={{ variant: "thin" } as never} />
      <Composition id="NewsHook" component={NewsHook as never} durationInFrames={400} fps={30} width={1080} height={1920} defaultProps={{} as never} />
      <Composition id="Reveal" component={Reveal as never} durationInFrames={400} fps={30} width={1080} height={1920} defaultProps={{} as never} />
      <Composition id="TrendLine" component={TrendLine as never} durationInFrames={400} fps={30} width={1080} height={1920} defaultProps={{} as never} />
      <Composition id="CardHook" component={CardHook as never} durationInFrames={356} fps={30} width={1080} height={1920} defaultProps={{} as never} />
      <Composition id="MinPayFeel" component={MinPayFeel as never} durationInFrames={278} fps={30} width={1080} height={1920} defaultProps={{} as never} />
      <Composition id="DebtTimeline" component={DebtTimeline as never} durationInFrames={383} fps={30} width={1080} height={1920} defaultProps={{} as never} />
      <Composition id="CompareBars" component={CompareBars as never} durationInFrames={400} fps={30} width={1080} height={1920} defaultProps={{} as never} />
      <Composition id="ReelClose" component={ReelClose as never} durationInFrames={420} fps={30} width={1080} height={1920} defaultProps={{} as never} />
      <Composition id="WaffleReveal" component={WaffleReveal as never} durationInFrames={70} fps={30} width={1080} height={1920} defaultProps={{ highlight: 20, headline: "SOLO 20 DE 100", sub: "ahorra para su retiro" } as never} />
      <Composition id="ShockNumber" component={ShockNumber as never} durationInFrames={300} fps={30} width={1080} height={1920} defaultProps={{ target: 730, prefix: "-$", valence: "loss", kicker: "LO QUE PIERDES", caption: "cada año, sin invertir" } as never} />
      <Composition id="ScaleReveal" component={ScaleReveal as never} durationInFrames={95} fps={30} width={1080} height={1920} defaultProps={{} as never} />
      <Composition id="PhotoHero" component={PhotoHero as never} durationInFrames={130} fps={30} width={1080} height={1920} defaultProps={{ photo: "photos/trump.jpg" } as never} />
      <Composition id="RiveHero" component={RiveHero as never} durationInFrames={90} fps={30} width={1080} height={1920} defaultProps={{ src: "rive/vehicles.riv" } as never} />
      <Composition id="EChartsHero" component={EChartsHero as never} durationInFrames={120} fps={30} width={1080} height={1920} defaultProps={{ variant: "area", theme: "light" } as never} />
      <Composition
        id="EditorialReel"
        component={EditorialReel as never}
        durationInFrames={600}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{ edition: "INFORME · 2026", source: "Dinero IA", scenes: [] as never }}
        calculateMetadata={({ props }: { props: { scenes: { durF: number }[] } }) => ({
          durationInFrames: Math.max(1, props.scenes.reduce((a, s) => a + (s.durF || 0), 0)),
        })}
      />
      <Composition
        id="EditorialHouseMotion"
        component={EditorialHouseMotion}
        durationInFrames={165}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{}}
      />
      <Composition
        id="EditorialHouse"
        component={EditorialHouse}
        durationInFrames={1}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{}}
      />
      <Composition
        id="StyleProbe"
        component={StyleProbe}
        durationInFrames={1}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{ variant: "editorial" as const }}
      />
      <Composition
        id="Ref0x100xOrb"
        component={Ref0x100xOrb}
        durationInFrames={75}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{ caption: "Then the market" }}
      />
      <Composition
        id="SigErosionHero"
        component={SigErosionHero}
        durationInFrames={90}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          plate: "erosion_plate.mp4",
          kicker: "SI LO DEJAS EN EFECTIVO",
          currency: "$",
          from: 100000,
          to: 96209,
          unit: "MXN",
          lossLabel: "se lo comió la inflación",
          contextLabel: "inflación 3.94% · 12 meses",
        }}
      />
      <Composition
        id="SigErosion"
        component={SigErosion}
        durationInFrames={110}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          kicker: "EN EFECTIVO",
          currency: "$",
          from: 100000,
          to: 96209,
          unit: "MXN",
          lossLabel: "es lo que de verdad te queda",
          contextLabel: "inflación 3.94% · 12 meses",
        }}
      />
      <Composition
        id="BeatBigNumber"
        component={BigNumberFx}
        calculateMetadata={dyn(120) as never}
        durationInFrames={120}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          caption: "la inflación se comió de tu sueldo",
          prefix: "$",
          value: 18400,
          suffix: " MXN",
          decimals: 0,
          subline: "en los últimos 12 meses",
        }}
      />
      <Composition
        id="BeatBars"
        component={BarsFx}
        calculateMetadata={dyn(140) as never}
        durationInFrames={140}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          caption: "lo que paga $10,000 en un año",
          bars: [
            { label: "Débito", value: 12 },
            { label: "Pagaré banco", value: 480 },
            { label: "Fondo gub.", value: 980, highlight: true },
          ],
          prefix: "$",
          suffix: "",
        }}
      />
      <Composition
        id="BeatAssetCard"
        component={AssetCardFx}
        calculateMetadata={dyn(160) as never}
        durationInFrames={160}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          caption: "julio de 2021",
          name: "Alphabet",
          ticker: "NASDAQ · GOOGL",
          logo: "google",
          spark: [56, 58, 60, 55, 61, 65, 71, 58, 71, 74, 81, 87, 91, 103, 117, 122, 134.73],
          priceLabel: "precio por acción",
          priceValue: 134.73,
          pricePrefix: "$",
          priceDecimals: 2,
          subline: "$10,000 USD = 74 acciones",
        }}
      />
      <Composition
        id="BeatTrendBreak"
        component={TrendBreakFx}
        calculateMetadata={dyn(180) as never}
        durationInFrames={180}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          caption: "y entonces llegó 2022",
          points: [134.73, 144.7, 133.68, 148.05, 141.9, 144.85, 135.3, 135.06, 139.07, 114.11, 113.76, 108.96, 116.32, 108.22, 95.65, 94.51, 100.99, 88.23],
          peakIndex: 3,
          counterLabel: "tu inversión",
          countFrom: 10989,
          countTo: 6549,
          countPrefix: "$",
          pctLabel: "−40%",
          peakLabel: "$148",
          troughLabel: "$88",
        }}
      />
      <Composition
        id="BeatVersus"
        component={VersusFx}
        calculateMetadata={dyn(180) as never}
        durationInFrames={180}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          caption: "$10,000 USD a cada una · julio 2021",
          left: {
            name: "Apple",
            ticker: "NASDAQ · AAPL",
            logo: "apple",
            value: 20268,
            tag: "×2.0",
          },
          right: {
            name: "Nvidia",
            ticker: "NASDAQ · NVDA",
            logo: "nvidia",
            value: 105061,
            tag: "×10.5",
          },
          prefix: "$",
          winner: "right",
        }}
      />
      <Composition
        id="BeatTimeline"
        component={TimelineFx}
        calculateMetadata={dyn(300) as never}
        durationInFrames={300}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          caption: "FTX · auge y colapso",
          nodes: [
            { year: "2019", title: "nace FTX, el casino cripto", tone: "white" },
            { year: "ene 2022", title: "valuación récord", amount: "$32,000 M USD", tone: "green" },
            { year: "nov 2022", title: "colapso en 72 horas", amount: "−$8,000 M USD", tone: "red" },
            { year: "mar 2024", title: "Sam Bankman-Fried", amount: "25 años de prisión", tone: "gold" },
          ],
          growFrames: [30, 100, 180, 250],
        }}
      />
      <Composition
        id="BeatBarRace"
        component={BarRaceFx}
        calculateMetadata={dyn(300) as never}
        durationInFrames={300}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          caption: "$250 USD al mes · 10% anual",
          monthly: 250,
          rate: 0.1,
          ageStart: 25,
          ageEnd: 65,
          racers: [
            { label: "empiezas a los 25", startAge: 25, tag: "40 años" },
            { label: "a los 35", startAge: 35, tag: "30 años" },
            { label: "a los 45", startAge: 45, tag: "20 años" },
          ],
          prefix: "$",
          winnerIndex: 0,
          countEndFrame: 240,
          pulseFrames: [260, 280],
        }}
      />
      <Composition
        id="BeatKinetic"
        component={KineticFx}
        calculateMetadata={dyn(100) as never}
        durationInFrames={100}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          lines: [
            [{ text: "tu banco" }, { text: "gana" }],
            [{ text: "con tu" }, { text: "dinero", accent: true }],
            [{ text: "tú no" }],
          ],
        }}
      />
      <Composition
        id="BeatMapZoom"
        component={MapZoomFx}
        calculateMetadata={dyn(150) as never}
        durationInFrames={150}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          countryName: "El Salvador",
          iso2: "SV",
          caption: "el país de la apuesta",
          label: "El Salvador",
          sublabel: "6.3 millones de personas",
        }}
      />
      <Composition
        id="BeatRecovery"
        component={RecoveryFx}
        calculateMetadata={dyn(160) as never}
        durationInFrames={160}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          caption: "Bitcoin: el desplome y la recuperación",
          points: [44739, 52000, 47000, 38000, 31000, 22000, 19000, 16000, 21000, 27000, 30000, 38000, 45000, 52000, 58000, 64089],
          troughIndex: 7,
          troughLabel: "$16,000",
          endLabel: "$64,000",
        }}
      />
      <Composition
        id="BeatDonut"
        component={DonutFx}
        calculateMetadata={dyn(150) as never}
        durationInFrames={150}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          caption: "de cada dólar que factura Apple",
          segments: [
            { label: "iPhone", value: 52 },
            { label: "Servicios", value: 24 },
            { label: "Mac", value: 10 },
            { label: "iPad", value: 8 },
            { label: "Otros", value: 6 },
          ],
          highlightIndex: 1,
          centerLabel: "Servicios",
        }}
      />
      <Composition
        id="BeatWaterfall"
        component={WaterfallFx}
        calculateMetadata={dyn(180) as never}
        durationInFrames={180}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          caption: "a dónde se va tu sueldo de $30,000",
          startLabel: "Sueldo",
          startValue: 30000,
          steps: [
            { label: "Renta", delta: -9000 },
            { label: "Comida", delta: -6000 },
            { label: "Transporte", delta: -3000 },
            { label: "Deudas", delta: -4500 },
          ],
          endLabel: "Te queda",
          prefix: "$",
        }}
      />
      <Composition
        id="BeatBubble"
        component={BubbleFx}
        calculateMetadata={dyn(170) as never}
        durationInFrames={170}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          caption: "las empresas más valiosas del mundo",
          bubbles: [
            { label: "Apple", value: 3.4e12, logo: "apple" },
            { label: "Nvidia", value: 3.3e12, logo: "nvidia" },
            { label: "Microsoft", value: 3.1e12, logo: "microsoft" },
            { label: "Alphabet", value: 2.1e12, logo: "google" },
            { label: "Amazon", value: 2.0e12, logo: "amazon" },
          ],
          prefix: "$",
          valueScale: 1e12,
          valueUnit: "T",
        }}
      />
      <Composition
        id="BeatCandlestick"
        component={CandlestickFx}
        calculateMetadata={dyn(170) as never}
        durationInFrames={170}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          caption: "el precio del Bitcoin en 2024",
          candles: [
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
          ],
          prefix: "$",
          readoutLabel: "cierre",
          highlightLast: true,
        }}
      />
      <Composition
        id="BeatCharacter"
        component={CharacterFx}
        calculateMetadata={dyn(150) as never}
        durationInFrames={150}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          imageSlug: "bukele",
          name: "Nayib Bukele",
          role: "Presidente de El Salvador",
          quote: "Compramos 1 Bitcoin al día",
        }}
      />
      <Composition
        id="BeatNewsCard"
        component={NewsCardFx}
        calculateMetadata={dyn(170) as never}
        durationInFrames={170}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          caption: "esta mañana",
          source: "Bloomberg",
          handle: "@business",
          sourceSlug: "bloomberg",
          headline: "El Salvador supera los $700 millones en Bitcoin",
          goldWords: ["$700", "millones"],
          dateLabel: "13 jun · 08:14",
          badge: "Última hora",
          verified: true,
        }}
      />
      <Composition
        id="BeatMultiMap"
        component={MultiMapFx}
        calculateMetadata={dyn(170) as never}
        durationInFrames={170}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          caption: "adopción cripto en la región",
          title: "Bitcoin en LATAM",
          sublabel: "4 países, una sola apuesta",
          scale: 360,
          countries: [
            { name: "El Salvador", iso2: "SV" },
            { name: "Argentina", iso2: "AR" },
            { name: "Brazil", iso2: "BR", label: "Brasil" },
            { name: "Mexico", iso2: "MX", label: "México" },
          ],
        }}
      />
      <Composition
        id="BeatLogoWall"
        component={LogoWallFx}
        calculateMetadata={dyn(150) as never}
        durationInFrames={150}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          caption: "ya aceptan pagos cripto",
          title: "Las marcas que se subieron",
          columns: 3,
          logos: [
            { slug: "tesla", label: "Tesla" },
            { slug: "paypal", label: "PayPal" },
            { slug: "starbucks", label: "Starbucks" },
            { slug: "microsoft", label: "Microsoft" },
            { slug: "visa", label: "Visa" },
            { slug: "mastercard", label: "Mastercard" },
          ],
        }}
      />
      <Composition
        id="BeatDebate"
        component={DebateFx}
        calculateMetadata={dyn(200) as never}
        durationInFrames={200}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          topic: "¿Bitcoin como moneda de curso legal?",
          left: {
            imageSlug: "bukele",
            name: "A favor",
            quote: "Es libertad financiera para el pueblo",
          },
          right: {
            imageSlug: "economista",
            name: "En contra",
            quote: "Demasiado volátil para ahorrar",
          },
        }}
      />
      <Composition
        id="BeatHeroCoin"
        component={HeroCoinFx}
        calculateMetadata={dyn(150) as never}
        durationInFrames={150}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          caption: "1 Bitcoin al día",
          label: "reserva nacional acumulada",
          value: 6089,
          prefix: "",
          suffix: " BTC",
          decimals: 0,
          subline: "comprado en plena caída",
        }}
      />
      {/* BeatHeroShot — el beat que SE MUEVE: clip i2v (still gpt-image-1 +
          movimiento Kling) a pantalla completa + kicker-gancho opcional. El clip
          vive en public/i2v/<clip>.mp4 (build916.ensure_moving_clips lo copia
          desde out/_i2v, $0). Es la FIRMA del canal (1-2 por video, hook/acento). */}
      <Composition
        id="BeatHeroShot"
        component={MovingHeroFx}
        calculateMetadata={dyn(150) as never}
        durationInFrames={150}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          clip: "b1_hero_colchon",
          photo: "",
          kicker: "Antes de invertir, necesitas esto",
          accentColor: "#00D9A5",
        }}
      />
      {/* BeatMovingData — ARQUITECTURA NUEVA (rechazo Manuel 2026-06-26): un mundo
          i2v caricatura-fino EN MOVIMIENTO de lecho a pantalla completa + la data
          EXACTA compuesta encima en codigo (nunca pantalla plana con numero quieto).
          Slice de prueba concepto-colchon: b3 build -> b4 timeline -> b5 climax. */}
      <Composition
        id="BeatColchonB3"
        component={MovingDataFx}
        calculateMetadata={dyn(240) as never}
        durationInFrames={240}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          clip: "colchon_b3",
          kind: "build",
          caption: "Así se infla tu colchón",
          prefix: "$",
          suffix: " MXN",
          accentColor: "#D4A574",
          steps: [
            { label: "empezar", value: 15000 },
            { label: "real", value: 45000 },
            { label: "sólida", value: 90000 },
          ],
          meterLabel: "Tu fondo de emergencia",
        }}
      />
      <Composition
        id="BeatColchonB4"
        component={MovingDataFx}
        calculateMetadata={dyn(220) as never}
        durationInFrames={220}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          clip: "colchon_b4",
          kind: "timeline",
          caption: "En 6 meses está lista",
          nodes: [
            { label: "Mes 1", tone: "white" },
            { label: "Mes 3", tone: "green" },
            { label: "Mes 6", tone: "gold" },
          ],
        }}
      />
      <Composition
        id="BeatColchonB5"
        component={MovingDataFx}
        calculateMetadata={dyn(240) as never}
        durationInFrames={240}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          clip: "colchon_b5",
          kind: "climax",
          caption: "Meta del fondo",
          prefix: "$",
          suffix: " MXN",
          accentColor: "#D4A574",
          value: 90000,
          subline: "6 meses × $15,000 MXN",
        }}
      />
      {/* BeatColchonB5Premium — REPLANTEO del lenguaje data-viz (rechazo Manuel
          2026-06-26: el overlay plano estaba "dramaticamente aburrido"). Misma
          data/lecho que BeatColchonB5, pero la cifra vive INTEGRADA al mundo i2v:
          cuenta atada a la caida, barrido especular al aterrizar, luz dorada en
          escena, pulso del colchon, grade unico. landFrame=180 (t6.0 = contacto
          con el colchon, verificado en pixeles). Sin withSeams (beat limpio). */}
      <Composition
        id="BeatColchonB5Premium"
        component={MovingDataPremium}
        calculateMetadata={dyn(240) as never}
        durationInFrames={240}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          clip: "colchon_b5",
          kicker: "Meta del fondo",
          prefix: "$",
          suffix: " MXN",
          accentColor: "#D4A574",
          value: 90000,
          subline: "6 meses × $15,000 MXN",
          landFrame: 180,
        }}
      />
      <Composition
        id="BeatNapkin"
        component={NapkinFx}
        calculateMetadata={dyn(160) as never}
        durationInFrames={160}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          napkin: "napkin_2",
          promise: "tu dinero se duplica en…",
          formula: "72 ÷ %  =  años",
        }}
      />
      <Composition
        id="BeatNewspaper"
        component={NewspaperFx}
        calculateMetadata={dyn(170) as never}
        durationInFrames={170}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          paper: "",
          kicker: "ÚLTIMA HORA",
          headline: "El Salvador rompe su récord en Bitcoin",
          stat: "$700M",
          nameplate: "LATAM TIMES",
          dateline: "Hoy",
        }}
      />
      <Composition
        id="BeatPhone"
        component={PhoneFx}
        calculateMetadata={dyn(150) as never}
        durationInFrames={150}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          phone: "",
          appName: "CetesDirecto",
          screenLabel: "saldo disponible",
          amount: "$12,480",
        }}
      />
      <Composition
        id="BeatChalkboard"
        component={ChalkboardFx}
        calculateMetadata={dyn(190) as never}
        durationInFrames={190}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          board: "",
          title: "el interés compuesto",
          steps: ["inviertes $1,000", "10% cada año", "en 30 años → $17,449"],
          accentStep: 2,
        }}
      />
      <Composition
        id="BeatTicket"
        component={TicketFx}
        calculateMetadata={dyn(170) as never}
        durationInFrames={170}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          ticket: "",
          store: "CAFÉ DIARIO",
          items: [
            { label: "latte grande", price: "$75" },
            { label: "x 30 días", price: "" },
          ],
          totalLabel: "AL MES",
          total: "$2,250",
        }}
      />
      <Composition
        id="BeatStackedArea"
        component={StackedAreaFx}
        calculateMetadata={dyn(170) as never}
        durationInFrames={170}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          caption: "de dónde sale el ahorro que acumulas",
          series: [
            { label: "Aportación", values: [200, 420, 660, 920, 1200, 1500] },
            { label: "Interés", values: [5, 22, 58, 120, 215, 350] },
            { label: "Patrón", values: [100, 210, 330, 460, 600, 750] },
          ],
          xLabels: ["Año 1", "Año 2", "Año 3", "Año 4", "Año 5", "Año 6"],
          highlightIndex: 1,
          prefix: "$",
        }}
      />
      <Composition
        id="BeatDialGauge"
        component={DialGaugeFx}
        calculateMetadata={dyn(150) as never}
        durationInFrames={150}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          caption: "qué tan caro está el mercado hoy",
          value: 38,
          min: 0,
          max: 100,
          label: "índice miedo / codicia",
          suffix: "",
          goodHigh: false,
        }}
      />
      <Composition
        id="BeatSlope"
        component={SlopeFx}
        calculateMetadata={dyn(160) as never}
        durationInFrames={160}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          caption: "tu poder de compra en 4 años",
          leftLabel: "2020",
          rightLabel: "2024",
          items: [
            { label: "Salario", left: 100, right: 118, color: "#00D9A5" },
            { label: "Canasta básica", left: 100, right: 142, color: "#FF6B6B" },
          ],
          prefix: "",
          suffix: "",
        }}
      />
      <Composition
        id="BeatProgressRing"
        component={ProgressRingFx}
        calculateMetadata={dyn(150) as never}
        durationInFrames={150}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          caption: "cuánto de tu deuda ya pagaste",
          percent: 64,
          label: "de $85,000 MXN",
          color: "#00D9A5",
        }}
      />
      <Composition
        id="BeatLollipop"
        component={LollipopFx}
        calculateMetadata={dyn(170) as never}
        durationInFrames={170}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          caption: "brecha salarial entre hombres y mujeres",
          items: [
            { label: "Directivos", value: 58000, value2: 47000 },
            { label: "Ingeniería", value: 42000, value2: 36000 },
            { label: "Ventas", value: 28000, value2: 25000 },
          ],
          prefix: "$",
          legend1: "Hombres",
          legend2: "Mujeres",
        }}
      />
      <Composition
        id="BeatFunnel"
        component={FunnelFx}
        calculateMetadata={dyn(170) as never}
        durationInFrames={170}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          caption: "de cada 100 que abren cuenta de inversión",
          stages: [
            { label: "Abren cuenta", value: 100 },
            { label: "Depositan", value: 62 },
            { label: "Invierten", value: 34 },
            { label: "Siguen al año", value: 11 },
          ],
          suffix: "",
        }}
      />
      <Composition
        id="BeatHistogram"
        component={HistogramFx}
        calculateMetadata={dyn(160) as never}
        durationInFrames={160}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          caption: "cuánto gana la gente en México",
          bins: [8, 22, 41, 58, 47, 30, 18, 10, 6, 3],
          xLabels: ["5k", "10k", "15k", "20k", "25k", "30k", "40k", "50k", "70k", "+90k"],
          markerIndex: 3,
          markerLabel: "tú",
          color: "#00D9A5",
        }}
      />
      <Composition
        id="BeatScaledIcon"
        component={ScaledIconFx}
        calculateMetadata={dyn(150) as never}
        durationInFrames={150}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          caption: "una casa vs lo que ganas en un año",
          items: [
            { label: "Tu sueldo anual", value: 360000 },
            { label: "Casa promedio", value: 2880000 },
          ],
          symbol: "$",
          prefix: "$",
          valueScale: 1000,
          valueUnit: "k",
        }}
      />
      <Composition
        id="BeatHeatmap"
        component={HeatmapFx}
        calculateMetadata={dyn(170) as never}
        durationInFrames={170}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          caption: "rendimiento mes a mes de tu portafolio",
          rows: [
            { label: "2022", values: [-4, 2, -6, 3, -8, -11, 5, -3, -9, 7, 4, -5] },
            { label: "2023", values: [6, 3, -2, 5, 1, 4, 8, -1, -3, 2, 9, 6] },
            { label: "2024", values: [3, 5, 7, -2, 4, 6, 2, 5, 3, 8, 11, 7] },
          ],
          colLabels: ["E", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"],
          diverging: true,
          suffix: "%",
        }}
      />
      <Composition
        id="BeatTickerTape"
        component={TickerTapeFx}
        calculateMetadata={dyn(180) as never}
        durationInFrames={180}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          caption: "los mercados hoy",
          items: [
            { symbol: "AAPL", price: 229.87, changePct: 1.2, logo: "apple" },
            { symbol: "NVDA", price: 131.26, changePct: 3.4, logo: "nvidia" },
            { symbol: "TSLA", price: 248.5, changePct: -2.1, logo: "tesla" },
            { symbol: "BTC", price: 64089, changePct: 0.8, logo: "bitcoin" },
            { symbol: "GOOGL", price: 178.35, changePct: -0.6, logo: "google" },
            { symbol: "META", price: 563.27, changePct: 2.3, logo: "meta" },
          ],
          prefix: "$",
          decimals: 2,
          speed: 1,
        }}
      />
      <Composition
        id="BeatTreemap"
        component={TreemapFx}
        calculateMetadata={dyn(160) as never}
        durationInFrames={160}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          caption: "cómo se reparte un portafolio de $100,000",
          items: [
            { label: "Acciones EU", value: 45000 },
            { label: "Bonos", value: 22000 },
            { label: "Cripto", value: 12000 },
            { label: "Bienes raíces", value: 11000 },
            { label: "Efectivo", value: 6000 },
            { label: "Oro", value: 4000 },
          ],
          prefix: "$",
          valueScale: 1000,
          valueUnit: "k",
        }}
      />
      <Composition
        id="BeatRadar"
        component={RadarFx}
        calculateMetadata={dyn(160) as never}
        durationInFrames={160}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          caption: "dos formas de invertir, comparadas",
          axes: ["Rendimiento", "Riesgo", "Liquidez", "Costo", "Simpleza"],
          series: [
            { label: "Cetes", values: [4, 1, 5, 5, 5] },
            { label: "Acciones", values: [5, 5, 4, 3, 2] },
          ],
          max: 5,
        }}
      />
      <Composition
        id="BeatScoreboard"
        component={ScoreboardFx}
        calculateMetadata={dyn(150) as never}
        durationInFrames={150}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          caption: "tus finanzas este mes",
          cards: [
            { label: "Ingresos", value: 32000, deltaPct: 4.2, prefix: "$", color: "#00D9A5" },
            { label: "Gastos", value: 23500, deltaPct: 6.8, prefix: "$", color: "#5BC0BE", higherIsBetter: false },
            { label: "Ahorro", value: 8500, deltaPct: -2.1, prefix: "$", color: "#F5B544" },
            { label: "Tasa ahorro", value: 27, deltaPct: 1.5, suffix: "%", color: "#5BC0BE" },
          ],
        }}
      />
      <Composition
        id="BeatSankey"
        component={SankeyFx}
        calculateMetadata={dyn(170) as never}
        durationInFrames={170}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          caption: "a dónde se va tu sueldo de $30,000",
          source: { label: "Sueldo", value: 30000 },
          targets: [
            { label: "Renta", value: 9000 },
            { label: "Comida", value: 6000 },
            { label: "Transporte", value: 3000 },
            { label: "Deudas", value: 4500 },
            { label: "Ahorro", value: 7500 },
          ],
          prefix: "$",
        }}
      />
      <Composition
        id="BeatTestimonial"
        component={TestimonialFx}
        calculateMetadata={dyn(180) as never}
        durationInFrames={180}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          caption: "lo dijo en cadena nacional",
          quote: "Compramos 1 Bitcoin al día y nadie nos detiene",
          name: "Nayib Bukele",
          role: "Presidente de El Salvador",
          avatarSlug: "",
          goldWords: ["Bitcoin"],
        }}
      />
      <Composition
        id="BeatStatCallout"
        component={StatCalloutFx}
        calculateMetadata={dyn(150) as never}
        durationInFrames={150}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          caption: "el saldo a favor de El Salvador",
          stat: "+$357M",
          statColor: "#00D9A5",
          context: "de ganancia en su reserva de Bitcoin a precios de hoy",
        }}
      />
      <Composition
        id="BeatCta"
        component={CtaFx}
        calculateMetadata={dyn(120) as never}
        durationInFrames={120}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          text: "Guarda esto antes de que lo necesites",
          boldWord: "Guarda",
          sub: "mañana: cuánto pierde tu aguinaldo en el banco",
        }}
      />
      <Composition
        id="DineroIAReel"
        component={DineroIAReel}
        durationInFrames={1500}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          title: "La IA que negocia tu salario",
          script_beats: [
            { text: "Hace 3 meses,", start_frame: 90, end_frame: 150 },
            { text: "Claude renegoció", start_frame: 150, end_frame: 240 },
            { text: "el sueldo de Ana.", start_frame: 240, end_frame: 330 },
            { text: "Resultado:", start_frame: 330, end_frame: 390 },
            { text: "+$8,000 MXN/mes.", start_frame: 390, end_frame: 480 },
          ],
          voice_audio_url: "",
          music_audio_url: null,
          accent_color: "#00D9A5",
        }}
      />
      <StoryboardLabCompositions />
    </>
  );
};
