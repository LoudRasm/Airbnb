import csv
import gzip
import json
from pathlib import Path

def load_config(path):
    # JSON is a subset of YAML. Keep this starter config in JSON syntax.
    path = Path(path).resolve()
    cfg = json.loads(path.read_text(encoding="utf-8"))
    if not cfg.get("snapshots") or len(set(cfg["snapshots"])) != len(cfg["snapshots"]):
        raise ValueError("snapshots must be nonempty and unique")
    from datetime import date
    for snapshot in cfg["snapshots"]:
        date.fromisoformat(snapshot)
    return cfg, path.parent.parent

def rows(path):
    path = Path(path)
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8-sig", newline="") as stream:
        yield from csv.DictReader(stream)

def write_csv(path, records, fields=None):
    records = list(records)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = fields or (list(records[0]) if records else [])
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)
