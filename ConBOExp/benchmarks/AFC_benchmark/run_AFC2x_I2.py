import numpy as np
import pickle
import pathlib

from Benchmark import Benchmark
from models import AFCModel

from lsemibo.coreAlgorithm import LSemiBOOptimizer
from lsemibo.gprInterface import InternalGPR
from gpr_external import ExternalGPR as InternalGPR
from lsemibo.classifierInterface import InternalClassifier
from lsemibo.coreAlgorithm.specification import Requirement


from staliro.staliro import staliro
from staliro.options import Options, SignalOptions
from staliro.signals import piecewise_constant

 
 
# Define Signals and Specification
class Benchmark_AFC2x(Benchmark):
    def __init__(self, benchmark, instance, results_folder) -> None:
        if benchmark != "AFC2x":
            raise ValueError("Inappropriate Benchmark name")

        self.benchmark = benchmark
        self.results_folder = results_folder
        
        rise = "(theta <= 8.8) and (F[0,0.05] (theta >= 40))"
        fall = "(theta >= 40) and (F[0,0.05] (theta <= 8.8))"
        mod_u_1 = "G[1,5] ((ut <= 0.008) and (ut >= -0.008))"
        AFC27_phi = f"G[11,50] (({rise} or {fall}) -> ({mod_u_1}))"
        


        mod_u_2 = "(ut <= 0.007) and (ut >= -0.007)"
        AFC29_phi = f"G[11,50] ({mod_u_2})"

        
        self.is_budget = 100
        self.cs_budget = 1000
        self.max_budget = 1500
        self.NUMBER_OF_MACRO_REPLICATIONS = 10

        self.top_k = 3
        self.classified_sample_bias = 0.9
        self.tf_dim = 11
        self.seed = 123466
        self.instance = instance
        self.phi_list = [AFC27_phi, AFC29_phi]
        #self.phi_list = [AT1_phi]
        self.pred_map = {"ut":([0,1,2,3,4,5,6,7,8,9,10], 0), 
                        "theta":([0,1,2,3,4,5,6,7,8,9,10], 2)
                    }

        self.R = 10
        self.M = 500
        
        
        self.model = AFCModel()

        signals = [
            SignalOptions(control_points=[(900, 1100)], factory=piecewise_constant),
            SignalOptions(control_points= [(0, 61.2)] * 10, signal_times=np.linspace(0.,50.,10), factory=piecewise_constant),
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
            save_path = result_directory.joinpath(f"{self.benchmark}_budget_{self.max_budget}_{self.NUMBER_OF_MACRO_REPLICATIONS}_reps_instance_{self.instance}_repnumber{i}")
            with open(save_path, 'wb') as file:
                    pickle.dump(result, file)
    