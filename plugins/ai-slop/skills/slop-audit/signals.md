# AI slop signals

The checklist for `/slop-audit` and `/slop-rewrite`. Each skill keeps an identical copy of this file, so edit both; `scripts/check-manifests.py` fails if they differ. Project rules (CLAUDE.md, AGENTS.md, KB, voice docs, DESIGN.md) override anything here. The examples are illustrative.

## Sentence-level tells

| Signal | What it looks like | Fix direction |
|---|---|---|
| Em dashes | `—` in rendered copy or metadata. Count them. | A comma, colon, parentheses, or two sentences |
| Negative parallelism | "It's not X, it's Y." "X, not Y." "Speed is a requirement, not a feature." "Answers, not noise." "Not only… but also." "It's not just about X, it's about Y." It also spans sentences: "This is not a bug. This is what X is." | State the positive claim plainly |
| "No X, no Y, no Z, just W" | "No ads, no tracking, no clutter, just your notes." | Keep the one "no" that matters, or say what the product does |
| Rule of three | Triplets by default: "design, build, and run", "simple, fast, and secure", "load quickly, work everywhere, and stay easy to maintain". Every blurb or meta description shaped as A, B and C. | Keep the one or two items that are true and specific |
| Slogan or aphorism closers | A one-line maxim ending a card, section or bio: "Same tools. Better results." "If it slows you down, we remove it." "so every release has a story, not just a number" | Cut it, since the paragraph already made the point |
| Boast closers | "We know how to make software fast." "It's caught real bugs." "Making the internet better for everyone." | Replace with one specific thing that was done |
| Authenticity tics | "honest", "real problems", "real money", "actually works", "no fluff", "genuinely" | Delete it and show the quality instead |
| Filler lines | Subtitles that restate the heading or say nothing: "Check out what we've been up to lately." "Credentials that speak for themselves." "Top insights and essential guides for modern teams." | Cut it, or replace it with a fact |
| Filler words | actually, really, just, basically, simply, truly | Delete unless the word carries meaning |
| Clichés | "for the long haul", "baked in", "from the ground up", "end to end", "under one roof", "six months later", "headquartered", "growing customer base", "passionate about" | Plain words |
| Inflated vocabulary | leverage, robust, seamless, empower, elevate, cutting-edge, delve, comprehensive, holistic, streamline, unlock, journey, landscape, ecosystem. Significance words: testament, pivotal, crucial, vital, underscores, showcasing, enduring, indelible mark, tapestry, interplay, intricate, vibrant, nestled, in the heart of, groundbreaking, renowned, fostering. Academic words: empirical, heuristic, deterministic, ubiquitous, supplant | The word you'd say out loud |
| Copula avoidance | "serves as", "stands as", "boasts", "features", "offers" where "is" or "has" would do: "The platform serves as a solution that boasts monitoring." | "is", "has", or the verb for what it does |
| Wordy filler phrases | "in order to", "due to the fact that", "at this point in time", "has the ability to", "in the event that", "it is important to note that" | "to", "because", "now", "can", "if", or cut |
| Hedging | "could potentially", "it could be argued that", "may possibly", "arguably" | Commit to the claim, or cut it |
| Unnecessary prefixes | "Note:", "Important:", "Please note that", "It's worth mentioning that" | Drop the prefix; the sentence works without it |
| Trailing -ing analysis | A clause tacked on to sound insightful: "…, highlighting its commitment to quality", "…, underscoring…", "…, ensuring teams can…", "…, reflecting broader trends" | Cut it, or state the actual consequence |
| Vague attributions | "Experts argue", "industry reports show", "observers have noted" | Name the source, or cut the claim |
| False ranges | "From X to Y" spanning things that aren't on one scale: "everything from automated testing to seamless deployment" | Say what it actually covers |
| Upbeat endings | "The future looks bright." "Exciting times lie ahead." "It continues to evolve." "A step in the right direction." | End on a concrete fact, or stop |
| Conclusion signposts | "In conclusion", "To summarize", "As we have seen", "Overall" | Cut the signpost and the summary that follows it |
| Résumé voice | "Engineered…", "Spearheaded…", "hardened the security layer", "applied deep domain expertise to make the output actually useful" | Say what the product does for the reader |
| Spec-fragment lists | "Simple interface, team sharing, file uploads." | One sentence about the most useful thing |
| No contractions | A whole page in "do not", "it is", "we would" | Use contractions everywhere except legal text |
| Staccato fragments | "They shipped it. In a weekend. With two people." | One ordinary sentence |
| Overused hinge words | One word carrying a page or the whole site: "honest" 6 times, "worth" 9 times, a brand metaphor 5 times | Keep only the uses that carry a claim |

## Chatbot artifacts

- **Assistant leftovers.** "Great question!", "Certainly!", "Here is a…", "I hope this helps", "Let me know if you'd like me to expand", "You're absolutely right". Delete them.
- **Knowledge-cutoff disclaimers.** "As of my last update", "based on available information", "while specific details are limited". State the fact with its date, or cut it.
- **Flattery of the reader or the subject.** Praise that carries no information. Cut it.

