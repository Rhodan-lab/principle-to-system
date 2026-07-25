# Phase 7 Physical Science Review

> Review date: 2026-07-26  
> Scope: Modules 06–12, all 21 learner-facing files  
> Status transition: Draft → Reviewed  
> Release status: Not Complete; independent review and later repository-wide release gates remain required.

## Review method

Each module was reviewed across `overview.md`, `technology.md`, and `explore.md`. The pass checked:

- factual and conceptual accuracy;
- equations, symbols, units, constants, and arithmetic;
- conservation laws, constitutive relations, and system boundaries;
- assumptions, approximations, model domains, and scale transitions;
- technology mechanisms, component interaction, performance, and failure modes;
- direct source links against the normalized central ledger;
- canonical module identifiers and cross-module connections;
- safe and age-appropriate learner activities;
- consistency across all three files in each module.

A module moved to Reviewed only after its three learner-facing files passed the same deterministic contract.

## Module 06 — Matter and Quantum Foundations

### Files reviewed

- `science/06-matter-quantum/overview.md`
- `science/06-matter-quantum/technology.md`
- `science/06-matter-quantum/explore.md`

### Scientific corrections

- Reframed quantisation as observable- and system-dependent rather than universal discreteness of every quantity.
- Corrected the relationship among quantum states, wavefunctions, orbitals, probability amplitudes, and measurement outcomes.
- Replaced the literal “virtual particles popping in and out” story with vacuum-state and perturbative-calculation language.
- Clarified that the uncertainty relation concerns statistical spreads for identically prepared states and is not explained only by measurement disturbance.
- Separated quark confinement from the residual nuclear interaction between nucleons.
- Restricted the `λ ≈ h/(mv)` form to nonrelativistic motion and retained `λ = h/p` as the general de Broglie relation.
- Added validity boundaries for nonrelativistic, independent-particle, Born–Oppenheimer, nuclear, and quantum-field models.

### Technology corrections

- Rewrote laser stimulated-emission language in terms of amplification of an optical mode.
- Corrected MRI magnetisation, radiofrequency excitation, signal induction, and relaxation language.
- Clarified that STM contrast depends on tip–sample separation and local electronic states, not purely geometric height.
- Removed unstable device-efficiency and resolution claims that lacked a specified operating boundary.
- Clarified magnet-quench severity without treating every quench as an identical catastrophic event.

### Safety changes

- Replaced the animal-death thought experiment with a two-path coherence example.
- Replaced open-ended spectroscopy with enclosed classroom equipment, simulations, or reference databases.
- Added explicit warnings against viewing the Sun, lasers, welding arcs, or intense sources through optical devices.

### Direct review sources added

- NIBIB MRI overview;
- NIST scanning probe microscopy programme;
- CERN Standard Model;
- NIST atomic spectroscopy databases;
- OpenStax quantum theory.

## Module 07 — Chemical Bonding and Reactions

### Scientific corrections

- Reframed ionic, covalent, and metallic bonding as useful limiting descriptions of a many-electron continuum.
- Replaced “full shell” causation with total-energy and electron-density reasoning.
- Limited VSEPR to its qualitative domain and identified transition-metal, delocalised, and hypervalent exceptions.
- Rewrote equilibrium constants using dimensionless activities and standard states.
- Corrected the Nernst electron number as a stoichiometric count per reaction as written.
- Clarified that catalysts participate in elementary steps and are regenerated overall rather than remaining unchanged at every instant.
- Separated thermodynamic driving force from reaction rate and catalyst mechanism.
- Corrected bond-energy reasoning: breaking interactions requires energy; net reaction energy depends on everything broken and formed under stated conditions.

### Technology corrections

- Replaced “energy stored in bonds” with recoverable electrochemical free energy in composition and electrode states.
- Corrected catalytic-converter product and pollutant language; carbon dioxide is less locally toxic than carbon monoxide but remains a greenhouse gas.
- Removed universal battery-efficiency claims and tied performance to chemistry, state of charge, temperature, current, ageing, and measurement boundary.

