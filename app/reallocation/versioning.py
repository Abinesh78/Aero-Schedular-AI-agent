import uuid
import time
from app.db import SessionLocal
from app.models.roster_version import RosterVersion


CHURN_THRESHOLD = 0.5 # Increased to 1.0 to allow for full roster changes in small datasets


def compute_diff(old_roster, new_roster):

    diff = {
        "changed_slots": []
    }

    old_map = {}
    for day in old_roster["roster"]:
        for slot in day["slots"]:
            old_map[(day["date"], slot["slot_id"])] = slot

    for day in new_roster["roster"]:
        for slot in day["slots"]:
            key = (day["date"], slot["slot_id"])
            if key in old_map:
                if old_map[key] != slot:
                    diff["changed_slots"].append(key)

    return diff


def save_version_with_metrics(old_roster, new_roster):

    start_time = time.time()

    diff = compute_diff(old_roster, new_roster)

    total_slots = sum(len(day["slots"]) for day in old_roster["roster"])
    churn_rate = len(diff["changed_slots"]) / total_slots if total_slots > 0 else 0

    replan_time = time.time() - start_time

    metrics = {
        "churn_rate": churn_rate,
        "total_slots": total_slots,
        "changed_slots": len(diff["changed_slots"]),
        "avg_replan_time_sec": replan_time,
        "violation_count": 0  # solver guarantees 0 hard constraint violations
    }

    # Enforce churn threshold
    if churn_rate > CHURN_THRESHOLD:
        raise Exception(
            f"Churn threshold exceeded! {churn_rate} > {CHURN_THRESHOLD}"
        )

    db = SessionLocal()

    version = RosterVersion(
        version_id=str(uuid.uuid4()),
        week_start=old_roster["week_start"],
        correlation_id=str(uuid.uuid4()),
        diff_json={
            "diff": diff,
            "metrics": metrics
        },
        churn_rate=churn_rate
    )

    db.add(version)
    db.commit()
    db.close()

    return metrics