"""Download atomically; inspect schema without reading huge files into RAM."""
import csv
import gzip
import json
import hashlib
import shutil
import urllib.request
from pathlib import Path

FILES = {"listings.csv.gz": ("data", {"id", "host_id", "price", "room_type", "neighbourhood_cleansed"}),
         "calendar.csv.gz": ("data", {"listing_id", "date", "available"}),
         "reviews.csv.gz": ("data", {"id", "listing_id", "date", "comments"}),
         "neighbourhoods.geojson": ("visualisations", set())}

def validate(path, required):
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8-sig") as stream:
            fields = next(csv.reader(stream), [])
        missing = required - set(fields)
        if missing:
            raise ValueError(f"{path}: missing columns {sorted(missing)}")
    else:
        obj = json.loads(path.read_text(encoding="utf-8"))
        if obj.get("type") != "FeatureCollection" or not obj.get("features"):
            raise ValueError(f"{path}: expected nonempty GeoJSON FeatureCollection")

def download(cfg, root):
    manifest = []
    for snapshot in cfg["snapshots"]:
        for name, (folder, required) in FILES.items():
            url = f'https://data.insideairbnb.com/{cfg["data_root"]}/{snapshot}/{folder}/{name}'
            dest = root / cfg["paths"]["raw"] / snapshot / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            if not dest.exists():
                temp = dest.with_name(name + ".part")
                try:
                    request = urllib.request.Request(url, headers={"User-Agent": "TorontoAirbnbCourse/0.1"})
                    with urllib.request.urlopen(request, timeout=120) as response, temp.open("wb") as out:
                        shutil.copyfileobj(response, out)
                    # Check schema before accepting the atomic file.
                    temp.rename(dest)
                    try:
                        validate(dest, required)
                    except Exception:
                        dest.unlink()
                        raise
                finally:
                    temp.unlink(missing_ok=True)
            validate(dest, required)
            digest = hashlib.sha256()
            with dest.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
            manifest.append({"snapshot_date": snapshot, "file": name, "url": url,
                             "bytes": dest.stat().st_size, "sha256": digest.hexdigest()})
    from .io import write_csv
    write_csv(root / cfg["paths"]["reports"] / "download_manifest.csv", manifest)
