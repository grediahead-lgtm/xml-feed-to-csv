import csv

from .parse import load_root, offers

BASE = ["id", "available", "name", "vendor", "price", "currency", "category", "url", "pictures", "description"]


def convert(data, max_param_columns=30):
    """Returns (fieldnames, rows, issues)."""
    root = load_root(data)
    rows, issues, seen, param_names = [], [], {}, []
    for n, (row, params) in enumerate(offers(root), start=1):
        for k in params:
            if k not in param_names:
                param_names.append(k)
        row["_params"] = params
        oid = row["id"]
        if not oid:
            issues.append({"offer": n, "code": "no_id", "message": "offer has no id"})
        elif oid in seen:
            issues.append({"offer": n, "code": "duplicate_id", "message": "id %s already used by offer %d" % (oid, seen[oid])})
            continue
        else:
            seen[oid] = n
        if not row["name"]:
            issues.append({"offer": n, "code": "no_name", "message": "offer %s has no name" % oid})
        try:
            if float(row["price"].replace(",", ".")) <= 0:
                issues.append({"offer": n, "code": "bad_price", "message": "offer %s price is not positive" % oid})
        except ValueError:
            issues.append({"offer": n, "code": "bad_price", "message": "offer %s price %r is not a number" % (oid, row["price"])})
        if not row["pictures"]:
            issues.append({"offer": n, "code": "no_picture", "message": "offer %s has no picture" % oid})
        rows.append(row)
    if len(param_names) > max_param_columns:
        issues.append({"offer": 0, "code": "many_params", "message": "%d different params; only the first %d became columns" % (len(param_names), max_param_columns)})
        param_names = param_names[:max_param_columns]
    for r in rows:
        params = r.pop("_params")
        for k in param_names:
            r["param: " + k] = params.get(k, "")
    return BASE + ["param: " + k for k in param_names], rows, issues


def write_csv(path, fieldnames, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: _cell(v) for k, v in r.items()})


def _cell(v):
    s = str(v)
    return "'" + s if s[:1] in ("=", "+", "-", "@") else s  # no formulas when the CSV is opened in a spreadsheet
