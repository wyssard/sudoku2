# Sudokumentation

## Welcome to the documentation of the sudoku2 package!

These docs try to give you an overview of the different aspects and use cases of the package. 

On the one hand, its built in solver can be comfortably used to guide you step-by-step to the solution of a Sudoku puzzle. On the other hand, the package provides an API which lets you easily extend the capabilities of the basic solver by adding custom solving algorithms or by implementing any arbitrary Python frontend to render the individual solving steps. 


> **Warning** Even the core functionality of the Package is still in development. Both the API and the features that are abstracted by it may still change heavily. Proceed with caution if you intend to integrate this package in your own project. Moreover, if you are reading this from a development branch, the docs may not exactly correspond to the present state of the code.

## Contents

If you intend to use the package as a **stand-alone tool** to solve Sudoku puzzles, please refer to:

- [Standard Solver](standard_solvers.md) - simple functional access to the pre-built solver
- [Custom Solver](custom_solver.md) - create a custom solver by explicitly deciding what solving algorithms to use and what solving steps to render

If you're interested in modifying the basic capabilities or to use the solver backend in your own project, refer to the **API** documentation.

- [API Structure](api_structure.md) - get an overview of how the different objects interact to create a solver
- [API Guide](api_guide.md) - a tutorial to step you through the creation and assembly of custom solver classes
