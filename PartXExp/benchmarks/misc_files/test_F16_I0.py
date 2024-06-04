from ..models import F16Model
from collections import OrderedDict
from math import pi

import pathlib
import numpy as np
from matplotlib import pyplot as plt

from staliro.core.sample import Sample
from staliro.options import Options, SignalOptions
from staliro.specifications import RTAMTDense
from staliro.staliro import simulate_model

F16_PARAM_MAP = OrderedDict({
    'air_speed': {
        'enabled': False,
        'default': 540
    },
    'angle_of_attack': {
        'enabled': False,
        'default': np.deg2rad(2.1215)
    },
    'angle_of_sideslip': {
        'enabled': False,
        'default': 0
    },
    'roll': {
        'enabled': True,
        'default': None,
        'range': (pi / 4) + np.array((-pi / 20, pi / 30)),
    },
    'pitch': {
        'enabled': True,
        'default': None,
        'range': (-pi / 2) * 0.8 + np.array((0, pi / 20)),
    },
    'yaw': {
        'enabled': True,
        'default': None,
        'range': (-pi / 4) + np.array((-pi / 8, pi / 8)),
    },
    'roll_rate': {
        'enabled': False,
        'default': 0
    },
    'pitch_rate': {
        'enabled': False,
        'default': 0
    },
    'yaw_rate': {
        'enabled': False,
        'default': 0
    },
    'northward_displacement': {
        'enabled': False,
        'default': 0
    },
    'eastward_displacement': {
        'enabled': False,
        'default': 0
    },
    'altitude': {
        'enabled': False,
        'default': 2338.0
    },
    'engine_power_lag': {
        'enabled': False,
        'default': 9
    }
})


blackbox = F16Model(static_params_map=F16_PARAM_MAP)

#####################################################################################################################
# Define Specifications

F16_phi = "G[0,15] (altitude>0)"

spec_dict = {
    "F16_phi": RTAMTDense(F16_phi, {"altitude": 0}),
    }



#####################################################################################################
# Define Signals
signals = [
    SignalOptions(control_points = [(0., 1.)] * 10, signal_times=np.linspace(0.0, 100.0, 10)),
    SignalOptions(control_points = [(0., 1.)] * 10, signal_times=np.linspace(0.0, 100.0, 10))
]

#####################################################################################################
# Define Options
options = Options(runs=1, iterations=1, interval=(0, 15),  static_parameters = blackbox.get_static_params(), signals=[])

#####################################################################################################
# Define Inputs and Outputs of model for plotting purpose

inputs = {0: ["Roll", 1], 1: ["Pitch", 1], 2: ["Yaw", 2]}
outputs = {0: "Altitude"}

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


        fig, (ax1) = plt.subplots(1)

        input_indices = 0
            
        out_trace = np.array(result.trace.states).T
        
        for out_index, out_name in zip(outputs.keys(), outputs.values()):
            ax1.plot(result.trace.times, out_trace[:,out_index], label = out_name)

        ax1.set_title(f"Input = {result.extra}")
        ax1.legend()
        plt.tight_layout()

        base_path = pathlib.Path()
        result_directory = base_path.joinpath("images")
        result_directory.mkdir(exist_ok=True)
        plt.savefig(result_directory.joinpath("F16_Signal_I0.pdf"))
        print("********************************************")
    return specification.evaluate(result.trace.states, result.trace.times)




signal_bounds = sum((signal.control_points for signal in signals), ())
bounds = options.static_parameters + signal_bounds
rng = np.random.default_rng(12345)
sample = np.array(Sample([rng.uniform(bound.lower, bound.upper) for bound in bounds]).values)



for iterate, key in enumerate(spec_dict.keys()):
    if iterate == 0:
        pl = True
    else:
        pl = False
    rob = generateRobustness(sample,  blackbox, options, spec_dict[key], pl)
    print(f"Rob. Sample for {key} = {rob}")


