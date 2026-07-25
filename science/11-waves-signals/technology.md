---
title: "Oscillations, Waves, Sound, Optics, and Signals"
slug: 11-waves-signals-technology
module: "Module 11"
domain: science
status: reviewed
prerequisites: [03-mathematical-models, 09-motion-forces]
connections: [20-sensors-control-infrastructure]
last_reviewed: 2026-07-26
content_license: CC-BY-4.0
---

## 1. Scientific principles used

The engineering of wave-based technologies relies on several core scientific principles:
- **Transduction:** The conversion of energy from one form to another (e.g., acoustic to electrical) while preserving the signal's waveform.
- **Total Internal Reflection:** The optical phenomenon where light travelling in a denser medium hits a boundary at an angle greater than the critical angle and is reflected in the ideal ray model while an evanescent field and real losses remain, allowing light to be guided along a path.
- **Superposition and Interference:** The addition of wave amplitudes, utilised in noise-cancelling headphones, interferometers, and phased array antennas.
- **Modulation:** The process of varying one or more properties of a periodic waveform (the carrier signal) with a modulating signal that contains information to be transmitted.
- **Resonance:** The tendency of a system to oscillate with greater amplitude at some frequencies than at others, used for filtering and signal selection.

## 2. The engineering problem

Human senses and vocal cords are limited in range and bandwidth. The fundamental engineering problem is how to capture information (sound, images, data), convert it into a format that can travel vast distances rapidly and reliably without degradation, and then reconstruct it accurately at the destination. This requires overcoming attenuation (energy loss over distance), dispersion (spreading of signals), and noise (unwanted interference).

## 3. Main components

To illustrate these principles, we examine a **Global Fibre Optic Communication Link**:
- **Transmitter (Laser Diode):** Generates a coherent beam of light (the carrier wave).
- **Modulator:** Alters the light beam (e.g., turning it on and off rapidly) to encode digital information.
- **Optical Fibre:** The transmission medium, consisting of a high-purity glass core surrounded by a cladding with a lower refractive index.
- **Optical Amplifiers (Erbium-Doped Fibre Amplifiers, EDFAs):** Periodically boost the optical signal strength without converting it back to an electrical signal.
- **Receiver (Photodiode):** Detects the incoming light pulses and converts them back into an electrical signal.
- **Demodulator/Decoder:** Extracts the original digital information from the electrical signal.

## 4. How the components interact

The interaction forms a continuous principle-to-system chain:
1. **Information to Electrical Signal:** A microphone or computer generates a time-varying electrical voltage representing data.
2. **Electrical to Optical (Modulation):** This voltage drives a modulator that rapidly varies the intensity of a laser beam. The continuous wave is now a signal.
3. **Propagation (Total Internal Reflection):** The modulated light enters the optical fibre. Because the core has a higher refractive index than the cladding, light striking the boundary at a shallow angle undergoes total internal reflection, propagating as guided electromagnetic modes determined by the core–cladding index profile.
4. **Amplification (Stimulated Emission):** As the light travels hundreds of kilometres, it attenuates. It passes through an EDFA, where a secondary "pump" laser excites erbium ions. When the weak signal photons pass by, they stimulate the ions to emit identical photons, amplifying the wave optically.
5. **Optical to Electrical (Transduction):** At the destination, the light strikes a photodiode. The energy of the photons excites electrons, creating a current proportional to the light intensity.
6. **Signal Processing:** The electrical signal is filtered, amplified, and decoded to reconstruct the original data.

## 5. Matter, energy, force, or information flow

In this system, the primary flow is **information encoded in energy**. Matter (the glass fibre, the electrons in the circuits) remains largely stationary, acting only as the medium. Electromagnetic energy (light) flows from transmitter to receiver, carrying the modulated information pattern. Power must be continuously supplied to the lasers and amplifiers to maintain this flow against the forces of attenuation and scattering.

## 6. System architecture

Modern optical networks use **Wavelength-Division Multiplexing (WDM)**. Instead of sending one signal down a fibre, multiple lasers emit light at slightly different wavelengths (colours). Each wavelength acts as an independent carrier, modulated with its own data stream. These are combined (multiplexed) into a single fibre. At the receiving end, a prism-like device or diffraction grating separates the wavelengths (demultiplexing) into different receivers. This architecture massively increases the data capacity of a single physical cable.

