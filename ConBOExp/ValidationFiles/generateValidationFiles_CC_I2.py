from benchmarks.models import CCModel
from staliro.core.sample import Sample
from staliro.options import Options, SignalOptions
from staliro.specifications import RTAMTDense
from staliro.staliro import simulate_model
from staliro.signals import piecewise_constant

import pandas as pd
import sys
import pickle
import pathlib
from staliro.core import Result
import numpy as np
##################################################################################################################################################

# Needs change in this section only
model = "CC"
benchmark = "CCall"
instance = 2
folder = f"{model}_instance_{instance}"

CC1_phi = "G[0, 100] (y54 <= 40)"
CC2_phi = "G[0, 70] (F[0,30] (y54 >= 15))"
CC3_phi = "G[0, 80] ((G[0, 20] (y21 <= 20)) or (F[0,20] (y54 >= 40)))"
CC4_phi = "G[0, 65] (F[0,30] (G[0,5] (y54 >= 8)))"
CC5_phi = "G[0, 72] (F[0,8] ((G[0,5] (y21 >= 9)) -> (G[5,20] (y54 >= 9))))"

phi_1 = "(G[0, 50] (y21 >= 7.5))"
phi_2 = "(G[0, 50] (y32 >= 7.5))"
phi_3 = "(G[0, 50] (y43 >= 7.5))"
phi_4 = "(G[0, 50] (y54 >= 7.5))"
CCx_phi = phi_1 + " and " + phi_2 + " and " + phi_3 + " and " + phi_4


spec_dict = {
    "CC1": RTAMTDense(CC1_phi, {"y54": 3}),
    "CC2": RTAMTDense(CC2_phi, {"y54": 3}),
    "CC3": RTAMTDense(CC3_phi, {"y21": 0, "y54":3}),
    "CC4": RTAMTDense(CC4_phi, {"y54": 3}),    
    "CC5": RTAMTDense(CC5_phi, {"y21": 0, "y54":3}),    
    "CCx": RTAMTDense(CCx_phi,{"y21":0, "y32":1, "y43":2, "y54":3}),
}

spec_dict_key_ref = {
    "CC1": "CC1",
    "CC2": "CC2",
    "CC3": "CC3",
    "CC4": "CC4",
    "CC5": "CC5",
    "CCx": "CCx",
}


signals = [
    SignalOptions(control_points = [(0., 1.)] * 10, signal_times=np.linspace(0.0, 100.0, 10, endpoint=False), factory=piecewise_constant),
    SignalOptions(control_points = [(0., 1.)] * 10, signal_times=np.linspace(0.0, 100.0, 10, endpoint=False), factory=piecewise_constant),
]

options = Options(runs=1, iterations=1, interval=(0, 100),  signals=signals)
blackbox = CCModel()

##################################################################################################################################################

def generateRobustness(sample, inModel, options: Options, specification):
    result = simulate_model(inModel, options, sample)
    return specification.evaluate(result.trace.states, result.trace.times), result.extra




df = pd.DataFrame(columns=["system","property","instance","input","parameters","falsified","simulations","simulation_time","total time","robustness"])
for rep in range(0,10):

    history_dict = {}
    file = pathlib.Path().joinpath(folder).joinpath(folder).joinpath(f"{benchmark}_budget_1500_10_reps_instance_{instance}_repnumber{rep}")
    with open(file, "rb") as f:
        data:Result = pickle.load(f)
    
    for j,prop_name in enumerate(spec_dict.keys()):
        fals_samples_index = len(data.runs[0].result.components[j])

        sample = np.array(data.runs[0].history[fals_samples_index-1].sample.values)
        rob, input_signal = generateRobustness(sample, blackbox, options, spec_dict[prop_name])

        
        times = np.array(input_signal.times)
        values = np.array(input_signal.states)
        
        inp_str = "["
        for t,v in zip(times, values.T):
            _v = ""
            for x in v:
                _v += f"{x} "
            inp_str += f"{t} {_v[:-1]}; "
        inp_str = inp_str[:-2] + "]"

        df = pd.concat([pd.DataFrame([[model, spec_dict_key_ref[prop_name], instance, inp_str, "", "yes" if rob<= 0 else "no", fals_samples_index, "", "", rob]], columns=df.columns), df], ignore_index=True)

    
df.to_csv(f"{model}_instance_{instance}.csv", index=False)        