## Formatting tells

- **Mechanical bold.** Bold on every key phrase, or lists of "**Header:** text" items. Keep bold for real emphasis, and turn inline-header lists into plain lists or prose.
- **Title Case Headings** where the project otherwise uses sentence case.
- **Emoji on headings and bullets** as decoration.
- **Curly quotes in Markdown or code** (“ ” ‘ ’), usually pasted from a chat window. Use straight quotes.

## Developer-text tells

- **Buzzword stacks.** "A modern, lightweight, blazing-fast, developer-friendly CLI", "robust, scalable, battle-tested, enterprise-grade". Keep one or two real qualities and be specific about them.
- **Docs that restate the signature.** "This function takes X and returns Y" when the signature already says so. Document only non-obvious behavior, limits and gotchas.
- **PR and commit padding.** "This PR addresses the issue where…", "This commit implements the functionality for…". Say what changed: "Fix race condition in queue drain".

## Structure tells

- **Template skeletons.** Every card or section has the same shape: an icon, a "…First" title, two sentences, then a slogan. Six-tile values grids. "Key takeaways", "The future of X", "Challenges and future outlook" and "Learn more" sections.
- **Repeated summaries.** The same point made in the hero, the intro, a section and the closer.
- **Back-to-back duplication.** A page hero that repeats the bio directly beneath it.
- **Repeated headings across pages**, like "Secure by Design" on one page and "Secure by Default" on two others.
- **One tagline everywhere.** The same positioning sentence in the hero, about page, footer, meta tags, JSON-LD, `llms.txt` and manifest. Count how many times it appears.

## Claims and numbers

- **Unmeasured figures.** "Handles thousands of jobs", "thousands of daily orders", "2-10x faster", invented percentage splits. If neither the repo nor live data backs the number, ask the owner about it.
- **Absolutes.** "Zero hallucinations", "100% consistent", "on everything we ship", "every screen you own".
- **Vanity counts.** Code-size metrics offered as proof of quality: "40 components, 12 hooks, 60 color tokens", "30+ ARIA attributes", "20 meta tags per page". Keep numbers a reader cares about, like "200 redirects kept their search rankings".
- **Unverifiable practice claims.** "security reviews on everything we ship", "performance budgets on every build".
- **Credit for platform features.** Standard Shopify or WordPress features described as if the author built them.
- **Stale time words.** "Recently launched", "new", "latest", "just shipped", year-vs-year comparisons, hard-coded "New" badges, a "Latest" section that isn't the latest.

## Positioning tells

- **Self-contradiction.** "We only build our own products," above a list of client websites
- **Services the owner doesn't offer.** Copy implying consulting, speaking, hiring or "contact sales". Lead-capture fields (Company, a `you@company.com` placeholder) on a site that says there's no sales team.
- **Hobby framing next to real production work**, such as "hobby projects that turned into real businesses".
- **Padded lists.** Tech walls that include tools the product doesn't use, concepts listed as if they were tools ("REST APIs", "Rate Limiting", "AES-256 Encryption"), table-stakes skills, and the same list repeated on three pages.
- **Missing the real work.** Copy that names older or generic work and leaves out the owner's current products.

## Visual tells

- **The landing-page stack.** A full-viewport centered hero with two buttons and a bouncing chevron, then a three-card icon grid, then a scrolling tech-logo marquee, then badged feature cards, then a contact banner. Each block is fine alone, but together they read as a template.
- **Decorative pills and badges** that repeat the heading, like "Certified" on every card under "Certifications", or "Strategy / Craft / Delivery" labels.
- **Stock icon tiles.** Gradient squares holding generic icons that don't fit the subject, such as a rocket for a database migration.
- **Default AI palettes.** Purple or indigo gradients, glassmorphism, gradient text, an emoji on every heading.
- **Fix direction.** Show the real product (screenshots, app icons, photos), cut the marquee and the chevron, and let one strong section replace three generic ones.

## Metadata tells

- Meta descriptions, JSON-LD descriptions and `llms.txt` summaries built from the boilerplate tagline or a buzzword pair ("scalable, secure").
- Descriptions that promise content the site doesn't have, such as "practical tutorials on Python, Go and Rust" on a blog with one Python post.
- `llms.txt` or JSON-LD implying services the owner doesn't offer.
- A mismatched OG image or card type, like a square image paired with the large card, or an OG component that's never wired up.

## Not tells (don't flag these)

- House-style choices the project documents.
- Em dashes inside quoted source material or code comments.
- Formal tone, missing contractions and boilerplate on legal pages. Check those pages for wrong statements instead.
- A list of three when there really are three things.
- Precise technical detail. Specific writing is the opposite of slop.
- Typographic (curly) quotes in rendered site copy whose style uses them.

*The sentence-level, chatbot and formatting signals draw on [Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing), maintained by WikiProject AI Cleanup.*
