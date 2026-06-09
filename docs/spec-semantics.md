# ECHO-13 Operational Semantics (small-step)

This document provides a concise small-step operational semantics for the core ECHO-13 model, expressed to map directly to the reference implementation in `echo13.py`.

Notation
- Σ = (E, P, B, Env, dt) global state at a discrete step
- E = { e_i } set of entities; each entity e = (id, p, τ, ρ, φ, T)
  - p ∈ R^2: position
  - τ ∈ R: tempo
  - ρ ∈ R+: density
  - φ ∈ R: phase
  - T = [p_0, p_1, ...]: append-only trace (history of positions)
- P = { {a,b} } set of unordered pairs (relational units)
- Braid(pair) = (crossings, width)
- Env = (echo, curvature, sediment)

Single-step transition (small-step)
Given a fixed time increment dt and deterministic directions dir(e) for each entity, a single step Σ --(dt)--> Σ' is defined by the following ordered operations (this order maps directly to `run_echo13` in `echo13.py`):

1. Entity motion (for each e ∈ E)
   - p' := p + τ * dir(e) * dt
   - T' := T ⧺ [p'] (append-only)
   - φ' := φ + α * dt  (in the implementation α = 0.01)
   - τ, ρ unchanged here (unless updated later by harmonize or SOR)

2. Relational evaluation (for each pair {a,b} ∈ P)
   - d := ||p'_a − p'_b||
   - If d < θ_harmonize then harmonize tempos:
       mean := (τ_a + τ_b)/2
       τ_a' := (τ_a + mean)/2
       τ_b' := (τ_b + mean)/2
     (This is the weighted averaging used in `Pair.harmonize`.)

3. Braid update (for each pair {a,b})
   - crossings := floor( min(|T_a'|, |T_b'|) / 12 )
   - width := d  (pair distance after motion)
   (See `Braid.update`.)

4. Environment update
   - Env.echo := Env.echo + k1 * width   (k1 = 0.001 in code)
   - Env.curvature := Env.curvature + k2 * crossings (k2 = 0.0005)
   - Env.sediment := Env.sediment + k3 (k3 = 0.0001)
   (See `Environment.update`.)

5. Soft Overlap Compression (SOR) for pair {a,b}
   - overlap := | { pos ∈ T_a' ∩ T_b' } |
   - ratio := overlap / max(|T_a'|, |T_b'|)
   - if ratio > threshold then
       Δ := k * log(1 + overlap)  (k = 0.5 in code)
       ρ_a' := ρ_a + Δ
       ρ_b' := ρ_b + Δ
   (See `soft_overlap_compression`.)

Determinism
- All rules above are fully deterministic given:
  - fixed initial Σ
  - deterministic direction functions dir(e)
  - fixed numeric constants (thresholds, coefficients)
  - deterministic numeric arithmetic
- The reference `run_echo13` seeds Python's PRNG with `random.seed(13)` before running, which keeps any seeded randomness repeatable. Avoid using external non-deterministic resources in experiments if you want bit-for-bit repeatability.

Invariants and properties
- Trace append-only: |T'| = |T| + 1 after each entity motion step.
- Non-destructive memory growth: SOR increases density ρ but never removes entries from traces.
- Deterministic update ordering: the engine executes steps in a fixed order (motion → harmonize → braid → environment → SOR).

Mapping to implementation
- `echo13.py` contains the minimal implementation. The functions and classes that implement the above rules are:
  - Entity.update: performs motion, appends to trace, updates phase
  - Pair.distance and Pair.harmonize: compute distance and harmonize tempos
  - Braid.update: computes crossings and width from traces and pair distance
  - Environment.update: updates echo, curvature, sediment
  - soft_overlap_compression: computes overlap ratio and increases densities
  - run_echo13: orchestrates the full step loop and shows example output

Suggested next steps
- Add automated tests that assert the invariants above (trace append-only, SOR increases density when traces overlap, deterministic runs produce identical final states).
- Add CI (GitHub Actions) to run pytest on push/PR.
- If formal analysis is desired, translate these small-step rules into an SOS inference-rule format or a mechanized model (TLA+/PlusCal, Coq, Lean) and prove determinism and invariants.
