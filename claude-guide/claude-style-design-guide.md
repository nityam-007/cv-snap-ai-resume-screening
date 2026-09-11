# Claude / Anthropic-Inspired Design Guide

A reference system for building presentations, decks, and interfaces in the visual language of Claude and Anthropic: warm, editorial, calm, and quietly confident — deliberately not another cold-blue "AI product" look.

> **Note on sourcing:** Anthropic hasn't published a public brand book, so this guide is built from the consistently observed tokens across claude.ai, the Anthropic site, and Anthropic's own published brand colors (dark, light, and the orange/blue/green accents below are well attested). Anything inferred rather than confirmed is marked *(inferred)*.

---

## 1. Design philosophy

- **Warm, not clinical.** Parchment and clay instead of white-and-blue "tech" chrome. The palette reads more like a print essay than a SaaS dashboard.
- **Editorial restraint.** One accent color does the work. Everything else stays quiet — ink, warm greys, paper.
- **Serif + sans pairing.** A serif carries personality in display moments; a clean sans carries everything functional. This split does a lot of the "feels considered" work on its own.
- **Generous whitespace over density.** Content breathes. Borders and dividers are hairline, not heavy.
- **Soft geometry.** Rounded corners throughout, but modestly — never pill-shaped bubbles on everything, never sharp SaaS-card 8px-everywhere sameness either.

---

## 2. Color

### Core palette

| Token | Name | Hex | Use |
|---|---|---|---|
| `--color-ink` | Dark | `#141413` | Primary text, dark surfaces |
| `--color-paper` | Light | `#FAF9F5` | Primary background (warm off-white, not pure white) |
| `--color-paper-alt` | Pampas | `#F4F3EE` | Secondary/panel background |
| `--color-mid-gray` | Mid Gray | `#87867F` | Secondary text, muted labels |
| `--color-light-gray` | Light Gray | `#D9D7CE` | Borders, dividers, disabled fills |
| `--color-white` | White | `#FFFFFF` | Cards on paper, input fields |

### Accent colors

| Token | Name | Hex | Use |
|---|---|---|---|
| `--color-accent` | Clay / Orange | `#D97757` | **Primary accent.** CTAs, links, active states, brand moments. Use sparingly — one hero use per view. |
| `--color-accent-hover` | Clay Dark | `#C15F3C` | Hover/pressed state of accent |
| `--color-blue` | Slate Blue | `#6A9BCC` | Secondary accent — info, links in dark contexts |
| `--color-green` | Sage | `#788C5D` | Success, positive states |

### Semantic mapping

| Purpose | Token |
|---|---|
| Background (default) | `--color-paper` |
| Background (raised/card) | `--color-white` |
| Background (subtle panel) | `--color-paper-alt` |
| Text (primary) | `--color-ink` |
| Text (secondary/muted) | `--color-mid-gray` |
| Border (default) | `--color-light-gray` |
| Interactive / CTA | `--color-accent` |
| Success | `--color-green` |
| Info | `--color-blue` |
| Error *(inferred)* | `#C4533D` (a desaturated red-clay, not a stock red — keep it in the same warm family) |

**Rule of thumb:** the accent color should appear on purpose, not by default. If more than ~10% of a view is orange, pull it back. The palette's power comes from restraint — one warm hit against a field of paper and ink.

---

## 3. Typography

| Role | Typeface | Fallback stack | Notes |
|---|---|---|---|
| Display / headings | A humanist serif (Anthropic uses a custom face, "Copernicus") | `ui-serif, Georgia, Cambria, "Times New Roman", Times, serif` | Used at large sizes for hero statements, section titles. Carries the "editorial" feel. |
| Body / UI | A neutral grotesque sans *(inferred; Styrene-family in product)* | `-apple-system, "Segoe UI", Helvetica, Arial, sans-serif` | All body copy, labels, buttons, nav — legibility over character. |
| Monospace | Any standard mono | `ui-monospace, "SF Mono", Menlo, Consolas, monospace` | Code, data labels only — don't decorate with it. |

### Type scale (base 16px)

| Level | Size | Weight | Line-height | Typeface |
|---|---|---|---|---|
| Display | 56px | 500 | 1.05 | Serif |
| H1 | 40px | 500 | 1.1 | Serif |
| H2 | 28px | 500 | 1.2 | Serif |
| H3 | 20px | 600 | 1.3 | Sans |
| Body Large | 18px | 400 | 1.6 | Sans |
| Body | 16px | 400 | 1.6 | Sans |
| Small / Caption | 13px | 400 | 1.5 | Sans |
| Label | 13px | 500 | 1.4 | Sans |

**Guidance:**
- Keep line length under ~75 characters for body text.
- Don't reach for all-caps tracked labels or middle-dot separators — that's generic "AI deck" chrome, not this system's voice.
- Use the serif deliberately, not everywhere. If everything is serif, nothing feels editorial.

---

## 4. Spacing & layout

8px base unit.

| Token | Value |
|---|---|
| `--space-1` | 4px |
| `--space-2` | 8px |
| `--space-3` | 16px |
| `--space-4` | 24px |
| `--space-5` | 32px |
| `--space-6` | 48px |
| `--space-7` | 64px |
| `--space-8` | 96px |

- Grid: 12-column, max content width ~1200px, generous outer margin (min 48px on desktop).
- Section rhythm: use `--space-7`–`--space-8` between major sections; `--space-4`–`--space-5` within a section.
- Alignment: predominantly left-aligned text blocks; center alignment reserved for short hero statements or slide title cards.

