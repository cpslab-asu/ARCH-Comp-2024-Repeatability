import numpy as np
from staliro.options import SignalOptions
from staliro.specifications import RTAMTDense
from staliro.signals import piecewise_constant

def load_specification_dict(benchmark, instance):

    
    
    F16_phi = "G[0,15] (altitude>0)"

    spec_dict = {
        "F16a": RTAMTDense(F16_phi, {"altitude": 0}),
        }
    
    if benchmark not in spec_dict.keys():
        raise ValueError(f"Inappropriate Benchmark name :{benchmark}. Expected one of {spec_dict.keys()}")
    
    return spec_dict[benchmark], None