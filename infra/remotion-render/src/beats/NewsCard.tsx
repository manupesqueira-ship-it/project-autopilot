import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { theme } from "../theme";
import { StudioScene } from "../studio/StudioScene";
import { BrandLogo } from "../studio/BrandLogo";

// Tarjeta de noticia / tweet: glass card oscuro (no plantilla blanca generica).
// avatar (logo de la fuente o monograma) + nombre + sello verificado + handle
// mono + titular word-by-word (con palabras clave en oro) + sello de fuente +
// fecha. Pensado para "el medio dijo X" dentro de un reel de finanzas.
export type NewsCardProps = {
  // kicker dim arriba de la tarjeta (opcional)
  caption?: string;
  // nombre visible de la fuente: "Reuters", "Bloomberg", "El Financiero"
  source: string;
  // @handle (se muestra en mono dim). default = derivado del source
  handle?: string;
  // slug simple-icons para el avatar (p.ej. "bloomberg"); si falta -> monograma
  sourceSlug?: string;
  // titular de la noticia
  headline: string;
  // palabras del titular que van en oro (montos/cifras). match exacto por token
  goldWords?: string[];
  // sello de fecha/hora en mono dim
  dateLabel?: string;
  // chip "DE ULTIMA HORA" / "OFICIAL"; si falta no se muestra
  badge?: string;
  verified?: boolean;
  accentColor?: string;
};

const CX = 100;
const CW = 880;
const CY = 430;
const PAD = 70;

const VerifiedTick: React.FC<{ size: number; color: string }> = ({
  size,
  color,
}) => (
  <svg width={size} height={size} viewBox="0 0 24 24">
    <path
      fill={color}
      d="M12 1.6 14.5 0l1.9 2.3 3 .2.2 3 2.3 1.9-1.6 2.5 1.6 2.5-2.3 1.9-.2 3-3 .2L14.5 24 12 22.4 9.5 24l-1.9-2.3-3-.2-.2-3L2.1 16.6 3.7 14 2.1 11.5l2.3-1.9.2-3 3-.2L9.5 0 12 1.6Z"
    />
    <path
      fill="#0D1117"
      d="m10.6 15.6-2.7-2.7 1.3-1.3 1.4 1.4 3.9-3.9 1.3 1.3-5.2 5.2Z"
    />
  </svg>
);

