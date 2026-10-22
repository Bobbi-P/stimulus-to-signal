"""Classic squid-axon Hodgkin–Huxley point membrane + explicitly illustrative propagation.
Units: time ms, voltage mV, current uA/cm^2, conductance mS/cm^2, distance mm.
This is a scientific simulation, not patient data.
"""
from functools import lru_cache
import numpy as np

DT = 0.025
T_END = 40.0
C_M = 1.0
G_NA, G_K, G_L = 120.0, 36.0, 0.3
E_NA, E_K, E_L = 50.0, -77.0, -54.387
STIM_START, STIM_END = 5.0, 8.0
REST = -65.0


def vtrap(x, y):
    z = x / y
    if abs(z) < 1e-6:
        return y * (1 - z / 2 + z * z / 12)
    return x / np.expm1(z)


def rates(v):
    am = 0.1 * vtrap(-(v + 40), 10)
    bm = 4 * np.exp(-(v + 65) / 18)
    ah = 0.07 * np.exp(-(v + 65) / 20)
    bh = 1 / (1 + np.exp(-(v + 35) / 10))
    an = 0.01 * vtrap(-(v + 55), 10)
    bn = 0.125 * np.exp(-(v + 65) / 80)
    return am, bm, ah, bh, an, bn


def derivative(t, s, stimulus, sodium_scale, potassium_scale):
    v, m, h, n = s
    am, bm, ah, bh, an, bn = rates(v)
    gna = G_NA * sodium_scale * m**3 * h
    gk = G_K * potassium_scale * n**4
    ina = gna * (v - E_NA)
    ik = gk * (v - E_K)
    il = G_L * (v - E_L)
    current = stimulus if STIM_START <= t < STIM_END else 0.0
    dv = (current - ina - ik - il) / C_M
    return np.array([dv, am * (1-m) - bm*m, ah*(1-h) - bh*h, an*(1-n)-bn*n])


@lru_cache(maxsize=80)
def simulate(stimulus=12.0, sodium_scale=1.0, potassium_scale=1.0):
    """Fixed-step RK4; returns arrays indexed at uniform 0.025 ms spacing."""
    stimulus, sodium_scale, potassium_scale = map(float, (stimulus, sodium_scale, potassium_scale))
    t = np.arange(0, T_END + DT/2, DT)
    s = np.empty((len(t), 4), dtype=float)
    am, bm, ah, bh, an, bn = rates(REST)
    s[0] = [REST, am/(am+bm), ah/(ah+bh), an/(an+bn)]
    for i in range(len(t)-1):
        ti, y = t[i], s[i]
        k1 = derivative(ti, y, stimulus, sodium_scale, potassium_scale)
        k2 = derivative(ti + DT/2, y + DT*k1/2, stimulus, sodium_scale, potassium_scale)
        k3 = derivative(ti + DT/2, y + DT*k2/2, stimulus, sodium_scale, potassium_scale)
        k4 = derivative(ti + DT, y + DT*k3, stimulus, sodium_scale, potassium_scale)
        s[i+1] = y + DT*(k1+2*k2+2*k3+k4)/6
        if not np.all(np.isfinite(s[i+1])):
            raise FloatingPointError(f'Nonfinite neuron state at time {t[i+1]} ms')
    v,m,h,n = s.T
    gna = G_NA * sodium_scale * m**3 * h
    gk = G_K * potassium_scale * n**4
    current = np.where((t >= STIM_START) & (t < STIM_END), stimulus, 0.)
    return dict(t=t, V=v, m=m, h=h, n=n, gNa=gna, gK=gk,
                INa=gna*(v-E_NA), IK=gk*(v-E_K),
                IL=G_L*(v-E_L), I_stim=current)


def sample(data, time_ms):
    idx = int(np.clip(round(time_ms / DT), 0, len(data['t'])-1))
    return {k: float(v[idx]) for k, v in data.items()}


def propagated_voltage(data, x_mm, time_ms, speed=0.4):
    """Illustrative delayed copies of point-membrane waveform, not a cable-equation solution."""
    delay = np.asarray(x_mm) / speed
    shifted_time = np.asarray(time_ms) - delay
    return np.interp(shifted_time, data['t'], data['V'], left=float(data['V'][0]), right=float(data['V'][-1]))
