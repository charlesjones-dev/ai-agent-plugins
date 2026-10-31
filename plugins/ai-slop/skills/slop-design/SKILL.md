---
name: slop-design
description: "Review one screen of a web, iOS or Android app for the marks of AI-generated design (hue gradients, glows, emoji used as icons, shouty copy, uneven spacing, generic cards, a template theme nobody changed) and fix it the way a designer works through a redline. Audits first and says where each sign lives, proposes a direction taken from the product and waits for the user, then fixes in ordered passes: spacing, color, icons, copy, type, layout, details, visuals and motion. Says so when the screen is already good. Follows Apple's Human Interface Guidelines on iOS and Material 3 on Android, and works from code and the user's screenshots without extra tools. Use when the user runs /slop-design, or asks to unslop, de-slop, polish or redesign a screen, page or app UI that looks AI-generated or templated."
argument-hint: "[screen, file, route, URL or screenshot] [platform=web|ios|android] [--fix]"
allowed-tools: [Read, Glob, Grep]
---

# Design slop review

AI-generated UI repeats the same choices: a purple-to-blue gradient on every surface, glows instead of depth, an emoji on every label, spacing typed by feel, and copy that shouts. On native apps it also fights the platform, with custom controls and fixed sizes where the system already has an answer.

This skill keeps the product and changes the craft. Features, content, navigation and section order stay. What changes is that someone chose each value on purpose. Quiet chrome carries the screen, and color and detail go to one or two places in the content that matter. The result should fit only this product.

## Arguments

The text typed after the command holds the arguments. In Claude Code it is inserted here: `$ARGUMENTS`. In other agents, read it from the user's message. It may be empty.

| Argument | Sets | Default |
|----------|------|---------|
| A screen name, file, route, URL or screenshot path | The screen to review | Asked, unless the conversation names one |
| `platform=web`, `ios` or `android` | Which platform reference to load | Detected from the project |
| `--fix` | Applies the proposed direction without stopping for approval, for unattended runs. It still stops when the screen is already good | Off |

Review one screen per run, or one flow of two or three closely related screens. A whole app gets a short list of its worst screens and a question about where to start.

## 1. Read the project's rules and design system

Read whichever of these exist: `CLAUDE.md`, `AGENTS.md`, `DESIGN.md`, a knowledge base (`.claude/rules/kb/`, `.claude/kb/`), and brand or style guides. Then find where the design tokens live. The platform reference lists the usual files.

- **Brand.** A real logo, brand color or typeface stays. A hue-to-hue gradient, a sparkle mark or a template theme is not brand, unless the user says so.
- **House style.** A choice the project documents is not slop, even when it matches a sign.
- **Shared tokens.** A change to a shared theme reaches every screen that uses it. List those screens before you propose one.

## 2. Pick the platform

Detect it from the target's files: `.vue`, `.tsx`, `.jsx`, `.html`, `.css` or a Nuxt or Vite config means web. `.swift` with SwiftUI or UIKit means iOS. Kotlin with `@Composable`, or `res/layout` XML, means Android.

Read [references/slop-signs.md](references/slop-signs.md) and [references/tokens.md](references/tokens.md) on every run. Then read the platform reference, and only that one:

- [references/web.md](references/web.md): Nuxt, Vue, Tailwind, TypeScript, React, plain HTML and CSS
- [references/ios.md](references/ios.md): SwiftUI first, UIKit second
- [references/android.md](references/android.md): Jetpack Compose first, XML views second

A feature built natively for both iOS and Android gets both native references and a separate audit for each. React Native, Flutter and Compose Multiplatform have no notes of their own. Follow the platform reference for each OS the screen ships on.

## 3. Gather the evidence

Locate the code behind the screen: the page or view, its child components, its styles and the theme they read. Then use whatever evidence exists, best first:

1. Screenshots the user attached.
2. Screenshots you capture. This step is optional, and the platform reference says how. Capture light and dark, default and large text, and narrow and wide where the platform has them.
3. The code alone. That is enough for an audit. Mark the findings that need a look on a device, such as contrast over a photo or text that may clip at large sizes.

Save captures in `slop-design/before/` and later `slop-design/after/` at the project root. If `git check-ignore slop-design` finds no rule, add `slop-design/` to `.git/info/exclude`, so the captures never reach a commit.

Install nothing, start no simulator or emulator, and change no device setting without asking. If a tool is missing, go on with the code and the user's screenshots.

## 4. Audit

Go through [references/slop-signs.md](references/slop-signs.md), then the signs in the platform reference. Write one line per finding: the sign, where it lives (`file:line`, or the region of a screenshot), and the fix in a few words. Group the lines by pass, so the audit becomes the fix plan.

Don't flag what the platform recommends: system controls, SF Symbols, Material components and the system font are good defaults. Don't flag documented house style.

End the audit with the name-swap test. Put a competitor's name on the screen. If it still fits, the copy, the moments and the signature detail need to change.

## 5. Decide how much to change

- **Heavy.** Signs in three or more passes, or no clear hierarchy. Run every pass with a new direction.
- **Light.** A designed screen with a few signs left. Fix only the findings, build on the brand the screen already has, and keep the palette, type and layout. Put bigger ideas in the report as suggestions.
- **Clean.** Say so plainly. Suggest at most three refinements, each with the file, the token or line, and the exact before and after values. Change nothing unless the user accepts them, and end the run there. Never redesign a good screen to make it different.

## 6. Propose a direction, then stop

Write five short lines from what the product does, as the screen, README, store listing or site describes it. Never from what is in fashion.