### Safety changes

- Replaced household heating comparisons with reference-data analysis.
- Replaced crushed-tablet reaction experiments with browser simulations.
- Replaced airbag-reaction prompts with catalytic-converter light-off analysis.

### Direct review source added

- United States Environmental Protection Agency automobile-emissions overview.

## Module 08 — Energy and Thermodynamics

### Scientific corrections

- Corrected temperature as a thermodynamic state variable; the average-translational-kinetic-energy identity is limited to idealised cases.
- Replaced “entropy equals disorder” with thermodynamic and statistical definitions.
- Defined heat and work as energy-transfer modes crossing a boundary.
- Reframed energy categories and removed the claim that chemical energy is simply stored in individual bonds.
- Corrected enthalpy from “heat content” to the state function `H = U + pV`.
- Added the surroundings term to the simplified net-radiation relation.
- Restricted Gibbs-free-energy criteria to specified constraints and separated thermodynamic direction from kinetics.
- Clarified the Third Law and the perfect-crystal, unique-ground-state condition.
- Replaced vague “energy quality degrades” language with exergy destruction through entropy generation.

### Engineering corrections

- Made Brayton-cycle assumptions explicit.
- Removed unstable combined-cycle efficiency numbers and tied performance to system design and operating conditions.
- Distinguished ideal Carnot bounds from real entropy-generating engines.

### Safety changes

- Replaced vigorous pumping with normal rated-use or simulation.
- Converted the sealed-vessel heating prompt into a simulation with an explicit hazard explanation.
- Replaced the rubber-band-on-skin demonstration with published data or a classroom model.

## Module 09 — Motion and Forces

### Scientific corrections

- Restated Newton's second law as `ΣF_ext = dp/dt`, with `ma` restricted to constant mass in an inertial frame.
- Corrected relativistic language: invariant mass remains unchanged; momentum and energy follow relativistic relations.
- Treated moment of inertia as a tensor generally and a scalar only for a specified axis.
- Clarified that third-law force pairs act on different bodies.
- Separated momentum conservation from unqualified internal-force cancellation.
- Restricted Newtonian gravity to weak-field, low-speed conditions.
- Corrected specific impulse as thrust divided by propellant weight-flow rate, with effective exhaust velocity `g₀Isp`.
- Reframed factors of safety as criterion-specific ratios rather than whole-structure load multipliers.

### Arithmetic correction

The worked cart example now consistently uses:

- mass `1.5 kg`;
- initial speed `2.0 m/s`;
- stopping time `0.20 s`;
- momentum change `−3.0 kg·m/s`;
- average force `−15 N`.

### Safety changes

- Replaced tossed keys with a soft foam-ball video.
- Replaced the high-speed crash example with a low-speed padded cart.
- Removed cutting or breaking a broom from the centre-of-mass activity.
- Replaced the historical cannon framing with a neutral orbital free-fall simulation.

## Module 10 — Electricity and Magnetism

### Scientific corrections

- Treated electric and magnetic fields as frame-dependent components of one electromagnetic field.
- Restricted Ohm's law to approximately ohmic elements under specified conditions.
- Replaced “current chooses the path of least resistance” with Kirchhoff/impedance-based current division.
- Corrected the revised-SI status of vacuum permeability and permittivity: unlike `c` and `e`, they are no longer exact defining constants.
- Added the limits of lumped-circuit models and the need for transmission-line or field models at high frequency or large size.
- Clarified magnetic flux linkage in induction.

### Safety changes

- Removed the instruction to connect loose wire directly across a battery.
- Replaced the electromagnet build with a virtual experiment.
- Restricted cord observations to unplugged, intact equipment without opening or handling damaged wiring.

### Direct review source added

- Bureau International des Poids et Mesures, *The International System of Units (SI), 9th edition*.

## Module 11 — Waves and Signals

### Scientific corrections

