from benchmarks.models import SCModel
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
model = "SC"
benchmark = "SC"
instance = 2
folder = f"Benchmark_{benchmark}_instance_{instance}"



SCa_phi = "G[30,35] ((pressure <= 87.5) and (pressure >= 87))"

spec_dict = {
    "SCa": RTAMTDense(SCa_phi, {"pressure":3}),
    }

#####################################################################################################
# Define Signals

signals = [
    SignalOptions(control_points = [(3.95, 4.01)]*20, signal_times=np.linspace(0.,35.,20, endpoint = False), factory=piecewise_constant),
]


#####################################################################################################
# Define Options
options = Options(runs=1, iterations=1, interval=(0, 35), signals=signals)


spec_dict_key_ref = {
    "SCa": "SCa",
}



blackbox = SCModel()

##################################################################################################################################################

def generateRobustness(sample, inModel, options: Options, specification):
    result = simulate_model(inModel, options, sample)
    return specification.evaluate(result.trace.states, result.trace.times), result.extra




df = pd.DataFrame(columns=["system","property","instance","input","parameters","falsified","simulations","simulation_time","total time","robustness"])
for rep in range(0,10):

    history_dict = {}
    file = pathlib.Path().joinpath("ConBO").joinpath(f"Benchmark_{benchmark}_instance_{instance}").joinpath(f"benchmark_{benchmark}_instance_{instance}_budget_1500_10_reps_{rep}_repnumber")
    with open(file, "rb") as f:
        data:Result = pickle.load(f)
    ts = np.diff(np.array([data.runs[0].result.start_timestamp] + data.runs[0].result.iteration_timestamps))
    model_ts = [j.timing.model for j in data.runs[0].history]
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

        print(f"model: {np.sum(model_ts[:fals_samples_index])}\ntotal: {np.sum(ts[:fals_samples_index])}")
        print("***********")
        assert np.sum(model_ts[:fals_samples_index])<= np.sum(ts[:fals_samples_index])
        df = pd.concat([pd.DataFrame([[model, spec_dict_key_ref[prop_name], instance, inp_str, "", "yes" if rob<= 0 else "no", fals_samples_index, np.sum(model_ts[:fals_samples_index]), np.sum(ts[:fals_samples_index]), rob]], columns=df.columns), df], ignore_index=True)

    
df.to_csv(f"CONBO_{model}_benchmark_{benchmark}_instance_{instance}.csv", index=False)