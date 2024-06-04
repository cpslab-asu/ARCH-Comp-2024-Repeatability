import numpy as np
from staliro.options import SignalOptions
from staliro.specifications import RTAMTDense
from staliro.signals import piecewise_constant

def load_specification_dict(benchmark, instance):

    
    
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
        
    if instance == 1:
        signals = [
                SignalOptions(control_points = [(1,3)]*8, signal_times=np.linspace(0.,40.,8)),
        ]
    elif instance == 2:
        signals = [
                SignalOptions(control_points = [(1,3)]*3, signal_times=np.linspace(0.,40.,3, endpoint=False), factory=piecewise_constant)
        ]
    
    if benchmark not in spec_dict.keys():
        raise ValueError(f"Inappropriate Benchmark name :{benchmark}. Expected one of {spec_dict.keys()}")
    
    return spec_dict[benchmark], signals