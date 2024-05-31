import logging

import numpy as np
from numpy.typing import NDArray

from staliro.options import Options, SignalOptions
from staliro.specifications import TLTK, RTAMTDense
from ..models import SCModel
from staliro.staliro import staliro, simulate_model
import scipy.io
import matplotlib.pyplot as plt

signals = [
    SignalOptions(control_points = [(3.95, 4.01)]*18, signal_times=np.linspace(0.,35.,18)),
]

print(signals)
options = Options(runs=1, iterations=1, interval=(0, 35), signals=signals)



phi = "G[30,35] ((pressure <= 87.5) and (pressure >= 87))"
specification_rtamt = RTAMTDense(phi, {"pressure":0})


def generateRobustness(sample, inModel, options: Options, specification):
    
    result = simulate_model(inModel, options, sample)
    
    return specification.evaluate(result.trace.states, result.trace.times)

sample1 = [3.99]*14 + [4.01]*4

autotrans_blackbox = SCModel()

rob1 = generateRobustness(sample1,  autotrans_blackbox, options, specification_rtamt)


print(f"Rob. Sample 1 = {rob1}")
# print(str(rob1))

