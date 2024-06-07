from collections import OrderedDict
from math import pi
import numpy as np
import pathlib
import pickle

from models import F16Model
from Benchmark import Benchmark


from staliro.staliro import staliro
from staliro.options import Options



from lsemibo.coreAlgorithm import LSemiBOOptimizer
from gpr_external import ExternalGPR as InternalGPR
from lsemibo.classifierInterface import InternalClassifier
from lsemibo.coreAlgorithm.specification import Requirement

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

class Benchmark_F16(Benchmark):
    def __init__(self, benchmark, instance, results_folder) -> None:
        if benchmark != "F16":
            raise ValueError("Inappropriate Benchmark name")

        self.benchmark = benchmark
        self.results_folder = results_folder
        
        self.model = F16Model(F16_PARAM_MAP)
        self.initial_conditions = self.model.get_static_params()

        phi = "G[0,15] altitude > 0"
        self.phi_list = [phi]
        #self.phi_list = [AT1_phi]
        self.pred_map = {"altitude":([0,1,2], 0)}
        
        self.is_budget = 100
        self.cs_budget = 1000
        self.max_budget = 1500
        self.NUMBER_OF_MACRO_REPLICATIONS = 10

        self.top_k = 3
        self.classified_sample_bias = 0.9
        self.tf_dim = 3
        self.seed = 123466
        self.instance = instance
        

        self.R = 10
        self.M = 500
        

        
        self.options = Options(runs=1, iterations=self.max_budget, interval=(0, 15),  static_parameters = self.initial_conditions, signals=[])
        
        
        self.specification = Requirement(self.tf_dim, self.phi_list, self.pred_map)
        
    
    def run(self):
        
        for i in range(self.NUMBER_OF_MACRO_REPLICATIONS):
            lsemibo = LSemiBOOptimizer( 
                method = "falsification_elimination",
                is_budget = self.is_budget,
                max_budget= self.max_budget,
                cs_budget = self.cs_budget,
                top_k = self.top_k,
                classified_sample_bias = 0.8,
                tf_dim = self.tf_dim,
                R = self.R,
                M = self.M,
                gpr_model = InternalGPR(),
                classifier_model = InternalClassifier(),
                is_type = "lhs_sampling",
                cs_type= "lhs_sampling",
                pi_type= "lhs_sampling",
                seed= self.seed+i)
            
            result = staliro(self.model, self.specification, lsemibo, self.options)
            
            base_path = pathlib.Path()
            result_directory = base_path.joinpath(self.results_folder)
            result_directory.mkdir(exist_ok=True)

            benchmark_directory = result_directory.joinpath(f"Benchmark_{self.benchmark}_instance_{self.instance}")
            benchmark_directory.mkdir(exist_ok=True)

            
            save_path = benchmark_directory.joinpath(f"benchmark_{self.benchmark}_instance_{self.instance}_budget_{self.max_budget}_{self.NUMBER_OF_MACRO_REPLICATIONS}_reps_{i}_repnumber")
            with open(save_path, 'wb') as file:
                    pickle.dump(result, file)
