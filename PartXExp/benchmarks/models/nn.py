from staliro.core.interval import Interval
from staliro.core.model import Model, ModelInputs, Trace, ExtraResult
import numpy as np
from numpy.typing import NDArray
try:
    import matlab
    import matlab.engine
except ImportError:
    _has_matlab = False
else:
    _has_matlab = True
 

NNDataT = NDArray[np.float_]
NNResultT = ExtraResult[NNDataT, NNDataT]

from matplotlib import pyplot as plt
class NNModel(Model[NNResultT, None]):
    MODEL_NAME = "narmamaglev_v1"

    def __init__(self) -> None:
        if not _has_matlab:
            raise RuntimeError(
                "Simulink support requires the MATLAB Engine for Python to be installed"
            )

        engine = matlab.engine.start_matlab()
        # engine.addpath("examples")
        model_opts = engine.simget(self.MODEL_NAME)
        
        self.sampling_step = 0.01
        self.engine = engine
        self.model_opts = engine.simset(model_opts, "SaveFormat", "Array")

        self.alpha_1 = 0.005
        self.beta_1 = 0.03
        
        self.alpha_2 = 0.005
        self.beta_2 = 0.04
        

    def simulate(
        self, inputs:ModelInputs, intrvl: Interval
    ) -> NNResultT:
        
        sim_t = matlab.double([0, intrvl.upper])
        n_times = intrvl.length // self.sampling_step + 2
        signal_times = np.linspace(intrvl.lower, intrvl.upper, int(n_times))
        signal_values = np.array([[signal.at_time(t) for t in signal_times] for signal in inputs.signals])
        # plt.plot(signal_times, signal_values[0,:])
        # plt.show()
        # dfagv
        self.engine.workspace["u_ts"] = 0.001
        model_input = matlab.double(
            np.row_stack((signal_times, signal_values)).T.tolist()
        )
        
        timestamps, _, data = self.engine.sim(
            self.MODEL_NAME, sim_t, self.model_opts, model_input, nargout=3
        )
        
        timestamps_array = np.array(timestamps).flatten()
        data_array = np.array(data)
        
        pos = data_array[:,0]

        pos_ref_mod = np.absolute(data_array[:,0] - data_array[:,2])
        mod_ref = np.absolute(data_array[:,2])

        
        p1 = pos_ref_mod - (self.alpha_1 + (self.beta_1 * mod_ref))
        p2 = (self.alpha_1 + (self.beta_1 * mod_ref)) - pos_ref_mod

        p3 = pos_ref_mod - (self.alpha_2 + (self.beta_2 * mod_ref))
        p4 = (self.alpha_2 + (self.beta_2 * mod_ref)) - pos_ref_mod

        sim_data = np.vstack([pos, data_array[:,2], p1, p2, p3, p4])
        outTrace = Trace(timestamps_array, sim_data.T)
        inTrace = Trace(signal_times, signal_values)
        return NNResultT(outTrace, inTrace)