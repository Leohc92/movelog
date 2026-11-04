import unittest

import polyline

from coros_geography import codes_from_location, countries_for_track, enrich_activity


class GeographyTests(unittest.TestCase):
    def test_known_locations_are_identified_by_land_boundaries(self):
        locations = [
            ([35.68, 139.76], "JP"),
            ([33.38, 126.62], "KR"),
            ([18.83, 98.97], "TH"),
            ([22.26, 114.2], "CN"),
        ]
        for coordinate, expected in locations:
            with self.subTest(expected=expected):
                self.assertEqual(
                    countries_for_track(polyline.encode([coordinate])), [expected]
                )

    def test_cross_border_track_counts_every_country(self):
        track = polyline.encode(
            [[48.8566, 2.3522], [41.9028, 12.4964], [47.3769, 8.5417]]
        )
        self.assertEqual(countries_for_track(track), ["CH", "FR", "IT"])

    def test_generic_workout_names_are_not_treated_as_china(self):
        for location in [None, "None", "徒步", "跑步", "爬楼", "室内有氧"]:
            with self.subTest(location=location):
                self.assertEqual(codes_from_location(location), [])

    def test_explicit_location_metadata_remains_supported(self):
        self.assertEqual(codes_from_location("{'country': 'Japan'}"), ["JP"])
        self.assertEqual(codes_from_location("上海市 公路骑行"), ["CN"])
        self.assertEqual(codes_from_location("香港特别行政区 徒步"), ["CN"])

    def test_gps_takes_precedence_over_stale_location_text(self):
        original = {
            "summary_polyline": polyline.encode([[35.68, 139.76]]),
            "location_country": "上海市",
        }
        self.assertEqual(enrich_activity(original)["country_codes"], ["JP"])
        self.assertNotIn("country_codes", original)


if __name__ == "__main__":
    unittest.main()
