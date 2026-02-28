# Aero Schedular AI Agent Implementation Plan

## Architectural Decisions
- **OR-Tools CP-SAT Solver**: Used for roster generation to handle complex constraints (multi-resource, scheduling windows) efficiently.
- **Micro-Graph Orchestration**: A state-based workflow for reallocation to ensure impact assessment, proposal, validation, and commitment happen in a reliable sequence.
- **SQLAlchemy ORM**: Used for data persistence and auditability.
- **FastAPI**: Provides a robust, self-describing API for external integrations.

## Future Improvements
- **Redis Caching**: Implement distributed caching for weather and roster data.
- **Real-time Weather Integration**: Connect to actual aviation weather APIs (AviationStack, etc.).
- **Proactive Maintenance Scheduling**: Integrate with maintenance logs to predict aircraft availability.
