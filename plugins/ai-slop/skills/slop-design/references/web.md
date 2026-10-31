# Web

For Nuxt, Vue, Tailwind and TypeScript, and for React and plain HTML and CSS. Read this with [slop-signs.md](slop-signs.md) and [tokens.md](tokens.md).

## Where the design lives

- **Tailwind 4:** the `@theme` block in the main CSS file (`--color-*`, `--font-*`, `--radius-*`, `--spacing`). **Tailwind 3:** `theme.extend` in `tailwind.config.{js,ts}`.
- **Nuxt:** `app.config.ts` (Nuxt UI's `ui.colors.primary` and `ui.colors.neutral`), `assets/css/main.css`, `nuxt.config.ts` (fonts and color-mode modules), then `layouts/`, `pages/` and `components/`.
- **Vue:** the `<style scoped>` blocks and CSS modules of the screen's SFCs.
- **React:** `globals.css` (shadcn's `--primary`, `--radius` and friends), a theme object (MUI `createTheme`, Chakra, styled-components), then the page and its components.
- **Plain HTML and CSS:** `:root` custom properties, then the stylesheets the page links.

## Signs to search for

| Sign | What it looks like in code |
|------|----------------------------|
| Hue gradient | `bg-gradient-to-*` or `bg-linear-to-*` with `from-purple-*`, `from-violet-*`, `from-indigo-*`, `via-fuchsia-*`; `linear-gradient(` between two hues |
| Gradient text | `bg-clip-text text-transparent`, `-webkit-background-clip: text` |
| Glow | `shadow-[0_0_…]`, colored shadows such as `shadow-violet-500/50`, `drop-shadow-[…]` on icons, `box-shadow: 0 0 24px rgba(…)` |
| Glass everywhere | `backdrop-blur-*` with `bg-white/10 border-white/20` on cards that sit on a plain page |
| Off-grid values | arbitrary values such as `mt-[13px]`, `p-[7px]`, `w-[347px]`, `text-[15.5px]`; inline `style` margins |
| Radius soup | `rounded-full` on cards and inputs, `rounded-xl`, `rounded-2xl` and `rounded-3xl` on siblings |
| Shouty type | `font-black` or `font-extrabold` headings, `uppercase tracking-widest` labels, `tracking-tight` on small text |
| Idle motion | `animate-pulse`, `animate-ping`, `animate-bounce` on things that aren't live; `transition-all`; `hover:scale-105`; `hover:-translate-y-1` on cards |
| No reduced motion | animations with no `motion-reduce:` variant and no `prefers-reduced-motion` query |
| Half a dark mode | `dark:` on some elements only; `text-white`, `bg-black` or hex values that ignore the theme |
| Emoji as icons | emoji in templates, JSX, nav arrays and data files that feed cards |
| Lost focus | `outline-none` or `focus:outline-none` with no `focus-visible:` style |
| Hover-only actions | controls that appear only on `:hover`, which touch screens never trigger |
| Stock theme | a shadcn, Nuxt UI or MUI theme with only the primary color changed; Inter loaded with no reason given |

The site-wide landing stack (centered hero, logo marquee, three equal feature cards) is also a `/slop-audit` finding. Here, fix it only on the screen under review.

## Pass notes

- **Spacing:** Tailwind's default scale is the 4 px grid (`p-4` is 16 px). Replace arbitrary values with scale steps. Cap content width with one `max-w-*` per layout, not per section.
- **Color:** define the roles from [tokens.md](tokens.md) as CSS variables, once for light and once for dark (`@theme` in Tailwind 4, `:root` and `.dark` for shadcn, `app.config.ts` for Nuxt UI). Components use the role utilities (`bg-surface`, `text-muted`) and never palette steps such as `bg-slate-800`.
- **Icons:** one set, the project's own (`lucide-vue-next`, `lucide-react`, Nuxt Icon's `i-lucide-*`, Heroicons). One size class per context (`size-4` or `size-5`) and one stroke width. Icon-only buttons get `aria-label`. Decorative icons get `aria-hidden="true"`.
- **Copy:** sentence case for labels and buttons, unless the project documents another style.
- **Type:** load fonts through the framework (`@nuxt/fonts`, `next/font`) or self-host them. Use `tabular-nums` for figures and `text-balance` for short headings. Body text is 16 px. Use `rem` so browser zoom and the user's font size work.
- **Layout:** check 375 px and 1440 px at least. Stack in reading order on narrow screens. An app shell spans the whole window, with side navigation and content that stretches, not a narrow centered column.
- **Details:** buttons, links and inputs get `hover`, `focus-visible`, `active` and `disabled` states from the palette. Hit areas reach 24 × 24 px, and 44 × 44 on touch-first screens.
- **Visuals:** `<img>` and `<NuxtImg>` get real `alt` text, fixed dimensions and a format such as WebP or AVIF.
- **Motion:** name the properties (`transition-colors`, `transition-[transform,opacity]`). Animate only `transform` and `opacity`. Wrap entrances in `motion-safe:`, or add a `prefers-reduced-motion: reduce` rule. In Vue, keep `<Transition>` durations within the token ranges.

## How to audit

1. **Code.** Start at the route (`pages/…`, `app/…/page.tsx`, the HTML file), follow its components and layouts, then the styles and tokens they read. Search for the signs above.
2. **Screenshots, optional.** Use a browser tool you already have, such as Playwright MCP or a preview tool. Or, if `playwright` or `@playwright/test` is in the project's dependencies and the app runs locally:

   ```
   npx playwright screenshot --viewport-size="1440, 900" --full-page --color-scheme=dark http://localhost:3000/dashboard slop-design/before/dashboard-1440-dark.png
   ```

   Repeat at 390 px wide and in light mode. Check `npx playwright screenshot --help`, because flags change between versions. If Playwright isn't installed, ask before you install it or its browsers. For a live site with no repo, review the screenshots and the served HTML, and say that the fixes are a proposal for whoever owns the code.
3. **Checks.** Run the project's scripts from `package.json`: typecheck (`nuxi typecheck`, `vue-tsc`, `tsc --noEmit`), lint, build, and visual or component tests if they exist. Check contrast for each text role in light and dark.
