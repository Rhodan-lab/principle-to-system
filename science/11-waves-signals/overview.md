---
title: "Oscillations, Waves, Sound, Optics, and Signals"
slug: 11-waves-signals
module: "Module 11"
domain: science
status: reviewed
prerequisites: [03-mathematical-models, 09-motion-forces]
connections: [20-sensors-control-infrastructure]
last_reviewed: 2026-07-26
content_license: CC-BY-4.0
---

## 1. The central questions

How does energy travel through space without the net transport of matter? Why do some systems vibrate at specific frequencies, and how do these vibrations propagate through different media? How can we mathematically describe the diverse phenomena of sound, light, and information-carrying signals using a unified framework?

## 2. Observable phenomena

The physical world is replete with oscillatory and wave phenomena. A pendulum swings back and forth, gradually coming to rest due to air resistance. A plucked guitar string produces a sustained musical note. Dropping a pebble into a pond creates expanding circular ripples. When light passes through a prism, it separates into a spectrum of colours, and when it passes through a narrow slit, it creates a diffraction pattern of alternating bright and dark bands. In modern life, invisible electromagnetic waves carry radio broadcasts, mobile phone calls, and Wi-Fi signals through the air and across global networks of optical fibres.

## 3. Essential concepts

**Oscillation** is the repetitive variation of a quantity about a central value or equilibrium point. The simplest form is Simple Harmonic Motion (SHM), where the restoring force is directly proportional to the displacement from equilibrium.

**Waves** are disturbances that propagate through space and time, transferring energy and momentum without the permanent displacement of the medium. Waves can be classified as mechanical (requiring a material medium, like sound) or electromagnetic (capable of travelling through a vacuum, like light). They are further categorised by the direction of disturbance relative to propagation: transverse waves (disturbance perpendicular to propagation) and longitudinal waves (disturbance parallel to propagation).

**Resonance** occurs when a system is driven by an external periodic force at or near its natural frequency, resulting in a significant increase in the amplitude of oscillation.

**Superposition and Interference** describe what happens when two or more waves overlap in space. The resultant displacement is the vector sum of the individual displacements. This can lead to constructive interference (amplification) or destructive interference (cancellation).

**Diffraction** is the spreading and interference of waves when they encounter an obstacle or pass through an aperture that is comparable in size to their wavelength.

**Signals and Modulation** involve the deliberate modification of a wave (the carrier) to encode information. This can be achieved by varying the wave's amplitude, frequency, or phase.

**Fourier Analysis** represents suitably behaved periodic signals with Fourier series and non-periodic signals with Fourier transforms, decomposing them into a sum of simple sine and cosine waves of different frequencies and amplitudes.

## 4. Mechanisms and causal chains

The propagation of a mechanical wave relies on the interplay between inertia and restoring forces within a medium. In a stretched string, displacing a segment creates tension that pulls it back toward equilibrium. Due to inertia, the segment overshoots, creating an oscillation. This motion exerts forces on adjacent segments, causing the disturbance to travel along the string.

For sound waves in air, a vibrating source compresses adjacent air molecules, creating a region of high pressure (compression). This pressure pushes against neighbouring molecules, transferring the disturbance. The original molecules then rebound, creating a region of low pressure (rarefaction). The alternating compressions and rarefactions propagate outward at the speed of sound.

In optics, the mechanism of refraction (bending of light) occurs because phase velocity and wavelength change across media while boundary conditions preserve frequency. When a wavefront enters a medium with a different refractive index at an angle, the part of the wave that enters first slows down before the rest of the wave, causing the direction of propagation to bend toward the normal.

## 5. Important quantities

- **Amplitude ($A$)**: The maximum displacement from equilibrium.
- **Period ($T$)**: The time taken for one complete cycle of oscillation.
- **Frequency ($f$)**: The number of cycles per unit time.
- **Angular frequency ($\omega$)**: The rate of change of the phase of a sinusoidal waveform.
- **Wavelength ($\lambda$)**: The spatial period of the wave; the distance over which the wave's shape repeats.
- **Wave speed ($v$)**: The speed at which the wave propagates through space.
- **Phase ($\phi$)**: The angular coordinate locating a sinusoidal oscillation within its cycle relative to a reference.

## 6. Mathematical models and equations

**Simple Harmonic Motion (SHM):**
The equation of motion for an undamped simple harmonic oscillator is derived from Newton's second law and Hooke's law ($F = -kx$):
$$ \frac{d^2x}{dt^2} + \omega_0^2 x = 0 $$
where $\omega_0 = \sqrt{\frac{k}{m}}$ is the natural angular frequency. The solution is:
$$ x(t) = A \cos(\omega_0 t + \phi) $$

**Damped Harmonic Motion:**
When a damping force proportional to velocity ($F_d = -b \frac{dx}{dt}$) is present:
$$ m\frac{d^2x}{dt^2} + b\frac{dx}{dt} + kx = 0 $$
For underdamped systems, the solution is an exponentially decaying oscillation:
$$ x(t) = A_0 e^{-\frac{b}{2m}t} \cos(\omega_d t + \phi), \qquad \omega_d=\sqrt{\frac{k}{m}-\left(\frac{b}{2m}\right)^2}. $$

**The Wave Equation:**
The propagation of a one-dimensional non-dispersive wave is described by the linear wave equation:
$$ \frac{\partial^2 y}{\partial t^2} = v^2 \frac{\partial^2 y}{\partial x^2} $$
A general solution is d'Alembert's formula, $y(x,t) = f(x - vt) + g(x + vt)$, representing waves travelling in the positive and negative $x$-directions. A harmonic travelling wave is often written as:
$$ y(x,t) = A \sin(kx - \omega t + \phi) $$
where $k = \frac{2\pi}{\lambda}$ is the wavenumber.

