
import logging

import numpy as np
from numpy.typing import NDArray
from collections import OrderedDict
from math import pi
import numpy as np
import math

# from models import F16Model
# from Benchmark import Benchmark
from staliro.options import Options, SignalOptions
from staliro.specifications import TLTK, RTAMTDense
# from ..models import AutotransModel
from staliro.staliro import staliro, simulate_model
import scipy.io
import matplotlib.pyplot as plt

import pathlib
# from partx.partxInterface import run_partx
import numpy as np

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
        'default': 2335.0
    },
    'engine_power_lag': {
        'enabled': False,
        'default': 9
    }
})

import numpy as np
from numpy.typing import NDArray
from aerobench.run_f16_sim import run_f16_sim
from aerobench.examples.gcas.gcas_autopilot import GcasAutopilot
from staliro.core.interval import Interval
from staliro.core.model import Model, ModelData, StaticInput, Signals

F16DataT = NDArray[np.float_]
F16ResultT = ModelData[F16DataT, None]


class F16Model(Model[F16ResultT, None]):
    def __init__(self, static_params_map) -> None:
        self.F16_PARAM_MAP = static_params_map


    def get_static_params(self):
        static_params = []
        for param, config in self.F16_PARAM_MAP.items():
            if config['enabled']:
                static_params.append(config['range'])
        return static_params


    def _compute_initial_conditions(self, X):
        conditions = []
        index = 0

        for param, config in self.F16_PARAM_MAP.items():
            if config['enabled']:
                conditions.append(X[index])
                index = index + 1
            else:
                conditions.append(config['default'])

        return conditions

    def simulate(
        self, static: StaticInput, signals: Signals, intrvl: Interval
    ) -> F16ResultT:
        
        init_cond = self._compute_initial_conditions(static)
        
        step = 1 / 30
        autopilot = GcasAutopilot(init_mode="roll", stdout=False, gain_str="old")

        result = run_f16_sim(init_cond, intrvl.upper, autopilot, step, extended_states=True)
        trajectories = result["states"][:, 11:12].T.astype(np.float64)

        timestamps = np.array(result["times"], dtype=(np.float32))

        return ModelData(trajectories, timestamps)
    
model = F16Model(F16_PARAM_MAP)

# phi = "((G[0, 30] (rpm <= 3000)) -> (G[0,8] (speed <= 50)))"
# specification_rtamt = RTAMTDense(phi, {"speed":0, "rpm": 1})


def SimFn(X):
    initial_conditions = [
        math.pi / 4 + np.array([-math.pi / 20, math.pi / 30]),  # PHI
        -math.pi / 2 * 0.8 + np.array([0, math.pi / 20]),  # THETA
        -math.pi / 4 + np.array([-math.pi / 8, math.pi / 8]),  # PSI
    ]
    
    options = Options(runs=1, iterations=1, interval=(0, 15),  static_parameters = initial_conditions, signals=[])
    result = simulate_model(model, options, X)
    return result

def monitorFn(param, result):

    # phi = f"G[0,{param[0]}] altitude > 0"
    # specification = RTAMTDense(phi, {"altitude":0})
            
    if param[0] < 15:
        new_param = param[0]*10
        whole, frac = math.floor(new_param), new_param-math.floor(new_param)
        
        if frac < (1/3):                    
            index = 3*whole
        elif frac < (2/3):                    
            index = 3*whole + 1
        else:                    
            index = 3*whole + 2
    else:
        index = 150*3
    
    
    return np.min(result.states[0,:index+1])





from partx.partxInterface import run_partx
import numpy as np
from partx.bayesianOptimization import InternalBO
from partx.gprInterface import InternalGPR
from gpr_external import ExternalGPR_nonoise

def test_function(X):
    inputs = X[:3]
    params = X[3:]
    
    out = SimFn(inputs)

    moni_out = monitorFn(params, out)
    return moni_out

# Define the Oracle Function which defines the constraints.
# Since there is no constraint, return True
oracle_fun = None

BENCHMARK_NAME = f"f16_ptx"
init_reg_sup = nit_reg_sup = np.array([
        math.pi / 4 + np.array([-math.pi / 20, math.pi / 30]),  # PHI
        -math.pi / 2 * 0.8 + np.array([0, math.pi / 20]),  # THETA
        -math.pi / 4 + np.array([-math.pi / 8, math.pi / 8]),  # PSI
        [1.,15.]
])
# Function Dimesnioanlity set to 2 since we are searching in the 2-dimensional space
tf_dim = 4

# Max Budget is set to 500
max_budget = 2000

# Initial Sampling in the subregion is set to 20
init_budget = 20

# BO sampling in each subregion is set to 20
bo_budget = 20

# Continued Sampling for subregions is set to 100
cs_budget = 100

# Define n_tries. Since there are no constraints involved, set them to 1
n_tries_random_sampling = 1
n_tries_BO = 1

# Alpha, for Region Calssification percentile is set to 0.05 
alpha = 0.05

# R and M for quantile estimation in subregions is set 10 and 100 respectively
R = 20
M = 500

# Minimum subregion cutoff is set 0.001. Anything less than 0.001 of the voulme of the hypercube will be calssified as unknown
delta = 0.001

# Helps in Result Calculation. Here, we want to obtain results at 50%, 95% and 99%.
fv_quantiles_for_gp = [0.5,0.05,0.01]

# Every time a subregion is branched, it branches into 2 non-overallping regions
branching_factor = 2

# If true, perform branching such that region is divided into two subregions
uniform_partitioning = True

# Starting seed
start_seed = 12345

# Using Internal GPR and BO model
gpr_model = ExternalGPR_nonoise()
bo_model = InternalBO()

# Defining the sampling types
init_sampling_type = "lhs_sampling"
cs_sampling_type = "lhs_sampling"
q_estim_sampling = "lhs_sampling"
mc_integral_sampling_type = "lhs_sampling"
results_sampling_type = "lhs_sampling"
results_at_confidence = 0.95

# Run Part-X for 5 macro-replications
num_macro_reps = 10

# All benchmarks will be stored in this folder
results_folder_name = "/scratch/tkhandai/Partx_RV_Res"

# Run all the replication serially. If > 1, will run the replications parallaly.
num_cores = 1

# Run Part-X
results = run_partx(BENCHMARK_NAME, test_function, oracle_fun, num_macro_reps, init_reg_sup, tf_dim,
                max_budget, init_budget, bo_budget, cs_budget, n_tries_random_sampling, n_tries_BO,
                alpha, R, M, delta, fv_quantiles_for_gp,
                branching_factor, uniform_partitioning, start_seed, 
                gpr_model, bo_model, 
                init_sampling_type, cs_sampling_type, 
                q_estim_sampling, mc_integral_sampling_type, 
                results_sampling_type, 
                results_at_confidence, results_folder_name, num_cores) 