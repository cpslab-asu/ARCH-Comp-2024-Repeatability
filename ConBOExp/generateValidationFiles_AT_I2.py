from benchmarks.models import AutotransModel
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
model = "AT"
benchmark = "ATall"
instance = 2
folder = f"Benchmark_{benchmark}_instance_{instance}"



#####################################################################################################################
# Define Specifications



#####################################################################################################################
# Define Specifications

AT1_phi = "G[0, 20] (speed <= 120)"

AT2_phi = "G[0, 10] (rpm <= 4750)"

gear_1_phi = f"(gear <= 1.5 and gear >= 0.5)"
AT51_phi = f"G[0, 30] (((not {gear_1_phi}) and (F[0.001,0.1] {gear_1_phi})) -> (F[0.001, 0.1] (G[0,2.5] {gear_1_phi})))"

gear_2_phi = f"(gear <= 2.5 and gear >= 1.5)"
AT52_phi = f"G[0, 30] (((not {gear_2_phi}) and (F[0.001,0.1] {gear_2_phi})) -> (F[0.001, 0.1] (G[0,2.5] {gear_2_phi})))"

gear_3_phi = f"(gear <= 3.5 and gear >= 2.5)"
AT53_phi = f"G[0, 30] (((not {gear_3_phi}) and (F[0.001,0.1] {gear_3_phi})) -> (F[0.001, 0.1] (G[0,2.5] {gear_3_phi})))"

gear_4_phi = f"(gear <= 4.5 and gear >= 3.5)"
AT54_phi = f"G[0, 30] (((not {gear_4_phi}) and (F[0.001,0.1] {gear_4_phi})) -> (F[0.001, 0.1] (G[0,2.5] {gear_4_phi})))"

AT6a_phi = "((G[0, 30] (rpm <= 3000)) -> (G[0,4] (speed <= 35)))"
AT6b_phi = "((G[0, 30] (rpm <= 3000)) -> (G[0,8] (speed <= 50)))"
AT6c_phi = "((G[0, 30] (rpm <= 3000)) -> (G[0,20] (speed <= 65)))"
AT6abc_phi = f"{AT6a_phi} and {AT6b_phi} and {AT6c_phi}"

spec_dict = {
    "AT1": RTAMTDense(AT1_phi, {"speed": 0}),
    "AT2": RTAMTDense(AT2_phi, {"rpm": 1}),
    "AT51": RTAMTDense(AT51_phi, {"gear": 2}),    
    "AT52": RTAMTDense(AT52_phi, {"gear": 2}),    
    "AT53": RTAMTDense(AT53_phi, {"gear": 2}),    
    "AT54": RTAMTDense(AT54_phi, {"gear": 2}),    
    "AT61": RTAMTDense(AT6a_phi, {"speed": 0, "rpm":1}),
    "AT62": RTAMTDense(AT6b_phi, {"speed": 0, "rpm":1}),
    "AT63": RTAMTDense(AT6c_phi, {"speed": 0, "rpm":1}),
    "AT64": RTAMTDense(AT6abc_phi, {"speed": 0, "rpm":1}),
    }

#####################################################################################################
# Define Signals
signals = [
    SignalOptions(control_points = [(0, 100)]*7, signal_times=np.linspace(0.,50.,7, endpoint=False), factory=piecewise_constant),
    SignalOptions(control_points = [(0, 325)]*3, signal_times=np.linspace(0.,50.,3, endpoint=False), factory=piecewise_constant),
]

#####################################################################################################
# Define Options
options = Options(runs=1, iterations=1, interval=(0, 50), signals=signals)

spec_dict_key_ref = {
    "AT1": "AT1",
    "AT2": "AT2",
    "AT51": "AT51",
    "AT52": "AT52",
    "AT53": "AT53",
    "AT54": "AT54",
    "AT61": "AT6a",
    "AT62": "AT6b",
    "AT63": "AT6c",
    "AT64": "AT6abc",
}


blackbox = AutotransModel()

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