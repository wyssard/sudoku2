# Using the Standard Solver

After having installed the package to your environment, the pre-constructed solver can be easily accessed in a functional way by means of the functions [`load`][sudoku.solvertools.load], [`solve`][sudoku.consolesolver.solve] and [`save`][sudoku.solvertools.save].

```py linenums="1"
from sudoku import load, solve, save
```


## Load

Use the [`load`][sudoku.solvertools.load] function to create and return a [`Sudoku`][sudoku.structure.Sudoku] object from the unsolved puzzle. The puzzle must be stored as `csv` file whose entries represent the initial configuration of the Sudoku grid. Any unspecified tiles take the value `0` as placeholder. Let's, e.g., consider the puzzle represented by the content of `example.csv`, to be stored in your current working directory, and load it into a `Sudoku` structure.

```py linenums="2"
s = load("example.csv")
```

```title="example.csv"
0, 0, 1, 0, 0, 4, 0, 8, 0
0, 0, 5, 0, 0, 0, 0, 0, 7
4, 7, 0, 0, 3, 0, 0, 6, 0
6, 4, 0, 0, 0, 8, 0, 0, 9
1, 0, 0, 0, 0, 0, 0, 0, 0
0, 0, 0, 0, 5, 0, 8, 0, 0
0, 0, 0, 2, 0, 0, 0, 3, 0
0, 0, 7, 0, 0, 0, 0, 0, 0
8, 9, 0, 0, 0, 5, 0, 0, 6
```

## Solve

Invoke the solving process by passing the `Sudoku` object to the [`solve`][sudoku.consolesolver.solve] function. Before returning the solved puzzle, this solver will guide you through the solving process by printing some of the solving steps to the console (including the final result). Any operation that lets us exclude one of the remaining candidates of an 'unsolved' tile is thereby considered a **solving step**. 

Use the second argument of the solve function to decide what solving steps to print. Refer to the documentation of [`solve`][sudoku.consolesolver.solve] to see what options are available. In this example, we will only print some less trivial steps by passing `#!python "interesting"` as argument. Moreover, for the purpose of this guide, we're using ASCII characters to format the output by setting the `unicode` keyword to `False`.

```py linenums="3"
solved = solve(s, "interesting", unicode=False)
```

The console output contains the present state of the puzzle as well as information about the conclusions made to remove certain candidates in the present step. Observe that both the affected candidates (i.e. those we are to remove) and those we considered to draw conclusions are highlighted by means of ANSI escape codes. Rendering thus depends on the console you're using. A typical output (without highlighting the considered candidates) could look like:

```
solving step 410: tile 16 is the only tile in column 7 with 4 as option
status: ok
+-----------------------+-----------------------+-----------------------+
| [9]    [6]    [1]     | [5]    [7]    [4]     | [3]    [8]    [2]     |
| [3]    [8]    [5]     | [6,9]  [6,9]  [2]     | [1,4]  [1,4,9][7]     |
| [4]    [7]    [2]     | [8]    [3]    [1]     | [9]    [6]    [5]     |
+-----------------------+-----------------------+-----------------------+
| [6]    [4]    [3]     | [1]    [2]    [8]     | [5,7]  [5,7]  [9]     |
| [1]    [5]    [8]     | [7]    [4]    [9]     | [6]    [2]    [3]     |
| [7]    [2]    [9]     | [6]    [5]    [3]     | [8]    [1]    [4]     |
+-----------------------+-----------------------+-----------------------+
| [5]    [1]    [6]     | [2]    [9]    [7]     | [4]    [3]    [8]     |
| [2]    [3]    [7]     | [4]    [8]    [6]     | [5]    [9]    [1]     |
| [8]    [9]    [4]     | [3]    [1]    [5]     | [2]    [7]    [6]     |
+-----------------------+-----------------------+-----------------------+

next step: (press ENTER)
```

Eventually, the solved puzzle is rendered to the console once more before the [`solve`][sudoku.consolesolver.solve] function returns.

```
solving step 415: puzzle solved
status: ok
+-----------+-----------+-----------+
| [9][6][1] | [5][7][4] | [3][8][2] |
| [3][8][5] | [9][6][2] | [1][4][7] |
| [4][7][2] | [8][3][1] | [9][6][5] |
+-----------+-----------+-----------+
| [6][4][3] | [1][2][8] | [7][5][9] |
| [1][5][8] | [7][4][9] | [6][2][3] |
| [7][2][9] | [6][5][3] | [8][1][4] |
+-----------+-----------+-----------+
| [5][1][6] | [2][9][7] | [4][3][8] |
| [2][3][7] | [4][8][6] | [5][9][1] |
| [8][9][4] | [3][1][5] | [2][7][6] |
+-----------+-----------+-----------+
```

## Save 
You may then want to write the solved puzzle to a file named, e.g., `solved.csv` by using the [`save`][sudoku.solvertools.save] function.

```py linenums="4"
save(solved, "solved.csv")
```

```title="solved.csv"
9,6,1,5,7,4,3,8,2
3,8,5,9,6,2,1,4,7
4,7,2,8,3,1,9,6,5
6,4,3,1,2,8,7,5,9
1,5,8,7,4,9,6,2,3
7,2,9,6,5,3,8,1,4
5,1,6,2,9,7,4,3,8
2,3,7,4,8,6,5,9,1
8,9,4,3,1,5,2,7,6
```

The whole program can now be compactly written as

```py linenums="1"
from sudoku import load, solve, save
save(solve(load("example.csv"), "interesting", unicode=False), "solved.csv")
```
