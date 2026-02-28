import re
from app.db import SessionLocal
from app.models.rules import RulesDoc


def parse_minima():

    db = SessionLocal()

    doc = db.query(RulesDoc).filter_by(id="weather_minima").first()

    if not doc:
        db.close()
        return {}

    content = doc.content

    minima = {}

    pattern = r"## (.*?)\n- Minimum ceiling: (\d+) ft\n- Minimum visibility: (\d+) km"

    matches = re.findall(pattern, content)

    for match in matches:
        sortie = match[0].split(" - ")[0].strip()
        ceiling = int(match[1])
        visibility = int(match[2])

        minima[sortie] = {
            "ceiling": ceiling,
            "visibility": visibility
        }

    db.close()
    return minima