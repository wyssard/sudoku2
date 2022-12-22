from sudoku import load, solve, generate_solver
from sudoku.formatting import print_grid
from sudoku.stepping import Skipper
from sudoku.solvingmethods import NTilesNOptions, RemoveAndUpdate

def create_solver_by_hand_1(stepper):
    remover = RemoveAndUpdate(stepper)
    solver = NTilesNOptions(1, stepper, remover)
    return solver

def create_solver_by_hand_2(stepper):
    remover = RemoveAndUpdate(stepper)
    solver = NTilesNOptions(1)
    solver.set_stepper(stepper)
    solver.set_remover(remover)
    return solver

def create_solver_with_generator(stepper):
    solver = generate_solver([NTilesNOptions(1)], stepper)
    return solver

def create_solver_fail_no_stepper_given(stepper):
    solver = NTilesNOptions(1)
    return solver

def create_solver_fail_no_remover_given(stepper):
    solver = NTilesNOptions(1, stepper)
    return solver

if __name__=="__main__":
    s = load("examples/evil4.csv")
    stepper = Skipper(print_grid)
    solver = create_solver_fail_no_remover_given(stepper)
    solver.launch(s)