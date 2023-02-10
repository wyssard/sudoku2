import numpy as np
from matplotlib import pyplot as plt
from matplotlib.animation import ArtistAnimation
from matplotlib.text import Text
from matplotlib.figure import Figure
from typing import List

from sudoku.structure import Sudoku, index_to_pos
from sudoku.formatting import BlankFormatter
from sudoku.consolesolver import ConsoleTrigger
from sudoku.solvertools import generate_solver, load
from sudoku.solvingmethods import ScaledXWing, Bifurcation
from sudoku.stepping import InterestingStep, AnyStep, NoTrigger

        
class mplFormatter(BlankFormatter):
    OFFSET = 0.3
    IMAGE_WIDTH = 5

    def __init__(self) -> None:
        super().__init__()
        self._init_plot()

    def _init_plot(self):
        self.fig = plt.figure(figsize=(self.IMAGE_WIDTH, self.IMAGE_WIDTH), constrained_layout=True)
        self.table_ax = self.fig.add_subplot()
        self.table_ax.axis("off")

        self.colors = np.ones((9,9))*0.2
        self.img = self.table_ax.imshow(self.colors, cmap="Greys", vmin=0, vmax=1)

        for l in range(1, 10):
            lw = 3 if not l%3 else 1.5
            self.table_ax.axhline(l-0.5, color="white", linewidth=lw)
            self.table_ax.axvline(l-0.5, color="white", linewidth=lw)
        
        self.text_artists: List[List[Text]] = [[] for _ in range(81)]

    def _clear_text(self):
        for p in range(81):
            for t in self.text_artists[p]:
                t.remove()
            self.text_artists[p] = []
        
    def _reorder_options(self, options) -> List[List[int]]:
        option_rows = [[], [], []]
        for i, o in enumerate(options):
            option_rows[i//3].append(o)
        return option_rows

    def _color_option(self, o: int, considered: set, affected: set):
        if o in considered:
            return "green"
        elif o in affected:
            return "red"
        else:
            return "0.4"

    def _build_text(self, col, row, o, considered, affected, size):
        return self.table_ax.text(col, row, o, fontsize=size,
            color=self._color_option(o, considered, affected),
            horizontalalignment="center", verticalalignment="center")

    def _place_and_highlight(self, text_target: list, row: int, col: int, options: set, considered_options: set, affected_options: set) -> None:        
        if len(options) == 1:
            o = list(options)[0]
            text_target.append(self._build_text(
                col, row, o, considered_options, affected_options, 18))

        else:
            for o_idx, o_row in enumerate(self._reorder_options(options)):
                x = col+(o_idx-1)*self.OFFSET
                for i, o in enumerate(o_row):
                    y = row+(i-1)*self.OFFSET

                    text_target.append(
                        self._build_text(
                            x, y, o, considered_options, affected_options, 7))

        if considered_options|affected_options:
            self.colors[row, col] = 0.1
        else:
            self.colors[row, col] = 0.2
    
    def _is_tile_concerned(self, idx, considered_tiles, considered_options, affected_tiles, affected_options) -> dict:
        return {
            "considered_options": considered_options if idx in considered_tiles else set(),
            "affected_options": affected_options if idx in affected_tiles else set()
        }

    def render(self, sudoku: Sudoku, considered_tiles=None, considered_options=None, affected_tiles=None, affected_options=None, solving_step: int = 0, solving_message: str = None):
        defaults = super().render(sudoku, considered_tiles, considered_options, affected_tiles, affected_options, solving_step, solving_message)
        print(f"solving step {solving_step}: {solving_message}")
        print(f"status: {'violated' if sudoku.violated else 'ok'}")
        
        options = sudoku.get_options()
        self._clear_text()
        for t_idx in range(81):
            rcs_idx = index_to_pos(t_idx)
            row = rcs_idx["r"]
            col = rcs_idx["c"]
            self._place_and_highlight(
                self.text_artists[t_idx], row, col, 
                options[row][col], 
                **self._is_tile_concerned(t_idx, **defaults))
        
        self.img.set_data(self.colors)

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        
class mplAnimator(mplFormatter):
    def __init__(self) -> None:
        self._init_plot()
        self.imgs = []
        self.texts = []
    
    def render(self, sudoku: Sudoku, considered_tiles=None, considered_options=None, affected_tiles=None, affected_options=None, *args):
        defaults = self._get_defaults(considered_tiles, considered_options, affected_tiles, affected_options)
        options = sudoku.get_options()
        self.texts = []
        for t_idx in range(81):
            rcs_idx = index_to_pos(t_idx)
            row = rcs_idx["r"]
            col = rcs_idx["c"]
            self._place_and_highlight(
                self.texts, row, col, 
                options[row][col], 
                **self._is_tile_concerned(t_idx, **defaults))
        
        self.imgs.append([self.table_ax.imshow(self.colors, cmap="Greys", vmin=0, vmax=1)]+self.texts)
  
    def animate(self):
        return ArtistAnimation(self.fig, self.imgs, interval=100)


def solve(sudoku: Sudoku):
    plt.ion()
    formatter = mplFormatter()
    stepper = InterestingStep(formatter, ConsoleTrigger())
    solver = generate_solver([ScaledXWing(2), Bifurcation()], stepper)
    s = solver.launch(sudoku)
    
    plt.ioff()
    formatter.render(s)
    plt.show()
    
    return s

def solving_animation(sudoku: Sudoku):
    formatter = mplAnimator()
    solver = generate_solver([ScaledXWing(2), Bifurcation()],
        AnyStep(formatter, NoTrigger()))
    solver.launch(sudoku)
    anim = formatter.animate()
    anim.save("img/solve_anim_i.mp4")

def launch_solve(path):
    solve(load(path))

def launch_animate(path):
    solving_animation(load(path))

if __name__=="__main__":
    launch_solve("puzzles/mid.csv")