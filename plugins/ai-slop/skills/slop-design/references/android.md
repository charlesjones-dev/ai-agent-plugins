# Android

For Jetpack Compose first and XML views second, following Material 3. Read this with [slop-signs.md](slop-signs.md) and [tokens.md](tokens.md). On Android the theme's tokens win: color scheme roles, the type scale, shape tokens, window size classes and Material components. Most Android slop is code that bypasses them.

## Where the design lives

- **Compose:** `ui/theme/Color.kt`, `Theme.kt` (the `MaterialTheme` call with its color scheme, typography and shapes), `Type.kt`, and any `Shape.kt` or `Dimens.kt`.
- **XML:** `res/values/colors.xml`, `themes.xml` and its `values-night` twin, `dimens.xml`, `styles.xml`, `res/font/`, `res/drawable/` and `res/layout/`.
- **Manifest:** `android:screenOrientation` and `android:resizeableActivity` on each activity.
- **The screen:** a `@Composable` screen function and its children, or a Fragment or Activity with its layout XML. `@Preview` functions show which variants the author checked.

## Signs to search for

| Sign | What it looks like in code |
|------|----------------------------|
| Template theme left in place | `Purple80`, `PurpleGrey80`, `Pink80`, `Purple40` in `Color.kt`; `purple_500`, `purple_700`, `teal_200` in `colors.xml`. With dynamic color on, this purple shows only on Android 11 and older and in previews, so check both |
| Hard-coded color | `Color(0xFF8B5CF6)` inside composables; `android:textColor="#FFFFFF"`; `Color.White` text on a custom surface; any color that doesn't come from `MaterialTheme.colorScheme` or a `?attr/` |
| Dark mode dodged | a theme that ignores `isSystemInDarkTheme()`; no `values-night` folder for XML themes; `AppCompatDelegate.MODE_NIGHT_NO` |
| Gradient and glow | `Brush.linearGradient(listOf(purple, blue))` on backgrounds, buttons or text; `Modifier.shadow(…, spotColor = …)` with a hue; `blur()` blobs; gradient `<shape>` drawables |
| Shadow on everything | large elevations on every card, where M3 uses tonal surface containers |
| Off-grid values | `padding(13.dp)`, `Spacer(Modifier.height(37.dp))`, `17.dp`; `padding(top = 24.dp)` to clear the status bar |
| Fixed type | `fontSize = 15.sp` in each composable instead of `MaterialTheme.typography`; `android:textSize` in `dp`, which never scales |
| Radius soup | `RoundedCornerShape(13.dp)`, `20.dp` and `CircleShape` on sibling cards instead of `MaterialTheme.shapes` |
| Emoji as icons | `Text("🔥 Trending")`, emoji in `NavigationBarItem` labels or icons, emoji in string resources |
| Mixed icons | filled and outlined icons mixed at random, PNG icons from other sets, icons tinted in their own colors |
| Flat hierarchy | every action a filled `Button`; `Toast` for messages that belong in a `Snackbar` |
| Foreign patterns | an iOS back chevron with a "Back" label; a hamburger drawer for three to five top destinations on a phone; a custom top bar instead of `TopAppBar`; a bottom bar stretched across a tablet; hover-only actions; native screens rendered in a WebView |
| Insets ignored | content under the status or navigation bar; `Scaffold { _ -> … }` that drops the inner padding; reliance on `windowOptOutEdgeToEdgeEnforcement`, which apps targeting Android 16 can no longer use |
| Phone-only layout | `screenOrientation="portrait"`, which Android 16 ignores on screens 600 dp wide and up for apps targeting it; a phone column stretched across a tablet; `LocalConfiguration.current.screenWidthDp` checks instead of window size classes |
| Small targets | `Modifier.size(24.dp).clickable` on icons; turning off the minimum touch target |
| Text that can't grow | `maxLines = 1` with an ellipsis on important labels; fixed `height(…)` around text, which clips at 200% font scale |
| Idle motion | `infiniteRepeatable` pulses on static content; high-bounce springs on ordinary controls; confetti; loops that ignore "Remove animations" |
| Silent controls | `contentDescription = null` on icon-only buttons; descriptions such as "icon" or "image"; `clickable` on a `Box` with no `role` |

## Pass notes

