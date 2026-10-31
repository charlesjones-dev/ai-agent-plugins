# iOS

For SwiftUI first and UIKit second, following Apple's Human Interface Guidelines. Read this with [slop-signs.md](slop-signs.md) and [tokens.md](tokens.md). On iOS the system tokens win: semantic colors, text styles, SF Symbols, system margins and standard controls. Most iOS slop is code that replaces them with fixed values.

## Where the design lives

- `Assets.xcassets`: `AccentColor` and named color sets. Check that each one has a Dark appearance, and a High Contrast one where the brand needs it.
- Theme code: `Theme.swift`, `Color+*.swift`, `Font+*.swift`, a `DesignSystem/` folder, custom `ButtonStyle` and `ViewModifier` types.
- `Info.plist`: `UIAppFonts` for custom fonts, and `UIUserInterfaceStyle`. A value of `Light` there forces light mode for the whole app.
- The screen: a `View` struct and its subviews, or a `UIViewController` with its views, XIBs or storyboards. `#Preview` blocks show which variants the author checked.

## Signs to search for

| Sign | What it looks like in code |
|------|----------------------------|
| Hard-coded color | `Color(red:green:blue:)`, a `Color(hex:)` helper, `UIColor(red:…)` in views; `.foregroundStyle(.white)` on a custom background |
| Dark mode dodged | `.preferredColorScheme(.light)` on the root, `UIUserInterfaceStyle` set to `Light`, color sets with no Dark appearance |
| Gradient and glow | `LinearGradient(colors: [.purple, .blue], …)` on backgrounds, buttons or text; `.shadow(color: .purple.opacity(…), radius: 20)`; blurred circles in a background `ZStack` |
| Fake glass | white fills at low opacity with a white stroke instead of a material; on iOS 26 and later, `.glassEffect()` on cards, rows and other content |
| Fixed type | `.font(.system(size: 17, weight: .bold))` throughout; `.custom("Name", size: 16)` with no `relativeTo:`; `.lineLimit(1)` with `.minimumScaleFactor(0.5)`; fixed `frame(height:)` around text; `.dynamicTypeSize(...)` caps on whole screens |
| Emoji as icons | `Text("🔥")` in rows, `Label("🚀 Launch", …)`, emoji in tab items |
| Mixed icons | SF Symbols next to PNG icons; symbols at random point sizes; `.symbolRenderingMode(.multicolor)` everywhere |
| Magic numbers | `.padding(13)`, `.padding(.top, 47)` to clear the notch, `.offset(x: 3)` nudges, `frame(width: 350)` sized for one iPhone, math on `UIScreen.main.bounds` |
| Radius soup | a different `cornerRadius` on every card; the deprecated `.cornerRadius()` mixed with `clipShape(RoundedRectangle(…))`; inner corners that don't match their container |
| Web patterns | a hamburger menu or side drawer for two to five top destinations; a custom top bar with its own back arrow, which breaks swipe-back; custom overlays instead of `.sheet`, `.alert` or `.confirmationDialog`; toast banners; a floating action button; a marketing hero with a gradient button as the app's home screen; page-dot carousels for core content |
| Hand-built controls | a `ScrollView` of custom rows where a `List` or `Form` fits; custom toggles, checkboxes or segmented controls; every action a filled pill |
| Safe area ignored | `.ignoresSafeArea()` on content instead of on the background only; controls under the home indicator |
| Small targets | icon buttons with a 24 pt frame and no padding or `contentShape` to reach 44 × 44 pt |
| Idle motion | `.repeatForever` pulses or shimmers on static content; high-bounce springs on ordinary controls; no check of `accessibilityReduceMotion` |
| Haptic noise | `UIImpactFeedbackGenerator(style: .heavy)` or `.sensoryFeedback` on every tap or scroll |
| Silent controls | icon-only buttons with no `accessibilityLabel`; decorative images not hidden; `onTapGesture` on a view where a `Button` belongs, so VoiceOver doesn't announce a button |

## Pass notes

