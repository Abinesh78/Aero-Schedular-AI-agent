from typing import TypedDict, Dict, Any, Callable
from app.scheduling.solver import generate_draft_roster
from app.dispatch.dispatch_engine import apply_dispatch_logic
from app.reallocation.reallocator import reallocate
from app.reallocation.versioning import save_version_with_metrics


# ---------------------------------------
# Simple Graph Implementation (Mocking Langgraph)
# ---------------------------------------

class SimpleGraph:
    def __init__(self):
        self.nodes: Dict[str, Callable] = {}
        self.edges: Dict[str, str] = {}
        self.entry_point: str = None

    def add_node(self, name: str, func: Callable):
        self.nodes[name] = func

    def add_edge(self, start: str, end: str):
        self.edges[start] = end

    def set_entry_point(self, name: str):
        self.entry_point = name

    def compile(self):
        return self

    def invoke(self, state: Dict[str, Any]):
        current = self.entry_point
        while current and current != "END":
            state = self.nodes[current](state)
            current = self.edges.get(current)
        return state


# ---------------------------------------
# Define Workflow State
# ---------------------------------------

class Level2State(TypedDict):
    original_roster: Dict[str, Any]
    event: Dict[str, Any]
    new_roster: Dict[str, Any]
    affected: list
    metrics: Dict[str, Any]


# ---------------------------------------
# Workflow Nodes
# ---------------------------------------

def assess_impact(state: Level2State):

    print("-> Assessing impact...")
    return state


def identify_affected(state: Level2State):

    print("-> Identifying affected slots...")

    event = state["event"]
    original = state["original_roster"]

    affected = []

    if event["type"] == "AIRCRAFT_UNSERVICEABLE":
        for day in original["roster"]:
            for slot in day["slots"]:
                if (
                    slot["resource_id"] == event["aircraft_id"]
                    and event["from_day"] <= day["date"] <= event["to_day"]
                ):
                    affected.append(slot["slot_id"])

    elif event["type"] == "WEATHER_UPDATE":
        for day in original["roster"]:
            if event["from_day"] <= day["date"] <= event["to_day"]:
                for slot in day["slots"]:
                    affected.append(slot["slot_id"])

    state["affected"] = affected
    return state


def propose_reallocation(state: Level2State):

    print("-> Proposing reallocation...")

    new_roster, _ = reallocate(
        state["original_roster"],
        state["event"]
    )

    state["new_roster"] = new_roster
    return state


def validate_constraints(state: Level2State):

    print("-> Validating constraints...")

    # Solver guarantees hard constraints
    # We just ensure no empty roster

    if not state["new_roster"]["roster"]:
        raise Exception("Reallocation failed — empty roster")

    return state


def commit_version(state: Level2State):

    print("-> Committing version...")

    metrics = save_version_with_metrics(
        state["original_roster"],
        state["new_roster"]
    )

    state["metrics"] = metrics
    return state


from app.orchestration.toolkit import (
    fetch_current_roster,
    apply_disruption,
    propose_reallocation,
    validate_roster_constraints,
    commit_roster_version
)

# ---------------------------------------
# Workflow Nodes (Aligned with Toolkit)
# ---------------------------------------

def assess_impact_node(state: Level2State):
    print("-> Assessing impact...")
    state["event"] = apply_disruption(state["event"])
    return state


def propose_node(state: Level2State):
    print("-> Proposing reallocation...")
    state["new_roster"] = propose_reallocation(
        state["original_roster"],
        state["event"]
    )
    return state


def validate_node(state: Level2State):
    print("-> Validating constraints...")
    if not validate_roster_constraints(state["new_roster"]):
        raise Exception("Validation failed")
    return state


def commit_node(state: Level2State):
    print("-> Committing version...")
    state["metrics"] = commit_roster_version(
        state["original_roster"],
        state["new_roster"]
    )
    return state


# ---------------------------------------
# Build Graph
# ---------------------------------------

def build_level2_graph():

    graph = SimpleGraph()

    graph.add_node("assess", assess_impact_node)
    graph.add_node("propose", propose_node)
    graph.add_node("validate", validate_node)
    graph.add_node("commit", commit_node)

    graph.set_entry_point("assess")

    graph.add_edge("assess", "propose")
    graph.add_edge("propose", "validate")
    graph.add_edge("validate", "commit")
    graph.add_edge("commit", "END")

    return graph.compile()
