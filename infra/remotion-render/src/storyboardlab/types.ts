// Storyboard Lab — tipos del styleframe.
// Un styleframe es una IMAGEN (composición antes de animar). Resolvemos COMPOSICIÓN
// antes que movimiento: si no funciona como imagen, una animación no lo rescata.

export type Align = "left" | "center" | "right";

export type Block =
  | { type: "text"; text: string; x: number; y: number; w?: number; size: number; color?: string; weight?: number; align?: Align; opacity?: number; letterSpacing?: number }
  | { type: "number"; text: string; x: number; y: number; w?: number; size: number; color?: string; align?: Align }
  | { type: "rect"; x: number; y: number; w: number; h: number; fill?: string; stroke?: string; radius?: number }
  | { type: "divider"; x: number; y: number; w: number; color?: string; thickness?: number }
  | { type: "chartph"; x: number; y: number; w: number; h: number; label?: string; trend?: "up" | "down" | "flat" }
  | { type: "objectph"; x: number; y: number; w: number; h: number; label?: string; shape?: "box" | "circle" }
  | { type: "label"; text: string; x: number; y: number; w?: number; size?: number; color?: string; align?: Align };

export type StyleframeSpec = {
  id: string;
  title?: string;   // nombre de la escena / master objetivo
  note?: string;    // recordatorio de intención (no se anima aún)
  bg?: "gradient" | "base";
  blocks: Block[];
};
