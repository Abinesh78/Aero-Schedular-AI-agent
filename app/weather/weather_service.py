import time
from datetime import datetime, timedelta

# -------------------------------------------------------
# SIMPLE IN-MEMORY CACHE
# -------------------------------------------------------

_weather_cache = {}

CACHE_TTL_SECONDS = 10  # 5 minutes


def _generate_deterministic_weather(icao, start_time):
    """
    Deterministic weather based on slot time.
    No randomness.
    """

    # Simple deterministic rule:
    # If slot contains "S1" → bad weather
    # If slot contains "S2" → good weather

    if "S1" in start_time:
        return {
            "ceiling": 1500,
            "visibility": 4,
            "wind": 18
        }
    else:
        return {
            "ceiling": 4000,
            "visibility": 10,
            "wind": 8
        }


def get_weather(icao, start_time, end_time):
    """
    Deterministic weather tool with caching + fallback.
    """

    cache_key = f"{icao}_{start_time}_{end_time}"

    # -----------------------------
    # Check Cache
    # -----------------------------
    if cache_key in _weather_cache:
        cached = _weather_cache[cache_key]
        if datetime.utcnow() < cached["expires_at"]:
            return cached["data"]

    # -----------------------------
    # Simulated Retry Logic
    # -----------------------------
    max_retries = 3

    for attempt in range(max_retries):
        try:
            weather_data = _generate_deterministic_weather(icao, start_time)

            result = {
                "ceiling": weather_data["ceiling"],
                "visibility": weather_data["visibility"],
                "wind": weather_data["wind"],
                "fetched_at": datetime.utcnow().isoformat(),
                "confidence": 0.95
            }

            # Store in cache
            _weather_cache[cache_key] = {
                "data": result,
                "expires_at": datetime.utcnow() + timedelta(seconds=CACHE_TTL_SECONDS)
            }

            return result

        except Exception:
            time.sleep(0.2)

    # -----------------------------
    # Deterministic Fallback
    # -----------------------------
    return {
        "ceiling": None,
        "visibility": None,
        "wind": None,
        "fetched_at": datetime.utcnow().isoformat(),
        "confidence": 0.0
    }