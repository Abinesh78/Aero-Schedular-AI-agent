from app.scheduling.solver import generate_draft_roster
from app.dispatch.dispatch_engine import apply_dispatch_logic


def reallocate(original_roster, event):

    blocked_aircraft = {}
    blocked_instructors = {}
    blocked_students = {}

    fixed_assignments = {}
    affected = []

    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    # -----------------------------
    # Handle Event Types
    # -----------------------------

    if event["type"] == "AIRCRAFT_UNSERVICEABLE":
        blocked_aircraft[event["aircraft_id"]] = [
            d for d in days if event["from_day"] <= d <= event["to_day"]
        ]

    elif event["type"] == "INSTRUCTOR_UNAVAILABLE":
        blocked_instructors[event["instructor_id"]] = [
            d for d in days if event["from_day"] <= d <= event["to_day"]
        ]

    elif event["type"] == "STUDENT_UNAVAILABLE":
        blocked_students[event["student_id"]] = [
            d for d in days if event["from_day"] <= d <= event["to_day"]
        ]

    # -----------------------------
    # Identify affected slots
    # -----------------------------

    for day in original_roster["roster"]:
        for slot in day["slots"]:

            date = day["date"]
            slot_id = slot["slot_id"]

            if event["type"] == "AIRCRAFT_UNSERVICEABLE":
                if (
                    slot["resource_id"] == event["aircraft_id"]
                    and date in blocked_aircraft[event["aircraft_id"]]
                ):
                    affected.append(slot_id)
                else:
                    fixed_assignments[slot_id] = slot

            elif event["type"] == "INSTRUCTOR_UNAVAILABLE":
                if (
                    slot["instructor_id"] == event["instructor_id"]
                    and date in blocked_instructors[event["instructor_id"]]
                ):
                    affected.append(slot_id)
                else:
                    fixed_assignments[slot_id] = slot

            elif event["type"] == "STUDENT_UNAVAILABLE":
                if (
                    slot["student_id"] == event["student_id"]
                    and date in blocked_students[event["student_id"]]
                ):
                    affected.append(slot_id)
                else:
                    fixed_assignments[slot_id] = slot

            elif event["type"] == "WEATHER_UPDATE":
                if event["from_day"] <= date <= event["to_day"]:
                    affected.append(slot_id)
                else:
                    fixed_assignments[slot_id] = slot

    # -----------------------------
    # Re-run solver with freezing
    # -----------------------------

    new_roster = generate_draft_roster(
        blocked_aircraft=blocked_aircraft,
        blocked_instructors=blocked_instructors,
        blocked_students=blocked_students,
        fixed_assignments=fixed_assignments
    )

    new_roster = apply_dispatch_logic(new_roster)

    return new_roster, affected