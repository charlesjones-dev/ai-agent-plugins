# Slop signs

The platform-neutral checklist for `/slop-design`. Each line pairs a sign with its fix, grouped by the pass that fixes it. The platform references add the signs that only show up in that platform's code. Project rules and documented house style override this file.

## Spacing

- One-off values that sit off the grid, such as 13, 7 or 37 → the nearest step of the scale, or a named token
- Sibling rows or cards with different heights, paddings or gaps → one height, one padding, one gap
- A label closer to the group above than to its own items → less space inside a group, more between groups
- Icons, labels or numbers that drift out of their column → a fixed icon box and one leading edge
- A nudge (offset, translate, negative margin) to fix one alignment → fix the layout that caused it
- A large empty band in one place and cramped content in another → one rhythm across the screen

## Color

- A hue-to-hue gradient (purple to blue, violet to pink, teal to indigo) behind the page, across cards and buttons, or on the active item → a single neutral surface, with the accent saved for the spots that carry meaning
- Gradient text in a headline, figure or wordmark → solid primary text
- A colored glow or colored shadow around cards, buttons, icons or pills → depth from surface steps and a separator, or a small neutral shadow
- Blurred color blobs or radial washes behind content → remove them
- Neon or saturated borders → a separator at low contrast
- Five near-identical tints for text → two or three text roles from one ramp
- Emphasis everywhere, so the eye has no place to start → one accent, spent on one or two spots per screen
- Hard-coded hex or RGB values in views → semantic roles from the theme
- A dark mode made by inverting colors, or no dark mode where the platform expects one → roles defined for both appearances
- An accent with text on it that fails contrast → a darker accent, or dark text on it

## Icons

- Emoji used as navigation icons, list markers, status or label decoration (🚀 📊 🔥 ✨ 💡 ⚡) → icons from one set, or nothing
- A sparkle on anything that touches AI → remove it, or use a plain icon that says what happens
- Icons from two or three sets, or at many sizes and weights → one set, one size per context, one weight
- Icons in their own bright colors → the same color as the text next to them
- An icon on every card title and every heading → keep only the icons that help someone scan
- Icon-only controls with no accessible name → a label for assistive technology

## Copy

- A greeting headline ("Welcome back, Sam! 👋") → the name of the place or the period
- Exclamation marks in interface text → plain statements
- Hype words (supercharge, seamless, unlock, effortless, magic, next-level) → what the thing does
- Wordy labels and placeholders ("Search anything...", "Click here to get started") → short labels ("Search", "Start")
- A vague button ("Submit", "OK", "Continue") where the action has a name → the action ("Save changes", "Delete photo")
- A change with no reference ("+12%!") → what it compares to ("+12% vs last week")
- Claims no one can check ("Loved by 10,000+ teams", "10x faster") → ask; keep them quiet and specific if real, remove them if not
- Fake-looking data ("$123,456", "Lorem ipsum", "John Doe", "[X]") → plausible names and numbers
- Badges everywhere ("NEW", "PRO", "Beta 🚀") → remove them, or keep one quiet text badge where the product needs it
- Labels in all caps with wide letter spacing → the platform's normal capitalization

## Type

- Headings at the heaviest weights, everywhere → a lighter weight, with size and color for hierarchy
- More than four or five sizes, or more than three weights, on one screen → a handful of roles from the type scale
- Fixed text sizes that ignore the user's text size setting (native) or zoom (web) → the platform's scalable type roles
- Tightened tracking at body and caption sizes → default tracking; tighten only big display text
- Figures in mixed formats ("$48,210" next to "$1,204.5") or proportional digits in columns → one format, tabular digits
- Italic or bold used for emphasis in every second line → color or position for hierarchy
- Text squeezed to fit (shrink-to-fit, one line with an ellipsis on important text) → let it wrap, or shorten the copy

## Layout

- The landing stack on an app screen: a centered hero, a badge pill above the headline, two buttons, a row of equal feature cards → the platform's own screen pattern, with the content first
- A row of identical cards that each hold the same kind of content → one main block, with smaller supporting blocks of another kind
- Three or more competing primary buttons in one region → one primary action, at most one secondary
- An app squeezed into a narrow centered column on a wide window → the platform's adaptive layout
- Web patterns in a native app, or one OS's patterns on the other → the platform's navigation, sheets, dialogs and controls (see the platform reference)
- Content under system bars, notches or the home indicator → content inside the safe area or insets, backgrounds may run behind

## Details

- Every element a pill, or radii that change from card to card → radius by element size, inner radius = outer radius − padding
- Glowing capsules around counters, tier names, keyboard shortcuts and states → plain muted text, a small dot, or a keycap for a shortcut
- Charts with rainbow series, glowing bars or decorative gradients → muted axes and grid, one accent on the series that matters
- A sparkline, mini chart or icon decorating every stat card → a label, a figure and its change
- Two charts of the same size competing → one main chart, the rest as a list or a short table
- A selected state shown with a gradient and a glow → a small surface step or the accent on the marker
- Missing pressed, focus, disabled or selected states → states from the palette, with a visible focus indicator
- A logo built from a sparkle inside a gradient square → the wordmark in the interface family, or a flat mark in one color (ask before you change a logo)
- Blank or spinner-only empty, loading and error states → one line that says what happened and one action

## Visuals

- Glossy 3D shapes, orbs, nebulas, liquid chrome, glowing grids → the product itself or its real content
- Robot mascots, neon brains, circuit-board traces or holograms to stand for an AI feature → the output the feature produces
- Words, buttons or a logo rendered inside a picture → live text in the interface over a picture with no words
- An image with hard edges on a background of a different color → an image that matches the surface, or a frame that belongs to the layout
- A decorative image on every section → one image where it helps, often none

## Motion

- Pulsing, pinging, shimmering or breathing elements that aren't live → static
- Bouncy springs and overshoot on ordinary controls → one calm curve or spring
- Cards that scale or jump on hover or press → a color or surface change on hover, a slight scale-down on press
- Elements sliding in from several sides when the screen opens → at most one short entrance for the main content
- Parallax and elements that float while scrolling → a still layout
- Animating layout properties (width, height, position, margins, large blurs) → transform and opacity
- Motion that ignores the reduced-motion setting → a fade or no animation when it is on
- A haptic on every tap → haptics only for events that matter

## Unmade decisions

These aren't slop on their own, but they are where a cleaned-up screen ends up when no one decides. Check for them after the passes.

- A component library's stock theme with only the primary color changed → a palette and type chosen from the direction
- A headline that would fit a competitor → the product's own nouns and verbs
- A hero image slot left blank or filled with generic stock → a product preview, or a sized slot with a description
- The same palette, type and layout as the last screen this agent cleaned up → a direction derived from this product

## Not slop

- System controls, SF Symbols, Material Symbols and the platform's default font, used as the platform intends
- A gradient, color or illustration style that the user confirms the brand owns
- A dense screen for experts, such as a trading or monitoring view, when the density serves the task
- Documented house style, even when it matches a sign above
