---
name: Halal Dual-Strategy Screener
description: After-hours ledger for daily Shariah-compliant dividend and growth picks.
colors:
  antique-brass: "#c4a35a"
  ink-on-gold: "#1a1408"
  pine-vault: "#0f1a17"
  forest-chamber: "#15241f"
  moss-panel: "#1c322b"
  mint-ledger: "#e8f0ec"
  sage-caption: "#9bb0a6"
  hairline-frost: "rgba(232, 240, 236, 0.12)"
  compliant-mint: "#6fbf9a"
  dusty-coral: "#e08a7a"
  veil: "rgba(6, 10, 9, 0.62)"
typography:
  display:
    fontFamily: "Fraunces, Palatino Linotype, Palatino, serif"
    fontSize: "clamp(1.8rem, 4vw, 2.6rem)"
    fontWeight: 600
    lineHeight: 1.15
    letterSpacing: "-0.02em"
  headline:
    fontFamily: "Fraunces, Palatino Linotype, Palatino, serif"
    fontSize: "clamp(1.35rem, 2.5vw, 1.75rem)"
    fontWeight: 550
    lineHeight: 1.2
    letterSpacing: "-0.02em"
  title:
    fontFamily: "Fraunces, Palatino Linotype, Palatino, serif"
    fontSize: "1.35rem"
    fontWeight: 550
    lineHeight: 1.2
    letterSpacing: "-0.02em"
  body:
    fontFamily: "Source Sans 3, Segoe UI, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "normal"
  label:
    fontFamily: "Source Sans 3, Segoe UI, sans-serif"
    fontSize: "0.72rem"
    fontWeight: 600
    lineHeight: 1.3
    letterSpacing: "0.08em"
rounded:
  none: "0px"
  button: "2px"
spacing:
  xs: "0.25rem"
  sm: "0.55rem"
  md: "1.25rem"
  lg: "1.5rem"
  xl: "2.5rem"
components:
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.sage-caption}"
    rounded: "{rounded.button}"
    padding: "0.55rem 0.9rem"
  button-ghost-hover:
    backgroundColor: "transparent"
    textColor: "{colors.mint-ledger}"
    rounded: "{rounded.button}"
    padding: "0.55rem 0.9rem"
  button-ticker:
    backgroundColor: "transparent"
    textColor: "{colors.mint-ledger}"
    padding: "0"
  button-ticker-hover:
    backgroundColor: "transparent"
    textColor: "{colors.antique-brass}"
    padding: "0"
  panel:
    backgroundColor: "{colors.moss-panel}"
    textColor: "{colors.mint-ledger}"
    rounded: "{rounded.none}"
    padding: "1.25rem 1.25rem 1.5rem"
  drawer:
    backgroundColor: "{colors.forest-chamber}"
    textColor: "{colors.mint-ledger}"
    rounded: "{rounded.none}"
    padding: "1.25rem 1.25rem 2rem"
    width: "min(420px, 100%)"
  eyebrow:
    textColor: "{colors.antique-brass}"
    typography: "{typography.label}"
  stat-value:
    textColor: "{colors.mint-ledger}"
    typography: "{typography.title}"
---

# Design System: Halal Dual-Strategy Screener

## Overview

**Creative North Star: "The Quiet Ledger"**

A formal after-hours document. Type and hairlines do the work; gold is a citation, not decoration. The dashboard is a view-only daily brief: two strategy tracks and a shared paper ledger, read in low ambient light after the close.

The world is restrained institutional. Density is high enough to scan five names and a handful of ratios without scrolling past the point. Surfaces are square chambers of dark pine with a frost hairline. Fraunces carries the brand and the figures; Source Sans 3 carries the table and the legal line. Confirmed visual rejections: chrome, drop shadows, rounded marketing cards, emoji, and a second accent hue.

**Key Characteristics:**
- Dark pine interiors with one antique-brass voice
- Hairline frost borders instead of shadows
- Square panels; 2px radius only on buttons
- Serif for brand and numbers; sans for tables and body
- Immediate color-shift states. No choreographed motion

## Colors

A forest vault with a single metal. Brass is rare. Mint ink and sage captions do the reading.

### Primary
- **Antique Brass**: Brand wordmark, track eyebrows, ticker hover, and the occasional link. Its scarcity is the signal.
- **Ink on Gold**: Text on a solid brass fill, if a filled control is ever reintroduced. Not used on the live dashboard.

### Neutral
- **Pine Vault**: Page ground and the deepest wash of the canvas gradient.
- **Forest Chamber**: Drawer body and the mid wash of the page.
- **Moss Panel**: Upper stop of panel fills (translucent over the vault).
- **Mint Ledger**: Primary reading ink on dark surfaces.
- **Sage Caption**: Secondary copy, table headers, labels, empty states, footer.
- **Hairline Frost**: Every divider, panel stroke, and table rule. One weight, one recipe.

### Status
- **Compliant Mint**: Positive P&L only. Not a brand accent.
- **Dusty Coral**: Negative P&L and load errors. Not a warning banner system.

**The One Brass Rule.** Antique brass appears on the brand wordmark, uppercase eyebrows, and hover citations. It does not fill panels, tables, or backgrounds.

**The Hairline Recipe Rule.** Borders and rules use Hairline Frost. Do not invent a second border color or a thicker rule to create hierarchy.

## Typography

**Display Font:** Fraunces (with Palatino Linotype, Palatino, serif)
**Body Font:** Source Sans 3 (with Segoe UI, sans-serif)
**Label Font:** Source Sans 3, uppercase, tracked

**Character:** A quiet document pairing. Fraunces is the ledger hand for names and figures. Source Sans 3 is the clerk: tables, captions, and legal copy.