export const NewsCard: React.FC<NewsCardProps> = ({
  caption,
  source,
  handle,
  sourceSlug,
  headline,
  goldWords = [],
  dateLabel,
  badge,
  verified = true,
  accentColor = theme.green,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const clamp = {
    extrapolateLeft: "clamp" as const,
    extrapolateRight: "clamp" as const,
  };

  const enter = spring({ frame: frame - 4, fps, config: { damping: 14, mass: 0.8 } });
  const breathe = Math.sin(frame / 14) * 4;

  const goldSet = React.useMemo(
    () => new Set(goldWords.map((w) => w.toLowerCase())),
    [goldWords],
  );
  const tokens = headline.split(" ");
  const HEAD_START = 22;
  const STEP = 3;

  const at = handle ?? "@" + source.toLowerCase().replace(/[^a-z0-9]+/g, "");

  return (
    <StudioScene spotlightColor={accentColor}>
      <AbsoluteFill style={{ fontFamily: theme.font }}>
        {caption && (
          <div
            style={{
              position: "absolute",
              top: 290,
              width: "100%",
              textAlign: "center",
              fontSize: 36,
              fontWeight: 600,
              letterSpacing: "0.04em",
              textTransform: "uppercase",
              color: theme.textDim,
              opacity: interpolate(frame, [2, 12], [0, 1], clamp),
            }}
          >
            {caption}
          </div>
        )}

        <div
          style={{
            position: "absolute",
            left: CX,
            top: CY,
            width: CW,
            borderRadius: 44,
            background:
              "linear-gradient(165deg, rgba(255,255,255,0.085) 0%, rgba(255,255,255,0.035) 55%, rgba(255,255,255,0.06) 100%)",
            border: "1.5px solid rgba(255,255,255,0.15)",
            boxShadow: `0 30px 80px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.12), 0 0 70px ${accentColor}12`,
            opacity: Math.min(enter * 1.3, 1),
            transform: `translateY(${(1 - enter) * 60 + breathe}px) scale(${0.94 + enter * 0.06})`,
            padding: PAD,
            boxSizing: "border-box",
          }}
        >
          {/* fila identidad: avatar + nombre + verificado + handle */}
          <div style={{ display: "flex", alignItems: "center", gap: 28 }}>
            <div
              style={{
                width: 116,
                height: 116,
                borderRadius: "50%",
                background: "#FFFFFF",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0,
                boxShadow: `0 0 30px rgba(255,255,255,0.18), 0 12px 34px rgba(0,0,0,0.4)`,
              }}
            >
              {sourceSlug ? (
                <BrandLogo slug={sourceSlug} size={70} on="light" />
              ) : (
                <span
                  style={{
                    fontSize: 64,
                    fontWeight: 900,
                    color: "#1A1A1A",
                  }}
                >
                  {source.charAt(0).toUpperCase()}
                </span>
              )}
            </div>
            <div style={{ minWidth: 0, flex: 1 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <span
                  style={{
                    fontSize: 48,
                    fontWeight: 800,
                    color: theme.text,
                    whiteSpace: "nowrap",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                  }}
                >
                  {source}
                </span>
                {verified && <VerifiedTick size={42} color={accentColor} />}
              </div>
              <div
                style={{
                  fontFamily: theme.mono,
                  fontSize: 30,
                  fontWeight: 500,
                  color: theme.textDim,
                  letterSpacing: "0.04em",
                  marginTop: 4,
                }}
              >
                {at}
              </div>
            </div>
            {badge && (
              <div
                style={{
                  alignSelf: "flex-start",
                  fontSize: 22,
                  fontWeight: 800,
                  letterSpacing: "0.1em",
                  // badge "ultima hora" = acento DORADO, NO rojo (rojo = SOLO perdida)
                  color: theme.gold,
                  border: `2px solid ${theme.gold}`,
                  borderRadius: 999,
                  padding: "8px 18px",
                  textTransform: "uppercase",
                  whiteSpace: "nowrap",
                  opacity: 0.7 + Math.sin(frame / 8) * 0.3,
                }}
              >
                {badge}
              </div>
            )}
          </div>

          {/* separador */}
          <div
            style={{
              height: 1.5,
              background:
                "linear-gradient(90deg, transparent, rgba(255,255,255,0.18), transparent)",
              margin: "44px 0 40px",
            }}
          />

          {/* titular word-by-word */}
          <div
            style={{
              fontSize: 66,
              fontWeight: 800,
              lineHeight: 1.16,
              letterSpacing: "-0.01em",
              color: theme.text,
            }}
          >
            {tokens.map((w, i) => {
              const o = interpolate(
                frame,
                [HEAD_START + i * STEP, HEAD_START + 6 + i * STEP],
                [0, 1],
                clamp,
              );
              const dy = interpolate(
                frame,
                [HEAD_START + i * STEP, HEAD_START + 8 + i * STEP],
                [10, 0],
                clamp,
              );
              const isGold = goldSet.has(
                w.toLowerCase().replace(/[.,;:¡!¿?"]/g, ""),
              );
              return (
                <span
                  key={i}
                  style={{
                    display: "inline-block",
                    opacity: o,
                    transform: `translateY(${dy}px)`,
                    color: isGold ? theme.gold : theme.text,
                    textShadow: isGold ? `0 0 26px ${theme.gold}55` : "none",
                    marginRight: "0.28em",
                  }}
                >
                  {w}
                </span>
              );
            })}
          </div>

          {/* sello de fuente + fecha */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 16,
              marginTop: 56,
              opacity: interpolate(
                frame,
                [HEAD_START + tokens.length * STEP + 4, HEAD_START + tokens.length * STEP + 16],
                [0, 1],
                clamp,
              ),
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 12,
                background: `${accentColor}1c`,
                border: `1.5px solid ${accentColor}55`,
                borderRadius: 999,
                padding: "10px 22px",
              }}
            >
              <div
                style={{
                  width: 16,
                  height: 16,
                  borderRadius: "50%",
                  background: accentColor,
                  boxShadow: `0 0 14px ${accentColor}`,
                }}
              />
              <span
                style={{
                  fontFamily: theme.mono,
                  fontSize: 26,
                  fontWeight: 600,
                  letterSpacing: "0.08em",
                  color: theme.text,
                  textTransform: "uppercase",
                }}
              >
                Fuente · {source}
              </span>
            </div>
            {dateLabel && (
              <span
                style={{
                  fontFamily: theme.mono,
                  fontSize: 26,
                  fontWeight: 500,
                  color: theme.textDim,
                  letterSpacing: "0.04em",
                }}
              >
                {dateLabel}
              </span>
            )}
          </div>
        </div>
      </AbsoluteFill>
    </StudioScene>
  );
};
