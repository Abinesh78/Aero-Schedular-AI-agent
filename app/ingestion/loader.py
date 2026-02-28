import json
import os
import uuid
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models.ingestion_run import IngestionRun
from app.models.student import Student
from app.models.instructor import Instructor
from app.models.aircraft import Aircraft
from app.models.simulator import Simulator
from app.models.timeslot import TimeSlot
from app.models.rules import RulesDoc

from .schemas import (
    StudentSchema,
    InstructorSchema,
    AircraftSchema,
    SimulatorSchema,
    TimeSlotSchema
)

from .utils import compute_hash


# -------------------------------------------------------
# GENERIC JSON INGEST FUNCTION
# -------------------------------------------------------

def generic_json_ingest(model_class, schema_class, file_path, entity_name):

    db: Session = SessionLocal()

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    input_hash = compute_hash(file_bytes)

    # Check idempotency
    existing_run = db.query(IngestionRun).filter_by(input_hash=input_hash).first()
    if existing_run:
        print(f"{entity_name} already ingested. Skipping.")
        db.close()
        return

    data = json.loads(file_bytes)

    diff = {
        entity_name: {
            "added": [],
            "modified": [],
            "removed": []
        }
    }

    existing_objects = db.query(model_class).all()
    existing_ids = {obj.id for obj in existing_objects}
    new_ids = set()

    for item in data:
        validated = schema_class(**item)
        new_ids.add(validated.id)

        existing = db.query(model_class).filter_by(id=validated.id).first()

        if not existing:
            db.add(model_class(**validated.dict()))
            diff[entity_name]["added"].append(validated.id)
        else:
            for key, value in validated.dict().items():
                setattr(existing, key, value)
            diff[entity_name]["modified"].append(validated.id)

    # Detect removed records
    removed_ids = existing_ids - new_ids
    for rid in removed_ids:
        diff[entity_name]["removed"].append(rid)

    # Log ingestion run
    ingestion_record = IngestionRun(
        id=str(uuid.uuid4()),
        input_hash=input_hash,
        diff_json=diff
    )

    db.add(ingestion_record)
    db.commit()
    db.close()

    print(f"{entity_name} ingestion completed.")


# -------------------------------------------------------
# INGEST RULE DOCUMENTS (.md files)
# -------------------------------------------------------

def ingest_rules_docs():

    db = SessionLocal()

    docs = [
        ("weather_minima", "app/data/weather_minima.md"),
        ("dispatch_rules", "app/data/dispatch_rules.md")
    ]

    for doc_id, path in docs:
        with open(path, "r") as f:
            content = f.read()

        existing = db.query(RulesDoc).filter_by(id=doc_id).first()

        if not existing:
            db.add(RulesDoc(
                id=doc_id,
                doc_name=doc_id,
                content=content
            ))
        else:
            existing.content = content

    db.commit()
    db.close()

    print("Rules docs ingested.")


# -------------------------------------------------------
# MAIN INGESTION ENTRY POINT
# -------------------------------------------------------

def run_full_ingestion():

    base_path = "app/data"
    generic_json_ingest(Student, StudentSchema, f"{base_path}/students.json", "students")
    generic_json_ingest(Instructor, InstructorSchema, f"{base_path}/instructors.json", "instructors")
    generic_json_ingest(Aircraft, AircraftSchema, f"{base_path}/aircraft.json", "aircraft")
    generic_json_ingest(Simulator, SimulatorSchema, f"{base_path}/simulators.json", "simulators")
    generic_json_ingest(TimeSlot, TimeSlotSchema, f"{base_path}/time_slots.json", "time_slots")

    ingest_rules_docs()

    print("Full ingestion completed.")