- **Spacing:** use a 4 dp grid with 8 dp steps for most gaps. Screen margins are 16 dp on compact widths and 24 dp on medium and wider. Use `ListItem` for rows (56, 72 or 88 dp tall for one, two or three lines) instead of hand-built rows.
- **Color:** read only `MaterialTheme.colorScheme` roles in Compose, or theme attributes such as `?attr/colorSurfaceContainer` in XML. Use dynamic color (`dynamicLightColorScheme`, `dynamicDarkColorScheme`) on Android 12 and later when the brand allows it. Build the fallback scheme from the brand's seed color, for example with Material Theme Builder, never from the template purple. Show depth with the `surfaceContainer` steps. Put extra roles such as success in the theme, not inline.
- **Icons:** use Material Symbols in one style (outlined, rounded or sharp), with one weight and one fill rule. The navigation bar shows the filled icon for the selected item and the outlined icon for the others. Keep icons at 24 dp, and let `Icon` take `LocalContentColor`.
- **Copy:** sentence case for titles, buttons and labels, as Material does. A `Snackbar` holds a short message and at most one action.
- **Type:** use `MaterialTheme.typography` roles in `sp`. Put a brand face in the `Typography` object (`res/font` or downloadable fonts), and leave the default type in place without a reason to change it. Use `fontFeatureSettings = "tnum"` for figures. Check at 200% font scale. Android 14 and later scale large text less than small text, but layouts must still allow growth.
- **Layout:** use a `Scaffold` with a `TopAppBar`, and a `NavigationBar` on compact widths or a `NavigationRail` on medium and wider (`NavigationSuiteScaffold` switches for you). Read `currentWindowAdaptiveInfo().windowSizeClass`. Use `ListDetailPaneScaffold` for list and detail screens on large displays. Call `enableEdgeToEdge()`, and pad content with the `Scaffold` inner padding or `WindowInsets.safeDrawing`. Keep predictive back working: no custom swipe-back gestures.
- **Details:** use `MaterialTheme.shapes` (`extraSmall` 4, `small` 8, `medium` 12, `large` 16, `extraLarge` 28 dp). Show button hierarchy with `Button` for the one primary action, then `FilledTonalButton`, `OutlinedButton` and `TextButton`. Prefer lists to stacks of cards. Use an extended FAB only for the screen's main action. The default ripple is the pressed state, so don't add a scale effect as well.
- **Visuals:** show real content. An empty state is one icon, one line and one action. Give images a `ContentScale`, a placeholder and a size.
- **Motion:** use the theme's motion tokens or the Compose defaults (`animate*AsState`, `AnimatedVisibility`, `AnimatedContent`). Use about 100–200 ms for feedback and 250–400 ms for transitions. When `ValueAnimator.areAnimatorsEnabled()` returns false ("Remove animations" is on), stop loops and skip large movement. Use haptics through `LocalHapticFeedback` or `performHapticFeedback` for confirmations and errors only.

## How to audit

1. **Code.** Find the screen's composable or its Fragment and layout XML. Follow the child composables, the theme files and the resources. Search for the signs above.
2. **Screenshots.** Ask the user for screenshots if they have none to attach: light and dark, a phone and a tablet or unfolded foldable, and a large font scale if they can. These, with the code, are enough.
3. **Previews.** Read the `@Preview` functions. If the screen has none for dark mode, font scale or screen size, offer to add the multipreview annotations `@PreviewLightDark`, `@PreviewFontScale` and `@PreviewScreenSizes`, so the user can check every variant in Android Studio.
4. **Device or emulator, optional.** Only when `adb` is installed and a device or emulator already runs the app on the screen under review:

   ```
   adb devices
   adb -s <serial> exec-out screencap -p > slop-design/before/home-light.png
   adb -s <serial> shell cmd uimode night yes
   adb -s <serial> shell settings put system font_scale 2.0
   ```

   Before you change a setting, read its current value (`cmd uimode night`, `settings get system font_scale`), and set it back when you finish. Don't start an emulator or install a build unless the user asks.
5. **Checks.** Run the project's Gradle tasks if the user agrees, such as `./gradlew :app:lintDebug` and a debug build. Run screenshot tests (Roborazzi, Paparazzi or Compose Preview Screenshot Testing) if the project has them. TalkBack and Accessibility Scanner need a person, so list them under "Not verified".
