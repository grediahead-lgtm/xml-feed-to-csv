import csv
import os
import sys
import tempfile
import unittest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))

from feed_csv.__main__ import main  # noqa: E402
from feed_csv.convert import convert, write_csv  # noqa: E402
from feed_csv.parse import categories, load_root  # noqa: E402

with open(os.path.join(ROOT, "examples", "feed.xml"), "rb") as f:
    EXAMPLE = f.read()


class ParseTests(unittest.TestCase):
    def test_category_paths_and_loops(self):
        root = load_root(b'<r><category id="1">A</category><category id="2" parentId="1">B</category>'
                         b'<category id="8" parentId="9">X</category><category id="9" parentId="8">Y</category></r>')
        paths = categories(root)
        self.assertEqual(paths["2"], "A / B")
        self.assertIn("8", paths)  # a parentId loop does not hang

    def test_entities_and_doctype_are_refused(self):
        bomb = b'<?xml version="1.0"?><!DOCTYPE x [<!ENTITY a "aaaa">]><x>&a;</x>'
        with self.assertRaises(ValueError):
            load_root(bomb)

    def test_invalid_xml_has_a_clear_message(self):
        with self.assertRaises(ValueError) as cm:
            load_root(b"<a><b></a>")
        self.assertIn("not valid XML", str(cm.exception))


class ConvertTests(unittest.TestCase):
    def test_example(self):
        fields, rows, issues = convert(EXAMPLE)
        self.assertEqual([r["id"] for r in rows], ["1001", "1002", "1003"])  # the duplicate id is dropped
        self.assertEqual(rows[0]["category"], "Зоотовари / Лежаки")
        self.assertEqual(rows[0]["pictures"].count("|"), 1)
        self.assertEqual(rows[0]["description"], "М'який лежак для собак")
        self.assertIn("param: Розмір", fields)
        self.assertEqual(rows[1]["param: Колір"], "")
        codes = sorted(i["code"] for i in issues)
        self.assertEqual(codes, ["bad_price", "bad_price", "duplicate_id", "no_picture"])

    def test_param_column_limit(self):
        offers = "".join('<offer id="%d"><name>n</name><price>1</price><param name="p%d">v</param></offer>' % (i, i) for i in range(5))
        fields, _, issues = convert(("<r>%s</r>" % offers).encode(), max_param_columns=3)
        self.assertEqual(len([f for f in fields if f.startswith("param: ")]), 3)
        self.assertIn("many_params", [i["code"] for i in issues])

    def test_csv_blocks_formulas(self):
        fields, rows, _ = convert(EXAMPLE)
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "o.csv")
            write_csv(p, fields, rows)
            with open(p, encoding="utf-8") as f:
                got = list(csv.DictReader(f))
        self.assertTrue(got[2]["name"].startswith("'="))


class CliTests(unittest.TestCase):
    def test_cli(self):
        with tempfile.TemporaryDirectory() as d:
            out, iss = os.path.join(d, "o.csv"), os.path.join(d, "i.json")
            self.assertEqual(main([os.path.join(ROOT, "examples", "feed.xml"), "--out", out, "--issues", iss]), 0)
            self.assertTrue(os.path.getsize(out) > 0 and os.path.getsize(iss) > 0)


if __name__ == "__main__":
    unittest.main()
