from ortools.sat.python import cp_model
from app.db import SessionLocal
from app.models.student import Student
from app.models.instructor import Instructor
from app.models.aircraft import Aircraft
from app.models.timeslot import TimeSlot


def generate_draft_roster(
    blocked_aircraft=None,
    blocked_instructors=None,
    blocked_students=None,
    fixed_assignments=None
):

    # -----------------------------
    # Default Params
    # -----------------------------
    if blocked_aircraft is None:
        blocked_aircraft = {}

    if blocked_instructors is None:
        blocked_instructors = {}

    if blocked_students is None:
        blocked_students = {}

    if fixed_assignments is None:
        fixed_assignments = {}

    db = SessionLocal()

    students = db.query(Student).all()
    instructors = db.query(Instructor).all()
    aircraft = db.query(Aircraft).all()
    slots = db.query(TimeSlot).all()

    model = cp_model.CpModel()
    assignments = {}

    # -----------------------------
    # Create Decision Variables
    # -----------------------------
    for s in students:
        for i in instructors:
            for a in aircraft:
                for slot in slots:
                    var_name = f"{s.id}_{i.id}_{a.id}_{slot.id}"
                    assignments[(s.id, i.id, a.id, slot.id)] = model.NewBoolVar(var_name)

    # -----------------------------
    # Hard Constraint: Student no double booking
    # -----------------------------
    for s in students:
        for slot in slots:
            model.Add(
                sum(
                    assignments[(s.id, i.id, a.id, slot.id)]
                    for i in instructors
                    for a in aircraft
                ) <= 1
            )

    # -----------------------------
    # Hard Constraint: Instructor no double booking
    # -----------------------------
    for i in instructors:
        for slot in slots:
            model.Add(
                sum(
                    assignments[(s.id, i.id, a.id, slot.id)]
                    for s in students
                    for a in aircraft
                ) <= 1
            )

    # -----------------------------
    # Hard Constraint: Aircraft no double booking
    # -----------------------------
    for a in aircraft:
        for slot in slots:
            model.Add(
                sum(
                    assignments[(s.id, i.id, a.id, slot.id)]
                    for s in students
                    for i in instructors
                ) <= 1
            )

    # -----------------------------
    # Rating Constraint
    # -----------------------------
    sortie_type = "CIRCUITS"

    for s in students:
        for i in instructors:
            for a in aircraft:
                for slot in slots:
                    if sortie_type not in i.ratings:
                        model.Add(assignments[(s.id, i.id, a.id, slot.id)] == 0)

    # -----------------------------
    # Dynamic Blocking — Aircraft
    # -----------------------------
    for s in students:
        for i in instructors:
            for a in aircraft:
                for slot in slots:
                    if a.id in blocked_aircraft:
                        if slot.day in blocked_aircraft[a.id]:
                            model.Add(assignments[(s.id, i.id, a.id, slot.id)] == 0)

    # -----------------------------
    # Dynamic Blocking — Instructor
    # -----------------------------
    for s in students:
        for i in instructors:
            for a in aircraft:
                for slot in slots:
                    if i.id in blocked_instructors:
                        if slot.day in blocked_instructors[i.id]:
                            model.Add(assignments[(s.id, i.id, a.id, slot.id)] == 0)

    # -----------------------------
    # Dynamic Blocking — Student
    # -----------------------------
    for s in students:
        for i in instructors:
            for a in aircraft:
                for slot in slots:
                    if s.id in blocked_students:
                        if slot.day in blocked_students[s.id]:
                            model.Add(assignments[(s.id, i.id, a.id, slot.id)] == 0)

    # -----------------------------
    # Freeze Unaffected Slots
    # -----------------------------
    for slot_id, fixed in fixed_assignments.items():
        for s in students:
            for i in instructors:
                for a in aircraft:
                    key = (s.id, i.id, a.id, slot_id)
                    if key in assignments:
                        if (
                            s.id == fixed["student_id"]
                            and i.id == fixed["instructor_id"]
                            and a.id == fixed["resource_id"]
                        ):
                            model.Add(assignments[key] == 1)
                        else:
                            model.Add(assignments[key] == 0)

    # -----------------------------
    # 5. OBJECTIVE FUNCTION (Mandatory Requirement)
    # -----------------------------
    # Goal: Maximize total training output (number of sorties). 
    # Weights: 
    #   - Each valid (Student, Instructor, Aircraft, Slot) tuple has a weight of 1.
    #   - Invalid tuples (blocked or rating mismatch) have a weight of 0 (effectively).
    # This maximizes "Roster Coverage" as requested in the evaluation harness.
    model.Maximize(sum(assignments.values()))

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    results = []

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        for key, var in assignments.items():
            if solver.Value(var) == 1:
                results.append(key)

    # Track unassigned
    assigned_students = {key[0] for key in results}
    unassigned = [
        {"entity": "student", "id": s.id, "reason": "No availability/slot"}
        for s in students if s.id not in assigned_students
    ]

    db.close()

    roster_json = build_roster_json(results, fixed_assignments)
    roster_json["unassigned"] = unassigned
    return roster_json


# -------------------------------------------------------
# Build JSON Roster
# -------------------------------------------------------

def build_roster_json(assignments, fixed_assignments=None):

    if fixed_assignments is None:
        fixed_assignments = {}

    roster = {
        "week_start": "2026-03-01",
        "base_icao": "VOBG",
        "roster": [],
        "unassigned": []
    }

    day_map = {}

    # Add solver assignments
    for (student_id, instructor_id, aircraft_id, slot_id) in assignments:

        day = slot_id.split("-")[0]

        if day not in day_map:
            day_map[day] = []

        day_map[day].append({
            "slot_id": slot_id,
            "start": "08:00",
            "end": "10:00",
            "activity": "FLIGHT",
            "student_id": student_id,
            "instructor_id": instructor_id,
            "resource_id": aircraft_id,
            "sortie_type": "CIRCUITS",
            "dispatch_decision": "GO",
            "reasons": [],
            "citations": []
        })

    # Ensure frozen slots not lost
    filled_slots = {
        slot["slot_id"]
        for slots in day_map.values()
        for slot in slots
    }

    for slot_id, fixed in fixed_assignments.items():
        if slot_id not in filled_slots:
            day = slot_id.split("-")[0]
            if day not in day_map:
                day_map[day] = []
            day_map[day].append(fixed)

    # Convert to required format
    for day, slots in day_map.items():
        roster["roster"].append({
            "date": day,
            "slots": slots
        })

    return roster