### Hierarchy
- **Display** (600, clamp 1.8–2.6rem, tracking -0.02em): Brand wordmark only, in Antique Brass.
- **Headline** (550, clamp 1.35–1.75rem, tracking -0.02em): Page title. Cap the measure at about 18ch.
- **Title** (550, 1.35rem panels / 1.2rem stats / 1.05rem subsection): Panel headings and numeric figures.
- **Body** (400, 1rem, 1.5 line-height): Lede and footer. Lede measure about 52ch.
- **Label** (600, 0.72–0.78rem, uppercase, tracking 0.04–0.08em): Eyebrows, column headers, stat labels.

### Named Rules
**The Two-Hands Rule.** Fraunces is for brand, headings, and figures. Source Sans 3 is for tables, captions, and prose. Do not reverse them.

**The Small-Caps Citation Rule.** Uppercase labels are citations, not decoration. Keep them sage or brass. Never mint-on-mint at display size.

## Layout

A single centered column: `min(1120px, calc(100% - 2rem))`, top padding 2.5rem, bottom 4rem. Vertical rhythm is 1.5rem between panels, 2.5rem around header and footer. Respect notch and home-indicator insets via `env(safe-area-inset-*)`.

The header becomes two columns at 800px (1.6fr brand block, 1fr as-of meta, aligned to the bottom). Main stacks three square chambers: Dividend, Growth, Paper portfolio.

Below 720px, wide data tables reflow into labeled ledger cards (one pick or position per chamber). Stat tiles use a two-column grid, collapsing to one column under 380px. The audit drawer becomes a full-width sheet. Touch targets for tickers and Close are at least 44px.

Above 720px, tables stay tabular and may scroll horizontally inside the chamber rather than breaking the column. Stat tiles sit in an auto-fit grid (`minmax(9.5rem, 1fr)`). Cell padding is 0.7rem by 0.55rem. Group spacing is tight; section spacing is generous.

## Elevation & Depth

The system is flat. Depth is tonal, not shadowed. The page canvas uses two large, low-chroma radial washes (moss at the top-left, olive at the top-right) over a 165deg pine gradient. Those washes are atmosphere on the body, not a card material.

Panels are translucent moss over pine, framed by a 1px Hairline Frost stroke. The audit drawer is an opaque Forest Chamber sheet that enters from the right over a 62% pine veil. No `box-shadow` is used.

**The Flat-By-Default Rule.** Surfaces stay flat at rest and in hover. Hover is a color citation (brass or mint), never a lift.

## Shapes

Chambers are orthogonal: panels, tables, the drawer, and stat tiles have no radius. The only rounding is 2px on the ghost button, almost a square. Geometry is a ledger page, not a product card.

Hairlines are 1px, never 2px, and never a colored left rail. The drawer is a full-height sheet at `min(420px, 100%)` with a single left hairline.

**The Square Chamber Rule.** Do not round panels, tables, or the drawer. The 2px button radius is the exception, not a scale.

## Components

Live primitives only. Unused filled and small-button leftovers were removed from CSS and are not part of the system.

### Buttons
- **Shape:** Almost-square (2px) on the ghost control. Ticker buttons have no chrome.
- **Ghost:** Transparent fill, Hairline Frost stroke, Sage Caption label, padding 0.55rem by 0.9rem. Hover shifts the label to Mint Ledger. Used for Close on the audit drawer.
- **Ticker (linkish):** Unstyled text button. Strong ticker over a sage company name. Hover paints the ticker Antique Brass.
- **Focus:** Native browser focus. Do not add a glow ring unless a later pass specifies one.

### Cards / Containers
- **Corner Style:** Square (0)
- **Background:** Vertical wash from translucent Moss Panel to translucent Pine Vault
- **Shadow Strategy:** None. Hairline Frost stroke only
- **Internal Padding:** 1.25rem, 1.5rem at the bottom
- **Header:** Eyebrow, title, lede. Meta can sit opposite on wide viewports

### Tables
- Desktop: collapse, full width, 0.92rem body. Headers are uppercase sage labels. Rows divide with Hairline Frost. Numeric audit cells use tabular nums.
- Mobile (below 720px): each row becomes a labeled ledger card via `data-label`; the ticker cell leads without a duplicate label. Empty states are a single sage sentence, not an illustration.

### Stat tiles
- No box. A top hairline and padding. Uppercase sage label over a Fraunces figure. Positive figures take Compliant Mint; negative take Dusty Coral.

### Inputs / Fields
- None on the public UI. The product is view-only. Do not add form chrome unless the product gains a real control.

### Navigation
- No app nav. Identity is the Fraunces brass wordmark in the header. As-of date and universe counts sit opposite it from 800px up.

### Audit drawer (signature)
- Right sheet over a pine veil. Clicking the veil or pressing Escape closes it. Eyebrow "Compliance audit", ticker as title, sage name beside it. Metric table, then a sage hint. Close is the ghost button.

## Do's and Don'ts

### Do:
- **Do** keep Antique Brass rare: wordmark, eyebrows, ticker hover, links.
- **Do** divide space with Hairline Frost, not shadows or extra fill colors.
- **Do** set figures in Fraunces and table copy in Source Sans 3.
- **Do** keep panels square and the column at 1120px.
- **Do** write empty, loading, and error states as sage or dusty-coral sentences.

### Don't:
- **Don't** introduce a second accent, gradient text, or glass blur.
- **Don't** round chambers or add drop shadows.
- **Don't** use emoji, decorative icons, or monospace as a costume for "finance."
- **Don't** add per-visitor controls, primary filled buttons, or form fields to the public page.
- **Don't** use em dashes or emoji in product copy.
