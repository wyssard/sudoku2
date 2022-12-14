from susolc import load, generate_solver, Sudoku
from susolc.stepping import InterestingStepFlush, Skipper
from susolc.formatting import print_grid
from susolc.solvingmethods import NTilesNOptions, XWing, YWing, Bifurcation

from time import perf_counter

def solve(s: Sudoku) -> Sudoku:
    stepper = InterestingStepFlush(print_grid)
    solver = generate_solver([NTilesNOptions, XWing, YWing, Bifurcation], stepper)
    t0 = perf_counter()
    s = solver.launch(s)
    dt = perf_counter()-t0
    stepper.show(s)
    print(f"solved in {round(dt, 5)} seconds")
    return s

if __name__=="__main__":
    s = solve(load("examples/evil2.csv"))
