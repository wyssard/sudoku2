from sudoku import load, solve, save
save(solve(load("example.csv"), "interesting", unicode=False), "solved.csv")