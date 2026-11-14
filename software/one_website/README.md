# Principia & Atlas — One Website

A single-origin, read-only research preview combining both Principia learning journeys with Atlas's accepted Phase 4 evidence workspace.

## Pages

- / — editorial home and pathways
- /learn/refrigerator/ — thermodynamics learning journey and Counterfactual Lab
- /learn/distributed-information/ — queue/retry system journey and Counterfactual Lab
- /research/ — Atlas exact-revision, provenance, and accepted research workspace

The canonical repositories remain independently authoritative. Principia owns its simulations, learning content, investigations, and release status. Atlas owns exact revisions, evidence, provenance, research decisions, and review metadata. No review status or lifecycle state flows automatically between them.

## Local build

Clone both public repositories as siblings, check Atlas out to the exact commit recorded in atlas-commit.txt, then run these commands from the Principia checkout:

~~~bash
python3 software/one_website/build.py build --atlas-repo ../Atlas --output dist
python3 software/one_website/build.py verify --output dist
python3 -m http.server 8000 --directory dist
~~~

Open http://127.0.0.1:8000/ . The site loads JSON through same-origin browser fetch; opening the HTML directly with file:// is not supported.

To run a full two-build deterministic comparison:

~~~bash
python3 software/one_website/build.py check --atlas-repo ../Atlas
~~~

The builder uses the existing official Atlas product-input packaging and verification and both official Principia route builders. It checks the pinned Atlas git commit before building. site-manifest.json seals a SHA-256 digest for every published file. Verification rejects missing, undeclared, modified and symlinked assets.

The static export intentionally excludes facilitator recorder, Pilot Lab, hosted authentication, APIs, operational data export tools, and private learner storage. Existing local product/release mechanisms are unchanged.

## Vercel

Import Rhodan-lab/principle-to-system as a new Vercel project, with the repository root as the project root. The root vercel.json runs software/one_website/vercel-build.sh and publishes dist/.

At **build time**, the shell script clones the public Atlas repository, checks out only the exact commit in atlas-commit.txt, packages both sources, and cleans up the temporary checkout. At **website runtime**, the application reads only its packaged same-origin assets. No Atlas API key or production database is needed.

The GitHub Actions workflow validate-one-website.yml checks both sources and uploads a preview artifact after the build. It does not deploy the site. The output is intended for review before production publication.

## Scope and limitations

This is a static research preview, not production SaaS or a live cross-repository integration. Atlas is pinned to its accepted read-only workspace fixture, not its complete corpus or continuously updated evidence. The two Principia routes remain local-alpha educational models: no real-world engineering, learning-effectiveness, independent human verification, or accessibility certification claims are implied.

No account, learner persistence, analytics, canonical content writes, automatic review promotion, or Atlas synchronization is introduced. A web host still serves the site files over a network; "no external runtime calls" means no third-party data services or cross-repository API requests from the browser.

Pin updates, source-governance decisions, and public-domain deployments require separate review. See software/principia_atlas/README.md for the existing sealed local product, and Atlas's PROJECT_STATE.md for its knowledge authority.

## Observatory UX and model-formula restoration (2026-11)

This edition replaces the site's earlier landing page with a responsive editorial observatory, free-choice expedition cards, and a **keyboard-accessible live Model Studio**. The two Principia investigations use a consistent responsive design, an improved model workspace, accessible SVG charts, and a dedicated mathematical interpretation panel. Atlas keeps its accepted, read-only research logic and data but receives a coordinated visual skin and unified navigation.

The static export now declares four first-party UI assets at its root: `styles.css`, `site.js`, `experience.css`, and `experience.js`. The builder adds them to its SHA-256 inventory. The old source bundles remain independently validated before the public presentation layer is added.

### Mathematics and worked examples

**Refrigerator** (energy balance):

```text
C · dT/dt = UA · (T_room − T) + P_load − I_on · P_cool
T_eq = T_room + (P_load − I_on·P_cool) / UA
τ = C / UA
```

In the configured model, power is watts, heat capacity is joules/kelvin, time is seconds, and temperature differences may be expressed in kelvin or degrees Celsius. The model simulates the trajectory using explicit Euler steps; a constant-parameter analytical solution is shown only as a numerical cross-check and **not** a measurement. Current numerical answers appear **only after** the user selects a prediction and runs the model.

**Distributed information** (bounded, initially empty fluid queue):

```text
λ_offered = λ_external · (1 + p_retry)
ρ = λ_offered / μ
B(t) = min(K, max(0, (λ_offered − μ) · t))
R(t) = max(0, (λ_offered − μ) · t − K)
```

