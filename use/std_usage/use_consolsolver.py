from sudoku import load, solve

def main():
    solve(load("examples/evil4.csv"), "skip")

if __name__=="__main__":
    main()