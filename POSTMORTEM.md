# Post-Mortem

## What went well
- **Constraint Solver**: OR-Tools provided a very robust way to handle the 7-day roster generation without manual backtracking logic.
- **Micro-Graph Workflow**: Implementing a custom state machine for reallocation proved faster and more reliable than heavier orchestration frameworks in this specific environment.

## Challenges
- **Environmental DLLs**: Encountered issues with `uuid-utils` on the specific Windows environment which necessitated a pivot from `langgraph` to a custom lightweight graph implementation.
- **Roster Churn**: Balancing the need for a valid roster with the desire to minimize "flicker" for students and instructors required careful thresholding.

## Lessons Learned
- **Zero-Dependency Core**: For technical assessments, prioritizing a zero-dependency or lightweight core (like our `SimpleGraph`) ensures maximum portability across host systems.
- **Schema Strictness**: Early investment in Pydantic schemas significantly reduced debugging time during the complex ingestion phase.
