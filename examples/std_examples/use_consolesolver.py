from sudoku import load, solve

def main():
    solve(load("puzzles/evil4.csv"), "interesting", unicode=False)

if __name__=="__main__":
    main()