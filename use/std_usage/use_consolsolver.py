from sudoku import load, solve

def main():
    solve(load("puzzles/evil4.csv"), "interesting")

if __name__=="__main__":
    main()