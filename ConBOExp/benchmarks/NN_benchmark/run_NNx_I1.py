import numpy as np
import pickle
import pathlib

from Benchmark import Benchmark

from lsemibo.coreAlgorithm import LSemiBOOptimizer
from gpr_external import ExternalGPR as InternalGPR
from lsemibo.classifierInterface import InternalClassifier
from lsemibo.coreAlgorithm.specification import Requirement
from models import NNModel

from staliro.staliro import staliro
from staliro.options import Options, SignalOptions

 
 
# Define Signals and Specification
class Benchmark_NNx(Benchmark):
    def __init__(self, benchmark, instance, results_folder) -> None:
        if benchmark != "NNx":
            raise ValueError("Inappropriate Benchmark name")

        self.benchmark = benchmark
        self.results_folder = results_folder
        
        phi_1 = "F[0,1] (pos >= 3.2)"
        phi_2 = "F[1,1.5] (G[0,0.5]((pos >= 1.75) and (pos <= 2.25)))"
        phi_3 = "G[2,3] ((pos >= 1.825) and (pos <= 2.175))"
        

        self.is_budget = 100
        self.cs_budget = 1000
        self.max_budget = 1500
        self.NUMBER_OF_MACRO_REPLICATIONS = 10

        self.top_k = 3
        self.classified_sample_bias = 0.9
        self.tf_dim = 8
        self.seed = 123466
        self.instance = instance
        self.phi_list = [phi_1, phi_2, phi_3]
        
        #self.phi_list = [AT1_phi]
        self.pred_map = {"pos":([0,1,2], 0),
                        "ref": ([0,1,2], 1) ,
                        "p1":([0,1,2], 2),
                        "p2":([0,1,2], 3),
                        "p3":([0,1,2], 4),
                        "p4":([0,1,2], 5)
                    }

        self.R = 10
        self.M = 500
        
        
        self.model = NNModel()

        signals = [
                SignalOptions(control_points = [(1,3)]*8, signal_times=np.linspace(0.,40.,8)),
        ]

        self.options = Options(
            runs=1,
            iterations=self.max_budget,
            interval=(0, 40),
            signals=signals,
        )
        
        
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

