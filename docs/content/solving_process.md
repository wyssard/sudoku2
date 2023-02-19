# Solving Process

When working with the [Custom Solver](custom_solver.md) or when making use of the [API](api_guide.md), your interaction with the package goes beyond the simplified functional access and you will be confronted with the objects that, e.g., represent the solving algorithms or the rendering frontend. In order to understand how these objects interact with each other, a basic understanding of the solving procedure, illustrated by the flowchart below, is indispensible.

We come back to some specific nodes of the diagram when discussing the [API](api_guide.md) or the [Custom Solver](custom_solver.md) generator.

## Flowchart

```mermaid
flowchart
    init([Launch Solver]) --> InitialAlgorithm[Use initial Algorithm]
    InitialAlgorithm --> LaunchSolver[Launch Algorithm] 
    LaunchSolver --> Solved{Puzzle \nsolved?}

    Solved --Yes--> Return([Return Solved Puzzle])

    Solved --No---> SolverLoop[Loop over Tiles]
    SolverLoop --> Increase[Next Tile]
    Increase --> TerminateLoop{Last \nitem?}
    
    TerminateLoop --Yes--> CheckSuccess{Algorithm \ncould remove \nat least one\n candidate?}
    
    CheckSuccess --No---> FallbackLeft{Fallback \nAlgorithm \nspecified?}
    FallbackLeft --Yes--> Fallback[Continue with Fallback Algorithm]

    CheckSuccess --Yes--> Advance[Continue with less elaborate Algorithm]
    Fallback & Advance --> LaunchSolver

    FallbackLeft --No--> Fail([Can't solve puzzle])

    TerminateLoop --No--> FindPattern[[Search for Pattern on the Sudoku grid \nthat lets us deduce \nwhat Candidates we can remove \nfrom neighboring Tiles]]
    FindPattern --> PatternFound{Pattern \nmatched?}

    PatternFound --No--> Increase

    PatternFound --Yes--> TryRemove[Check if there are any Candidates \nconcerned by the Pattern]
    TryRemove --> ToRemove{Concerned\ncandidates\nfound?}

    ToRemove --No--> Increase

    ToRemove --yes--> Remove[Remove Candidates]
    Remove --> Render{{Render Solving Step}}
    Render --> Trigger[Trigger Next Step]
    Trigger --> CleanUp[[Update Routine involving very basic Solving Algorithms]]
    CleanUp --> Increase
    
```

## A Word of Caution

Since there are some severe differences in between the implemented solving algorithms, the API does not force you (so far) to entirely stick to the prescription suggested by the diagram. For example, you are free to decide whether to implement a loop over tiles or to replace it by a better suiting approach.

!!! note
    Future versions may address this inconvenience by providing further abstraction that ultimately forces you to stick to the suggested prescription by means of an intermediate abstract class. Since, however, the procedures that are not yet abstracted are very simple (they come in form of simple conditions or loops), further abstraction may also be omitted completely, to make the code more readable.