---

## 5. Shape, elevation, borders

| Token | Value | Use |
|---|---|---|
| `--radius-sm` | 6px | Inputs, small buttons, tags |
| `--radius-md` | 12px | Cards, panels |
| `--radius-lg` | 20px | Hero containers, modals |
| `--border-hairline` | 1px solid `--color-light-gray` | Default dividers/card borders |
| `--shadow-sm` | `0 1px 2px rgba(20,20,19,0.06)` | Resting card |
| `--shadow-md` | `0 4px 16px rgba(20,20,19,0.08)` | Popovers, dropdowns |

Avoid heavy drop shadows and glassmorphism. Depth comes from a hairline border and a very soft shadow, not blur effects.

---

## 6. Components

### Buttons

| Variant | Background | Text | Border | Notes |
|---|---|---|---|---|
| Primary | `--color-accent` | White | none | Hover → `--color-accent-hover` |
| Secondary | Transparent | `--color-ink` | 1px `--color-light-gray` | Hover → `--color-paper-alt` fill |
| Ghost/Text | Transparent | `--color-accent` | none | Underline on hover, not before |

Radius: `--radius-sm`. Padding: `10px 20px`. Weight: 500.

### Cards

- White background on paper page, or paper-alt background on white page — always contrast the surface one step from its parent.
- `--radius-md`, hairline border, `--shadow-sm`.
- Don't apply identical shadow-and-radius to every single content block regardless of hierarchy — reserve card treatment for things that are genuinely discrete, groupable units.

### Inputs

- White fill, hairline border, `--radius-sm`.
- Focus state: border becomes `--color-accent`, plus a 2px soft accent-tinted outline ring (`rgba(217,119,87,0.25)`).

### Tags / Badges

- Small pill or `--radius-sm` rectangle, `--color-paper-alt` fill, `--color-ink` text, 13px medium weight. Accent-colored badge variant reserved for "new" or highlighted status only.

### Navigation

- Flat, minimal chrome. Text links in `--color-mid-gray`, becoming `--color-ink` on hover/active — not accent-colored nav items (accent stays reserved for actions, not wayfinding).

### Alerts / callouts

| Type | Left border | Background |
|---|---|---|
| Info | `--color-blue` | tint of blue at 8% opacity on paper |
| Success | `--color-green` | tint of green at 8% opacity |
| Warning/Error | `#C4533D` | tint at 8% opacity |

---

## 7. States

| State | Treatment |
|---|---|
| Hover | Slight background shift or accent darkening — no scale/transform tricks |
| Active/Pressed | Darken accent one step, no shadow |
| Focus (keyboard) | Visible 2px accent-tinted ring — never remove outline without replacing it |
| Disabled | 40% opacity, no pointer events, no color change beyond opacity |
| Selected | `--color-paper-alt` fill or accent-colored left border, not full accent fill (reserve solid accent fill for buttons/CTAs) |

---

## 8. Motion

- Micro-interactions only: 150–200ms ease-out on hover/focus transitions.
- Avoid orchestrated entrance animations on every card/section — if you use one motion moment, make it a single deliberate reveal (e.g., a hero element), not a repeated pattern.
- Respect `prefers-reduced-motion`.

---

## 9. Voice, in brief

- Plain, direct, active voice. No filler, no forced enthusiasm.
- Buttons/CTAs say exactly what will happen ("Save changes," not "Submit" or "Get started →").
- Avoid tracked-out ALL-CAPS eyebrows, middle-dot metadata strings, and arrow-suffixed links — these read as generic AI-deck chrome, not this system.

---

## 10. Quick-reference token block (CSS)

```css
:root {
  /* Color */
  --color-ink: #141413;
  --color-paper: #FAF9F5;
  --color-paper-alt: #F4F3EE;
  --color-mid-gray: #87867F;
  --color-light-gray: #D9D7CE;
  --color-white: #FFFFFF;
  --color-accent: #D97757;
  --color-accent-hover: #C15F3C;
  --color-blue: #6A9BCC;
  --color-green: #788C5D;
  --color-error: #C4533D;

  /* Type */
  --font-serif: ui-serif, Georgia, Cambria, "Times New Roman", Times, serif;
  --font-sans: -apple-system, "Segoe UI", Helvetica, Arial, sans-serif;
  --font-mono: ui-monospace, "SF Mono", Menlo, Consolas, monospace;

  /* Space */
  --space-1: 4px; --space-2: 8px; --space-3: 16px; --space-4: 24px;
  --space-5: 32px; --space-6: 48px; --space-7: 64px; --space-8: 96px;

  /* Shape */
  --radius-sm: 6px; --radius-md: 12px; --radius-lg: 20px;
  --border-hairline: 1px solid var(--color-light-gray);
  --shadow-sm: 0 1px 2px rgba(20,20,19,0.06);
  --shadow-md: 0 4px 16px rgba(20,20,19,0.08);
}
```

---

## For your pitch deck specifically

- **Title slides:** paper background, large serif headline (Display size), one accent-colored detail (a rule, a single word, a small mark) — not a full-bleed orange background.
- **Data slides:** keep charts in ink/mid-gray with the accent reserved for the one data series or number you want the audience to remember.
- **Section breaks:** can invert to ink background with paper text for rhythm — use sparingly, once or twice in a deck, not every section.
