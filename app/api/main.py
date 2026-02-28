from fastapi import FastAPI, Query
from app.scheduling.solver import generate_draft_roster
from app.dispatch.dispatch_engine import apply_dispatch_logic
from app.reallocation.reallocator import reallocate
from app.reallocation.versioning import save_version_with_metrics
from app.db import SessionLocal
from app.models.roster_version import RosterVersion
from app.ingestion.loader import run_full_ingestion

app = FastAPI(title="Airman Agent API")


@app.post("/ingest/run")
def run_ingest():
    """Manually trigger data ingestion."""
    run_full_ingestion()
    return {"status": "success", "message": "Data ingestion completed"}


@app.post("/roster/generate")
def generate_roster():
    """Generate the initial 7-day draft roster."""
    roster = generate_draft_roster()
    roster = apply_dispatch_logic(roster)
    return roster


@app.post("/dispatch/recompute")
def recompute_dispatch(
    date: str = Query(..., description="Date to recompute (e.g., 'Mon')"),
    request_id: str = Query(None, description="Idempotency key")
):
    """Re-run dispatch logic/weather for a specific date."""
    roster = generate_draft_roster()
    roster = apply_dispatch_logic(roster)
    return roster


@app.post("/reallocate")
def reallocate_roster(event: dict):
    """Handle dynamic disruptions and reallocate resources."""
    original = generate_draft_roster()
    original = apply_dispatch_logic(original)

    new_roster, affected = reallocate(original, event)
    metrics = save_version_with_metrics(original, new_roster)

    return {
        "affected": affected,
        "metrics": metrics,
        "roster": new_roster
    }


@app.get("/roster/versions")
def get_versions():
    """List all roster versions with audit trail."""
    db = SessionLocal()
    versions = db.query(RosterVersion).all()

    result = []
    for v in versions:
        result.append({
            "version_id": v.version_id,
            "week_start": v.week_start,
            "churn_rate": v.churn_rate,
            "diff": v.diff_json,
            "created_at": v.created_at,
            "created_by": v.created_by
        })

    db.close()
    return result


@app.get("/eval/run")
def run_evaluation():
    """Run the evaluation harness metrics."""
    from app.evaluation.eval_runner import run_eval
    metrics = run_eval()
    return metrics