## 7. Design constraints

- **Attenuation:** Even ultra-pure glass absorbs and scatters some light. Engineers must choose wavelengths where glass is most transparent (typically around 1550 nm in the infrared).
- **Dispersion:** Different wavelengths travel at slightly different speeds (chromatic dispersion), and light taking different paths through the fibre arrives at different times (modal dispersion). This causes short pulses to spread out and overlap, limiting the maximum data rate.
- **Non-linear Effects:** At high optical powers, the refractive index of the glass actually changes slightly, causing signals to interfere with themselves and each other.

## 8. Performance and efficiency

The performance of a communication system is often measured by its **bandwidth** (data rate, e.g., Terabits per second) and **latency** (time delay). Fibre optics offer exceptionally high bandwidth and low latency compared to copper cables. Reliability is measured in part by the **Bit Error Rate (BER)**—the fraction of bits received incorrectly. Advanced modulation schemes (like Quadrature Amplitude Modulation, QAM) pack more bits into each symbol, increasing efficiency but requiring higher signal-to-noise ratios.

## 9. Reliability and failure modes

- **Fibre Breakage:** Physical damage from construction equipment (backhoes) or natural disasters (earthquakes, undersea landslides) is the most common failure. Networks are designed with ring topologies so traffic can be instantly rerouted if a cut occurs.
- **Component Degradation:** Lasers and amplifiers degrade over time.
- **Signal Degradation:** If amplifiers are spaced too far apart, the signal drops below the noise floor and cannot be recovered.

## 10. Safety principles

- **Laser Safety:** The infrared lasers used in telecommunications are invisible but powerful enough to cause permanent retinal damage. Technicians must never look directly into an active fibre.
- **Glass Handling:** Cleaving optical fibres produces microscopic, needle-like glass shards that can easily penetrate skin or eyes. Strict handling and disposal protocols are required.

## 11. Environmental and lifecycle considerations

Manufacturing high-purity optical fibre is energy-intensive. However, once deployed, fibre optic networks are highly energy-efficient per bit of data transmitted compared to copper networks or wireless towers. The primary environmental impact is the physical deployment—trenching for terrestrial cables or laying heavy armoured cables across the seabed. At the end of their life, the glass fibres are difficult to recycle economically, though the protective plastic and metal armoring can be recovered.

## 12. Connections to other technologies

- **Acoustics and Audio Engineering:** Uses similar principles of waves, resonance, and Fourier analysis to design concert halls, microphones, and speakers.
- **Medical Imaging (Ultrasound):** Uses high-frequency sound waves and their reflections to image internal organs.
- **Radar and Lidar:** Uses the reflection and Doppler shift of electromagnetic waves to determine the position and velocity of objects.

## Phase 7 review boundaries and validity limits

- A wave transports energy and momentum, while material elements in a mechanical medium usually oscillate around equilibrium; some waves and nonlinear flows can also produce net transport.
- Refraction follows phase matching and a change in phase velocity or refractive index, not a vague distinction between “optically dense” and “less dense” matter.
- Fourier series apply to suitably behaved periodic signals; Fourier transforms generalise the idea to non-periodic signals. Real measurements also involve finite windows, sampling, leakage, and noise.
- Destructive interference means local cancellation of the chosen field variable. Energy conservation must be evaluated from flux and boundary conditions; energy may be redistributed, reflected, or stored rather than always appearing at a nearby bright fringe.
- Fiber guidance is described by electromagnetic modes. Total internal reflection is a useful ray approximation, but evanescent fields, bending loss, scattering, absorption, and dispersion remain.

## 13. Sources



1. MIT OpenCourseWare. *8.03SC Physics III: Vibrations and Waves*. https://ocw.mit.edu/courses/8-03sc-physics-iii-vibrations-and-waves-fall-2016/
2. MIT OpenCourseWare. *6.003 Signals and Systems*. https://ocw.mit.edu/courses/6-003-signals-and-systems-fall-2011/
3. OpenStax. *College Physics 2e: Oscillatory Motion and Waves*. https://openstax.org/books/college-physics-2e/pages/16-introduction-to-oscillatory-motion-and-waves
4. Agrawal, G. P. *Fiber-Optic Communication Systems*. https://doi.org/10.1002/9780470918524
