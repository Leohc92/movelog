"""Identify countries offline from GPS tracks and bundled Natural Earth boundaries."""

import argparse
import ast
from functools import lru_cache
import gzip
import json
from pathlib import Path

import polyline
from shapely import STRtree, contains, make_valid, points, prepare
from shapely.geometry import shape

DATA_FILE = Path(__file__).with_name("geography") / "country-boundaries.geojson.gz"


@lru_cache(maxsize=1)
def world():
    with gzip.open(DATA_FILE, "rt", encoding="utf-8") as file:
        data = json.load(file)
    geometries = [
        make_valid(shape(feature["geometry"])) for feature in data["features"]
    ]
    prepare(geometries)
    return data, geometries, STRtree(geometries)


def codes_from_location(location):
    if not location or location == "None":
        return []
    data, _, _ = world()
    aliases = data["aliases"]

    def normalize(value):
        return aliases.get(str(value).strip().lower())

    if location.startswith("{"):
        try:
            parsed = ast.literal_eval(location)
        except (ValueError, SyntaxError):
            try:
                parsed = json.loads(location)
            except (ValueError, TypeError):
                return []
        country = (
            normalize(parsed.get("country", "")) if isinstance(parsed, dict) else None
        )
        return [country] if country else []
    exact = normalize(location)
    if exact:
        return [exact]
    codes = {
        code
        for name, code in aliases.items()
        if len(name) > 1
        and any("\u4e00" <= character <= "\u9fff" for character in name)
        and name in location
    }
    if not codes and any(name in location for name in data["china_locations"]):
        codes.add("CN")
    return sorted(codes)


def countries_for_track(encoded):
    coordinates = polyline.decode(encoded)
    valid = [
        (lng, lat)
        for lat, lng in coordinates
        if -90 <= lat <= 90 and -180 <= lng <= 180
    ]
    if not valid:
        return []
    data, geometries, tree = world()
    gps_points = points(valid)
    candidates = tree.query(gps_points)
    countries = set()
    for index in set(candidates[1]):
        code = data["features"][index]["properties"]["code"]
        if code in countries:
            continue
        selected = gps_points[candidates[0][candidates[1] == index]]
        if contains(geometries[index], selected).any():
            countries.add(code)
    return sorted(countries)


def enrich_activity(activity):
    encoded = activity.get("summary_polyline")
    codes = countries_for_track(encoded) if encoded else []
    if not codes:
        codes = codes_from_location(activity.get("location_country"))
    return {**activity, "country_codes": codes}


def enrich_file(path):
    original = json.loads(path.read_text())
    updated = [enrich_activity(activity) for activity in original]
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n")
    temporary.replace(path)
    codes = sorted({code for activity in updated for code in activity["country_codes"]})
    print(
        json.dumps(
            {
                "records": len(updated),
                "country_count": len(codes),
                "countries": codes,
                "unknown": sum(not activity["country_codes"] for activity in updated),
            }
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--file",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "src/static/activities.json",
    )
    enrich_file(parser.parse_args().file)
