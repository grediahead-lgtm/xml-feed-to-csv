"""Parse a YML-style supplier feed (<yml_catalog><shop><categories/><offers/></shop></yml_catalog>)."""
import xml.etree.ElementTree as ET

MAX_BYTES = 50 * 1024 * 1024


def load_root(data):
    """data: bytes. Refuses DOCTYPE/ENTITY (entity-expansion attacks) and huge files."""
    if len(data) > MAX_BYTES:
        raise ValueError("feed is larger than %d MB" % (MAX_BYTES // 1024 // 1024))
    head = data[:4096].lower()
    if b"<!doctype" in head or b"<!entity" in data[:65536].lower():
        raise ValueError("DOCTYPE/ENTITY declarations are not allowed in feeds")
    try:
        return ET.fromstring(data)
    except ET.ParseError as e:
        raise ValueError("feed is not valid XML: %s" % e)


def _text(el, tag):
    c = el.find(tag)
    return (c.text or "").strip() if c is not None and c.text else ""


def categories(root):
    """id -> full path 'Parent / Child'."""
    nodes = {}
    for c in root.iter("category"):
        cid = c.get("id")
        if cid:
            nodes[cid] = (c.get("parentId"), (c.text or "").strip())
    paths = {}
    for cid in nodes:
        parts, seen, cur = [], set(), cid
        while cur in nodes and cur not in seen:  # a loop in parentId must not hang us
            seen.add(cur)
            parent, name = nodes[cur]
            parts.append(name)
            cur = parent
        paths[cid] = " / ".join(reversed(parts))
    return paths


def offers(root):
    cats = categories(root)
    for o in root.iter("offer"):
        row = {
            "id": o.get("id", ""),
            "available": o.get("available", ""),
            "name": _text(o, "name") or _text(o, "model"),
            "vendor": _text(o, "vendor"),
            "price": _text(o, "price"),
            "currency": _text(o, "currencyId"),
            "category": cats.get(_text(o, "categoryId"), _text(o, "categoryId")),
            "url": _text(o, "url"),
            "pictures": "|".join((p.text or "").strip() for p in o.findall("picture") if p.text),
            "description": " ".join(_text(o, "description").split()),
        }
        params = {}
        for p in o.findall("param"):
            k = (p.get("name") or "").strip()
            if k:
                params[k] = (p.text or "").strip()
        yield row, params
