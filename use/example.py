from susolc import load, generate_solver, Sudoku
from susolc.stepping import InterestingStep
from susolc.formatting import print_grid
from susolc.solvingmethods import NTilesNOptions, XWing, Bifurcation

def solve(s: Sudoku) -> Sudoku:
    stepper = InterestingStep(print_grid)
    solver = generate_solver([NTilesNOptions, XWing, Bifurcation], stepper)
    return solver.launch(s)

if __name__=="__main__":
    s = solve(load("examples/evil4.csv"))
