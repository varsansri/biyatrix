# biyatrix — Design System

## Color Strategy: Drenched
The surface IS the color. Deep black with neon green as the living organism.

## Colors (OKLCH)
- Background: oklch(4% 0.01 145) — near black, green-tinted
- Surface: oklch(7% 0.012 145)
- Surface 2: oklch(10% 0.015 145)
- Border: oklch(16% 0.02 145)
- Accent (neon): oklch(85% 0.28 135) — electric green #57ff2c
- Accent (mid): oklch(70% 0.22 145) — #22c55e
- Accent light: oklch(78% 0.2 148) — #4ade80
- Text primary: oklch(92% 0.015 145) — near white with green tint
- Text muted: oklch(55% 0.06 145)

## Typography
- Font: Inter (system fallback: -apple-system, sans-serif)
- Body: 15px / 1.6 line-height, max 65ch
- Hierarchy: 22px headings, 15px body, 13px secondary, 11px labels
- Weight contrast: 700 headings, 400 body, 600 interactive

## Spacing Rhythm
- Not uniform. Vary padding for breath.
- Section gaps: 24px
- Card internals: 18px
- Dense elements: 10-12px

## Motion
- ease-out-quart on all transitions
- 200-300ms for micro-interactions
- 300-400ms for card reveals (slide + fade)
- Recording pulse: CSS animation, no bounce

## Logo
- Pixel art butterfly, image-rendering: pixelated
- filter: drop-shadow(0 0 6px #57ff2c) — glows in the dark
- 28px in nav

## Components
- Cards: border-radius 14px, surface bg, 1px border
- Buttons: border-radius 10-12px
- Tags/chips: border-radius 20px (pill)
- No glassmorphism. No gradient text. No side-stripe borders.
