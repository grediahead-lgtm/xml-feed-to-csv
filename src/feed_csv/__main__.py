import argparse
import json
import sys

from .convert import convert, write_csv


def main(argv=None):
    ap = argparse.ArgumentParser(prog="feed_csv", description="Convert a YML/XML supplier feed to CSV.")
    ap.add_argument("feed", help="path to the XML feed file")
    ap.add_argument("--out", default="feed.csv")
    ap.add_argument("--issues", help="write the problems as JSON to this file")
    args = ap.parse_args(argv)
    with open(args.feed, "rb") as f:
        fields, rows, issues = convert(f.read())
    write_csv(args.out, fields, rows)
    if args.issues:
        with open(args.issues, "w", encoding="utf-8") as f:
            json.dump(issues, f, ensure_ascii=False, indent=2)
    counts = {}
    for i in issues:
        counts[i["code"]] = counts.get(i["code"], 0) + 1
    print(json.dumps({"offers_exported": len(rows), "issues": counts}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
