"""Generate numeric verification evidence and sample model-data CSV."""
import csv
import numpy as np
from model import simulate, sample, DT, STIM_START, STIM_END

def main():
    baseline=simulate(0); weak=simulate(2); strong=simulate(12)
    assert all(np.all(np.isfinite(arr)) for d in [baseline,weak,strong] for arr in d.values())
    assert abs(baseline['V'][0]+65)<1e-8
    assert np.max(np.abs(baseline['V'] + 65))<1.0, 'Unexpected drift at zero input'
    assert np.max(baseline['V'])<0, 'Zero stimulus should not fire'
    assert np.max(weak['V'])<0, '2 µA/cm² should be subthreshold for configured pulse'
    assert np.max(strong['V'])>0, '12 µA/cm² stimulus should fire under configured pulse'
    assert 0<DT<=.05
    print('PASS: zero current / rest stability / nonfinite-state checks')
    print(f'Zero stimulus max voltage: {max(baseline["V"]):.4f} mV')
    print(f'Weak stimulus max voltage: {max(weak["V"]):.4f} mV')
    print(f'Strong stimulus max voltage: {max(strong["V"]):.4f} mV')
    q=sample(strong,6.0)
    reconstructed=(q['I_stim']-q['INa']-q['IK']-q['IL'])
    print(f'Worked example at t=6 ms: I_stim={q["I_stim"]:.4f}, I_Na={q["INa"]:.4f}, I_K={q["IK"]:.4f}, I_L={q["IL"]:.4f} µA/cm²')
    print(f'Using C_m=1 µF/cm², dV/dt=(I_stim - I_Na - I_K - I_L)/C_m = {reconstructed:.4f} mV/ms')
    with open('sample_states.csv','w',newline='') as f:
        w=csv.writer(f)
        w.writerow(['time_ms','membrane_voltage_mV','stimulus_uA_cm2','sodium_conductance_mS_cm2','potassium_conductance_mS_cm2','sodium_current_uA_cm2','potassium_current_uA_cm2'])
        for i in range(0,len(strong['t']),20):
            w.writerow([round(float(strong[k][i]),6) for k in ['t','V','I_stim','gNa','gK','INa','IK']])
    print('Wrote sample_states.csv for workflow documentation')
if __name__=='__main__': main()
