# Design tokens

Defaults for every pass. If the project's own token set is sound, use its values and correct only how the screen applies them. On iOS and Android the system tokens come first: the platform reference says which ones.

A token is a named value. Views read `surface` or `spacing.md`, never `#1C1C1E` or `13`. A fix that replaces one hard-coded value with another hard-coded value is not finished.

## Spacing

Base unit 4. Scale: 4, 8, 12, 16, 24, 32, 48, 64, 96. Half steps of 2 are acceptable inside tight controls. Keep an odd number that exists to center an element precisely.

| Use | Range |
|-----|-------|
| Inside a control (icon to label, padding of a chip) | 4–12 |
| Between items of one group (rows, fields) | 4–12 |
| Between groups (a heading and its list, two cards) | 16–24 |
| Between sections of a screen | 32–48, landing sections 64–96 |
| Screen edge, phone | 16, or the platform margin |
| Screen edge, tablet or desktop | 24–32 |

## Color roles

Define roles once, for light and dark, and let views read only roles. Each platform names them differently:

| Role | Web (CSS variable) | iOS (SwiftUI / UIKit) | Android (Compose M3 / XML attr) |
|------|--------------------|-----------------------|----------------------------------|
| Background | `--color-bg` | `Color(.systemBackground)`, or `.systemGroupedBackground` for grouped lists | `colorScheme.surface` / `?attr/colorSurface` |
| Surface (card, cell) | `--color-surface` | `.secondarySystemBackground`, `.secondarySystemGroupedBackground` | `surfaceContainerLow` or `surfaceContainer` |
| Raised (input, selected row) | `--color-raised` | `.tertiarySystemBackground`, or a `systemFill` for controls | `surfaceContainerHigh` |
| Separator | `--color-border` | `Color(.separator)` | `outlineVariant` |
| Text, primary | `--color-text` | `.primary` / `.label` | `onSurface` |
| Text, secondary | `--color-text-2` | `.secondary` / `.secondaryLabel` | `onSurfaceVariant` |
| Text, muted (meta only) | `--color-text-3` | `.tertiary` / `.tertiaryLabel` | `onSurfaceVariant` (M3 has two text roles; don't add alpha tints) |
| Accent | `--color-accent` | `.tint`, the `AccentColor` asset | `primary` |
| On accent | `--color-on-accent` | set by the system on prominent buttons | `onPrimary` |
| Error | `--color-danger` | `.red` | `error` |
| Success, warning | `--color-success` | `.green`, `.orange` | custom roles in the theme, never inline |

Rules:

- Surfaces stay neutral. Tint the neutral ramp toward the product's material only slightly, so no surface reads as a color.
- Keep the accent's share of the screen small, roughly one to five percent: the main call to action, the current selection, one key number.
- A real brand color becomes the accent. Without one, take the accent from the direction, and steer away from violet and indigo unless the brand already owns them.
- Status colors carry meaning only, toned to sit with the palette.
- In dark mode, lift an element by lightening its surface instead of adding a shadow.

## Contrast

| What | Minimum |
|------|---------|
| Body and label text | 4.5:1 |
| Large text (24 px, or 18.7 px bold, and up) | 3:1 |
| Icons that carry meaning, control borders, focus indicators | 3:1 |

Check light and dark. Check text that sits on the accent or on a photo.

## Type roles

| Role | Web | iOS text style | Android M3 role |
|------|-----|----------------|-----------------|
| Display (hero, big figure) | 40–64 px, fluid | `.largeTitle` or a custom size that scales | `displaySmall` to `displayLarge` |
| Screen title | 24–32 px | `.largeTitle` / `.title` (navigation title) | `headlineSmall` / `headlineMedium` |
| Section heading | 18–20 px | `.title3` / `.headline` | `titleLarge` / `titleMedium` |
| Body | 16 px | `.body` | `bodyLarge` |
| Secondary text | 14 px | `.subheadline` / `.callout` | `bodyMedium` |
| Button and label | 14–16 px, medium | `.body` (system buttons) | `labelLarge` |
| Caption and meta | 12–13 px | `.footnote` / `.caption` | `bodySmall` / `labelSmall` |

- Two weights, regular and medium. Semibold for rare emphasis. Never the heaviest weights for headings.
- Line height about 1.4–1.5 for body text, 1.1–1.25 for headings.
- Letter spacing 0 below about 20 px. Display text may go slightly negative.
- Tabular digits for figures that change or line up: `font-variant-numeric: tabular-nums` (web), `.monospacedDigit()` (SwiftUI), `fontFeatureSettings = "tnum"` (Compose).
- Keep a serif display face for big headlines. Labels and buttons stay in the interface family.

## Radius

| Element | Web | iOS | Android (M3 shape) |
|---------|-----|-----|--------------------|
| Tag, small chip, keycap | 4–6 | 4–6 | `extraSmall` 4 dp |
| Button, input, row | 8–10 | system button shapes, or 8–12 | `small` 8 dp, buttons use their own shape |
| Card | 12–16 | 12–16, continuous corners | `medium` 12 dp / `large` 16 dp |
| Sheet, dialog, panel | 16–24 | system sheets | `extraLarge` 28 dp |

Nested radius: inner = outer − padding between them, and never below 4 unless the inner element is square. One radius per element size across the screen.

## Elevation

- Prefer surface steps plus a separator.
- In light mode, shadows stay gray, diffuse and short. Never tinted.
- Floating chrome over content uses the platform's material or tonal surface, not a fake glass of white at 10% opacity.

## Icons

| Platform | Set | Size |
|----------|-----|------|
| Web | the project's set (Lucide, Heroicons, Phosphor, Material Symbols), one only | 16 or 20 in UI, 24 in navigation, one stroke width |
| iOS | SF Symbols | follows the text style beside it |
| Android | Material Symbols, one style (outlined, rounded or sharp) | 24 dp, 20 dp in dense rows |

Icons share the color of the text next to them. The gap from icon to label is fixed, 8–12.

## Touch targets

| Platform | Minimum hit area |
|----------|------------------|
| Web | 24 × 24 CSS px (WCAG 2.2 AA), 44 × 44 for touch-first screens |
| iOS | 44 × 44 pt |
| Android | 48 × 48 dp |

The visible control may be smaller. The hit area may not.

## Motion

| Use | Duration |
|-----|----------|
| Hover, press, toggle | 100–200 ms |
| Menu, popover, tooltip | 150–250 ms |
| Sheet, page, layout change | 250–400 ms |
| Stagger between items | 30–50 ms, six items at most |

- One easing curve across the screen. On the web, an ease-out such as `cubic-bezier(0.2, 0, 0, 1)`. On native, the system's default springs or the theme's motion tokens.
- Enter by rising 4–12 and fading in. Press by scaling to about 0.97.
- With reduced motion on, replace movement with a fade or no animation.
