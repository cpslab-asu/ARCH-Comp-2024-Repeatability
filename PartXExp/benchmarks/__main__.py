#!/usr/bin/env python3

from argparse import ArgumentParser
from importlib import import_module
from sys import exit

ALL_BENCHMARKS = {"AT1", "AT2", "AT51", "AT52", "AT53", "AT54", "AT61", "AT62", "AT63", "AT64", "CC1", "CC2", "CC3", "CC4", "CC5", "CCx"}

def _get_benchmark(name, instance, results_folder):
    if instance == "1":
        if "AT" in name:
            mod = import_module(f"AT_benchmark_I1.run_{name}")
        elif "CC" in name:
            mod = import_module(f"CC_benchmark_I1.run_{name}")
    elif instance == "2":
        if "AT" in name:
            mod = import_module(f"AT_benchmark_I2.run_{name}")
        elif "CC" in name:
            mod = import_module(f"CC_benchmark_I2.run_{name}")

    cls_name = f"Benchmark_{name}"
    ctor = getattr(mod, cls_name)

    return ctor(name, instance, results_folder)


if __name__ == "__main__":
    parser = ArgumentParser(description="Run arch benchmarks")
    parser.add_argument("-b", "--benchmark", default = "")
    # parser.add_argument("benchmark", nargs="*", help="Name of benchmarks to run")
    parser.add_argument("-i", "--instance", default = "")
    parser.add_argument("-f", "--folder", default = "/scratch/tkhandai/Arch_Comp_2024")
    
    args = parser.parse_args()
    
    if args.benchmark not in ALL_BENCHMARKS:
        # print(benchmark_names)
        raise ValueError(f"Unknown benchmark {args.benchmark}")
    results_folder = args.folder
    
    benchmarks = _get_benchmark(args.benchmark, args.instance, results_folder)

    if not benchmarks:
        raise ValueError("Must specify at least one benchmark to run")

    results = benchmarks.run()
