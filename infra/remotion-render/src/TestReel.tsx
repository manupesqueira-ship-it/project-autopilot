import React from "react";
import {
  AbsoluteFill,
  interpolate,
  Sequence,
  useCurrentFrame,
} from "remotion";
import { theme } from "./theme";
import { NewsCard } from "./beats/NewsCard";
import { StatCallout } from "./beats/StatCallout";
import { MultiMap } from "./beats/MultiMap";
import { DebateCards } from "./beats/DebateCards";
import { LogoWall } from "./beats/LogoWall";
import { Testimonial } from "./beats/Testimonial";
import { HeroCoin } from "./beats/HeroCoin";

// Reel de PRUEBA (no es entrega): encadena los visuales narrativos nuevos en una
// sola composicion con crossfade real (Sequences solapadas + rampa de opacidad).
// $0, self-contained, NO toca build916/guiones. Tema fresco: stablecoins en LATAM.
const OVERLAP = 12;

type Scene = { node: React.ReactNode; dur: number };

const FadeWrap: React.FC<React.PropsWithChildren<{ dur: number }>> = ({
  dur,
  children,
}) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(
    frame,
    [0, 10, dur - 10, dur],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );
  return <AbsoluteFill style={{ opacity }}>{children}</AbsoluteFill>;
};

export const TestReel: React.FC = () => {
  const scenes: Scene[] = [
    {
      dur: 100,
      node: (
        <NewsCard
          caption="Finanzas LATAM"
          source="Bloomberg"
          sourceSlug="bloomberg"
          handle="@business"
          badge="DE ÚLTIMA HORA"
          dateLabel="Hoy"
          verified
          headline="El dólar digital ya mueve $5 billones al año"
          goldWords={["$5", "billones"]}
        />
      ),
    },
    {
      dur: 95,
      node: (
        <StatCallout
          caption="Crecimiento en Argentina"
          stat="+340%"
          statColor={theme.green}
          context="creció el uso de stablecoins en un año"
          accentColor={theme.green}
        />
      ),
    },
    {
      dur: 112,
      node: (
        <MultiMap
          caption="Quién lo está adoptando"
          title="El dólar digital en la región"
          countries={[
            { name: "Argentina", iso2: "AR", label: "Argentina" },
            { name: "Mexico", iso2: "MX", label: "México" },
            { name: "Brazil", iso2: "BR", label: "Brasil" },
          ]}
        />
      ),
    },
    {
      dur: 135,
      node: (
        <DebateCards
          topic="¿El dólar digital reemplaza al peso?"
          left={{
            imageSlug: "bukele",
            name: "A favor",
            quote: "Protege tus ahorros de la inflación",
          }}
          right={{
            imageSlug: "economista",
            name: "En contra",
            quote: "Le quita soberanía a tu país",
          }}
        />
      ),
    },
    {
      dur: 95,
      node: (
        <LogoWall
          caption="Ya aceptan pagos cripto"
          title="Quién ya lo integra"
          logos={[
            { slug: "visa", label: "Visa" },
            { slug: "mastercard", label: "Mastercard" },
            { slug: "paypal", label: "PayPal" },
            { slug: "stripe", label: "Stripe" },
            { slug: "mercadopago", label: "Mercado Pago" },
            { slug: "nubank", label: "Nubank" },
          ]}
        />
      ),
    },
    {
      dur: 125,
      node: (
        <Testimonial
          caption="Lo que dicen los expertos"
          quote="El que ahorra en dólar digital no le teme a la inflación"
          goldWords={["dólar", "digital"]}
          name="Banco Mundial"
          role="Informe 2025"
          avatarSlug="worldbank"
        />
      ),
    },
    {
      dur: 110,
      node: (
        <HeroCoin
          caption="El dólar que no se devalúa"
          label="en circulación hoy"
          value={5}
          prefix="$"
          suffix=" billones"
          decimals={0}
          subline="y subiendo cada mes"
        />
      ),
    },
  ];

  let cursor = 0;
  return (
    <AbsoluteFill style={{ backgroundColor: "#070A0F" }}>
      {scenes.map((s, i) => {
        const from = cursor;
        cursor += s.dur - OVERLAP;
        return (
          <Sequence key={i} from={from} durationInFrames={s.dur}>
            <FadeWrap dur={s.dur}>{s.node}</FadeWrap>
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};

export const TEST_REEL_DURATION = (() => {
  const durs = [100, 95, 112, 135, 95, 125, 110];
  return durs.reduce((a, b) => a + b, 0) - OVERLAP * (durs.length - 1);
})();
