from sudoku import load, generate_solver, Sudoku
from sudoku.stepping import InterestingStepFlush, Skipper
from sudoku.formatting import print_grid
from sudoku.solvingmethods import NTilesNOptions, XWing, YWing, Bifurcation

from time import perf_counter
import numpy as np
from matplotlib import pyplot as plt

def solve(s: Sudoku) -> Sudoku:
    stepper = Skipper(print_grid)
    solver = generate_solver([XWing, NTilesNOptions, YWing, Bifurcation], stepper)
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

def produce_plot(dest: str, sudoku: Sudoku, time: float, steps: int):
    sol = sudoku.get_solved()
    comp = np.array(sudoku.get_complexity_map())
    min_steps = int(np.min(comp[comp.nonzero()])*0.8)

    fig = plt.figure(figsize=(3.5, 4.2), tight_layout=True)


    tab_ax = fig.add_subplot()
    tab_ax.axis("off")
    tab_ax.set_title("Sudoku Solved", loc="left", fontsize=20, fontweight="bold", pad=30)
    tab_ax.text(-0.4, -1.2, rf"in $\bf{round(time, 5)}$ seconds,", fontsize=9, color="0.4")
    tab_ax.text(-0.4, -0.8, rf"requiring $\bf{steps}$ option-removal steps", fontsize=9, color="0.4")
   
    cmap = tab_ax.imshow(comp, cmap="inferno", vmin=min_steps)
    cbar = fig.colorbar(cmap, ax=tab_ax, 
        shrink=0.7, orientation="horizontal", pad=0.03)
    cbar.set_label(label="solving step at which solution was found", fontsize=7)
    cbar.ax.tick_params(labelsize=7)

    for r in range(9):
        for c in range(9):
            tab_ax.text(c, r, sol[r][c], 
            color="black" if comp[r,c] > min_steps+(steps-min_steps)/2 else "white",
            fontsize="medium", horizontalalignment="center", verticalalignment="center")


    for ml in np.arange(0.5, 8.5):
        tab_ax.axhline(ml, color="white")
        tab_ax.axvline(ml, color="white")

    line_params = {"color": "white", "linewidth": 3}
    
    tab_ax.axhline(2.5, **line_params)
    tab_ax.axhline(5.5, **line_params)
    tab_ax.axvline(2.5, **line_params)
    tab_ax.axvline(5.5, **line_params)


    plt.savefig(dest, dpi=500)
    
if __name__=="__main__":
    solved = solve(load("examples/evil4.csv"))
    produce_plot("img/solved.png", **solved)
