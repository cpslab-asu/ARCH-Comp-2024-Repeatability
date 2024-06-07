import numpy as np
import pickle
import pathlib

from Benchmark import Benchmark

from lsemibo.coreAlgorithm import LSemiBOOptimizer
from gpr_external import ExternalGPR as InternalGPR
from lsemibo.classifierInterface import InternalClassifier
from lsemibo.coreAlgorithm.specification import Requirement
from models import AutotransModel

from staliro.staliro import staliro
from staliro.options import Options, SignalOptions
from staliro.signals import piecewise_constant

 
 
# Define Signals and Specification
class Benchmark_ATall(Benchmark):
    def __init__(self, benchmark, instance, results_folder) -> None:
        if benchmark != "ATall":
            raise ValueError("Inappropriate Benchmark name")

        self.benchmark = benchmark
        self.results_folder = results_folder
        
        AT1_phi = "G[0, 20] (speed <= 120)"
        AT2_phi = "G[0, 10] (rpm <= 4750)"

        gear_1_phi = f"(gear <= 1.5 and gear >= 0.5)"
        AT51_phi = f"G[0, 30] (((not {gear_1_phi}) and (F[0.001,0.1] {gear_1_phi})) -> (F[0.001, 0.1] (G[0,2.5] {gear_1_phi})))"

        gear_2_phi = f"(gear <= 2.5 and gear >= 1.5)"
        AT52_phi = f"G[0, 30] (((not {gear_2_phi}) and (F[0.001,0.1] {gear_2_phi})) -> (F[0.001, 0.1] (G[0,2.5] {gear_2_phi})))"

        gear_3_phi = f"(gear <= 3.5 and gear >= 2.5)"
        AT53_phi = f"G[0, 30] (((not {gear_3_phi}) and (F[0.001,0.1] {gear_3_phi})) -> (F[0.001, 0.1] (G[0,2.5] {gear_3_phi})))"

        gear_4_phi = f"(gear <= 4.5 and gear >= 3.5)"
        AT54_phi = f"G[0, 30] (((not {gear_4_phi}) and (F[0.001,0.1] {gear_4_phi})) -> (F[0.001, 0.1] (G[0,2.5] {gear_4_phi})))"

        AT6a_phi = "((G[0, 30] (rpm <= 3000)) -> (G[0,4] (speed <= 35)))"
        AT6b_phi = "((G[0, 30] (rpm <= 3000)) -> (G[0,8] (speed <= 50)))"
        AT6c_phi = "((G[0, 30] (rpm <= 3000)) -> (G[0,20] (speed <= 65)))"

        AT6abc_phi = f"{AT6a_phi} and {AT6b_phi} and {AT6c_phi}"
        self.is_budget = 100
        self.cs_budget = 1000
        self.max_budget = 1500
        self.NUMBER_OF_MACRO_REPLICATIONS = 10

        self.top_k = 3
        self.classified_sample_bias = 0.9
        self.tf_dim = 10
        self.seed = 123466
        self.instance = instance
        self.phi_list = [AT1_phi, AT2_phi, AT51_phi, AT52_phi, AT53_phi, AT54_phi, AT6a_phi, AT6b_phi, AT6c_phi, AT6abc_phi]
        #self.phi_list = [AT1_phi]
        self.pred_map = {"speed":([0,1,2,3,4,5,6,7,8,9], 0), 
                        "rpm":([0,1,2,3,4,5,6,7,8,9], 1),
                        "gear":([0,1,2,3,4,5,6,7,8,9], 2)
                    }

        self.R = 10
        self.M = 500
        
        
        self.model = AutotransModel()

        signals = [
            SignalOptions(control_points = [(0, 100)]*7, signal_times=np.linspace(0.,50.,7, endpoint=False), factory=piecewise_constant),
            SignalOptions(control_points = [(0, 325)]*3, signal_times=np.linspace(0.,50.,3, endpoint=False), factory=piecewise_constant),
        ]

        self.options = Options(runs=1, iterations=self.max_budget, interval=(0, 50),  signals=signals)
        
        
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