**Wave Speed:**
The speed of a wave depends on the properties of the medium. For a string under tension $T_s$ with linear mass density $\mu$:
$$ v = \sqrt{\frac{T_s}{\mu}} $$
For electromagnetic waves in a vacuum, the speed is the speed of light, $c = \frac{1}{\sqrt{\mu_0 \epsilon_0}}$.

**Fourier Series:**
A periodic function $f(t)$ with period $T$ can be expressed as:
$$ f(t) = \frac{a_0}{2} + \sum_{n=1}^{\infty} \left[ a_n \cos(n\omega_0 t) + b_n \sin(n\omega_0 t) \right] $$
where $\omega_0 = \frac{2\pi}{T}$ is the fundamental frequency.

## 7. Definitions of symbols and units

- $x, y$: Displacement (metres, m)
- $t$: Time (seconds, s)
- $m$: Mass (kilograms, kg)
- $k$: Spring constant (newtons per metre, N/m) or Wavenumber (radians per metre, rad/m)
- $\omega, \omega_0, \omega_d$: Angular frequency (radians per second, rad/s)
- $A, A_0$: Amplitude (metres, m)
- $\phi$: Phase constant (radians, rad)
- $b$: Damping coefficient (kilograms per second, kg/s)
- $v, c$: Wave speed (metres per second, m/s)
- $\lambda$: Wavelength (metres, m)
- $f$: Frequency (hertz, Hz, equivalent to s$^{-1}$)
- $T$: Period (seconds, s)
- $T_s$: Tension (newtons, N)
- $\mu$: Linear mass density (kilograms per metre, kg/m)

## 8. Assumptions and approximations

- **Linearity:** The wave equation and superposition principle assume linear restoring forces. For large amplitudes, non-linear effects (like shock waves or harmonic distortion) become significant.
- **Small Angle Approximation:** For a simple pendulum, SHM is only valid for small angular displacements ($\sin \theta \approx \theta$).
- **Non-dispersive Media:** The basic wave equation assumes wave speed is independent of frequency. In dispersive media (like glass for light, or deep water for surface waves), different frequencies travel at different speeds.
- **Ideal Fluids:** Basic acoustic models often assume inviscid, adiabatic processes, ignoring energy loss due to heat conduction and viscosity.

## 9. Spatial and temporal scales

Wave phenomena span an enormous range of scales.
- **Temporal:** Frequencies range from fractions of a hertz (seismic waves, ocean tides) to $10^{15}$ Hz (visible light) and beyond $10^{20}$ Hz (gamma rays).
- **Spatial:** Wavelengths range from thousands of kilometres (radio waves, tsunamis) to nanometres (visible light) and picometres (X-rays). The scale of the wave relative to the environment determines its behaviour; light casts sharp shadows around everyday objects because its wavelength is microscopic, whereas sound diffracts around corners because its wavelength is comparable to human-scale objects.

## 10. Common misconceptions

- **Misconception:** Waves transport matter from one place to another.
  **Correction:** Waves transport energy and momentum. The particles of the medium only oscillate locally around their equilibrium positions.
- **Misconception:** Sound travels faster in air than in solids because air is less dense.
  **Correction:** Sound generally travels much faster in solids than in gases because solids have a much higher elastic modulus (stiffness), which dominates the effect of their higher density.
- **Misconception:** Destructive interference destroys energy.
  **Correction:** Energy is conserved. Local cancellation of displacement or field amplitude does not destroy energy; the energy balance depends on flux, reflection, storage, and the complete boundary conditions.

## 11. Connections to other modules

- **03-mathematical-models:** Provides the calculus and differential equations necessary to formulate the wave equation and Fourier analysis.
- **09-motion-forces:** The foundation of kinematics and dynamics required to understand restoring forces and simple harmonic motion.
- **10-electricity-magnetism:** Explains the nature of light and radio waves as oscillating electric and magnetic fields.
- **06-matter-quantum:** Extends wave concepts to matter (wave-particle duality) and probability amplitudes.
- **20-sensors-control-infrastructure:** Applies the principles of signals, modulation, and Fourier analysis to modern data transmission.

## Phase 7 review boundaries and validity limits

- A wave transports energy and momentum, while material elements in a mechanical medium usually oscillate around equilibrium; some waves and nonlinear flows can also produce net transport.
- Refraction follows phase matching and a change in phase velocity or refractive index, not a vague distinction between “optically dense” and “less dense” matter.
- Fourier series apply to suitably behaved periodic signals; Fourier transforms generalise the idea to non-periodic signals. Real measurements also involve finite windows, sampling, leakage, and noise.
- Destructive interference means local cancellation of the chosen field variable. Energy conservation must be evaluated from flux and boundary conditions; energy may be redistributed, reflected, or stored rather than always appearing at a nearby bright fringe.
- Fiber guidance is described by electromagnetic modes. Total internal reflection is a useful ray approximation, but evanescent fields, bending loss, scattering, absorption, and dispersion remain.

## 12. Sources



1. MIT OpenCourseWare. *8.03SC Physics III: Vibrations and Waves*. https://ocw.mit.edu/courses/8-03sc-physics-iii-vibrations-and-waves-fall-2016/
2. MIT OpenCourseWare. *6.003 Signals and Systems*. https://ocw.mit.edu/courses/6-003-signals-and-systems-fall-2011/
3. OpenStax. *College Physics 2e: Oscillatory Motion and Waves*. https://openstax.org/books/college-physics-2e/pages/16-introduction-to-oscillatory-motion-and-waves
4. Agrawal, G. P. *Fiber-Optic Communication Systems*. https://doi.org/10.1002/9780470918524
