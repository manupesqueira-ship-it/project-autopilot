import React from "react";
import * as si from "simple-icons";

// Marcas que simple-icons NO trae (Microsoft/Google/Amazon retiraron sus logos
// del set por licencia) → SVG inline oficial multicolor, $0. Color de marca se
// respeta en ambos fondos (los multicolor leen bien sobre dark y light).
// palette-ok-file: este archivo renderiza LOGOS DE MARCA reales; sus colores
// (azul Google, etc.) son obligatorios y no aplican a la paleta semantica.
const INLINE_LOGOS: Record<string, (size: number) => React.ReactElement> = {
  microsoft: (size) => (
    <svg width={size} height={size} viewBox="0 0 23 23">
      <rect x="1" y="1" width="10" height="10" fill="#F25022" />
      <rect x="12" y="1" width="10" height="10" fill="#7FBA00" />
      <rect x="1" y="12" width="10" height="10" fill="#00A4EF" />
      <rect x="12" y="12" width="10" height="10" fill="#FFB900" />
    </svg>
  ),
  google: (size) => (
    <svg width={size} height={size} viewBox="0 0 48 48">
      <path
        fill="#EA4335"
        d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"
      />
      <path
        fill="#4285F4"
        d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"
      />
      <path
        fill="#FBBC05"
        d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"
      />
      <path
        fill="#34A853"
        d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"
      />
    </svg>
  ),
  amazon: (size) => (
    <svg width={size} height={size} viewBox="0 0 100 100">
      <text
        x="50"
        y="56"
        textAnchor="middle"
        fontFamily="InterVar, Inter, Helvetica, sans-serif"
        fontWeight={800}
        fontSize="34"
        letterSpacing="-1"
        fill="currentColor"
      >
        amazon
      </text>
      {/* smile arrow (a -> z) */}
      <path
        d="M22 64 C40 76, 60 76, 76 65"
        stroke="#FF9900"
        strokeWidth="6"
        strokeLinecap="round"
        fill="none"
      />
      <path
        d="M76 65 l-10 -1 l6 8 z"
        fill="#FF9900"
      />
    </svg>
  ),
};

// Logos de marca via simple-icons (3000+ SVG oficiales, $0).
// En guion: "logo": "nvidia" | "apple" | ... (slug de simple-icons).
// Marcas con hex oscuro (Apple #000) se pintan blancas sobre fondo dark.
export const BrandLogo: React.FC<{
  slug: string;
  size: number;
  on?: "dark" | "light";
}> = ({ slug, size, on = "dark" }) => {
  const inline = INLINE_LOGOS[slug.toLowerCase()];
  if (inline)
    return (
      <span style={{ color: on === "dark" ? "#FFFFFF" : "#1A1A1A", display: "flex" }}>
        {inline(size)}
      </span>
    );
  const key =
    "si" +
    slug
      .split(/[^a-z0-9]+/i)
      .map((p) => p.charAt(0).toUpperCase() + p.slice(1))
      .join("");
  const icon = (si as unknown as Record<string, { hex: string; path: string }>)[
    key
  ];
  // marca sin icono (p.ej. FTX, borrado del catálogo) → monograma
  if (!icon)
    return (
      <div
        style={{
          fontSize: size * 0.62,
          fontWeight: 900,
          lineHeight: 1,
          color: on === "dark" ? "#FFFFFF" : "#1A1A1A",
          fontFamily: "InterVar, Inter, Helvetica, sans-serif",
        }}
      >
        {slug.charAt(0).toUpperCase()}
      </div>
    );
  const r = parseInt(icon.hex.slice(0, 2), 16);
  const g = parseInt(icon.hex.slice(2, 4), 16);
  const b = parseInt(icon.hex.slice(4, 6), 16);
  const luma = 0.299 * r + 0.587 * g + 0.114 * b;
  const fill =
    on === "dark" && luma < 80
      ? "#FFFFFF"
      : on === "light" && luma > 200
        ? "#1A1A1A"
        : `#${icon.hex}`;
  return (
    <svg width={size} height={size} viewBox="0 0 24 24">
      <path d={icon.path} fill={fill} />
    </svg>
  );
};