- Clarified wave energy and momentum transport without claiming that all waves produce no net material transport.
- Reframed diffraction as spreading and interference rather than literal bending around every obstacle.
- Distinguished Fourier series from Fourier transforms and added windowing, sampling, leakage, and noise limits.
- Corrected refraction in terms of phase velocity, refractive index, and boundary conditions.
- Added the damped angular-frequency expression to the underdamped oscillator solution.
- Reframed destructive interference through field variables, energy flux, reflection, and storage.
- Replaced the simple zig-zag fibre picture with guided electromagnetic modes, evanescent fields, bending loss, absorption, scattering, and dispersion.
- Distinguished channel bandwidth from achievable data rate.

### Safety changes

- Replaced roadside Doppler observation with recorded or simulated motion.
- Replaced fragile-glass resonance with a virtual driven oscillator.
- Restricted tone comparisons to low comfortable volume or visual signal plots.
- Replaced chair-and-string coupled oscillators with a simulation or equation model.
- Replaced direct laser-pointer prism activity with a ray-optics simulation.

## Module 12 — Fluids and Materials

### Scientific corrections

- Reframed Bernoulli's equation as a conditional mechanical-energy relation rather than a universal constriction-to-pressure-drop rule.
- Integrated pumps, elevation, viscosity, losses, compressibility, and boundary conditions into flow reasoning.
- Replaced one-line lift explanations with pressure/shear integration and momentum deflection.
- Clarified Newtonian viscosity as a constitutive model, not a universal fluid property.
- Treated stress and strain as tensors generally.
- Restricted scalar Hooke-law expressions to simple linear-elastic loading.
- Added the geometry and assumption limits of the ideal Griffith relation.
- Replaced universal isotropy claims with texture-, crystal-, and processing-dependent language.
- Corrected continuum assumptions to include relevant molecular, granular, and microstructural scales.
- Reframed fatigue around finite-life, crack-growth, and damage-tolerance assessment.

### Safety changes

- Replaced deliberate paperclip fracture with manufacturer data or simulation.
- Replaced scratched-glass bending with a fracture model.
- Replaced cutting bottles and restricting hoses with a virtual pipe model.
- Replaced taped-spaghetti claims with a fibre–matrix load-sharing model.
- Reduced the paper-airflow demonstration to gentle airflow.

### Direct review source added

- NASA Glenn Research Center, *Bernoulli and Newton*.

## Source result

Phase 7 added five direct reviewed records to the Phase 6 ledger:

1. NIBIB MRI;
2. NIST scanning probe microscopy;
3. EPA automobile emissions;
4. BIPM SI Brochure;
5. NASA Bernoulli and Newton.

The integrated Phase 7 branch contains **121 central source records**:

- 110 Phase 5 baseline records;
- 6 Phase 6 review records;
- 5 Phase 7 review records.

The source registry and report are:

- `sources/phase-7-reviewed-sources.json`;
- `reports/phase-7-physical-science-sources.json`;
- `scripts/apply_phase7_review_sources.py`.

## Validation result

The final branch passed, in dependency order:

1. Phase 4 canonical metadata validation;
2. Phase 5 normalized-source validation;
3. Phase 6 source-registry validation;
4. Phase 6 Foundations scientific-review validation;
5. Phase 7 source-registry validation;
6. Phase 7 21-file scientific-review validation.

The validation process also checks idempotence: applying the review transformer again must produce no content changes.

## Dependency correction

The original Phase 6 PR was merged into its Phase 5 feature branch after Phase 5 had already entered `main`, so Phase 6 did not reach `main`. This was not hidden or bypassed.

The corrected merge order is:

1. PR #8 integrates the completed Phase 6 review into `main`;
2. PR #7 remains based on `agent/phase-6-foundations-review` during review;
3. after PR #8 merges, PR #7 is retargeted to `main`;
4. the read-only Phase 7 gate is rerun before any merge decision.

## Remaining caveats

- Reviewed is not an independent scientific certification.
- The modules introduce broad domains and cannot replace specialised upper-level treatments.
- Technology examples are representative rather than exhaustive designs.
- Some source records are textbooks or institutional educational material rather than primary literature because the modules are foundational surveys.
- Modules 13–20 remain Draft.
