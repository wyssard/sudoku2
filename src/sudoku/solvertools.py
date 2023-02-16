"""
Module providing the core tools to build and interact with a Sudoku solver.
"""

from __future__ import annotations

from .structure import Sudoku
from .stepping import StepperBase
from .solvingmethods import FmtSolvingMethod, RemoveAndUpdate, NTilesNOptions

from csv import reader, writer
from pathlib import Path
from typing import Tuple, List


def generate_solver(method_order: Tuple[FmtSolvingMethod], stepper: StepperBase) -> FmtSolvingMethod:
    """
    Build a Sudoku solver by deciding in what order the solving methods (i.e.
    the instances of `FmtSolvingMethod` classes) are chained together. The 
    order of the `method_order` array implies that after the failure of the 
    n-th method, the n+1-th method will be used. On the other hand, at success
    of the n-th method, the solver will proceed by calling the 1st element of
    `method_order`. Moreover, any `StepperBase` object must be provided to guide
    the user through the solving process.

    Args:
        method_order: Solving Algorithm objects in their preferred order
        stepper: The Stepping object used by the Solver

    Returns:
        The Solver

    """

    remover = RemoveAndUpdate(stepper)
    init_methods: List[FmtSolvingMethod] = []

    init_run = NTilesNOptions(1, stepper, remover)

    for method in method_order:
        method.set_stepper(stepper)
        method.set_remover(remover)
        init_methods.append(method)

    init_run.set_fall_back(init_methods[0])
    init_methods[-1].set_advance(init_methods[0])

    for i in range(0, len(method_order)-1):
        method = init_methods[i]
        method.set_advance(init_methods[0])
        method.set_fall_back(init_methods[i+1])
    
    return init_run
     
def load(path: Path) -> Sudoku:
    """
    Load a Sudoku puzzle stored as `csv` file at `path` and build a `Sudoku`
    structure form the tow-dimensional grid.

    Args:
        path: The path to the `.csv` file
    
    Returns:
        The Puzzle in its initial shape

    """
    with open(path) as csv_file:
        rows = reader(csv_file, skipinitialspace=True)
        content = [(int(elt) if elt else 0) for row in rows for elt in row]

    sudoku = Sudoku(content)
    return sudoku

def save(sudoku: Sudoku, path: Path):
    """
    Write the solved `sudoku` puzzle to a `csv` file at `path`

    Args:
        sudoku: The puzzle to save
        path: `.csv` file to write to

    """
    with open(path, "w", newline="") as csv_file:
        writer(csv_file).writerows(sudoku.get_solved())
    