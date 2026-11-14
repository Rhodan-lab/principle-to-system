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
