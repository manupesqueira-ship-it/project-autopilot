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

export type PictogramProps = {
  caption: string;
  count: number;
  total?: number;
  statSuffix: string;
  accent?: string;
};

const Person: React.FC<{ fill: string; glow: boolean; accent: string }> = ({
  fill,
  glow,
  accent,
}) => (
  <g
    style={
      glow
        ? { filter: `drop-shadow(0 0 6px ${accent}) drop-shadow(0 0 16px ${accent}66)` }
        : undefined
    }
  >
    <circle cx={0} cy={-21} r={8.5} fill={fill} />
    <path
      d="M -13.5 -9 Q -13.5 -11.5 -10 -11.5 L 10 -11.5 Q 13.5 -11.5 13.5 -9 L 11 9 L -11 9 Z"
      fill={fill}
    />
    <rect x={-9.5} y={8} width={7.5} height={20} rx={3.5} fill={fill} />
    <rect x={2} y={8} width={7.5} height={20} rx={3.5} fill={fill} />
  </g>
);

export const PictogramPersons: React.FC<PictogramProps> = ({
  caption,
  count,
  total = 100,
  statSuffix,
  accent = theme.green,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const cols = 10;
  const rows = Math.ceil(total / cols);
  const cell = 86;
  const gridW = cols * cell;
  const gridH = rows * cell;
  const gx = (1080 - gridW) / 2 + cell / 2;
  const gy = 640 + cell / 2;

  // 8-38: aparece grid gris · 42-110: se encienden las `count` en verde
  const litCount = Math.floor(
    interpolate(frame, [42, 110], [0, count], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    })
  );

  const capWords = caption.split(" ");
  const numberShown = litCount;
  const numberPop = spring({
    frame: frame - 42,
    fps,
    config: { damping: 14, mass: 0.6 },
  });

  return (
    <StudioScene spotlightColor={accent}>
      <AbsoluteFill style={{ fontFamily: theme.font }}>
        <div
          style={{
            position: "absolute",
            top: 280,
            width: "100%",
            textAlign: "center",
            fontSize: 40,
            fontWeight: 500,
            color: theme.textDim,
          }}
        >
          {capWords.map((w, i) => {
            const o = interpolate(frame, [2 + i * 3, 8 + i * 3], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            });
            return (
              <span key={i} style={{ opacity: o }}>
                {w}{" "}
              </span>
            );
          })}
        </div>

        <div
          style={{
            position: "absolute",
            top: 408,
            width: "100%",
            textAlign: "center",
            opacity: interpolate(frame, [40, 50], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
            transform: `scale(${0.9 + numberPop * 0.1})`,
          }}
        >
          <span
            style={{
              fontSize: 130,
              fontWeight: 900,
              color: accent,
              textShadow: `0 0 40px ${accent}88`,
              fontVariantNumeric: "tabular-nums",
            }}
          >
            {numberShown}
          </span>
          <span
            style={{
              fontSize: 44,
              fontWeight: 600,
              color: theme.textDim,
              marginLeft: 22,
            }}
          >
            {statSuffix}
          </span>
        </div>

        <svg width="1080" height="1920" style={{ position: "absolute" }}>
          {Array.from({ length: total }).map((_, i) => {
            const col = i % cols;
            const row = Math.floor(i / cols);
            const x = gx + col * cell;
            const y = gy + row * cell;

            const appear = spring({
              frame: frame - 8 - (row * 2 + col) * 0.7,
              fps,
              config: { damping: 16, mass: 0.5 },
            });

            const lit = i < litCount;
            const justLit = lit && i === litCount - 1;
            const litPop = justLit ? 1.18 : 1;

            return (
              <g
                key={i}
                transform={`translate(${x}, ${y}) scale(${(0.6 + appear * 0.4) * litPop})`}
                opacity={appear}
              >
                <Person
                  fill={lit ? accent : "rgba(255,255,255,0.09)"}
                  glow={lit}
                  accent={accent}
                />
              </g>
            );
          })}
        </svg>
      </AbsoluteFill>
    </StudioScene>
  );
};
