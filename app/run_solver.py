import json
from app.scheduling.solver import generate_draft_roster
from app.dispatch.dispatch_engine import apply_dispatch_logic

if __name__ == "__main__":
    roster = generate_draft_roster()
    roster = apply_dispatch_logic(roster)
    print(json.dumps(roster, indent=2))
