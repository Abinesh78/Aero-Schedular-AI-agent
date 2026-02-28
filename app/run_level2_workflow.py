import json
from app.orchestration.level2_workflow import build_level2_graph
from app.scheduling.solver import generate_draft_roster
from app.dispatch.dispatch_engine import apply_dispatch_logic

if __name__ == "__main__":
    workflow = build_level2_graph()
    
    # Setup initial state
    original = generate_draft_roster()
    original = apply_dispatch_logic(original)
    
    event = {
        "type": "AIRCRAFT_UNSERVICEABLE",
        "aircraft_id": "AC01",
        "from_day": "Mon",
        "to_day": "Tue"
    }
    
    final_state = workflow.invoke({
        "original_roster": original,
        "event": event,
        "new_roster": {},
        "affected": [],
        "metrics": {}
    })
    
    print("\nFINAL METRICS:")
    print(json.dumps(final_state["metrics"], indent=2))
