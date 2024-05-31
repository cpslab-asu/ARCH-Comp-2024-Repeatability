import logging

import numpy as np
from numpy.typing import NDArray
import logging

from ..models import AFCModel

from staliro.options import Options
from staliro.specifications import RTAMTDense
from staliro.staliro import simulate_model
from staliro.options import Options, SignalOptions
from staliro.signals import piecewise_constant
###############################################################################
# Define BlackBox Model
# Here, we define the Auto-Transmission Black Box Model from MATLAB into Python

model = AFCModel()
#####################################################################################################################
# Define Signals and Specification


signals = [
    SignalOptions(control_points=[(900, 1100)], factory=piecewise_constant),
    SignalOptions(control_points= [(0, 61.2)] * 10, signal_times=np.linspace(0.,50.,10), factory=piecewise_constant),
]
options = Options(runs=1, iterations=1, interval=(0, 50),  signals=signals)
##################################################
# Define Specification
rise = "(theta <= 8.8) and (F[0,0.05] (theta >= 40))"
fall = "(theta >= 40) and (F[0,0.05] (theta <= 8.8))"
mod_u_1 = "G[1,5] ((ut <= 0.008) and (ut >= -0.008))"
AFC27_phi = f"G[11,50] (({rise} or {fall}) -> ({mod_u_1}))"

specification_rtamt = RTAMTDense(AFC27_phi, {"theta": 2, "ut": 0})

##################################################


def generateRobustness(sample, inModel, options: Options, specification):
    
    result = simulate_model(inModel, options, sample)
    
    print(result.trace.states)
    print(result.trace.times)
    # plt.plot(result.times, result.states[2,:])
    # plt.show()
    return specification.evaluate(result.trace.states, result.trace.times)




sample = [958,19, 14, 51, 58, 47, 56, 38, 4, 7, 57]

rob = generateRobustness(sample, model, options, specification_rtamt)
print(rob)
