import logging

import numpy as np
from numpy.typing import NDArray
import logging

from ..models import NNModel

from staliro.options import Options
from staliro.specifications import RTAMTDense
from staliro.staliro import simulate_model
from staliro.options import Options, SignalOptions
from staliro.signals import piecewise_constant
###############################################################################
# Define BlackBox Model
# Here, we define the Auto-Transmission Black Box Model from MATLAB into Python

model = NNModel(0.005, 0.03)
#####################################################################################################################
# Define Signals and Specification


signals = [
    SignalOptions(control_points = [(1,3)]*3, signal_times=np.linspace(0.,40.,3)),
    ]
options = Options(
    runs=1,
    iterations=1,
    interval=(0, 40),
    signals=signals,
)

# signals = [
#     SignalOptions(control_points = [(1,3)]*3, signal_times=np.linspace(0.,3.,3, endpoint=False), factory=piecewise_constant),
#     ]

# options = Options(
#     runs=1,
#     iterations=1,
#     interval=(0, 3),
#     signals=signals,
# )

print(options)
##################################################
# Define Specification
phi_1 = "F[0,1] (pos >= 3.2)"
phi_2 = "F[1,1.5] (G[0,0.5]((pos >= 1.75) and (pos <= 2.25)))"
phi_3 = "G[2,3] ((pos >= 1.825) and (pos <= 2.175))"
phi = f"(({phi_1}) and ({phi_2}) and ({phi_3}))"
specification = RTAMTDense(phi, {"pos": 0})
##################################################


def generateRobustness(sample, inModel, options: Options, specification):

    result = simulate_model(inModel, options, sample)
    # times = states_times
    return specification.evaluate(result.trace.states, result.trace.times)


sample = [1,2,1]

rob = generateRobustness(sample, model, options, specification)
print(rob)
