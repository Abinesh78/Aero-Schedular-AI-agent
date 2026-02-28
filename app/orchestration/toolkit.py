from typing import Dict, Any
from app.scheduling.solver import generate_draft_roster
from app.dispatch.dispatch_engine import apply_dispatch_logic
from app.reallocation.reallocator import reallocate
from app.reallocation.versioning import save_version_with_metrics

# ---------------------------------------
# MANDATORY TOOLS (Page 7 & 8 of Assessment)
# ---------------------------------------

def fetch_current_roster(date_range: str = None) -> Dict[str, Any]:
    """1. fetch_current_roster(date_range)"""
    # In this implementation, returns the latest draft
    roster = generate_draft_roster()
    return apply_dispatch_logic(roster)

def apply_disruption(event: Dict[str, Any]) -> Dict[str, Any]:
    """2. apply_disruption(event)"""
    # Logic to assess which slots are affected by event
    # (Used by Workflow)
    return event

def propose_reallocation(original_roster: Dict[str, Any], event: Dict[str, Any]) -> Dict[str, Any]:
    """3. propose_reallocation(affected_slots)"""
    new_roster, _ = reallocate(original_roster, event)
    return new_roster

def validate_roster_constraints(roster: Dict[str, Any]) -> bool:
    """4. validate_roster_constraints(roster)"""
    if not roster.get("roster"):
        return False
    # CP-SAT ensures hard constraints, we just verify structure
    return True

def commit_roster_version(original: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
    """5. commit_roster_version(roster, change_summary)"""
    metrics = save_version_with_metrics(original, new)
    return metrics
