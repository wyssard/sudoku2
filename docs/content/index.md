# Sudokumentation

## Welcome to the documentation of the sudoku2 package!

These docs shall give you an overview of the possible applications of the package; On the one hand, the built in solver can be comfortably used to guide you step-by-step to the solution of a Sudoku puzzle. On the other hand, the package provides an API which lets you easily extend the capabilities of the basic solver by adding custom solving algorithms or by implementing any arbitrary Python frontend to render the individual solving steps. 

!!! warning 
    Even the core functionality of the Package is still in development. Both the API and the features that are abstracted by it may still change heavily. Proceed with caution if you intend to integrate this package in your own project. Moreover, if you are reading this from a development branch, the docs may not exactly correspond to the present state of the code.

## Installation

To install the library, clone its source code from GitHub and install it to your Python environment using `pip`.

```shell
$ git clone https://github.com/wyssard/sudoku2.git
$ pip install ./sudoku2
```


## Usage

!!! info 
    For any use of the package that goes beyond the Standard Solver, it's strongly recommended to start the journey through these docs with the description of the [Solving Process](solving_process). 

If you intend to use the package as a **stand-alone tool** to solve Sudoku puzzles, please refer to:

- [Standard Solver](standard_solvers) - simple functional access to the pre-built solver
- [Custom Solver](custom_solver) - create a custom solver by explicitly deciding what solving algorithms to use and what solving steps to render

If you're interested in modifying the basic capabilities or to use the solver backend in your own project, refer to: 

- [API Guide](api_guide) - walks you through the steps to extend the default behavior
- [API Reference](api/sudoku/solvingmethods) - documentation of the public API
