# sudoku-helper

![GitHub](https://img.shields.io/github/license/wyssard/sudoku2) 
![GitHub issues](https://img.shields.io/github/issues/wyssard/sudoku2)


A Sudoku solver written in Python, serving as an exercise project for the `set` datatype. Observe that speed is no priority of this solver (hence displaying the time required to solve the puzzle might be rather hypocritical ;)). The project much rather focuses on providing a simple interface to guide the user step-by-step to the solution of the puzzle. A connection to that interface that allows for printing the individual solving steps to the console has already been implemented. Correspondingly, the solver tries to avoid the use of backtracking algorithms but solves the puzzle by means of algorithms that search for patterns that enable for the immediate exclusion of candidates. The creation of the solver was precisely motivated by the idea of finding such solving algorithms by my own.

The solver thus operates by excluding candidates from tiles by removing the values of neighboring tiles that have already been fixed but also by using more elaborate strategies such as X- and Y-Wing. Only if the solver gets stuck, a bifurcation method is applied to tiles with only two candidates left to minimize backtracking. 

The puzzles to be solved are stored as `.csv` files. Some example puzzles taken from [sudoku.com](https://www.sudoku.com) can be found in the [examples](/examples/) directory.



## Installation

Install this library using `pip`.

```shell
$ git clone https://github.com/wyssard/sudoku2.git
$ pip install /sudoku2/
```

## Usage

### Default Solver

> **Warning**: The following section is deprecated and must be updated to the new solver layout.

Access the default solver by importing the `load`, `solve` and `save` functions from `sudoku`:

```python
from sudoku import load, solve, save 
```

and solve an example puzzle from the [example](/examples/) directory:

```python
s = solve(load("/example/evil4.csv"), "grid", "interesting")
```

where `"grid"` specifies the formatting of the puzzle in the console (no other formatted output is available at this stage). The 'stepping' argument `"interesing"` causes the solver to print any solving step to the console that made use of a more elaborate solving method. Alternatively, this argument can be set to `"any"` in order to print every solving step or to `"skip"` to prevent the solver from printing the steps completely. An optional boolean argument can be given to erase the previous solving step from the console thus deleting the solving history.

Running the program, the user is prompted to step through the solving steps in the console; one such step could look like:

```shell
╭─────────────────────────────┬─────────────────────────────┬─────────────────────────────╮
│ [8]      [3]      [5]       │ [2]      [7]      [6]       │ [9]      [4]      [1]       │
│ [7]      [9]      [2]       │ [1,4,5]  [1,3,4]  [1,3,4]   │ [6]      [3,5]    [8]       │
│ [1]      [6]      [4]       │ [8,5]    [8,3]    [9]       │ [3,7]    [3,5,7]  [2]       │
├─────────────────────────────┼─────────────────────────────┼─────────────────────────────┤
│ [4,5]    [8,2]    [9]       │ [6]      [8,2,4]  [8,2,4]   │ [3,7]    [1]      [3,5,7]   │
│ [3]      [1]      [6]       │ [7]      [2,4]    [5]       │ [8]      [9,2]    [9,4]     │
│ [4]      [8]      [7]       │ [3]      [9]      [1]       │ [2]      [6]      [5]       │
├─────────────────────────────┼─────────────────────────────┼─────────────────────────────┤
│ [6]      [5]      [1]       │ [8,4]    [8,2,3,4][8,2,3,4] │ [2,4]    [9,2,3,7][9,3,4,7] │
│ [9]      [7]      [8]       │ [1,4]    [6]      [1,2,3,4] │ [5]      [2,3]    [3,4]     │
│ [2]      [4]      [3]       │ [9]      [5]      [7]       │ [1]      [8]      [6]       │
╰─────────────────────────────┴─────────────────────────────┴─────────────────────────────╯

solving step 397: found Y-Wing with anchor at 60 and nodes at 70, 71, remove the shared option {3} from 68
status: ok
next step: (press ENTER)
```

(the concerned tiles are highlighted by means of ANSI escape sequences)

Eventually, the solved puzzle is printed to the console as:

```shell 
╭───────────┬───────────┬───────────╮
│ [8][3][5] │ [2][7][6] │ [9][4][1] │
│ [7][9][2] │ [4][1][3] │ [6][5][8] │
│ [1][6][4] │ [5][8][9] │ [7][3][2] │
├───────────┼───────────┼───────────┤
│ [5][2][9] │ [6][4][8] │ [3][1][7] │
│ [3][1][6] │ [7][2][5] │ [8][9][4] │
│ [4][8][7] │ [3][9][1] │ [2][6][5] │
├───────────┼───────────┼───────────┤
│ [6][5][1] │ [8][3][2] │ [4][7][9] │
│ [9][7][8] │ [1][6][4] │ [5][2][3] │
│ [2][4][3] │ [9][5][7] │ [1][8][6] │
╰───────────┴───────────┴───────────╯
```



Save the solved puzzle as a `.csv` file using the `save` function:

```python
save(s, "solved.csv")
```

### Custom Solver

Instead of using the default solver, the `sudoku.generate_solver` function may be used to manually specify the solving methods one likes to use. This solver-generator is based on the idea of extending the solver by implementing custom solving methods. Such solving methods should inherit from the `sudoku.solvingmethods.FmtSolvingMethod` abstract class. Observe that this feature is still in development. The creation of custom solver classes is not straight forward at this stage and would require the user to dig into the code of the present solving methods.

An example that makes use of this function to customize the solver can be found in the [example.py](/use/example.py) file. This script also provides a function to plot the solved puzzle using [matplotlib](https://github.com/matplotlib/matplotlib). The corresponding result for the puzzle from above can then be rendered as:

![solved.png](img/solved.png)

## Solving Methods

A brief description of the solving methods used should go here.
