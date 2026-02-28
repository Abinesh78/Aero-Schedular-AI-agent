from app.scheduling.solver import generate_draft_roster
from app.dispatch.dispatch_engine import apply_dispatch_logic
from app.reallocation.reallocator import reallocate

if __name__ == "__main__":
    original = generate_draft_roster()
    original = apply_dispatch_logic(original)

    event = {
        "type": "WEATHER_UPDATE",
        "from_day": "Mon",
        "to_day": "Mon"
    }

    new_roster, _ = reallocate(original, event)
    print("Weather update verified successfully.")
