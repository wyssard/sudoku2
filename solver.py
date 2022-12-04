from __future__ import annotations

from sudoku import Sudoku, CONTAINER_TYPES
from _formatting import STEPPERS, Stepper

from csv import reader
from pathlib import Path
from typing import Set, List
from copy import deepcopy
import logging

        



def solve(path: Path, formatting: str, stepping: bool) -> Sudoku:
    fmtsol = _FormattedSolving(formatting, stepping)

    with open(path) as csvfile:
        rows = reader(csvfile, skipinitialspace=True)
        content = [(int(elt) if elt else 0) for row in rows for elt in row]

    sudoku = fmtsol.load_content(Sudoku(), content)

    return fmtsol.n_times_n_options_removal(sudoku, 1)

def load(path: Path) -> Sudoku:
    with open(path) as csvfile:
        rows = reader(csvfile, skipinitialspace=True)
        content = [(int(elt) if elt else 0) for row in rows for elt in row]

    return Sudoku(content)

def save(sudoku: Sudoku, dest: Path):
    pass

if __name__=="__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
    s = solve("examples/evil2.csv", "grid", False)
    # print(s)
    