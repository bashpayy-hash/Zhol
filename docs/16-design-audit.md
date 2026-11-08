# 16. Design audit, 8 November 2026

Two rubrics the owner pointed to:
- **Superfuture Design Review** (github.com/Superfuture/design-review): ten dimensions; findings ranked blocking, important, polish.
- **Emil Kowalski's skills** (github.com/emilkowalski/skills, `apple-design` and `review-animations`): Apple's fluid-interface principles and a strict motion standard.

Both were read from their public repositories and applied by hand. Their telemetry ping and paid tier were not used.

Evidence:
- **Pages:** nine pages at 390×844 and 1440×900.
- **WCAG:** axe-core 4.10 (wcag2a, wcag2aa, best-practice) on eight pages.
- **Contrast and tap targets:** measured on every visible text element and control.
- **Motion:** read in `site/assets/zhol.css`, `reveal.js` and `map.js`.
- **Renders:** looked at frame by frame (map entrance, week player, fly-to).
- **The owner's own rules:** VISION.md still governs. Where a rubric disagrees with it, VISION.md wins and the conflict is noted below.

## Fixed in this pass

| Severity | What | Fix |
|---|---|---|
| Blocking | Country codes on the beta page: brick red on espresso, 1.99:1 (WCAG AA needs 4.5:1) | `.slide.dark .cc` uses the light red for dark backgrounds |
| Blocking | "Source" links in light quote cards on a dark slide took the dark-slide red: 2.51:1 | `.slide.dark .clip a` keeps the page red, 6.9:1 |
| Blocking | Kickers on dark cards (Story, Audience): `--red-on-dark` #e9785e on #4a372d, 3.90:1 | `--red-on-dark` is now #f09580: 4.97:1 on dark cards, 6.18:1 on espresso |
| Important | Answer pages had no h1 (axe: page-has-heading-one) | The answer headline is the h1, same size as before |
| Important | Hours table on the beta page had an empty header cell | A screen-reader label, "Day" |
| Important | Tap targets on a phone: logo 22 px, footer links 16 px, "Open the full answer" 29 px, disclosure rows 21 px, selects 43 px | 44 px minimum: padding and hit areas, with no visual change; the language pill keeps its look with a larger invisible hit area |
| Important | Arrows ("Milano -> München") in the beta corridor picker and the sample message (VISION: no small arrows) | Shown as "Milano – München" |
| Important (motion) | Map points were positioned with `left`/`top` on every zoom frame, which means layout work each frame | Positioned with `transform: translate3d()`; a ResizeObserver keeps them in place |
| Polish (motion) | Hover lifts and the map-point hover were not gated to a mouse, so a tap triggers them on touch | `@media (hover: hover) and (pointer: fine)` |
| Polish (motion) | Buttons pressed down with no transition | `transform var(--dur) var(--ease)` on `.btn` |
| Polish (motion) | The "next event" ping looped forever, a slow oscillation Apple warns against | It pulses three times, then rests |
| Polish (motion) | While "Play the weeks" runs, the place list replayed its entrance keyframes every 1.5 s | No entrance animation while playing |
| Polish | The phone menu was cut off at the right edge with no hint it scrolls | A soft fade at the edge |

After the fixes:
- axe reports **no violations** on the eight pages;
- the page checklist (`tests/browser/pages_check.js`) passes;
- the survey flow (`tests/browser/survey_flow.js`) passes.

## Still open, ranked

**Important**
1. **Long pages on a phone.** Story is about 14,200 px tall, Audience 13,900 px, Beta 13,800 px: 16 to 17 screens each. This works against the owner's "introduce it gradually".
   - Fix: give them what the home page got. Each section shows a title and one number, opens in place, and the number walls stay folded.
2. **Too many type sizes.** The pages use 33 distinct sizes (11 to 82 px); the rubric asks for 5 to 7 steps.
   - Fix: a token scale of 13, 15, 17, 20, 26, 34 and 46 px plus the display clamp. Map every `font-size` to it.
3. **The radar shows stale data.** It is from 7 November, with 0 sources and 0 news articles. The Story strip says "0 come from the news … read twice a day".
   - This is content, not layout, but it is the first thing a careful reader will notice. Fix the scheduled refresh first.
4. **Raw URLs in the beta sample message.** Long links break across lines in the WhatsApp bubble.
   - Fix: name the source (Bison Futé, Land Tirol, WKO) and keep the link behind it.

**Polish**
5. **Accordion timing conflicts with VISION.md.** Answer blocks open over `--dur-card` (320 ms), animating `grid-template-rows`.
   - Emil's standard says UI motion under 300 ms on transform and opacity only.
   - VISION.md sets 320 ms for cards, so it stays. The height animation is the usual trade-off for revealing content in place.
6. **Close could be faster than open.** Opening and closing a block take the same time; a faster close (e.g. 200 ms) would feel more responsive.
7. **Sticky header style.** It is an opaque bar with a 1 px rule. Apple's pattern is a translucent bar with a soft edge where content scrolls under. Optional; it would change the paper look VISION.md sets.

## Rubrics compared with what VISION.md already requires

- **Agree:**
  - one typeface (Inter);
  - no capitals by CSS;
  - custom strong ease-out (`cubic-bezier(.22,1,.36,1)`) and no `ease-in`;
  - entrances from `translateY` plus opacity, never `scale(0)`;
  - stagger of 70 ms;
  - `prefers-reduced-motion` honoured everywhere;
  - map zoom animated from the current view (Apple's interruptibility rule);
  - 44 px buttons.
- **Disagree, VISION.md kept:**
  - 320 ms for card motion (Emil: under 300 ms);
  - an opaque paper header (Apple: translucent material).

## Strengths

- **One focal action per screen.** Home, survey and radar each have one red primary button and one ghost button.
- **Motion has a reason.** The map's sweep shows reading west to east. The week player and fly-to explain where things are. Nothing animates on a frequent keyboard action.
- **Honest data states.** Every number on the home page has a source. The map says "nothing this week" instead of hiding points. Undated tensions are labelled.
