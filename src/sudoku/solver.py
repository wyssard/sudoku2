from __future__ import annotations

from .structure import Sudoku
from .formatting import ConsoleFormatter
from .stepping import StepperBase, Skipper, AnyStep, InterestingStep, ConsoleTrigger
from .solvingmethods import FmtSolvingMethod, RemoveAndUpdate, NTilesNOptions, ScaledXWing, YWing, Bifurcation

from csv import reader, writer
from pathlib import Path
from typing import Tuple, List, Dict, Type


_FORMATTERS = {
    "console": ConsoleFormatter
}

_STEPPERS: Dict[str, Type[StepperBase]] = {
    "any": AnyStep,
    "skip": Skipper,
    "interesting": InterestingStep
}


def generate_solver(method_order: Tuple[FmtSolvingMethod], stepper: StepperBase):
    """
    Build a Sudoku solver by deciding in what order the solving methods (i.e.
    the instances of `FmtSolvingMethod` classes) are chained together. The 
    order of the `method_order` array implies that after the failure of the 
    n-th method, the n+1-th method will be used. On the other hand, at success
    of the n-th method, the solver will proceed by calling the 1st element of
    `method_order`. Moreover, any `StepperBase` object must be provided to guide
    the user through the solving process.
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
    """
    Solve a Sudoku given as `Sudoku` object (possibly obtained by the `load`
    function). Currently, the `formatting` parameter only takes 'console' as 
    possible value. You can choose between the steppers 'any', to render every
    solving step, 'skip' to completely suppress rendering, or 'interesting' to
    only print more elaborate solving methods. Use the `flush` parameter to 
    erase the rendered output of the previous solving step before continuing.
    """
    stepper = _STEPPERS[stepping](_FORMATTERS[formatting](flush=flush), ConsoleTrigger())
    solver = _create_solver(stepper)
    s = solver.launch(sudoku)
    stepper.show(s)
    return s

def load(path: Path) -> Sudoku:
    """
    Load a Sudoku puzzle stored as `csv` file at `path` and build a `Sudoku`
    structure form the tow-dimensional grid.
    """
    with open(path) as csv_file:
        rows = reader(csv_file, skipinitialspace=True)
        content = [(int(elt) if elt else 0) for row in rows for elt in row]

    sudoku = Sudoku(content)
    return sudoku

def save(sudoku: Sudoku, path: Path):
    """
    Write the solved `sudoku` puzzle to a `csv` file at `path`
    """
    with open(path, "w", newline="") as csv_file:
        writer(csv_file).writerows(sudoku.get_solved())
    