An illustrative `M/M/1` steady-state mean-time-in-system formula `W = 1/(μ − λ_offered)` is displayed **separately**, and only for `λ_offered < μ`. The M/M/1 delay assumption is stochastic and does **not** describe delay measured by the deterministic fluid queue simulation. Retries are **one-pass** additional attempts, not recursively generated retry storms. Queue capacity and rejected work are explicit, avoiding the false impression that an uncapped positive growth equation describes the finite buffer.

The derivation UI uses **native MathML** with spoken-label equivalents, a plain-language reading, unit definitions, and a clear model-assumption disclosure. It requires no CDN or third-party math renderer.

### Quality gates

The `test_one_website_math.mjs` suite compares rendered formula quantities with the actual deterministic thermal and queue adapters for default, stable, and overloaded scenarios; it also checks the independent homepage previews and MathML structure. The one-website workflow runs Node syntax checks, these numeric regressions, existing Python site constraints, a fully pinned Atlas build, sealed static package verification, and a downloadable site artifact.

No credentials, persistence, third-party requests, source mutation, status promotion, or live Atlas synchronization are introduced.

## Atlas Evidence Studio — evidence-led workspace redesign

The Atlas research page at `/research/` is now a dedicated **Evidence Studio**, combining an editorial reading language (warm paper, restrained terracotta, precise serif typography) with the practical workspace ergonomics of Google Antigravity (searchable routes, a primary reading pane, and a contextual inspector). This is an original design, not a reproduction of either company's assets or trademarked interface.

Design research:
- Anthropic Claude Design: https://www.anthropic.com/news/claude-design-anthropic-labs — consistent product system, iterative visual work.
- Antigravity features: https://antigravity.google/docs/features — command search and split contextual surfaces.
- Antigravity side panels: https://antigravity.google/docs/side-panel/ — context alongside the primary work area.

### Working interactions

- Research views retain their **original 13 route identities**, canonical text, exact entry order, warnings, and read-only export download.
- A searchable left index supports `/` or `Ctrl/Cmd + K` to focus filtering. Press `Enter` to open the first visible view; `Escape` clears the query. Search is only over labels of existing verified routes; it is **not full corpus search**.
- The Context inspector explains the current *view kind* and links to related existing routes. The separate Integrity tab describes the original export's verified local identity. The UI never creates a review decision, reconstructs provenance, or claims independent human verification.
- Focus reading hides secondary panes without losing the active source route. An inspector toggle keeps the page useful at narrower widths.
- A new five-card **accepted research trail** is rendered on the overview only *after* the source-owned Atlas runtime reports a fully verified export. The cards preserve original order and use the accepted route labels directly, with an explicit warning that the sequence is not a causal dependency graph.
- The source-owned Atlas `app.js` remains the sole authority for SHA-256 and byte-length verification, route fail-closed behavior, original renderers, export bytes, decisions and state.

### Safeguards and implementation boundary

This redesign lives entirely in `software/one_website/atlas-workspace.css` and `atlas-workspace.js`, plus deterministic build injection into the sealed static product. **No file in `Rhodan-lab/Atlas` is changed.** The original generated `research/app.js`, `research/styles.css`, and `research/data/*` remain byte-for-byte accepted exports. Enhancements are not activated until the existing runtime indicates `.runtime-card.ready`. They are inert on package verification failure. No external API fetch, local storage, cookie, analytics, canonical mutation, search index sync, or source status change is added.

Automated regressions cover known research-route grouping, search normalization, read-only interaction constraints, injected asset identity, accessibility semantics and mobile/forced-color/reduced-motion fallbacks. The Vercel build still needs a pinned Atlas checkout and the original integrity checks to pass.

## Root-wide experience system, edition III (November 2026)

This release is a **structural redesign across the entire unified website**, not another Atlas-only visual patch. It preserves the independently verified canonical sources and reworks the website's navigation and task surfaces.

### Design rationale and original interpretation

