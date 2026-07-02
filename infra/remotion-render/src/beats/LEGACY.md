# Beats = LEGACY / material crudo

Estos ~50 beats **predatan** la gramática visual validada a mano (ver
`docs/PLAN_GRAMATICA_VISUAL_v4.md`). Marcado **no destructivo**:

- **No son masters.** Ninguno está aprobado como unidad visual de la gramática v4.
- **No se borran ni se editan.** El pipeline los sigue usando hasta que un **master
  aprobado** los reemplace por familia de escena.
- **No se promueven tal cual.** Cada master nuevo se DERIVA de un styleframe aprobado
  (no se "asciende" un beat legacy sin pasar por storyboard → styleframe → aprobación → ficha).

Manifiesto completo: `infra/grammar/masters/legacy_manifest.json`.
Sistema de masters: `infra/grammar/masters/` (schema, registry, ficha).
