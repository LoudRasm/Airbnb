"""Dependency-free SVG charts; extend to publication figures in TV3/TV4 modules."""
from html import escape
import json



def bars(records, label, value, path, title):
    pairs = [(str(r[label]), float(r[value])) for r in records if r[value] != ""]
    high = max([v for _, v in pairs] + [1])
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="{100+len(pairs)*40}"><rect width="100%" height="100%" fill="white"/><text x="20" y="30">{escape(title)}</text>']
    for i, (name, val) in enumerate(pairs):
        y = 65 + i*40
        parts.append(f'<text x="20" y="{y+15}">{escape(name)}</text><rect x="180" y="{y}" width="{600*val/high}" height="22" fill="#237a8b"/><text x="{190+600*val/high}" y="{y+15}">{val:.2f}</text>')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(parts) + "</svg>", encoding="utf-8")

def spatial(geo, listings, path, title):
    points = [(r["longitude"], r["latitude"]) for r in listings if r["longitude"] is not None and r["latitude"] is not None]
    polygons = []
    for feature in geo["features"]:
        geometry = feature.get("geometry") or {}
        if geometry.get("type") == "Polygon":
            polygons.extend(geometry["coordinates"])
        elif geometry.get("type") == "MultiPolygon":
            for poly in geometry["coordinates"]:
                polygons.extend(poly)
    all_points = points + [tuple(p[:2]) for poly in polygons for p in poly]
    if not all_points:
        raise ValueError("No valid spatial coordinates")
    xs, ys = zip(*all_points)
    xmin, xmax, ymin, ymax = min(xs), max(xs), min(ys), max(ys)
    def xy(x, y):
        return (30+800*(x-xmin)/(xmax-xmin or 1), 550-470*(y-ymin)/(ymax-ymin or 1))
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="600"><rect width="100%" height="100%" fill="white"/><text x="20" y="30">{escape(title)}</text>']
    for poly in polygons:
        coords = " ".join(f"{xy(p[0],p[1])[0]},{xy(p[0],p[1])[1]}" for p in poly)
        parts.append(f'<polygon points="{coords}" fill="#eeeeee" stroke="#888888"/>')
    for x, y in points:
        px, py = xy(x, y)
        parts.append(f'<circle cx="{px}" cy="{py}" r="2" fill="#237a8b"/>')
    parts.append('<text x="20" y="590">Longitude/latitude schematic; no area or density inference</text></svg>')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(parts), encoding="utf-8")
