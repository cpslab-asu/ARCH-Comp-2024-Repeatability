from ..models import CCModel

import pathlib
import numpy as np
from matplotlib import pyplot as plt

from staliro.core.sample import Sample
from staliro.options import Options, SignalOptions
from staliro.specifications import RTAMTDense
from staliro.staliro import simulate_model




#####################################################################################################################
# Define Specifications

CC1_phi = "G[0, 100] (y54 <= 40)"
CC2_phi = "G[0, 70] (F[0,30] (y54 >= 15))"
CC3_phi = "G[0, 80] ((G[0, 20] (y21 <= 20)) or (F[0,20] (y54 >= 40)))"
CC4_phi = "G[0,65] (F[0,30] (G[0,5] (y54 >= 8)))"
CC5_phi = "G[0,72] (F[0,8] ((G[0,5] (y21 >= 9)) -> (G[5,20] (y54 >= 9))))"

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



#####################################################################################################
# Define Signals
signals = [
    SignalOptions(control_points = [(0., 1.)] * 10, signal_times=np.linspace(0.0, 100.0, 10)),
    SignalOptions(control_points = [(0., 1.)] * 10, signal_times=np.linspace(0.0, 100.0, 10))
]

#####################################################################################################
# Define Options
options = Options(runs=1, iterations=1, interval=(0, 100),  signals=signals)

#####################################################################################################
# Define Inputs and Outputs of model for plotting purpose

inputs = {0: ["Throttle", 10], 1: ["Brake", 10]}
outputs = {0: "C2-C1", 1: "C3-C2", 2: "C4-C3", 3:"C5-C4"}

#####################################################################################################
# Define Run
def generateRobustness(sample, inModel, options: Options, specification, plot = False):
    result = simulate_model(inModel, options, sample)
    if plot:
        print("********************************************")
        total_dimensionality = sum([val[1] for val in inputs.values()])
        print(f"Number of control points (dimensionality) = {total_dimensionality}")
        print(f"Number of Input Signals = {len(inputs)}")
        print(f"Number of Output Signals = {len(outputs)}")


        fig, (ax1, ax2) = plt.subplots(2)

        
        input_indices = 0
        for input_num, (inp_index, [inp_name, dim]) in enumerate(zip(inputs.keys(), inputs.values())):
            
            ax1.plot(result.extra.times , result.extra.states[inp_index], label = inp_name)
            ax1.plot(options.signals[input_num].signal_times, sample[input_indices:input_indices + dim], ".")
            input_indices = input_indices+dim
            
        out_trace = np.array(result.trace.states)
        for out_index, out_name in zip(outputs.keys(), outputs.values()):
            ax2.plot(result.trace.times, out_trace[:,out_index], label = out_name)

        ax1.legend()
        ax2.legend()
        plt.tight_layout()

        base_path = pathlib.Path()
        result_directory = base_path.joinpath("images")
        result_directory.mkdir(exist_ok=True)
        plt.savefig(result_directory.joinpath("CC_Signal_I1.pdf"))
        print("********************************************")
    return specification.evaluate(result.trace.states, result.trace.times)




signal_bounds = sum((signal.control_points for signal in signals), ())
bounds = options.static_parameters + signal_bounds
rng = np.random.default_rng(12345)
sample = np.array(Sample([rng.uniform(bound.lower, bound.upper) for bound in bounds]).values)

autotrans_blackbox = CCModel()


for iterate, key in enumerate(spec_dict.keys()):
    if iterate == 0:
        pl = True
    else:
        pl = False
    rob = generateRobustness(sample,  autotrans_blackbox, options, spec_dict[key], pl)
    print(f"Rob. Sample for {key} = {rob}")


