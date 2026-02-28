from app.weather.weather_service import get_weather
from app.weather.minima_parser import parse_minima
from app.db import SessionLocal
from app.models.simulator import Simulator


def apply_dispatch_logic(roster_json):

    minima_rules = parse_minima()
    db = SessionLocal()
    simulators = db.query(Simulator).all()

    for day in roster_json["roster"]:
        for slot in day["slots"]:

            sortie_type = slot["sortie_type"]

            weather = get_weather(
                roster_json["base_icao"],
                slot["slot_id"],   # using slot_id for deterministic behavior
                slot["end"]
            )

            # Fallback handling
            if weather["ceiling"] is None or weather["visibility"] is None:
                slot["dispatch_decision"] = "NEEDS_REVIEW"
                slot["reasons"] = ["WEATHER_UNAVAILABLE"]
                slot["citations"] = ["rules:weather_minima"]
                continue

            if sortie_type not in minima_rules:
                continue

            required_ceiling = minima_rules[sortie_type]["ceiling"]
            required_visibility = minima_rules[sortie_type]["visibility"]

            # Weather below minima
            if (
                weather["ceiling"] < required_ceiling
                or weather["visibility"] < required_visibility
            ):
                slot["reasons"] = ["WX_BELOW_MINIMA"]
                slot["citations"] = ["rules:weather_minima"]

                # Try SIM conversion
                if simulators:
                    sim = simulators[0]
                    slot["activity"] = "SIM"
                    slot["resource_id"] = sim.id
                    slot["dispatch_decision"] = "GO"
                    slot["reasons"].append("CONVERTED_TO_SIM")
                else:
                    slot["dispatch_decision"] = "NEEDS_REVIEW"
            else:
                slot["dispatch_decision"] = "GO"
                slot["reasons"] = ["WX_OK"]
                slot["citations"] = ["rules:weather_minima"]

    db.close()
    return roster_json