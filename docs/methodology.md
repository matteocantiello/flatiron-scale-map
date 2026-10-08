# Methodology

How the ranges in `data/centers.toml` were chosen, and what the figure does and doesn't claim.

## The question

Where in length and time do the systems each Flatiron center studies sit? The axes are the
**characteristic length** and **characteristic time** of the *physical system or process under
study*, not the resolution of a simulation or the size of a dataset. A cosmological simulation
resolves sub-kpc scales, but the system is the large-scale structure of the Universe.

Each center gets a **core range**: the envelope of the systems at the center of its research
program, judged from the center's public pages in October 2026. The ranges are deliberately
generous at the scale of decades and deliberately ignore one-off projects. Those are listed
separately as edge cases. They are judgment calls, not official numbers.

## The light-crossing line

The line t = L/c marks the time light takes to cross a system of size L. Coherent system-scale
dynamics cannot be faster than that, so the half-plane below the line is empty for every center.
Each core box is clipped to t ≥ L/c (log₁₀ c = 8.4768), and the excluded half is drawn as a flat
field.

The two ends of the figure sit on the line: electron dynamics at ångströms and attoseconds (CCQ),
and cosmology at the Hubble radius and Hubble time (CCA). Biology and neuroscience sit far above
it, because their dynamics are set by diffusion, transport and chemistry, not by light.

## Center by center

Bounds are log₁₀ m and log₁₀ s, as in `data/centers.toml`.

### CCQ: Center for Computational Quantum Physics
- **Length −10.5 → −7.5.** From electron orbitals and crystal unit cells (~0.3 Å) to moiré
  superlattices (~30 nm), the largest periodic structures in its quantum-materials work.
- **Time −18 → −11.** From attosecond electron dynamics (Dynamics and Control) to picosecond
  relaxation. Much of the center's work is equilibrium many-body physics, which has no intrinsic
  timescale; the box marks the dynamical range.
- Clipped at the bottom-right corner by t = L/c.

### ICC: Initiative for Computational Catalysis
- **Length −10 → −7.** From bonds and active sites (~1 Å) to nanoparticles, zeolite pores and
  electrode–electrolyte interfaces (~100 nm). It combines electronic structure, molecular dynamics
  and machine learning across heterogeneous and homogeneous catalysis.
- **Time −15 → 4.** From femtosecond bond vibrations and electron transfer to catalytic turnover
  and deactivation (seconds to hours). Catalysis is a rare-event problem, so ICC spans ~19 decades
  in time while sitting inside CCQ's length range. This is the clearest case for a 2D map.
- Microkinetic models reach reactor-scale *rates* without spatial resolution, so reactor sizes are
  not included.

### CCB: Center for Computational Biology
- **Length −10 → 0.** From atoms in cryo-EM maps and designed proteins (~1 Å) to vascular and
  lymphatic transport networks (~1 m, Biological Transport Networks group). Most of the work sits
  between nanometers and millimeters: cytoskeleton, cells, embryos.
- **Time −12 → 6.** From picosecond protein motions to embryonic development (days).
- Genomics lives in sequence space and has no physical length; it is not represented.
- Clipped at the bottom-right corner by t = L/c.

### CCN: Center for Computational Neuroscience
- **Length −6 → −1.** From synapses and dendritic spines (~1 µm) to the whole brain (~10 cm).
- **Time −3 → 9.** From millisecond spikes to learning, development and aging (years to decades;
  the Statistical Analysis of Neural Data group studies how dynamics change over these timescales).
- Artificial neural networks, also studied at CCN, have no physical scale and are not represented.

### CCA: Center for Computational Astrophysics
- **Length 4 → 26.6.** From neutron stars and stellar-mass black-hole horizons (~10 km) to the
  observable Universe (~4 × 10²⁶ m).
- **Time −3 → 17.6.** From millisecond neutron-star spin and compact-object mergers to the Hubble
  time.
- The right edge at 26.6 lies wholly below t = L/c, so after clipping the region's top-right
  corner is the point where the Hubble time meets the light-crossing line (L ≈ 10²⁶·¹ m).

### CCM: Center for Computational Mathematics
CCM creates mathematical methods, algorithms and software used by the other centers: fast
transforms and solvers, statistical inference, signal and image processing. Its tools run from
cryo-EM (ångströms) to cosmological surveys. It has no system scale of its own, so it is drawn as a
band across the full length axis rather than as a region. A 37-decade box would dominate the figure
and imply it studies systems at every scale, when it builds tools used at every scale.

## Edge cases left out

Kept in `data/extensions.toml` and drawn with `--with-extensions`:

| Center | Edge case | Length | Time |
|---|---|---|---|
| CCQ | cavity-coupled materials (light–matter control) | to ~1 µm | fs – ps |
| CCN | behavior and natural scenes | to ~10 m | 0.1 s – decades |
| CCA | kinetic plasma scales (skin depths, gyro-radii) | mm – 10 km | ns – ms |

Also considered and not drawn: primordial black-hole horizons inside stars ("Hawking stars", CCA),
10⁻¹³–10⁻⁷ m. Including it would stretch CCA's region into CCQ's territory. That is true, but
misleading on an overview.

## Reading the figure

- **Three clusters.** Atomic (CCQ and ICC), biological (CCB and CCN) and astrophysical (CCA alone
  spans ~22 decades in length).
- **CCQ and ICC separate only in time:** ~7 decades for CCQ against ~19 for ICC.
- **Between ~1 m and ~10 km no center has a core program.** Geophysical and engineered scales are
  not part of Flatiron's research portfolio.

## Limitations

- The boxes are envelopes, not distributions: they show where the work *can* sit, not where most of
  it does.
- Bounds are rounded to half-decades at best. Moving any bound by ±0.5 decade would not change the
  picture.
- The ranges reflect public descriptions as of October 2026. Groups change; the data file is meant
  to be edited.

## Sources

Center pages on simonsfoundation.org, accessed 2026-10-06 (URLs are in `data/centers.toml`):

- Center for Computational Astrophysics: groups from planets to cosmology.
- Center for Computational Biology: research areas including Biological Transport Networks,
  Biophysical Modeling, Developmental Dynamics, Structural and Molecular Biophysics.
- Center for Computational Mathematics: Image and Signal Processing, Numerical Analysis, Machine
  Learning and Computational Statistics.
- Center for Computational Neuroscience: Computational Vision, Neural Circuits and Algorithms,
  Statistical Analysis of Neural Data, and others.
- Center for Computational Quantum Physics: Dynamics and Control, Quantum Materials, Theory and
  Methods.
- Initiative for Computational Catalysis: electronic structure, molecular dynamics and machine
  learning for heterogeneous and homogeneous catalysis.
