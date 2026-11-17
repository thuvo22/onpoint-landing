"""prices.json must agree with the schema prices and the live estimator (run from tools/: python3 -m unittest test_prices_json)."""
import json, os, re, sys, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import schema_prices  # noqa: E402


class PricesJson(unittest.TestCase):
    def setUp(self):
        self.p = json.load(open(os.path.join(ROOT, "prices.json")))
        self.bath, self.dry = self.p["services"][0], self.p["services"][1]

    def test_minimums_match_schema(self):
        self.assertEqual(self.bath["minimum_price"], schema_prices.BATH["priceSpecification"]["minPrice"])
        self.assertEqual(self.dry["minimum_price"], schema_prices.DRY["priceSpecification"]["minPrice"])

    def test_planning_ranges_match_estimator(self):
        html = open(os.path.join(ROOT, "bathroom", "cost-estimator.html")).read()
        shown = re.findall(r'range: "\$([\d,]+) to \$([\d,]+)"', html)
        want = [(f"{r['min']:,}", f"{r['max']:,}") for r in self.bath["planning_ranges"]]
        self.assertEqual(shown, want)

    def test_never_mentions_blueprint(self):
        # Thu 11/17: never mention the paid Blueprint anywhere public
        self.assertNotRegex(json.dumps(self.p), r"(?i)blueprint|credited toward")


if __name__ == "__main__":
    unittest.main()
