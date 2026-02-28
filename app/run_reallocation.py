from app.scheduling.solver import generate_draft_roster
from app.dispatch.dispatch_engine import apply_dispatch_logic
from app.reallocation.reallocator import reallocate
from app.reallocation.versioning import save_version_with_metrics

if __name__ == "__main__":
    original = generate_draft_roster()
    original = apply_dispatch_logic(original)

    event = {
        "type": "AIRCRAFT_UNSERVICEABLE",
        "aircraft_id": "AC01",
        "from_day": "Mon",
        "to_day": "Tue"
    }

    new_roster, affected = reallocate(original, event)
    metrics = save_version_with_metrics(original, new_roster)

    print("Reallocation complete.")
    print(f"Affected slots: {len(affected)}")
    print(f"Churn rate: {metrics['churn_rate']}")
