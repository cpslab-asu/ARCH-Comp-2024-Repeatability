from ..models import NNModel

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

p11_phi = "(p1 >= 0)"
p12_phi = "(F[0,2] (G[0,1] (not(p2 <= 0))))"
NN1_phi = f"G[1,37] ({p11_phi} -> {p12_phi})"


p21_phi = "(p3 >= 0)"
p22_phi = "(F[0,2] (G[0,1] (not(p4 <= 0))))"
NN2_phi = f"G[1,37] ({p21_phi} -> {p22_phi})"

phi_1 = "F[0,1] (pos >= 3.2)"
phi_2 = "F[1,1.5] (G[0,0.5]((pos >= 1.75) and (pos <= 2.25)))"
phi_3 = "G[2,3] ((pos >= 1.825) and (pos <= 2.175))"
NNx_phi = f"{phi_1} and {phi_2} and {phi_3}"

spec_dict = {
    "NN1": RTAMTDense(NN1_phi, {"p1": 2, "p2": 3}),
    "NN2": RTAMTDense(NN2_phi, {"p3": 4, "p4": 5}),
    "NNx": RTAMTDense(NNx_phi, {"pos": 0}),
    }



#####################################################################################################
# Define Signals
signals = [
        SignalOptions(control_points = [(1,3)]*3, signal_times=np.linspace(0.,40.,3, endpoint=False), factory=piecewise_constant)
]

#####################################################################################################
# Define Options
options = Options(runs=1, iterations=1, interval=(0, 40),  signals=signals)

#####################################################################################################
# Define Inputs and Outputs of model for plotting purpose

inputs = {0: ["Ref", 3]}
outputs = {
    0: "Pos",  
    1: "Ref", 
    2:r"$|pos-ref| - (0.005 + (0.03 \times |ref|))$",
    3:r"$(0.005 + (0.03 \times |ref|)) - |pos-ref|$",
    4:r"$|pos-ref| - (0.005 + (0.04 \times |ref|))$",
    5:r"$(0.005 + (0.04 \times |ref|)) - |pos-ref|$"
    }

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
        plt.savefig(result_directory.joinpath("NN_Signal_I2.pdf"))
        print("********************************************")
    return specification.evaluate(result.trace.states, result.trace.times)




signal_bounds = sum((signal.control_points for signal in signals), ())
bounds = options.static_parameters + signal_bounds
rng = np.random.default_rng(12345)
sample = np.array(Sample([rng.uniform(bound.lower, bound.upper) for bound in bounds]).values)

autotrans_blackbox = NNModel()


for iterate, key in enumerate(spec_dict.keys()):
    if iterate == 0:
        pl = True
    else:
        pl = False
    rob = generateRobustness(sample,  autotrans_blackbox, options, spec_dict[key], pl)
    print(f"Rob. Sample for {key} = {rob}")


