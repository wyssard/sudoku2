from __future__ import annotations

from .structure import Sudoku
from .formatting import print_grid
from .stepping import StepperBase, Skipper, AnyStep, InterestingStep
from .solvingmethods import FmtSolvingMethod, RemoveAndUpdate, NTilesNOptions, XWing, Bifurcation

from csv import reader, writer
from pathlib import Path
from typing import Tuple, List


_FORMATTERS = {
    "grid": print_grid
}

_STEPPERS = {
    "any": AnyStep,
    "skip": Skipper,
    "interesting": InterestingStep
}


def generate_solver(method_order: Tuple[FmtSolvingMethod], stepper: StepperBase):
    remover = RemoveAndUpdate(stepper)

    init_methods: List[FmtSolvingMethod] = []

    for method in method_order:
        init_methods.append(method(stepper, remover))

    init_methods[0].set_fall_back(init_methods[1])
    init_methods[-1].set_advance(init_methods[0])

    for i in range(1, len(method_order)-1):
        method = init_methods[i]
        method.set_advance(init_methods[0])
        method.set_fall_back(init_methods[i+1])
    
    return init_methods[0]

        
def _create_solver(stepper: StepperBase) -> FmtSolvingMethod:
    remover = RemoveAndUpdate(stepper)

    n_tiles_n_options = NTilesNOptions(stepper, remover)
    x_wing = XWing(stepper, remover)
    bifurcation = Bifurcation(stepper, remover)

    n_tiles_n_options.set_fall_back(x_wing)

    x_wing.set_advance(n_tiles_n_options)
    x_wing.set_fall_back(bifurcation)

    bifurcation.set_advance(n_tiles_n_options)

    return n_tiles_n_options


def solve(sudoku: Sudoku, formatting: str, stepping: bool) -> Sudoku:
    solver = _create_solver(_STEPPERS[stepping](_FORMATTERS[formatting]))
    return solver.launch(sudoku)

def load(path: Path) -> Sudoku:
    with open(path) as csvfile:
        rows = reader(csvfile, skipinitialspace=True)
        content = [(int(elt) if elt else 0) for row in rows for elt in row]

    sudoku = Sudoku(content)
    return sudoku

def save(sudoku: Sudoku, path: Path):
    with open(path, "w", newline="") as csvfile:
        writer(csvfile).writerows(sudoku.get_solved())

if __name__=="__main__":
    s = solve(load("examples/evil4.csv"), "grid", "any")
    