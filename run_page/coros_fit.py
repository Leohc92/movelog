"""Convert COROS FIT exports to the dashboard's public activity format."""

from datetime import timezone
from zoneinfo import ZoneInfo

from garmin_fit_sdk import Decoder, Stream
import polyline


def sport_type(code):
    if code in (100, 101, 102, 103):
        return "Run"
    if code in (104, 105, 106, 900):
        return "Hike"
    if code in (200, 201, 202, 203, 204, 205, 299):
        return "Ride"
    if code in (300, 301):
        return "Swim"
    if code == 402:
        return "WeightTraining"
    if code == 902:
        return "StairStepper"
    return "Workout"


def read_activity(path, label_id, code, previous=None, timezone_name="Asia/Shanghai"):
    previous = previous or {}
    messages, errors = Decoder(Stream.from_file(str(path))).read()
    if errors:
        raise ValueError("FIT decode failed; existing activity data was kept")
    sessions = messages.get("session_mesgs", [])
    if len(sessions) != 1:
        raise ValueError("Expected one FIT session; multi-sport exports need review")
    session = sessions[0]
    start = session["start_time"].replace(tzinfo=timezone.utc)
    seconds = round(session.get("total_timer_time") or session["total_elapsed_time"])
    distance = float(session.get("total_distance") or 0)
    points = []
    for values in messages.get("record_mesgs", []):
        lat, lon = values.get("position_lat"), values.get("position_long")
        if lat is None or lon is None:
            continue
        point = (lat * 180 / 2**31, lon * 180 / 2**31)
        if not (-90 <= point[0] <= 90 and -180 <= point[1] <= 180):
            continue
        if not points or point != points[-1]:
            points.append(point)
    kind = sport_type(code)
    names = {
        "Run": "跑步",
        "Ride": "骑行",
        "Hike": "徒步",
        "Swim": "游泳",
        "WeightTraining": "力量训练",
        "StairStepper": "爬楼",
        "Workout": "综合训练",
    }
    return {
        "run_id": int(start.timestamp()),
        "coros_id": str(label_id),
        "coros_fit_imported": True,
        "name": previous.get("name") or names[kind],
        "distance": distance,
        "moving_time": f"{seconds // 3600}:{seconds % 3600 // 60:02}:{seconds % 60:02}",
        "type": kind,
        "start_date": start.isoformat().replace("+00:00", "Z"),
        "start_date_local": previous.get("start_date_local")
        or start.astimezone(ZoneInfo(timezone_name)).strftime("%Y-%m-%dT%H:%M:%S"),
        "location_country": previous.get("location_country"),
        "summary_polyline": polyline.encode(points) if len(points) >= 2 else None,
        "average_heartrate": session.get("avg_heart_rate"),
        "average_speed": session.get("enhanced_avg_speed")
        or session.get("avg_speed")
        or (distance / seconds if seconds else 0),
        "elevation_gain": session.get("total_ascent"),
        "source": "COROS",
        "streak": 1,
    }
