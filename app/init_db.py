from app.db import engine, Base
import app.models.student
import app.models.instructor
import app.models.aircraft
import app.models.simulator
import app.models.rules
import app.models.timeslot
import app.models.roster
import app.models.roster_version
import app.models.ingestion_run

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

print("Tables recreated successfully")