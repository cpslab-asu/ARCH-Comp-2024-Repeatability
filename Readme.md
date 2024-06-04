# Code for Pys-TaLiRo


# Installation

We use the Poetry tool which is a dependency management and packaging tool in Python. It allows you to declare the libraries your project depends on and it will manage (install/update) them for you. Please follow the installation of poetry at [https://python-poetry.org/docs/#installation](https://python-poetry.org/docs/#installation)

After you've installed poetry, you can install partx by running the following command in the root of the project: 

```
poetry install
```

## 1. Part-X

To run code for `Part-X` on the benchmarks:

1. Enter the `PartXExp` directory

    ```
    cd PartXExp
    ```

2. Use the following command to run the benchmark:

    ```
    poetry run python benchmarks -m <MODEL> -p <PROPERTY> -i <INSTANCE> -f <Folder for Results>
    ```

    Here are the follwoing combinations for MODEL, PROPERTY, and INSTANCE:

    | MODEL | INSTANCE | PROPERTY                                          |
    |----------|-------------|-------------------------------------------------------|
    | AT       | 1           | AT1, AT2, AT51, AT52, AT53, AT54, AT6a, AT6b, AT6c, AT6abc |
    | AT       | 2           | AT1, AT2, AT51, AT52, AT53, AT54, AT6a, AT6b, AT6c, AT6abc |
    | NN       | 1           | NN1, NN2, NNx                                         |
    | NN       | 2           | NN1, NN2, NNx                                         |
    | CC       | 1           | CC1, CC2, CC3, CC4, CC5, CCx                          |
    | CC       | 2           | CC1, CC2, CC3, CC4, CC5, CCx                          |
    | F16      | 0           | F16a                                                  |
    | SC       | 1           | SCa                                                   |
    | SC       | 2           | SCa                                                   |
    | AFC      | 2           | AFC27, AFC29, AFC33                                   |

    For example: To run SCa property on the Steam Condenser (SC) model for instance 2 type of signals abd store the result in the current directory, use the following command:

    ```
    poetry run python benchmarks -m SC -p SCa -i 1 -f .
    ```

3. Generating Validation Files

    TODO

## 2. Conjunctive Bayesian Optimization (ConBO)

To run code for `ConBO` on the benchmarks:

1. Enter the `ConBOExp` directory

    ```
    cd ConBoExp
    ```

2. Use the following command to run the benchmark:

    ```
    poetry run python benchmarks -b <Benchmark> -i <INSTANCE> -f <Folder for Results>
    ```

    Here are the follwoing combinations for MODEL, PROPERTY, and INSTANCE:

    | Benchmark | Instance |
    |-------------|---------------|
    | ATall       | 1, 2          |
    | CCall       | 1, 2          |
    | NN1x        | 1, 2          |
    | NNx         | 1, 2          |
    | AFC2x       | 2             |
    | AFC33       | 2             |
    | SC          | 1, 2          |
    | F16         | 0             |
    | PM          | 1, 2          |

    For example: To run SCa property on the Steam Condenser (SC) model for instance 2 type of signals abd store the result in the current directory, use the following command:

    ```
    poetry run python benchmarks -b SC -i 1 -f .
    ```

3. Generating Validation Files

    TODO


# Miscellaneous Files

For clarity, readability, and maintainability, we also provide the input signals and the corresponding trajectories for different instances and the associated robsutness all systems. To run those:

```
cd PartXExp
poetry run python -m benchmarks.misc_files.test_<MODEL>_I<INSTANCE>
```

The following are the possible options:

| MODEL | Instance |
|-------------|---------------|
| AT       | 1         |
| CC       | 1, 2          |
| NN        | 1, 2          |
| AFC2x       | 2             |
| AFC33       | 2             |
| SC          | 1, 2          |
| F16         | 0             |

For example: To see the signals and robustness for all properties generated on CC for instance 2, use the following command:

```
poetry run python -m benchmarks.misc_files.test_CC_I2
```