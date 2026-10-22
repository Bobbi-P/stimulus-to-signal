# Stimulus to Signal — Interactive neural-signaling story

An original **six-view**, Python-based dynamic scientific visualization aligned to the provided *Stimulus to Signal* proposal and midterm brief. Educational **simulation**, not observational data.

## Run

Requires Python 3.10+.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python verify.py
python app.py
```

Open **http://127.0.0.1:8050**. Keep the terminal running during the live demo. The `verify.py` script writes `sample_states.csv` to show example model data.

## Storyboard

1. **Stimulus:** moving stimulation slider changes the current pulse, 5–8 ms.
2. **Voltage & excitation:** traces show nonlinear membrane response and illustrative −55 mV guide.
3. **Ion channels:** time-linked Na⁺/K⁺ conductance and current traces with actual values on hover.
4. **Action-potential stages:** accumulated waveform and a current phase estimate with play, pause, step, reset.
5. **Propagation:** position-time voltage heatmap plus voltage-vs-position slice, using a **didactic time-delay approximation** rather than a cable equation.
6. **Scenario comparison:** 0, weak, strong stimulation, or reduced Na⁺ conductance compared on identical axes.

All dynamic graphs respond to shared parameters and simulation time. Interactions include controls, tooltips, comparison dropdown, and time playback.

## Mathematical model, equations and units

Classic Hodgkin–Huxley **single-compartment** conductance model (squid-axon parameters):

- `C_m dV/dt = I_stim - I_Na - I_K - I_L`, with `C_m = 1 µF/cm²`.
- `I_Na = (120 * sodium_scale) m³h (V - 50)`.
- `I_K = (36 * potassium_scale) n⁴ (V + 77)`.
- `I_L = 0.3(V + 54.387)`.
- `dm/dt = α_m(V)(1−m) − β_m(V)m`; corresponding equations for `h`, `n`.
- `α_m = 0.1 (V+40)/(1-exp(-(V+40)/10))`.
- `β_m = 4 exp(-(V+65)/18)`.
- `α_h = .07 exp(-(V+65)/20)`; `β_h = 1/(1+exp(-(V+35)/10))`.
- `α_n = .01 (V+55)/(1-exp(-(V+55)/10))`.
- `β_n = .125 exp(-(V+65)/80)`.

Time `ms`; voltage `mV`; current density `µA/cm²`; conductance `mS/cm²`; distance `mm`. Integration: fixed-step RK4, `dt = 0.025 ms`; initial voltage `-65 mV`, gating variables at equilibrium at -65 mV; simulated time `0..40 ms`; square current pulse `5 ≤ t < 8 ms`.

**Important:** A horizontal −55 mV visual guide is approximate; HH dynamics have no hard fixed threshold. Signed ionic currents represent current direction. Computed states are cached by rounded slider inputs. If a state is nonfinite, the model raises an exception instead of hiding or interpolating it. No observational missing data, percentages, or medians are involved.

### Propagation caveat

For teaching the sequencing of activation in space, `V(x,t) = V_point(t − x/c)` with an **illustrative** propagation speed `c = 0.4 mm/ms`. This is **not** a spatial Hodgkin–Huxley/cable-equation solution; propagation speed and responses to axon parameters are not predictions. This is a justified contingency simplifying the spatial model, as allowed in the proposal. Do not claim it quantitatively validates conduction velocity.

## Data-to-visual reproducibility

1. `model.py` defines inputs/units, gating functions and current/voltage differential equations.
2. Its RK4 integrator generates aligned arrays of t, V, m/h/n, conductances and current densities.
3. `verify.py` checks initialization at −65 mV, zero-input resting stability, no spike at zero input, a strong-input spike, and finite results. It prints a **numerical worked example** at `t=6 ms`, including a reconstructed `dV/dt`.
4. `verify.py` exports sampled records to CSV (named columns specify units).
5. `app.py` transforms shared trajectories into six linked views, switching comparators without altering trace axes.

## Live presentation outline (15 minutes)

- 0–2 minutes: question, neuron model and simulation data.
- 2–10 minutes: demonstrate views 1–5; adjust stimulus; play, pause, step and inspect a tooltip.
- 10–12 minutes: view 6 compare zero, weak and strong stimuli; ask audience: **“Does a stronger stimulus make a spike arbitrarily taller, or mainly change whether one occurs?”**
- 12–13 minutes: inspect `model.py`, `verify.py`, sample CSV and limitations.
- 13–15 minutes: discussion/questions.

## Report completion checklist

The submitted PDF still needs actual screenshots of **all six working views**, instructor feedback and revisions (not supplied), real peer evaluation notes (not invented), source URLs and repository/application links when published, and an explicit AI-assistance and independent-verification disclosure. The app and this README do not constitute the final submitted PDF by themselves.

## Sources

- Hodgkin, A. L., & Huxley, A. F. (1952). *A quantitative description of membrane current and its application to conduction and excitation in nerve.* Journal of Physiology, 117, 500–544. https://doi.org/10.1113/jphysiol.1952.sp004764
- Purves, D. et al. (2001). *Neuroscience*, 2nd edition. Sinauer Associates.

## Attribution

App and model code created with AI assistance for development and drafting. Numerical model behavior must be independently checked and reviewed by project author before submission; do not imply the design was independently coded or scientifically validated by a reviewer.