- **Spacing:** the system margins (16–20 pt on iPhone) and the default `padding()` and stack spacing come first. Add a few named constants for the rest. Use `@ScaledMetric` for spacing and sizes that should grow with Dynamic Type. `List` and `Form` bring correct insets for free.
- **Color:** use semantic colors (`Color(.systemBackground)`, the grouped variants, `.primary`, `.secondary`, `.tertiary`, `Color(.separator)`). Brand colors live as named color sets with Light and Dark appearances, never as literals in views. Set `.tint()` once near the root. Let the system color the controls.
- **Icons:** use SF Symbols wherever the set covers the idea. Size symbols with the text style next to them (`.font(.body)`, `.imageScale`), not with point sizes. Keep one rendering mode per context. The tab bar picks the fill variant on its own, so pass the base symbol name. Draw custom icons as custom symbols so they scale and take weight like SF Symbols.
- **Copy:** use title-style capitalization for navigation titles, buttons and menu items, as the system apps do, unless the project uses sentence case throughout. Use sentence case for descriptions, footers and alert messages. An alert's title states the situation, and its buttons name the action ("Delete", not "OK"), with `role: .destructive` where it applies.
- **Type:** use text styles (`.largeTitle` to `.caption2`). For a brand face, use `Font.custom(_:size:relativeTo:)` so it scales. SF Pro, the system font, is the right default and is never slop. Use `.monospacedDigit()` for figures. Use `ViewThatFits` or a stack that changes axis at accessibility sizes, instead of shrinking the text.
- **Layout:** use `NavigationStack` with a large title on top-level screens, `TabView` for top destinations, and `.sheet` with `presentationDetents` for tasks. Use `NavigationSplitView` on iPad. Read size classes, not screen widths. Backgrounds may extend under the bars, and content stays in the safe area.
- **Details:** show button hierarchy with `.borderedProminent` for the one primary action, then `.bordered` and plain buttons. Use `controlSize` instead of custom frames. Use `ContentUnavailableView` (iOS 17) for empty states, `ProgressView` for loading, and `ContainerRelativeShape` for corners that follow their container.
- **Visuals:** materials (`.regularMaterial`, `.thinMaterial`) belong to chrome that floats over content. From iOS 26, standard bars, tab bars, toolbars and sheets get Liquid Glass on their own. Use `.glassEffect()` only for custom floating controls, never on content. Content images are real, not stock 3D art.
- **Motion:** use system springs (`.smooth`, `.snappy`), and always pass a `value:` to `.animation`. Use `.contentTransition(.numericText())` for changing figures. Read `@Environment(\.accessibilityReduceMotion)` (UIKit: `UIAccessibility.isReduceMotionEnabled`), and when it is on, use a fade instead of movement and stop loops. Use `.sensoryFeedback` for a completed action, a selection change or an error, not for navigation.

## How to audit

1. **Code.** Find the screen's `View` or view controller. Follow its subviews, custom styles and modifiers, the theme files and the asset catalog. Color sets keep their appearances in `Contents.json`. Search for the signs above.
2. **Screenshots.** Ask the user for screenshots if they have none to attach: light and dark, and the largest text size if they can. These, with the code, are enough.
3. **Simulator, optional.** Only when a simulator is already booted with the app on the screen under review:

   ```
   xcrun simctl list devices booted
   xcrun simctl io <udid> screenshot slop-design/before/home-light.png
   xcrun simctl ui <udid> appearance dark
   xcrun simctl ui <udid> content_size accessibility-extra-large
   ```

   Before you change a setting, read its current value (run `appearance` or `content_size` with no value), and set it back when you finish. Don't boot, create or erase a simulator, and don't build or install the app, unless the user asks.
4. **Checks.** Build with the project's scheme if the user agrees, for example `xcodebuild -scheme <scheme> -destination 'generic/platform=iOS Simulator' build`. Run snapshot tests if the project has them. If the screen has no `#Preview` for dark mode or a large Dynamic Type size, offer to add one, so the user can check both in Xcode. VoiceOver and the Accessibility Inspector audit need a person, so list them under "Not verified".
