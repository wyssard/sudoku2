from sudoku import generate_solver, ScaledXWing, YWing, Bifurcation, InterestingStep, ConsoleFormatter, ConsoleTrigger, load
solver = generate_solver(
    [ScaledXWing(2), YWing(), Bifurcation()],
    InterestingStep(ConsoleFormatter(), ConsoleTrigger())
)
solved = solver.launch(load("example.csv"))