import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

// Transiciones de costura (teardown 0x100x, motion_grammar.md):
// viven en el LEAD/TAIL de cada beat — el beat saliente renderiza su mitad
// (exitFx) y el entrante la suya (enterFx), asi el concat queda invisible y
// la voz no se mueve un frame.
//   scrollUp   = whip vertical (tilt de camara entre escenas)
//   zoomPunch  = zoom-through con micro flash (energia hacia un impacto)
//   flashWhite = bloom blanco quemado (1x por video, antes del CTA)
export type SeamName = "scrollUp" | "zoomPunch" | "flashWhite";

export type SeamFxProps = {
  enterFx?: SeamName;
  exitFx?: SeamName;
};

export const SeamFx: React.FC<React.PropsWithChildren<SeamFxProps>> = ({
  enterFx,
  exitFx,
  children,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames: d } = useVideoConfig();
  const clamp = {
    extrapolateLeft: "clamp" as const,
    extrapolateRight: "clamp" as const,
  };

  let ty = 0;
  let scale = 1;
  let flash = 0;

  if (enterFx === "scrollUp") {
    ty += interpolate(frame, [0, 7], [1920, 0], {
      ...clamp,
      easing: Easing.out(Easing.cubic),
    });
  } else if (enterFx === "zoomPunch") {
    scale *= interpolate(frame, [0, 8], [1.09, 1], {
      ...clamp,
      easing: Easing.out(Easing.cubic),
    });
    flash = Math.max(flash, interpolate(frame, [0, 4], [0.85, 0], clamp));
  } else if (enterFx === "flashWhite") {
    scale *= interpolate(frame, [0, 9], [1.05, 1], {
      ...clamp,
      easing: Easing.out(Easing.cubic),
    });
    flash = Math.max(flash, interpolate(frame, [0, 5], [1, 0], clamp));
  }

  if (exitFx === "scrollUp") {
    ty += interpolate(frame, [d - 5, d - 1], [0, -1920], {
      ...clamp,
      easing: Easing.in(Easing.cubic),
    });
  } else if (exitFx === "zoomPunch") {
    scale *= interpolate(frame, [d - 6, d - 1], [1, 1.35], {
      ...clamp,
      easing: Easing.in(Easing.quad),
    });
    flash = Math.max(flash, interpolate(frame, [d - 3, d - 1], [0, 0.85], clamp));
  } else if (exitFx === "flashWhite") {
    flash = Math.max(flash, interpolate(frame, [d - 4, d - 1], [0, 1], clamp));
  }

  return (
    <AbsoluteFill style={{ backgroundColor: "#070A0F" }}>
      <AbsoluteFill
        style={{ transform: `translateY(${ty}px) scale(${scale})` }}
      >
        {children}
      </AbsoluteFill>
      {flash > 0 && (
        <AbsoluteFill style={{ backgroundColor: "#FFFFFF", opacity: flash }} />
      )}
    </AbsoluteFill>
  );
};

export function withSeams<P extends object>(
  C: React.FC<P>,
): React.FC<P & SeamFxProps> {
  const Wrapped: React.FC<P & SeamFxProps> = ({ enterFx, exitFx, ...rest }) => (
    <SeamFx enterFx={enterFx} exitFx={exitFx}>
      <C {...(rest as P)} />
    </SeamFx>
  );
  Wrapped.displayName = `withSeams(${C.displayName ?? C.name ?? "Beat"})`;
  return Wrapped;
}