- **Product.** One sentence: who uses it, and the job it does for them.
- **Character.** Two or three specific adjectives, plus the material or place the product belongs to, which tints the neutrals and picks the accent. Generic praise such as polished, modern, clean, sleek or minimal doesn't count: any template could claim it.
- **Moments.** The one or two places on this screen that get color and detail, taken from the content: a chart, the current item, a photo, a progress state. Everything else stays quiet.
- **Signature.** One recurring detail tied to what the product does, applied the same way each time it shows up.
- **Scope.** The files that change, any shared token that changes and the screens it reaches, and what stays (brand, navigation, platform controls).

For example, for a tide app for small-boat sailors: *Character* exact, calm, weathered, near slate and chart paper. *Moments* today's tide curve and the wind arrow. *Signature* times in the mono face, as on a harbor board. Write fresh lines for each product. Don't reuse these.

Show the audit, the verdict, the direction and the pass plan. Then wait for the user to steer. Continue without waiting only when `--fix` is set, or when the request itself said to apply changes without a review.

## 7. Fix in passes

Run the passes in this order, and complete each one on every part of the screen before the next. The order has reasons. Rhythm changes how every later choice reads, so spacing leads. The length of a line drives its font size and its place, so the words are settled before type and layout. Imagery and animation should sit on a screen that already stands on its own, so they close the list. Take values from [references/tokens.md](references/tokens.md) and the platform reference, unless the project's own tokens are sound.

1. **Spacing.** One base grid. Equal things get equal sizes. Gaps between groups are wider than gaps within a group. Icons, labels and numbers each line up in one column. Replace one-off values with scale steps or tokens, and respect the platform's margins and safe areas.
2. **Color.** Semantic roles only: background, surface, raised surface, separator, two or three text roles, one accent and the status colors. Surfaces stay neutral. Reserve the accent for the main call to action, the current selection or a single key number. The moments may be rich. Strip out multi-hue gradients, gradient-filled text, glow effects, tinted shadows, blurred color blobs and neon outlines. Every role works in light and dark and meets the contrast minimums.
3. **Icons.** Replace each emoji that acts as an icon or ornament with a glyph from a single icon family, or delete it. Use one size and one weight, and let icons inherit the color of the text beside them. Drop icons that add nothing. Every icon-only control gets an accessible name.
4. **Copy.** Interface text only. `/slop-audit` covers the copy of a whole site. The title names the place or the period, not a greeting. Drop exclamation marks and hype words. Labels are short, and a button says what it does. A delta names its baseline, such as "vs last week". Ask about claims you can't check, and remove them unless the user confirms them. Mock data looks real. Follow the platform's capitalization, and never use all caps with wide letter spacing for labels.
5. **Type.** Use the platform's type roles, a few sizes and two or three weights. Build hierarchy mostly from size and tone, and use weight last. Use one family plus at most one partner, such as a mono for figures. Figures use tabular digits and one format. On native apps the system font is the right default. On the web, a default face that nobody chose may change to fit the character.
6. **Layout.** Keep the sections, their order and the navigation. Use the platform's own patterns instead of web patterns. Give the moments the space. Each region gets one primary action. Check the narrow and the wide layout.
7. **Details.** Corner radius follows element size, and nested corners match (inner radius = outer radius − padding). Pressed, focus, selected and disabled states exist and stay in the palette. Glowing pills and badges become quiet text. One chart leads, with one accent. Supporting data takes a smaller form of another kind, such as a list or a short table. Empty, loading and error states look designed. Place the signature detail.
8. **Visuals.** Remove decorative filler: blobs, orbs, nebulas, robots, glowing brains, stock 3D shapes. Show the product or its real content instead. If a marketing hero needs an image, leave a slot of the right size and write one sentence on what it should show, plus its alt text. Never generate paid images, and never bake text into an image.
9. **Motion.** Remove loops on things that aren't live, bouncy springs, scale-on-hover and catch-all transitions. Keep motion that explains a change. Use one curve or spring and a few durations. When the system asks for reduced motion, replace movement with a fade or with nothing. Use haptics on native apps only for events that matter.

If the work touches most lines of the screen, decide all nine passes first, then make the edit in one go with every pass in it.

## 8. Check

- Go through the audit list again. Fix each finding or say why it stays.
- Run the project's own typecheck, lint, build and UI or snapshot tests. If they can't run here, say so.
- Run the checks in the platform reference: dark mode, the largest text size, reduced motion, touch targets and contrast.
- Capture the after screenshots under the same conditions as the before ones, and compare them in pairs. Capture at most three rounds per run.
- Run the name-swap test again.

## 9. Report

Write it like a redline review:

- **Verdict:** heavy, light or clean, with the count of signs found and fixed.
- **Direction:** the five lines as approved.
- **Passes:** for each pass, what changed, with `file:line` and the old and new values.
- **Shared tokens:** each token that changed, and the other screens it reaches.
- **Screenshots:** the before and after paths, in pairs.
- **Not verified:** what still needs a device, a person or a tool that wasn't here.
- **Suggestions:** the bigger ideas you didn't apply.

Don't commit or push unless the user asks.

## Rules

- Keep the product: its name, features, data, content, section order, navigation and behavior. Filler such as lorem ipsum may become realistic sample content.
- Don't invent features, numbers, testimonials or claims.
- Don't swap one trend for another, such as glass on every surface, grain, neon or a bento grid.
- Work with the platform. A system control, text style or semantic color beats a custom one.
- Keep accessibility identifiers, test IDs, localization keys and analytics names, so tests, translations and dashboards keep working.
- Accessibility never gets worse: contrast, labels, touch targets, focus order and text scaling.
- Each product gets its own direction. Don't reuse the palette from the last run.

---

Inspired by [unslop](https://github.com/heydamir/unslop) by Damir Sokolovsky (@heydamir), licensed CC BY 4.0. This skill follows its approach (audit, direction, then ordered passes) in its own words, and adds the iOS and Android guidance.
