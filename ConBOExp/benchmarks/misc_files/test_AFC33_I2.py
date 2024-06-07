from ..models import AFCModel

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

mod_u_3 = "(ut <= 0.007) and (ut >= -0.007)"
AFC33_phi = f"G[11,50] ({mod_u_3})"

spec_dict = {
    "AFC33": RTAMTDense(AFC33_phi, {"ut": 0}),
    }

#####################################################################################################
# Define Signals
signals = [
    SignalOptions(control_points=[(900, 1100)], signal_times=np.linspace(0.,50.,1, endpoint=False), factory=piecewise_constant),
    SignalOptions(control_points= [(61.2, 81.2)] * 10, signal_times=np.linspace(0.,50.,10, endpoint=False), factory=piecewise_constant),
]

#####################################################################################################
# Define Options
options = Options(runs=1, iterations=1, interval=(0, 50), signals=signals)

#####################################################################################################
# Define Inputs and Outputs of model for plotting purpose

inputs = {0: ["Engine Speed", 1], 1: ["Throttle Angle", 10]}
outputs = {0: r"VerifMeas $(\mu_{t})$", 1: "Mode", 2: r"Angle $(\theta)$"}

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
        plt.savefig(result_directory.joinpath("AFC33_Signal_I2.pdf"))
        print("********************************************")
    return specification.evaluate(result.trace.states, result.trace.times)


signal_bounds = sum((signal.control_points for signal in signals), ())
bounds = options.static_parameters + signal_bounds
rng = np.random.default_rng(12345)
sample = np.array(Sample([rng.uniform(bound.lower, bound.upper) for bound in bounds]).values)

autotrans_blackbox = AFCModel()


for iterate, key in enumerate(spec_dict.keys()):
    if iterate == 0:
        pl = True
    else:
        pl = False
    rob = generateRobustness(sample,  autotrans_blackbox, options, spec_dict[key], pl)
    print(f"Rob. Sample for {key} = {rob}")
