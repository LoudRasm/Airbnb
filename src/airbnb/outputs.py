"""One source of truth for pipeline CSV schemas and destinations."""
from . import analysis


def csv_outputs(processed, reports, skip_llm):
    outputs = [
        (processed / 'listings.csv', 'listings', ['snapshot_date','listing_id','host_id','price','room_type','analysis_area','neighbourhood_cleansed','latitude','longitude','qa_flags']),
        (processed / 'calendar_summary.csv', 'calendar', ['snapshot_date','listing_id','available_days','observed_days','expected_days','availability_rate']),
        (processed / 'reviews.csv', 'reviews', ['review_id','listing_id','date','comments','first_seen_snapshot']),
        (processed / 'kpi_market.csv', 'market_kpi', ['snapshot_date','analysis_area','supply','median_price','price_n','currency','entire_home_share','multi_listing_host_share']),
        (processed / 'kpi_calendar.csv', 'calendar_kpi', ['snapshot_date','analysis_area','availability_rate','observed_days','expected_days','listing_n','coverage_rate']),
        (processed / 'kpi_churn.csv', 'churn_kpi', analysis.TRANSITION_FIELDS),
        (processed / 'baseline.csv', 'baseline', ['review_id','sentiment','source']),
        (processed / 'llm_reviews.csv', 'llm_reviews', ['review_id','sentiment','language','positive_aspects','negative_aspects','source']),
        (processed / 'kpi_guest.csv', 'guest_kpi', ['metric','value','sample_n','source','scope']),
        (reports / 'qa_report.csv', 'qa_report', ['snapshot_date','rule','affected_rows','action','rows_after','median_price_before','median_price_after']),
        (reports / 'eda_flags.csv', 'eda', ['snapshot_date','qa_flags','count']),
        (reports / 'evaluation.csv', 'evaluation', ['source','paired_n','manual_n','accuracy','macro_f1','meets_100_paired']),
        (processed / 'kpi_cohort.csv', 'cohort_summary', analysis.SUMMARY_FIELDS),
    ]
    outputs.extend([
        (processed / 'kpi_neighbourhood.csv', 'neighbourhood_kpi', ['snapshot_date', 'neighbourhood_cleansed', 'supply', 'median_price', 'price_n', 'currency', 'entire_home_share', 'multi_listing_host_share']),
        (reports / 'qa_missingness.csv', 'missingness', ['snapshot_date', 'column', 'column_present', 'rows', 'missing', 'missing_rate']),
        (reports / 'qa_kpi_impact.csv', 'kpi_impact', ['snapshot_date', 'kpi', 'before', 'after', 'delta']),
    ])
    if skip_llm:
        outputs = [entry for entry in outputs if entry[1] not in {'llm_reviews', 'guest_kpi', 'evaluation'}]
    return outputs
