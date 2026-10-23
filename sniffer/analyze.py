import json
from pathlib import Path

OUTPUT_DIR = Path("output")


def describe(data) -> str:
    if isinstance(data, dict):
        keys = ", ".join(list(data.keys())[:8])
        return f"object with keys: {keys}"
    if isinstance(data, list):
        if data and isinstance(data[0], dict):
            keys = ", ".join(list(data[0].keys())[:8])
            return f"list of {len(data)} objects with: {keys}"
        return f"list of {len(data)} items"
    return type(data).__name__


def find_records(data) -> list:
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        best: list = []
        for value in data.values():
            if isinstance(value, list) and len(value) > len(best):
                best = value
        return best
    return []


def analyze(calls: list[dict]) -> list[dict]:
    json_calls = [c for c in calls if c["is_json"] and c["body"]]
    results = []
    for i, c in enumerate(json_calls, start=1):
        try:
            data = json.loads(c["body"])
        except json.JSONDecodeError:
            continue
        records = find_records(data)
        results.append(
            {
                "index": i,
                "url": c["url"],
                "size": c["size"],
                "shape": describe(data),
                "record_count": len(records),
                "first_record": records[0] if records else None,
                "data": data,
            }
        )
    results.sort(key=lambda r: r["record_count"], reverse=True)
    return results


def save_bodies(results: list[dict]) -> Path:
    folder = OUTPUT_DIR / "bodies"
    folder.mkdir(parents=True, exist_ok=True)
    for r in results:
        path = folder / f"{r['index']:02d}.json"
        path.write_text(json.dumps(r["data"], indent=2), encoding="utf-8")
    return folder