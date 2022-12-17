from sudoku import load, generate_solver, Sudoku
from sudoku.stepping import InterestingStepFlush, Skipper
from sudoku.formatting import print_grid
from sudoku.solvingmethods import NTilesNOptions, XWing, YWing, Bifurcation

from time import perf_counter
import numpy as np
from matplotlib import pyplot as plt

def solve(s: Sudoku) -> Sudoku:
    stepper = Skipper(print_grid)
    solver = generate_solver([NTilesNOptions, XWing, YWing, Bifurcation], stepper)
    t0 = perf_counter()
    s = solver.launch(s)
    dt = perf_counter()-t0
    stepper.show(s)
    print(f"solved in {round(dt, 5)} seconds")
    print(f"total steps: {stepper._counter}")
    return {
        "sudoku": s,
        "time": dt,
        "steps": stepper._counter
    }

def produce_plot(sudoku: Sudoku, time: float, steps: int):
    res = sudoku.get_solved()
    sol = res["solution"]
    comp = np.array(res["complexity"])


    fig = plt.figure(figsize=(3.5, 4.2), tight_layout=True)


    tab_ax = fig.add_subplot()
    tab_ax.axis("off")
    tab_ax.set_title("Sudoku Solved", loc="left", fontsize=20, fontweight="bold", pad=30)
    tab_ax.text(-0.4, -1.2, rf"in $\bf{round(time, 5)}$ seconds,", fontsize=9, color="0.4")
    tab_ax.text(-0.4, -0.8, rf"requiring $\bf{steps}$ option-removal steps", fontsize=9, color="0.4")
   
    tab_ax.imshow(comp, cmap="inferno")

    for r in range(9):
        for c in range(9):
            tab_ax.text(c, r, sol[r][c], 
            color="black" if comp[r,c] > np.mean(comp) else "white",
            fontsize="medium", horizontalalignment="center", verticalalignment="center")


    for ml in np.arange(0.5, 8.5):
        tab_ax.axhline(ml, color="white")
        tab_ax.axvline(ml, color="white")

    line_params = {"color": "white", "linewidth": 3}
    
    tab_ax.axhline(2.5, **line_params)
    tab_ax.axhline(5.5, **line_params)
    tab_ax.axvline(2.5, **line_params)
    tab_ax.axvline(5.5, **line_params)


    plt.savefig("solved.png", dpi=500)
    
if __name__=="__main__":
    solved = solve(load("examples/evil4.csv"))
    produce_plot(**solved)
