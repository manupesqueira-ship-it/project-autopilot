import React from "react";

// Marca ₿ Bitcoin como VECTOR (no IA): moneda naranja con brillo + símbolo ₿
// blanco. Reutilizable en cualquier beat donde el BTC es el sujeto (hook,
// recovery). Color de marca oficial #F7931A. El glow es opcional (pulso del beat).
export const BitcoinMark: React.FC<{ size?: number; glow?: number }> = ({
  size = 150,
  glow = 1,
}) => {
  const c = "#F7931A";
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 100"
      style={{
        filter: `drop-shadow(0 0 ${22 * glow}px ${c}cc) drop-shadow(0 8px 20px rgba(0,0,0,0.5))`,
      }}
    >
      <defs>
        <radialGradient id="btcCoin" cx="38%" cy="30%" r="85%">
          <stop offset="0%" stopColor="#FCC067" />
          <stop offset="52%" stopColor={c} />
          <stop offset="100%" stopColor="#D9760B" />
        </radialGradient>
      </defs>
      <circle cx="50" cy="50" r="46" fill="url(#btcCoin)" />
      <circle
        cx="50"
        cy="50"
        r="46"
        fill="none"
        stroke="#FFFFFF"
        strokeOpacity="0.22"
        strokeWidth="1.4"
      />
      {/* símbolo ₿ como glifo nítido, inclinado ~13° como el logo oficial. En
          Windows cae a Segoe UI (que sí trae ₿) si la fuente cargada no lo tiene. */}
      <text
        x="50"
        y="51"
        textAnchor="middle"
        dominantBaseline="central"
        transform="rotate(13 50 50)"
        fontFamily="'Segoe UI', 'Inter', Arial, sans-serif"
        fontWeight={700}
        fontSize={64}
        fill="#FFFFFF"
      >
        ₿
      </text>
    </svg>
  );
};
