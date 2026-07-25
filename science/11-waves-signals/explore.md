---
title: "Oscillations, Waves, Sound, Optics, and Signals"
slug: 11-waves-signals-explore
module: "Module 11"
domain: science
status: draft
prerequisites: [03-mathematical-models, 09-motion-forces]
connections: [20-sensors-control-infrastructure]
last_reviewed: 2026-07-24
content_license: CC-BY-4.0
---

## 1. Observation prompts

- **The Doppler Effect:** Stand near a road and listen to the pitch of a car engine or siren as it approaches and then passes you. How does the pitch change? Does the volume change in the same way?
- **Water Waves:** Drop a single pebble into a still pond or a large basin of water. Observe the expanding circular ripples. What happens when the ripples hit the edge of the basin? Now drop two pebbles simultaneously a short distance apart. Observe the pattern where the two sets of ripples intersect.
- **Optical Refraction:** Place a straight pencil halfway into a glass of water. Look at it from the side, at the level of the water surface. Why does the pencil appear broken or bent?

## 2. Prediction questions

- If you tighten the string of a guitar (increasing the tension), will the frequency of the sound it produces when plucked increase, decrease, or stay the same? Why?
- Imagine a sound wave travelling from air into water. The speed of sound in water is roughly four times faster than in air. Will the frequency of the sound wave change? Will the wavelength change?
- If you shine a red laser pointer and a blue laser pointer through the same glass prism, which beam will bend (refract) more?

## 3. Worked reasoning examples

**Question:** A simple pendulum consists of a mass $m$ attached to a string of length $L$. If you double the mass of the bob, how does the period of oscillation change? What if you double the length of the string?

**Reasoning:**
1. Identify the relevant mathematical model. The period $T$ of a simple pendulum (for small angles) is given by $T = 2\pi\sqrt{\frac{L}{g}}$, where $g$ is the acceleration due to gravity.
2. Analyse the effect of mass. The equation for the period $T$ does not contain the mass variable $m$. Therefore, doubling the mass has no effect on the period. (The increased inertia is exactly cancelled by the increased gravitational force).
3. Analyse the effect of length. The period $T$ is proportional to the square root of the length $L$ ($T \propto \sqrt{L}$).
4. If the new length is $L' = 2L$, the new period is $T' = 2\pi\sqrt{\frac{2L}{g}} = \sqrt{2} \left(2\pi\sqrt{\frac{L}{g}}\right) = \sqrt{2}T$.
5. Conclusion: Doubling the mass does not change the period. Doubling the length increases the period by a factor of $\sqrt{2}$ (approximately 1.414).

## 4. Thought experiments

- **The Silent Bell:** Imagine a bell ringing inside a sealed glass jar. If you use a vacuum pump to slowly remove all the air from the jar, what will happen to the sound of the bell? What will happen to your ability to see the bell? What does this tell you about the nature of sound waves versus light waves?
- **The Infinite String:** Imagine plucking a perfectly elastic string that extends infinitely in one direction. Will the wave pulse ever reflect back to you? If there is no boundary, how does the energy dissipate?

## 5. Household and browser-based explorations

- **Resonance with Wine Glasses:** Wet your finger and rub it gently but firmly around the rim of a thin crystal wine glass. You should hear a clear, sustained tone. This is the resonant frequency of the glass. Add some water to the glass and repeat. Does the pitch go up or down? Why? (The water adds mass to the oscillating system without significantly changing its stiffness).
- **Browser Audio Oscillator:** Search online for a "browser tone generator" or "online oscillator". Play a pure sine wave at 440 Hz (Standard pitch A). Open a second tab with the same generator and set it to 442 Hz. Play both simultaneously. You will hear a distinct "wobbling" sound. These are "beats," caused by the alternating constructive and destructive interference of the two slightly different frequencies. The beat frequency is the difference between the two frequencies (2 Hz, or two wobbles per second).

## 6. Model-building prompts

- **Coupled Oscillators:** Tie a string horizontally between two chairs. Hang two identical simple pendulums from this horizontal string. Start one pendulum swinging while the other is at rest. Observe how the energy transfers back and forth between the two pendulums. How would you modify the differential equations of simple harmonic motion to account for this coupling?
- **Fourier Synthesis:** Using a spreadsheet or a programming language (like Python), create a graph of $y = \sin(x)$. Then add a second harmonic: $y = \sin(x) + \frac{1}{3}\sin(3x)$. Then add a third: $y = \sin(x) + \frac{1}{3}\sin(3x) + \frac{1}{5}\sin(5x)$. Observe how the sum of these smooth sine waves begins to approximate a sharp-edged square wave.

## 7. Self-explanation questions

- Explain in your own words the difference between transverse and longitudinal waves, providing one example of each.
- Why does a prism separate white light into a spectrum of colours, but a flat pane of window glass does not?
- When you speak into a microphone, what physical quantity is actually being modulated to create the electrical signal?

## 8. Transfer questions

- The equations governing the oscillation of a mass on a spring ($m\frac{d^2x}{dt^2} + kx = 0$) are mathematically identical to the equations governing an electrical LC circuit (an inductor and a capacitor, $L\frac{d^2q}{dt^2} + \frac{1}{C}q = 0$). What electrical quantity is analogous to mass? What is analogous to the spring constant?
- Earthquakes produce both P-waves (longitudinal) and S-waves (transverse). S-waves cannot travel through liquids. How do seismologists use this fact to deduce that the Earth has a liquid outer core?

## 9. Suggested learning paths

- **To understand the mathematics deeper:** Study differential equations, specifically second-order linear ODEs, which are the foundation of the wave equation.
- **To explore optics:** Investigate geometrical optics (ray tracing, lenses, mirrors) and physical optics (diffraction, interference, polarisation).
- **To explore signals:** Study introductory digital signal processing (DSP), focusing on the Nyquist-Shannon sampling theorem and the Fast Fourier Transform (FFT).

## 10. Reasoning notes

When analysing wave phenomena, always identify the medium (if any), the restoring force, and the source of the disturbance. Remember that waves transport energy, not matter. When dealing with interference, pay close attention to the phase difference between the waves; it is the phase, not just the amplitude, that determines whether they will add together or cancel out.
