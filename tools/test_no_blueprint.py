"""Thu 11/17: never mention the paid Blueprint anywhere public. Fails if any served file says Blueprint or 'credited toward'.
Run from tools/: python3 -m unittest test_no_blueprint"""
import os, re, subprocess, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class NoBlueprint(unittest.TestCase):
    def test_public_files(self):
        files = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout.split()
        hits = []
        for f in files:
            if f.startswith(("tools/", "tests/", ".")) or not f.endswith((".html", ".txt", ".js", ".json", ".xml")):
                continue
            s = open(os.path.join(ROOT, f), encoding="utf-8", errors="ignore").read()
            for m in re.finditer(r"(?i)blueprint|credited toward|paid (?:step|session|planning)", s):
                hits.append(f"{f}: {s[max(0, m.start() - 40):m.end() + 20]!r}")
        self.assertEqual(hits, [], "\n".join(hits[:20]))


if __name__ == "__main__":
    unittest.main()
