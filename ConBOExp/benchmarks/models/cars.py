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
 

CCDataT = NDArray[np.float_]
CCResultT = ExtraResult[CCDataT, CCDataT]

class CCModel(Model[CCResultT, None]):
    MODEL_NAME = "cars"

    def __init__(self) -> None:
        if not _has_matlab:
            raise RuntimeError(
                "Simulink support requires the MATLAB Engine for Python to be installed"
            )

        engine = matlab.engine.start_matlab()
        # engine.addpath("examples")
        model_opts = engine.simget(self.MODEL_NAME)

        self.sampling_step = 0.05
        self.engine = engine
        self.model_opts = engine.simset(model_opts, "SaveFormat", "Array")

    def simulate(self, inputs:ModelInputs, intrvl: Interval) -> CCResultT:
        sim_t = matlab.double([0, intrvl.upper])
        n_times = (intrvl.length // self.sampling_step) + 2
        signal_times = np.linspace(intrvl.lower, intrvl.upper, int(n_times))
        signal_values = np.array([[signal.at_time(t) for t in signal_times] for signal in inputs.signals])
        
        model_input = matlab.double(np.row_stack((signal_times, signal_values)).T.tolist())

        timestamps, _, data = self.engine.sim(
            self.MODEL_NAME, sim_t, self.model_opts, model_input, nargout=3
        )

        
        data_array = np.array(data)
        y54 = (data_array[:,4]-data_array[:,3]).reshape((-1,1))
        y43 = (data_array[:,3]-data_array[:,2]).reshape((-1,1))
        y32 = (data_array[:,2]-data_array[:,1]).reshape((-1,1))
        y21 = (data_array[:,1]-data_array[:,0]).reshape((-1,1))
        diff_array = np.hstack((y21, y32, y43, y54))
        timestamps_list = np.array(timestamps).flatten()
        data_list = np.array(diff_array)
        trace = Trace(timestamps_list, data_list)

        inTrace = Trace(signal_times, signal_values)
        return CCResultT(trace, inTrace)
