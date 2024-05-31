#!/usr/bin/env python3

from argparse import ArgumentParser
from importlib import import_module
from sys import exit

ALL_BENCHMARKS = {"ATall", "CCall", "NN1x", "NNx", "AFC2x", "SC", "F16", "PM"}

ALLOWED_COMBINATIONS = {
    "ATall": [1,2],
    "CCall": [1,2],
    "NN1x" : [1,2],
    "NNx": [1,2],
    "AFC2x": [2],
    "SC": [1,2],
    "F16": [0],
    "PM": [1,2]
}

def _get_benchmark(name, instance, results_folder):

    if int(instance) not in ALLOWED_COMBINATIONS[name]:
        raise ValueError(f"{name} does not have Instance {instance}")
    
    print(f"Running {name} with instance {instance}!!")
    
    
    if instance == "1":
        if "AT" in name:
            mod = import_module(f"AT_benchmark.run_{name}_I1")
        elif "CC" in name:
            mod = import_module(f"CC_benchmark.run_{name}_I1")
        elif "NN" in name:
            mod = import_module(f"NN_benchmark.run_{name}_I1")
        elif "F16" in name:
            mod = import_module(f"F16_benchmark.run_{name}_I0")        
        elif "SC" in name:
            mod = import_module(f"SC_benchmark.run_{name}_I1")        
        elif "PM" in name:
            mod = import_module(f"PM_benchmark.run_{name}_I1")        
    elif instance == "2":
        if "AT" in name:
            mod = import_module(f"AT_benchmark.run_{name}_I2")
        elif "CC" in name:
            mod = import_module(f"CC_benchmark.run_{name}_I2")
        elif "NN" in name:
            mod = import_module(f"NN_benchmark.run_{name}_I2")
        elif "F16" in name:
            mod = import_module(f"F16_benchmark.run_{name}_I0")        
        elif "SC" in name:
            mod = import_module(f"SC_benchmark.run_{name}_I2")        
        elif "PM" in name:
            mod = import_module(f"PM_benchmark.run_{name}_I1")        

    cls_name = f"Benchmark_{name}"
    ctor = getattr(mod, cls_name)

    return ctor(name, instance, results_folder)


if __name__ == "__main__":
    parser = ArgumentParser(description="Run arch benchmarks")
    parser.add_argument("-b", "--benchmark", default = "")
    parser.add_argument("-i", "--instance", default = "")
    parser.add_argument("-f", "--folder", default = "/scratch/tkhandai/Arch_Comp_2024/LSemiBO")
    
    args = parser.parse_args()
    
    if args.benchmark not in ALL_BENCHMARKS:
        # print(benchmark_names)
        raise ValueError(f"Unknown benchmark {args.benchmark}")
    results_folder = args.folder
    
    benchmarks = _get_benchmark(args.benchmark, args.instance, results_folder)

    if not benchmarks:
        raise ValueError("Must specify at least one benchmark to run")

    results = benchmarks.run()
