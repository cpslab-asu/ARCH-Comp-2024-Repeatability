import numpy as np
from staliro.options import SignalOptions
from staliro.specifications import RTAMTDense
from staliro.signals import piecewise_constant

def load_specification_dict(benchmark, instance):

    
    
    SCa_phi = "G[30,35] ((pressure <= 87.5) and (pressure >= 87))"

    spec_dict = {
        "SCa": RTAMTDense(SCa_phi, {"pressure":3}),
        }
        
    if instance == 1:
        signals = [
            SignalOptions(control_points = [(3.95, 4.01)]*18, signal_times=np.linspace(0.,35.,18)),
        ]
    elif instance == 2:
        signals = [
            SignalOptions(control_points = [(3.95, 4.01)]*20, signal_times=np.linspace(0.,35.,20, endpoint = False), factory=piecewise_constant),
        ]
    
    if benchmark not in spec_dict.keys():
        raise ValueError(f"Inappropriate Benchmark name :{benchmark}. Expected one of {spec_dict.keys()}")
    
    return spec_dict[benchmark], signals