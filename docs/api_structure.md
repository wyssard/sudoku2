# API Structure

Let us explore the different building blocks a generic solver consists of by going over the key objects found in the respective modules. We shall do this almost hierarchically by starting with the `FmtSolvingMethod` class found in `sudoku.solvingmethods`.

```mermaid
flowchart
    init([launch solver]) --> InitialAlgorithm[Use Initial Algorithm]
    InitialAlgorithm --> LaunchSolver[Launch Algorithm] 
    LaunchSolver --> Solved{Puzzle \nsolved?}

    Solved --yes--> Return([Return Solved Puzzle])

    Solved --no---> SolverLoop[Loop over Tiles]
    SolverLoop --> Increase[Increase]
    Increase --> TerminateLoop{Last \nitem?}
    
    TerminateLoop --Yes--> CheckSuccess{Algorithm \ncould remove \nat least one\n candidate?}
    
    CheckSuccess --No---> FallbackLeft{Fallback \nspecified?}
    FallbackLeft --yes--> Fallback[Continue with Fallback Algorithm]

    CheckSuccess --yes--> Advance[Continue with less elaborate Algorithm]
    Fallback & Advance --> LaunchSolver

    FallbackLeft --no--> Fail([Can't solve puzzle])

    TerminateLoop --No--> FindPattern[[Search for Pattern on the Sudoku grid \nthat lets us deduce \nwhat candidates we can remove \nfrom neighboring tiles]]
    FindPattern --> PatternFound{Match?}

    PatternFound --no--> Increase

    PatternFound --yes--> TryRemove[Check if there are any candidates \nconcerned by the pattern]
    TryRemove --> ToRemove{Found\nCandidates?}

    ToRemove --no--> Increase

    ToRemove --yes--> Remove[Remove Candidates]
    Remove --> Render{{Render Solving Step}}
    Render --> Trigger[Trigger Next Step]
    Trigger --> CleanUp[[Update Routine involving very basic solving algorithms]]
    CleanUp --> Increase
    

```

