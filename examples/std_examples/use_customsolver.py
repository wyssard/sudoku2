from sudoku import load, generate_solver, Sudoku, Skipper, ConsoleFormatter, ConsoleTrigger, ScaledXWing, Bifurcation

from time import perf_counter
import numpy as np
from matplotlib import pyplot as plt

def custom_solve(s: Sudoku) -> Sudoku:
    stepper = Skipper(ConsoleFormatter(), ConsoleTrigger())
    solver = generate_solver([ScaledXWing(2), Bifurcation()], stepper)
    t0 = perf_counter()
    s = solver.launch(s)
    dt = perf_counter()-t0
    stepper.show(s)
    print(f"solved in {round(dt, 6)} seconds")
    print(f"total steps: {stepper.counter}")
    return {
        "sudoku": s,
        "time": dt,
        "steps": stepper.counter
    }

def produce_plot(dest: str, sudoku: Sudoku, time: float, steps: int):
    sol = sudoku.get_solved()
    comp = np.array(sudoku.get_complexity_map())
    min_steps = int(np.min(comp[comp.nonzero()])*0.8)

    width = 6
    fig = plt.figure(figsize=(width, width*6/5), tight_layout=True)

    tab_ax = fig.add_subplot()
    tab_ax.axis("off")
    tab_ax.set_title("Sudoku Solved", loc="left", fontsize=25, fontweight="bold", pad=40)
    tab_ax.text(-0.5, -1.1, rf"in $\bf{round(time, 5)}$ seconds,", fontsize=12, color="0.4")
    tab_ax.text(-0.5, -0.7, rf"requiring $\bf{steps}$ option-removal steps", fontsize=12, color="0.4")
   
    cmap = tab_ax.imshow(comp, cmap="inferno", vmin=min_steps)
    cbar = fig.colorbar(cmap, ax=tab_ax, 
        shrink=0.7, orientation="horizontal", pad=0.03)
    cbar.set_label(label="solving step at which solution was found", fontsize=12, color="0.4")
    cbar.ax.tick_params(labelsize=12)

    for r in range(9):
        for c in range(9):
            tab_ax.text(c, r, sol[r][c], 
            color="black" if comp[r,c] > min_steps+(steps-min_steps)/2 else "white",
            fontsize=18, horizontalalignment="center", verticalalignment="center")


    for l in range(1,10):
        lw = 1.5 if l%3 else 3
        line_params = {"color": "white", "linewidth": lw}
        tab_ax.axhline(l-0.5, **line_params)
        tab_ax.axvline(l-0.5, **line_params)

    plt.savefig(dest)
    
if __name__=="__main__":
    solved = custom_solve(load("puzzles/evil4.csv"))
    produce_plot("img/solved.png", **solved)
