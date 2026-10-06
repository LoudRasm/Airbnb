"""One-command entry point, independent of current working directory."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from airbnb.io import load_config, rows, write_csv
from airbnb.download import download, validate, FILES
from airbnb.qa import clean_listings
from airbnb.calendar import aggregate
from airbnb.reviews import collect
from airbnb.kpi import summarize, guest_kpi
from airbnb.analysis import churn
from airbnb.eda import profile
from airbnb.baseline import predict
from airbnb.llm import analyze
from airbnb.evaluate import evaluate
from airbnb.viz import bars, spatial

def run(config_path, demo=False, skip_llm=False, no_download=False):
    cfg, root = load_config(config_path)
    # Never mix synthetic outputs/cache with real outputs.
    suffix = "demo" if demo else "real"
    processed = root / cfg["paths"]["processed"] / suffix
    reports = root / cfg["paths"]["reports"] / suffix
    figures = root / cfg["paths"]["figures"] / suffix
    if demo and not skip_llm:
        raise ValueError("Synthetic demo requires --skip-llm; use real data for API analysis")
    if not demo and not no_download:
        download(cfg, root)
    listings, calendar, qa, reviews = [], [], [], {}
    snapshots = sorted(cfg["snapshots"])
    for snapshot in snapshots:
        folder = root / ("data/samples/demo" if demo else cfg["paths"]["raw"]) / snapshot
        for name, (_, required) in FILES.items():
            validate(folder/name, required)
        clean, report = clean_listings(rows(folder/"listings.csv.gz"), snapshot, cfg)
        listings.extend(clean)
        qa.extend(report)
        cal, issues = aggregate(rows(folder/"calendar.csv.gz"), snapshot, cfg["calendar"]["window_days"], {r["listing_id"] for r in clean})
        calendar.extend(cal)
        issues.update(collect(rows(folder/"reviews.csv.gz"), snapshot, reviews))
        qa.extend({"snapshot_date": snapshot, "rule": key, "affected_rows": count, "action": "exclude_or_dedupe", "rows_after": "", "median_price_before": "", "median_price_after": ""} for key,count in issues.items())
    metrics = summarize(listings, calendar, cfg["currency"])
    write_csv(processed/"listings.csv", listings)
    write_csv(processed/"calendar_summary.csv", calendar, ["snapshot_date","listing_id","available_days","observed_days","expected_days","availability_rate"])
    write_csv(processed/"reviews.csv", reviews.values(), ["review_id","listing_id","date","comments","first_seen_snapshot"])
    write_csv(processed/"kpi_market.csv", metrics)
    write_csv(processed/"kpi_churn.csv", churn(listings, snapshots), ["previous_snapshot","snapshot_date","new","retained","disappeared","entry_rate","exit_rate"])
    write_csv(reports/"qa_report.csv", qa)
    if not demo:
        write_csv(root / "reports/qa_report.csv", qa)
    write_csv(reports/"eda_flags.csv", profile(listings))
    baseline = [predict(r) for r in reviews.values()]
    write_csv(processed/"baseline.csv", baseline, ["review_id","sentiment","source"])
    llm = [] if skip_llm else analyze(list(reviews.values()), cfg, root)
    # Serialize lists as JSON inside CSV fields.
    llm_csv = [{k: json.dumps(v) if isinstance(v,list) else v for k,v in r.items()} for r in llm]
    write_csv(processed/"llm_reviews.csv", llm_csv, ["review_id","sentiment","language","positive_aspects","negative_aspects","source"])
    write_csv(processed/"kpi_guest.csv", guest_kpi(llm), ["metric","value","sample_n","source","scope"])
    label_path = root / ("data/samples/demo_labels.csv" if demo else "data/samples/manual_labels.csv")
    labels = list(rows(label_path))
    # Compare both models on the SAME paired review sample when LLM is enabled.
    ids = {r["review_id"] for r in llm}
    comparisons = evaluate([r for r in baseline if not llm or r["review_id"] in ids], labels, "baseline") + evaluate(llm, labels, "llm")
    write_csv(reports/"evaluation.csv", comparisons, ["source","paired_n","manual_n","accuracy","macro_f1","meets_100_paired"])
    totals = [r for r in metrics if r["neighbourhood"] == "ALL"]
    marker = "SYNTHETIC DEMO — " if demo else ""
    bars(totals, "snapshot_date", "supply", figures/"supply.svg", marker+"Observed listing supply")
    bars(totals, "snapshot_date", "median_price", figures/"price.svg", marker+f'Median nightly price ({cfg["currency"]})')
    latest_folder = root / ("data/samples/demo" if demo else cfg["paths"]["raw"]) / snapshots[-1]
    geo = json.loads((latest_folder/"neighbourhoods.geojson").read_text())
    spatial(geo, [r for r in listings if r["snapshot_date"] == snapshots[-1]], figures/"spatial.svg", marker+"Listing locations and neighbourhood boundaries")
    if llm:
        from collections import Counter
        bars([{"sentiment":k,"count":v} for k,v in Counter(r["sentiment"] for r in llm).items()], "sentiment", "count", figures/"llm_sentiment.svg", "LLM sample sentiment")
    else:
        (figures/"llm_sentiment.svg").unlink(missing_ok=True)
    reports.mkdir(parents=True, exist_ok=True)
    (reports/"run_metadata.json").write_text(json.dumps({"demo":demo,"llm_status":"skipped" if skip_llm else "live_or_valid_cache", "config":cfg,"python":sys.version,"review_n":len(reviews)},indent=2))
    print(f"Completed {suffix}: {len(listings)} listings; outputs: {processed}, {reports}, {figures}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(Path(__file__).resolve().parent/"configs/toronto.yaml"))
    parser.add_argument("--demo", action="store_true")
    parser.add_argument("--skip-llm", action="store_true")
    parser.add_argument("--no-download", action="store_true")
    args = parser.parse_args()
    run(args.config, args.demo, args.skip_llm, args.no_download)