- [Anthropic's published brand guidance](https://github.com/anthropics/skills/blob/main/skills/brand-guidelines/SKILL.md): warm paper backgrounds, dark text, quiet separators and restrained coral accents; adapted into an **original** interface, not a copy of Anthropic's product or brand assets.
- [Google Antigravity's Knowledge Work layout](https://antigravity.google/blog/antigravity-for-knowledge-work): low-noise tasks, navigation and outputs-first contextual workspace, adapted to learning and evidence inspection.
- [Google Antigravity's side panel](https://antigravity.google/docs/side-panel): research context should be discoverable without obscuring the primary work surface. The existing Atlas contextual inspector is retained and restyled.
- Research content and source authority are separate from design; no styled element indicates a certification or higher review level that the accepted source does not contain.

### What is different on every route

1. **Global masthead:** One predictable navigation system across the home, both Principia routes, and Atlas. Product branding, current-page state and a single first-party search/jump dialog replace the previous inconsistent navigation, including the old floating bottom pill.
2. **Keyboard navigation:** Click **Jump**, press **Alt+G** anywhere, or use **Ctrl/Cmd+K** on Home / Principia. Atlas reserves its own Ctrl/Cmd+K shortcut for filtering its 13 accepted workspace views. Search is **only over authored first-party destinations**, not a fabricated corpus search.
3. **Principia learning routes:** The existing five-step reasoning navigation is moved into a real left investigation rail, the current lesson remains the central reading document, and the active prediction/simulation stays in the third pane where desktop width permits. Responsive breakpoints restore readable, non-overlapping stacked layout on tablets and phones.
4. **Research Atlas:** Retains the 13 exact accepted views, five accepted entries, contextual inspector and verified export. It shares the same masthead, colors, product identity and navigation as the rest of the site.
5. **Home / Discover:** Entirely new editorial systems atlas and navigable scientific diagram, three full destinations, accessible Model Studio (preserving its real calculations), a simple five-step method and an evidence boundary page section.
6. **Mathematical integrity:** No changes to the source simulation adapters, data, pinned knowledge export, source commit, prediction-before-model gate or comparison logic. MathML explanations remain attached to the live model steps.

### Asset and privacy contract

- The new root-wide files are **universe.css** and **universe.js**. They are first-party static assets included in the deterministic website manifest; no new dependency or external font is required.
- The builder does not rewrite any of the source-owned route content or Atlas JSON data. The extra UI is only the verified website's presentation layer.
- No user account, analytics, cookies, third-party requests, persistent preferences or canonical write capability is introduced.
- The generated website remains explicitly a pinned read-only research preview—not a new release of either canonical project.

### Quality gates

- Python manifest/injection tests assert that the shared CSS, JS, current-page semantics and source-owned apps are present.
- Node tests check keyword navigation, stable route identities, site-wide source boundary markers, UI feature contracts and the unchanged thermal/queue model preview.
- All three experiences and static data files are HTTP smoke-tested through a local server after the deterministic cross-repository build.
- Existing Atlas integrity checks, scientific model regressions, Vercel build, and repository status checks remain required.

## Expanding beyond two learning subjects — scientific exploration library

The unified website now offers **four interactive simulations** through the discovery page and an independently designed, navigable library at \`/explore/\`.

The original, formally packaged Product Alpha journeys remain exactly two:

- \`/learn/refrigerator/\` — thermal cabinet / heat balance.
- \`/learn/distributed-information/\` — bounded queue / retries.

Two further, explicitly **website-only conceptual experiments** are now available, grounded in reviewed Principia documents rather than promoted to Product Alpha routes:

- \`/explore/rainwater/\` — non-potable rainfall capture and storage buffer, drawn from \`design-challenges/nonpotable-rainwater-buffer.md\`.
- \`/explore/microgrid/\` — simplified solar–battery energy system, drawn from \`system-dossiers/solar-battery-microgrid.md\`.

### What learners can do

Every new interactive lab includes an observation, a dimensional equation, visible assumptions, synthetic weather scenarios, adjustable bounded variables, prediction-before-run gating, model output, an accessible SVG time-series, a complete per-step numerical table, baseline comparison and a link to the foundational source.

**Rainwater model (units liters)** — for a daily rainfall event \`P\` in millimeters:

\`\`\`text
capture = P(mm) × area(m²) × runoff_fraction  [liters]
available = stored + capture
served = min(available, non_potable_daily_demand)
overflow = max(0, available − served − capacity)
new_storage = min(capacity, available − served)
unmet = demand − served
capture_total = served_total + overflow_total + ending_storage
\`\`\`

An eight-day synthetic sequence starts with empty storage; rain occurs before daily demand; no evaporation/leakage/first-flush water loss is modeled. Reliability is the fraction of *stated scenario demand* served, not a drinking-water-quality or installation-safety measure. The simulation expressly prohibits connecting the concept to drinking-water plumbing.

**Solar microgrid (units kWh per 1-hour step)** — for irradiance \`G\` in W/m²:

\`\`\`text
PV(kWh) = G(W/m²) × area(m²) × efficiency × 1h / 1000
battery_delta = ηcharge × charge_input − discharge_to_load / ηdischarge
ending_energy = clamp(initial_energy + battery_delta, 10%-reserve, capacity)
unserved_critical_energy = max(0, demand_energy − served_energy)
initial_battery + generated_PV = end_battery + served + curtailment + conversion_loss
\`\`\`

This twelve-hour synthetic, islanded balance has 50% initial battery energy, fixed 10% energy reserve, 92% charge and discharge efficiencies, simplified direct PV service priority and no grid support. It deliberately omits real electrical protections, transient dynamics, grid-forming controls, installation decisions, inverter limits and night-long backup claims.

### Different evidence status by construction

The \`ROUTES\` contract and all Product Alpha route packages, pilot/rubric machinery and Atlas accepted export remain unchanged. New lab pages are generated **only** by the website static builder from \`exploration.html\`, \`exploration.js\`, \`exploration-models.js\` and \`exploration.css\`. No new Product Alpha model adapter, canonical decision, repository write or source-review transition is introduced.

The static inventory and SHA-256 manifest include all new pages and assets. The Vercel preview and GitHub Actions must verify scenario models' conservation under multiple conditions and inspect all lab pages through an HTTP server. All first-party visual assets work without dependencies, external APIs, persistence or user accounts.

### Scope and limitations

This expansion makes **four genuinely runnable laboratories**, not a claim that all Principia science modules have been turned into interactive lessons. Further science topics would require explicit models, content review and tests; placeholders or inert cards are not counted.

## Knowledge Atlas — a full explanation-first learning layer

The website's fifth destination, **\`/knowledge/\`**, unlocks a curated **15-chapter explanatory atlas**, grounded in source documents from the existing reviewed Principia repository. It addresses the major limitation of a simulation-only website: learners need to understand the causal story, formal quantity, assumptions, and evidence behind a number.

The Knowledge Atlas is written as an **original educational synthesis**, with clear attribution links to the relevant repository documents. It is **not a replacement for, or promotion of, the source owners' review decisions**. The underlying Atlas accepted research export and its distinct authority are not altered.

### What is actually provided

- **15 cross-linked chapters** organized by field: systems and boundaries, conservation, units, stocks/flows, models, feedback, thresholds, heat, retries and queues, rainwater, solar batteries, uncertainty, causality, resilience and evidentiary provenance.
- Each chapter has an investigative question, *four substantial explanation sections*, a mathematical lens, a numerically worked example, a misconception to challenge, and a *three-part, scenario-based thought experiment*. The content works from fundamentals toward model assumptions and what evidence would change a conclusion.
- Each chapter ends with a multiple-choice conceptual retrieval question whose correct choice is not revealed until the learner submits an answer. The options rotate deterministically to avoid a single correct-option pattern. Explanations describe why an option is correct or why the initial reasoning requires revision.
- A personal **"Explain it in your own words"** notebook is available on each chapter, kept only in the active tab's JavaScript memory; there are no accounts, cookies, analytics or saved cross-visit progress. Learners may copy their written explanation through the browser clipboard's explicit user action, with a manual fallback.
- Search, domain filters, source attribution links, a focus-reading option, chapter progress **within the current tab only**, suggested conceptual connections and links to the related experimental laboratory.
- The home page now features six entry chapters and links to the complete library. The four-lab catalog includes a knowledge bridge. Both original Product Alpha learning journeys gain linked background explanations.
- Both newer conceptual labs now have an explicit theory bridge and a **computed numerical interpretation** following prediction and simulation. It explains the actual water-volume or energy ledger, initial and final storage, constraints, and the conditional nature of the output.

### Educational design principles

These interaction choices reflect established principles that support conceptual organization, retrieval practice, explanatory elaboration, worked examples, and connecting words with visuals:

- National Research Council, *How Students Learn* (2005): https://www.nationalacademies.org/read/10126/chapter/2
- Weinstein, Madan and Sumeracki (2018), *Teaching the science of learning*: https://pmc.ncbi.nlm.nih.gov/articles/PMC5780548/
- National Academies, *How People Learn II* (2018), knowledge integration: https://www.nationalacademies.org/read/24783/chapter/7

These are **influences on teaching design**, not scientific validation of every new teaching passage.

### Build, integrity and source boundaries

The static build packages \`knowledge/index.html\`, \`knowledge-content.js\`, \`knowledge.js\`, \`knowledge.css\` alongside the original 4 simulations and the untouched accepted Atlas research export.

- \`knowledge-content.js\` contains a constrained, explicit concept graph and educational content; it is not a live GitHub search, generated research verdict, AI answer generator or claim of completeness.
- Source citations point to exact known paths under the Principia repository; none are dynamically rewritten or imported from a user-controlled URL.
- The standalone knowledge chapter runtime uses text nodes for user-visible fields instead of \`innerHTML\`; no arbitrary markup execution or untrusted network data is introduced.
- The Vercel \`/knowledge/\` rewrite, CSS and scripts are included in the website's SHA-256-sealed static asset inventory. The manifest's **Product Alpha ROUTES remain two**, and the original website-only rainwater/microgrid experiments retain their independent status.
- New tests check all 15 chapters and their 45 scenario narratives, semantic links, varied answer choices, source limits, mathematical interpretations, immutable asset list, runtime syntax, and HTTP accessibility.

**Non-goal:** publishing the whole 800-file repository as canonical, independently reviewed web lessons. The 15 chapters are a curated entrance into it, not a claim that all scientific material is complete or universally correct.
