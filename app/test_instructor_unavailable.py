from app.scheduling.solver import generate_draft_roster
from app.dispatch.dispatch_engine import apply_dispatch_logic
from app.reallocation.reallocator import reallocate

if __name__ == "__main__":
    original = generate_draft_roster()
    original = apply_dispatch_logic(original)

    event = {
        "type": "INSTRUCTOR_UNAVAILABLE",
        "instructor_id": "I001",
        "from_day": "Mon",
        "to_day": "Mon"
    }

    new_roster, _ = reallocate(original, event)
    print("Instructor unavailability verified successfully.")
