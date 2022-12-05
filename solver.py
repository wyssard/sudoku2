from __future__ import annotations

from sudoku import Sudoku
from _formatting import STEPPERS, Stepper
from _solvingmethods import FmtSolvingMethod, RemoveAndUpdate, NTilesNOptions, XWing, Bifurcation

from csv import reader
from pathlib import Path
import logging

        
def _prepare_solver(formatting: str, stepping: bool) -> FmtSolvingMethod:
    stepper: Stepper = STEPPERS[stepping](formatting)

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
    solver = _prepare_solver(formatting, stepping)
    return solver.launch(sudoku)

def load(path: Path) -> Sudoku:
    with open(path) as csvfile:
        rows = reader(csvfile, skipinitialspace=True)
        content = [(int(elt) if elt else 0) for row in rows for elt in row]

    sudoku = Sudoku(content)
    # print(sudoku)
    return sudoku



if __name__=="__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
    s = solve(load("examples/evil4.csv"), "grid", True)
    