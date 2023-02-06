from __future__ import annotations

from .structure import Sudoku
from .formatting import print_grid
from .stepping import StepperBase, Skipper, AnyStep, AnyStepFlush, InterestingStep, InterestingStepFlush
from .solvingmethods import FmtSolvingMethod, RemoveAndUpdate, NTilesNOptions, ScaledXWing, YWing, Bifurcation

from csv import reader, writer
from pathlib import Path
from typing import Tuple, List


_FORMATTERS = {
    "grid": print_grid
}

_STEPPERS = {
    "any": AnyStep,
    "anyFlush": AnyStepFlush,
    "skip": Skipper,
    "skipFlush": Skipper,
    "interesting": InterestingStep,
    "interestingFlush": InterestingStepFlush
}


def generate_solver(method_order: Tuple[FmtSolvingMethod], stepper: StepperBase):
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
    

    # return init_methods[0]
    return init_run
     
def _create_solver(stepper: StepperBase) -> FmtSolvingMethod:
    return generate_solver(
        [
            ScaledXWing(2), 
            YWing(), 
            NTilesNOptions(2), 
            ScaledXWing(3), 
            Bifurcation()
        ], stepper)


def solve(sudoku: Sudoku, formatting: str, stepping: str, flush: bool = False) -> Sudoku:
    stepper = _STEPPERS[f"{stepping}{'Flush' if flush else ''}"](_FORMATTERS[formatting])
    solver = _create_solver(stepper)
    s = solver.launch(sudoku)
    stepper.show(s)
    return s

def load(path: Path) -> Sudoku:
    with open(path) as csv_file:
        rows = reader(csv_file, skipinitialspace=True)
        content = [(int(elt) if elt else 0) for row in rows for elt in row]

    sudoku = Sudoku(content)
    return sudoku

def save(sudoku: Sudoku, path: Path):
    with open(path, "w", newline="") as csv_file:
        writer(csv_file).writerows(sudoku.get_solved())
    
