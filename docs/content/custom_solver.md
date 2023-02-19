# Create a Custom Solver

Did you ever get bored of the solving algorithms used by the [default solver](standard_solver.md) or wanted to print the solving steps using a more interesting frontend than the console? 

No worries, the solution to your problem is already at hand. This guide will show you how to build your own solver by assembling a solver similar to the standard configuration. Understanding how such a solver is put together will bring you into the position to implement your own behavior and inject it into a solver object. 


!!! tip
    In a nutshell, the [API Guide](api_guide.md) explains how to extend the basic capabilities with new behavior by means of inheritance whereas this guide shows you how your custom objects are eventually composed to a solver. You can find the source code for this guide under `examples/doc_reference` in the [source repository](https://github.com/wyssard/sudoku2). To get the expected behavior, make sure that you set `doc_reference` as your working directory.

## The `generate_solver` Function

The assembly of a solver happens by means of the [`generate_solver`][sudoku.solvertools.generate_solver] function which can be imported directly form the `sudoku` parent package:

```py linenums="1"
from sudoku import generate_solver
```


## Solving Algorithms

Considering its documentation, we see that this function first of all required a list of solving algorithms. As you will see in the [API Guide](api_guide.md), solving algorithms are objects inheriting from [`FmtSolvingMethod`][sudoku.solvingmethods.FmtSolvingMethod]. Instead of creating new algorithms, let us import a few of the prebuilt objects from `sudoku`:

```py linenums="2"
from sudoku import ScaledXWing, YWing, Bifurcation
```

!!! Note
    Since my naming is not yet fully consistent with the established algorithm names, I recommend considering the [documentations][sudoku.solvingmethods] of the respective solving methods.

## Stepping

When going on to the second argument of `generate_solver`, we see that a so-called `stepper` is required. Before adding such a [`StepperBase`][sudoku.stepping.StepperBase] object to our collection of solving methods, let me explain its purpose: 

As you can see in the [Flowchart](solving_process.md#flowchart), a rendering step is triggered after successful elimination of a candidate and the program awaits a certain signal before continuing. In this whole process, the **stepper** works a an intermediate object that stores the information about the solving step and that decides whether to trigger the rendering process. That is, depending on the stepper object used, certain solving steps may or may not be printed. In order for such a stepper to work, it needs to know what rendering frontend to use and what signal to await to let the solver continue its work after rendering. Thereby the rendering frontend is an object inheriting from [`BlankFormatter`][sudoku.formatting.BlankFormatter] while the trigger to continue to solving process is represented by an object based on [`NoTrigger`][sudoku.stepping.NoTrigger].

For this example, let us import the [`InterestingStep`][sudoku.stepping.InterestingStep] stepper, which omits rendering certain solving steps based on trivial considerations. 

```py linenums="3"
from sudoku import InterestingStep
```

Since we want to reproduce the standard solver, we must tell the stepper to use the console as frontend and to listen for the ++enter++ key to be pressed to resume. The respective classes are given by:

```py linenums="4"
from sudoku import ConsoleFormatting, ConsoleTrigger
```

and the stepper is constructed via:

```py linenums="5"
stepper = InterestingStep(ConsoleFormatter(), ConsoleTrigger())
```

## Assembly

Now, we finally have all the required objects at hand to build the solver. When passing the solving algorithms to `generate_solver`, its important to understand the implications of the list's order: As you can see in the [Flowchart](solving_process.md#flowchart), depending on the success of a solving method, the program decides what algorithm to proceed with. Thereby, the `n+1` element of the list of algorithms is automatically considered to be the *fallback* of the element at position `n`. Success of an algorithm, on the other hand, implies that the solver will continue with the element a position `0`, preferably the most basic algorithm. Failure of the last element will terminate the program as the solver is unable to make any further progress.

```py linenums="6"
solver = generate_solver([ScaledXWing(2), YWing(), Bifurcation()], stepper)
```

And there you go, try to solve the example puzzle from the [previous guide](standard_solver.md) by:

```py linenums="7"
from sudoku import load
solved = solver.launch(load("example.csv"))
```

## Sum Up

The whole program can now compactly be written as:

```py linenums="1"
from sudoku import generate_solver, ScaledXWing, YWing, Bifurcation, InterestingStep, ConsoleFormatter, ConsoleTrigger, load
solver = generate_solver(
    [ScaledXWing(2), YWing(), Bifurcation()],
    InterestingStep(ConsoleFormatter(), ConsoleTrigger())
)
solved = solver.launch(load("example.csv"))
```

!!! info
    A similar example with a little extra (graphical output using [matplotlib](https://matplotlib.org/)) can be found in the [source repository](https://github.com/wyssard/sudoku2) under `examples/std_examples`.

Follow the [API Guide](api_guide.md) to implement your own **solving algorithms**, **steppers** and **formatters**.