from pydantic import BaseModel
from typing import Dict, List

class StudentSchema(BaseModel):
    id: str
    availability: Dict
    stage: str
    priority: int
    solo_eligible: bool
    required_sorties_per_week: int

class InstructorSchema(BaseModel):
    id: str
    availability: Dict
    ratings: List[str]
    currency_valid_until: str
    max_duty_hours_per_day: int
    sim_instructor: bool

class AircraftSchema(BaseModel):
    id: str
    type: str
    availability: Dict
    maintenance: Dict

class SimulatorSchema(BaseModel):
    id: str
    type: str
    availability: Dict
    max_sessions_per_day: int

class TimeSlotSchema(BaseModel):
    id: str
    day: str
    start: str
    end: str