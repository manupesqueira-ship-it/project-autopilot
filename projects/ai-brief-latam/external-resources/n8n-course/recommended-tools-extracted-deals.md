# Recommended Tools — deals limpios

**Fuente:** `recommended-tools-original.pdf` del curso n8n.
**Procesamiento:** affiliate links removidos. Solo se conservan los deals con descuento real, vinculados a herramientas que ya están en nuestro `STACK.md` o son candidatas reales.
**Fecha extracción:** 2026-05-12.

---

## Deals activos relevantes para AI How-To LATAM

### 1. ElevenLabs Creator — 50% off primer mes

- **Precio normal:** $22/mo
- **Con descuento:** ~$11 primer mes, después $22/mo
- **Aplica a:** ADR-008 (voice clone para reels)
- **Cuándo activar:** Fase 2 (cuando Manuel grabe los 20 min de muestra para voice clone)
- **Cómo:** registro directo en elevenlabs.io. El código de descuento del curso suele ser un cupón temporal — verificar vigencia al momento de comprar. Si expiró, ElevenLabs frecuentemente corre promos similares.

### 2. Hostinger — VPS con n8n one-click template

- **Precio:** $6.49/mo (plan KVM2, 24 meses)
- **Aplica a:** ADR-015 (n8n self-hosted)
- **Cuándo activar:** inicio de Fase 0 (ya documentado en `runbooks/hostinger-vps-n8n-setup.md`)
- **Cómo:** registro directo en hostinger.com. El template de n8n está disponible nativamente en el panel sin necesidad de código del curso. Verificar datacenter region (BR São Paulo preferido para latencia LATAM).

### 3. Vapi — 1000 minutos gratis

- **Precio normal:** pay-as-you-go con minutos gratis variables
- **Con deal:** 1000 minutos free al registrarse
- **Aplica a:** posible Fase 3+ si construimos voice agent para newsletter (community management telefónico o voice notes)
- **Cuándo activar:** **NO ahora.** Vapi no está en stack actual. Solo si Fase 3 expande a voice agents.
- **Mantener en backlog.**

### 4. Retell AI — $10 free credits

- **Precio normal:** pay-as-you-go
- **Con deal:** $10 credits iniciales
- **Aplica a:** alternativa a Vapi, mismo caso de uso
- **Cuándo activar:** NO ahora. Backlog Fase 3+.

---

## Herramientas mencionadas en el PDF pero NO relevantes para nosotros

| Tool | Por qué no | Status |
|---|---|---|
| **Make.com** | Decidimos n8n. Make tiene billing trap caro a escala. | Descartado |
| **Zapier** | Misma razón. Más caro que n8n self-hosted. | Descartado |
| **Pipedream** | Niche developer; n8n nos da más control. | Descartado |
| **Apollo.io** | Lead-gen B2B SaaS — no es nuestro nicho. | Irrelevante |
| **Instantly** | Email cold outreach — no aplica a newsletter editorial. | Irrelevante |
| **Smartlead** | Cold email — no aplica. | Irrelevante |
| **Clay** | Data enrichment B2B — no aplica. | Irrelevante |
| **PhantomBuster** | Social scraping gris/legal-iffy — no aplica a marca sobria. | Descartado |
| **Tixae / Voiceflow** | Chatbot builders — no necesarios todavía. | Backlog Fase 4+ |

---

## Notas operativas

- **Affiliate hygiene:** el PDF original (`recommended-tools-original.pdf`) tiene affiliate links del autor del curso. Esos links se ignoraron deliberadamente al extraer este markdown — usá las URLs directas de cada tool.
- **Verificación de deals:** todos los descuentos arriba se documentaron el 2026-05-12. Pueden haber expirado. Verificar al momento de comprar.
- **No incluí precios "normales" de tools sin deal** (ej. precio standard de Anthropic, OpenAI) — esos ya están documentados en `docs/STACK.md` y `docs/COSTS_6MO.md`.

---

## Lo que ya tenemos definido y no necesitamos del PDF

- **Anthropic Claude** (Opus 4 + Sonnet 4.5): documentado en STACK
- **OpenAI gpt-image-2:** documentado en ADR-013
- **Upload-Post:** documentado en ADR-014
- **Supabase:** documentado, free tier suficiente Fase 1-2
- **Telegram Bot:** free, no requiere deal
- **GitHub:** free para repos privados

Estos no aparecen en el PDF del curso (o si aparecen, no aportan más info de la que ya tenemos).
