from ..models import AutotransModel

import pathlib
import numpy as np
from matplotlib import pyplot as plt

from staliro.core.sample import Sample
from staliro.options import Options, SignalOptions
from staliro.specifications import RTAMTDense
from staliro.staliro import simulate_model
from staliro.signals import piecewise_constant



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

#####################################################################################################
# Define Inputs and Outputs of model for plotting purpose

inputs = {0: ["Throttle", 7], 1: ["Brake", 3]}
outputs = {0: "Speed", 1: "RPM", 2: "Gear"}

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
        plt.savefig(result_directory.joinpath("AT_Signal_I2.pdf"))
        print("********************************************")
    return specification.evaluate(result.trace.states, result.trace.times)




signal_bounds = sum((signal.control_points for signal in signals), ())
bounds = options.static_parameters + signal_bounds
rng = np.random.default_rng(12345)
sample = np.array(Sample([rng.uniform(bound.lower, bound.upper) for bound in bounds]).values)

autotrans_blackbox = AutotransModel()


for iterate, key in enumerate(spec_dict.keys()):
    if iterate == 0:
        pl = True
    else:
        pl = False
    rob = generateRobustness(sample,  autotrans_blackbox, options, spec_dict[key], pl)
    print(f"Rob. Sample for {key} = {rob}")


