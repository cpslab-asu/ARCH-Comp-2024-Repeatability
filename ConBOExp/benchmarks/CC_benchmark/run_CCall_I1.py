import numpy as np
import pickle
import pathlib

from Benchmark import Benchmark

from lsemibo.coreAlgorithm import LSemiBOOptimizer
from gpr_external import ExternalGPR as InternalGPR
from lsemibo.classifierInterface import InternalClassifier
from lsemibo.coreAlgorithm.specification import Requirement
from models import CCModel

from staliro.staliro import staliro
from staliro.options import Options, SignalOptions


class Benchmark_CC(Benchmark):
    def __init__(self, benchmark, instance, results_folder) -> None:
        if benchmark != "CC":
            raise ValueError("Inappropriate Benchmark name")

        self.benchmark = benchmark
        self.results_folder = results_folder
        self.instance = instance
        
        

        CC1_phi = "G[0, 100] (y54 <= 40)"
        CC2_phi = "G[0, 70] (F[0,30] (y54 >= 15))"
        CC3_phi = "G[0, 80] ((G[0, 20] (y21 <= 20)) or (F[0,20] (y54 >= 40)))"
        CC4_phi = "G[0,65] F[0,30] G[0,5] (y54 >= 8)"
        CC5_phi = "G[0,72] (F[0,8] ((G[0,5] (y21 >= 9)) -> (G[5,20] (y54 >= 9))))"

        phi_1 = "(G[0, 50] (y21 >= 7.5))"
        phi_2 = "(G[0, 50] (y32 >= 7.5))"
        phi_3 = "(G[0, 50] (y43 >= 7.5))"
        phi_4 = "(G[0, 50] (y54 >= 7.5))"
        CCx_phi = phi_1 + " and " + phi_2 + " and " + phi_3 + " and " + phi_4


        self.is_budget = 200
        self.cs_budget = 1000
        self.max_budget = 1500
        self.NUMBER_OF_MACRO_REPLICATIONS = 10

        self.top_k = 3
        self.classified_sample_bias = 0.8
        self.tf_dim = 20

        #self.phi_list = [CC1_phi, CC2_phi, CC3_phi, CC4_phi, CC5_phi, phi_1, phi_2, phi_3, phi_4]
        self.phi_list = [CC1_phi, CC2_phi, CC3_phi, CC4_phi, CC5_phi, CCx_phi]
        self.pred_map = {"y21": ([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19], 0),
                         "y32": ([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19], 1),
                         "y43": ([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19], 2),
                         "y54": ([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19], 3)} 

        self.R = 20
        self.M = 500
        self.seed = 123458
        
        self.model = CCModel()

        signals = [
            SignalOptions(control_points = [(0., 1.)] * 10, signal_times=np.linspace(0.0, 100.0, 10)),
            SignalOptions(control_points = [(0., 1.)] * 10, signal_times=np.linspace(0.0, 100.0, 10)),
        ]
        self.options = Options(runs=1, iterations=self.max_budget , interval=(0, 100),  signals=signals)
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

