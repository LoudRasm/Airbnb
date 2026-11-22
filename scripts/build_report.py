"""Build the report from verified pipeline outputs, with an optional supplement."""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from airbnb.io import load_config, rows
from airbnb import evaluate, llm, reviews

BLUE, ORANGE, GREY = '#28628e', '#bd581b', '#aab2b9'
LABELS = {'positive': 'Positive', 'mixed': 'Mixed', 'negative': 'Negative'}
ASPECTS = {'amenities': 'Tiện nghi', 'noise': 'Tiếng ồn', 'cleanliness': 'Vệ sinh', 'check-in': 'Nhận phòng',
           'host': 'Chủ nhà', 'value': 'Giá trị', 'safety': 'An toàn', 'location': 'Vị trí'}


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for part in iter(lambda: f.read(1024 * 1024), b''):
            h.update(part)
    return h.hexdigest()


def tex(text):
    substitutions = {'\\': r'\textbackslash{}', '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#', '_': r'\_', '{': r'\{', '}': r'\}'}
    return ''.join(substitutions.get(c, c) for c in str(text))


def number(value, places=0):
    q = Decimal('1').scaleb(-places)
    return f'{Decimal(str(value)).quantize(q, rounding=ROUND_HALF_UP):,.{places}f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


def read_table(path):
    return list(rows(path))


def configure_plots():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'axes.titlesize': 10,
                         'axes.labelsize': 9, 'axes.spines.top': False, 'axes.spines.right': False,
                         'axes.axisbelow': True, 'pdf.fonttype': 42, 'savefig.bbox': 'tight'})
    return plt


def save_figure(fig, folder, name, plt):
    fig.savefig(folder / f'{name}.pdf', bbox_inches='tight')
    fig.savefig(folder / f'{name}.png', dpi=220, bbox_inches='tight')
    plt.close(fig)


def city_review_stats(raw_path, output):
    """Count the full latest city file, not only the group's 5,000 review IDs."""
    fingerprint = digest(raw_path)
    if output.exists():
        cached = json.loads(output.read_text())
        if cached.get('raw_sha256') == fingerprint:
            return cached
    ids = set()
    char_n = 0
    duplicate_n = 0
    for record in rows(raw_path):
        rid = record.get('id', '').strip()
        if not rid or not reviews.is_digit_id(rid):
            raise ValueError('City review file contains an invalid review ID')
        if rid in ids:
            duplicate_n += 1
            continue
        ids.add(rid)
        char_n += len(reviews.clean_comment(record.get('comments', '')))
    result = {'snapshot': raw_path.parent.name, 'review_count': len(ids), 'duplicate_rows': duplicate_n,
              'total_cleaned_chars': char_n, 'mean_cleaned_chars': char_n / len(ids), 'raw_sha256': fingerprint}
    output.write_text(json.dumps(result, indent=2) + '\n')
    return result


def produce(config_path, skip_pipeline=False, no_download=False, compile_pdf=True, include_supplement=False):
    cfg, root = load_config(config_path)
    if root != ROOT:
        raise ValueError('The report template belongs to this repository; keep the config in its configs directory')
    if not skip_pipeline:
        from airbnb.pipeline import run
        run(config_path, no_download=no_download)
    source = root / cfg['paths']['processed'] / 'real'
    report_source = root / cfg['paths']['reports'] / 'real'
    metadata = json.loads((report_source / 'run_metadata.json').read_text())
    if metadata.get('demo') or metadata.get('llm_status') != 'validated_cache_only':
        raise ValueError('Report requires a successful full real-data cache-only pipeline run')
    cache_path = root / cfg['llm']['cache']
    label_path = root / cfg['paths']['manual_labels']
    if (metadata.get('config') != cfg or metadata.get('llm_cache_sha256') != digest(cache_path)
            or metadata.get('manual_labels_sha256') != digest(label_path)):
        raise ValueError('Config, cache or hand labels changed after pipeline; rerun before building the report')
    folder = root / 'reports/generated/report'
    figures = root / 'figures/report'
    folder.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    listing = read_table(source / 'listings.csv')
    prediction = read_table(source / 'llm_reviews.csv')
    review_list = read_table(source / 'reviews.csv')
    labels = read_table(label_path)
    baseline = read_table(source / 'baseline.csv')
    neighbourhood = read_table(source / 'kpi_neighbourhood.csv')
    market = read_table(source / 'kpi_market.csv')
    cal = read_table(source / 'kpi_calendar.csv')
    transitions = read_table(source / 'kpi_churn.csv')
    evaluation = {kind: evaluate.evaluate_detailed(data, labels, kind)
                  for kind, data in [('baseline', baseline), ('llm', prediction)]}
    if len(prediction) != len({r['review_id'] for r in prediction}) or len(labels) != 100:
        raise ValueError('Expected unique LLM review IDs and exactly 100 hand labels')
    # Re-validate source ID/text/model/prompt provenance, still without API access.
    from airbnb.loading import read_assignment
    assigned = read_assignment(cfg, root)
    validated = llm.analyze(review_list, cfg, root, assigned.llm_ids)
    if len(validated) != 1000 or {r['review_id'] for r in prediction} != assigned.llm_ids:
        raise ValueError('Expected exactly the 1,000 assigned LLM review IDs')
    for r in prediction:
        for column in ('positive_aspects', 'negative_aspects'):
            r[column] = json.loads(r[column])
    if {r['review_id']: r for r in prediction} != {r['review_id']: r for r in validated}:
        raise ValueError('Processed predictions differ from the validated cache; rerun the pipeline')
    final_snap = cfg.get('price_snapshot', cfg['snapshots'][-1])
    latest = [r for r in listing if r['snapshot_date'] == final_snap]
    price = [Decimal(r['price']) for r in latest if r['price']]
    from statistics import median
    median_price = median(price)
    sentiment = Counter(r['sentiment'] for r in prediction)
    aspects = Counter(a for r in prediction for a in set(r['negative_aspects']))
    positive_aspects = Counter(a for r in prediction for a in set(r['positive_aspects']))
    negative_mentions = sum(bool(r['negative_aspects']) for r in prediction)
    positive_with_negative = sum(r['sentiment'] == 'positive' and bool(r['negative_aspects']) for r in prediction)
    final_neigh = sorted([r for r in neighbourhood if r['snapshot_date'] == final_snap], key=lambda r: -int(r['supply']))
    assert sum(int(r['supply']) for r in final_neigh) == len(latest)
    final_market = sorted([r for r in market if r['snapshot_date'] == final_snap], key=lambda r: r['analysis_area'])
    # Numeric totals use integer exposure counts, not means of rounded regional rates.
    calendar_rows = read_table(source / 'calendar_summary.csv')
    temporal = []
    for snap in cfg['snapshots']:
        records = [r for r in calendar_rows if r['snapshot_date'] == snap]
        available = sum(int(r['available_days']) for r in records)
        observed = sum(int(r['observed_days']) for r in records)
        expected = sum(int(r['expected_days']) for r in records)
        temporal.append({'snapshot': snap, 'available': available, 'observed': observed, 'expected': expected,
                         'availability': available / observed if observed else None, 'coverage': observed / expected if expected else None})
    # This prose is a fixed study of the assigned data. Reject changed findings rather than
    # silently regenerate new figures under old narrative claims.
    expected_calendar = [(52643, 89800), (59507, 89440), (53470, 89281), (45724, 88628)]
    if (dict(sentiment) != {'positive': 936, 'mixed': 50, 'negative': 14}
            or median_price != Decimal('213.545')
            or evaluation['baseline']['summary']['accuracy'] != .95
            or evaluation['llm']['summary']['accuracy'] != .96
            or evaluation['llm']['confusion_matrix']['mixed']['positive'] != 4
            or [(r['available'], r['observed']) for r in temporal] != expected_calendar):
        raise ValueError('Findings changed: update and review the report narrative before publishing new PDFs')
    by_review = {r['review_id']: r for r in review_list}
    errors = {}
    for kind, result in evaluation.items():
        errors[kind] = [{**r, 'comments': by_review[r['review_id']]['comments']} for r in result['errors']]
    gold = {r['review_id']: r['sentiment'] for r in labels}
    p_llm, p_base = [{r['review_id']: r['sentiment'] for r in table} for table in (prediction, baseline)]
    paired = Counter((p_base[r] == g, p_llm[r] == g) for r, g in gold.items())
    city = city_review_stats(root / cfg['paths']['raw'] / final_snap / 'reviews.csv.gz', folder / 'city_review_stats.json')
    # Transparent character-based estimate; raw API usage/thinking tokens were not captured by the group's cache.
    output_chars = sum(len(json.dumps({k: r[k] for k in ['sentiment','language','positive_aspects','negative_aspects']}, ensure_ascii=False)) for r in prediction) / len(prediction)
    prompt_chars = len(llm.build_prompt('', cfg['llm']['aspects']))
    sample_mean = sum(len(reviews.clean_comment(by_review[r['review_id']]['comments'])) for r in prediction) / len(prediction)
    costs = []
    for name, n, mean_chars in [('Mẫu LLM', len(prediction), sample_mean), ('Toàn thành phố tại mốc cuối', city['review_count'], city['mean_cleaned_chars'])]:
        tokens_in = n * (prompt_chars + mean_chars) / 4
        tokens_out = n * output_chars / 4
        costs.append({'scope': name, 'n': n, 'input_tokens': round(tokens_in), 'output_tokens': round(tokens_out),
                      'estimated_usd': (tokens_in * .30 + tokens_out * 2.50) / 1_000_000})
    commit = subprocess.check_output(['git','rev-parse','HEAD'], cwd=root, text=True).strip()
    frozen_paths = [root / 'data/samples/manual_labels.csv', *sorted((root / 'data/samples/labeling').glob('*.json'))]
    result = {'source_commit': commit, 'generated_utc': datetime.now(timezone.utc).isoformat(),
              'pipeline_metadata_sha256': digest(report_source / 'run_metadata.json'), 'cache_sha256': digest(cache_path),
              'hand_label_hashes': {str(p.relative_to(root)): digest(p) for p in frozen_paths},
              'counts': {'listings':len(listing),'llm':len(prediction),'manual':len(labels),'reviews':len(review_list)},
              'median_price':str(median_price),'languages':dict(Counter(r['language'] for r in prediction)),'sentiment':dict(sentiment),'negative_aspects':dict(aspects),
              'positive_aspects':dict(positive_aspects),'negative_mention_reviews':negative_mentions,
              'positive_with_negative_aspects':positive_with_negative,'evaluation':evaluation,'error_texts':errors,
              'paired_correctness':{f'baseline_{a}_llm_{b}':n for (a,b),n in paired.items()},
              'calendar':temporal,'city_reviews':city,'cost_estimates':costs}
    (folder / 'report_metrics.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    plt = configure_plots()
    # Space: actual GeoJSON + cohort counts. Grey polygons mean outside the assigned cohort, not no Airbnb supply.
    import geopandas as gpd
    import pandas as pd
    from matplotlib.patches import Patch
    geo = gpd.read_file(root / cfg['paths']['raw'] / final_snap / 'neighbourhoods.geojson')
    frame = pd.DataFrame(final_neigh)
    frame['supply'] = frame['supply'].astype(int)
    geo = geo.merge(frame, left_on='neighbourhood', right_on='neighbourhood_cleansed', how='left')
    colors = ['#e5e7e9' if pd.isna(v) else '#c2d8e5' if v < 10 else '#6f9ebc' if v < 30 else BLUE for v in geo['supply']]
    fig, (ax, bar) = plt.subplots(1, 2, figsize=(10.2, 3.25), gridspec_kw={'width_ratios':[1,1.25]})
    geo.plot(color=colors, edgecolor='white', linewidth=.25, ax=ax)
    ax.set_axis_off(); ax.set_title('Phân bố 1.000 chỗ ở trong mẫu', loc='left', fontweight='bold')
    ax.legend(handles=[Patch(color=c, label=l) for c,l in [('#e5e7e9','Ngoài mẫu'),('#c2d8e5','1–9'),('#6f9ebc','10–29'),(BLUE,'Từ 30')]], fontsize=7,loc='lower left',frameon=False,ncol=2)
    top = final_neigh[:6]
    names = [r['neighbourhood_cleansed'].replace('Waterfront Communities-The Island','Waterfront Communities\n– The Island') for r in top]
    values = [int(r['supply']) for r in top]
    names += [f'{len(final_neigh)-6} khu vực còn lại']; values += [len(latest)-sum(values)]
    bars=bar.barh(range(len(names)), values, color=[ORANGE]+[BLUE]*5+[GREY])
    bar.set_yticks(range(len(names)), names, fontsize=8);bar.invert_yaxis();bar.set_xlim(0,max(values)*1.22)
    bar.set_xlabel('Số chỗ ở trong mẫu (n = 1.000)');bar.set_title('Waterfront chiếm 20,9% mẫu', loc='left',fontweight='bold')
    for rect, v in zip(bars,values):bar.text(v+5,rect.get_y()+rect.get_height()/2,f'{v} ({v/10:.1f}%)',va='center',fontsize=8)
    bar.grid(axis='x',alpha=.18);fig.tight_layout(w_pad=2);save_figure(fig,figures,'report_space',plt)
    # Price: 8 assigned rectangles; all show valid-price denominator explicitly.
    fig, ax = plt.subplots(figsize=(9,2.25))
    vals=[float(r['median_price']) for r in final_market]
    bars=ax.bar([r['analysis_area'] for r in final_market],vals,color=[ORANGE if v==max(vals) else BLUE for v in vals],width=.6)
    ax.axhline(float(median_price),color='#555555',ls='--',lw=1,label=f'Trung vị chung {number(median_price,2)} CAD')
    for rect,row,v in zip(bars,final_market,vals):ax.text(rect.get_x()+rect.get_width()/2,v+5,f'{number(v,2)}\nn={row["price_n"]}',ha='center',va='bottom',fontsize=7,bbox={'facecolor':'white','edgecolor':'none','pad':.25})
    ax.set_ylim(0,max(vals)*1.3);ax.set_ylabel('CAD/đêm');ax.set_title('Trung vị A05 cao gấp 2,56 lần A08',loc='left',fontweight='bold');ax.legend(frameon=False,fontsize=8);ax.grid(axis='y',alpha=.18)
    fig.tight_layout();save_figure(fig,figures,'report_price',plt)
    # Time: equal date spacing here encodes snapshots, never a continuous demand model.
    fig,(a,b)=plt.subplots(1,2,figsize=(10,2.8),gridspec_kw={'width_ratios':[1.25,1]})
    for area in sorted({r['analysis_area'] for r in cal}):
        series=sorted([r for r in cal if r['analysis_area']==area],key=lambda r:r['snapshot_date'])
        a.plot(range(len(series)),[float(r['availability_rate'])*100 for r in series],color=GREY,alpha=.65,lw=.8)
    a.plot(range(len(temporal)),[r['availability']*100 for r in temporal],color=BLUE,marker='o',lw=2,label='Toàn bộ mẫu')
    for i,r in enumerate(temporal):a.annotate(f'{number(r["availability"]*100,1)}%',(i,r['availability']*100),xytext=(0,8),textcoords='offset points',ha='center',fontsize=8)
    a.set_xticks(range(len(temporal)),cfg['snapshots'],fontsize=7);a.set_ylim(0,100);a.set_ylabel('Ngày sẵn có / ngày quan sát (%)');a.set_title('Lịch sẵn có giảm sau mốc tháng 12',loc='left',fontweight='bold');a.legend(frameon=False,fontsize=8);a.grid(axis='y',alpha=.2)
    changed=[int(r['host_changed']) for r in transitions];bar=b.bar(range(len(changed)),changed,color=[GREY,BLUE,ORANGE],width=.5)
    b.set_xticks(range(len(changed)),['09→12/2025','12/2025→03/2026','03→06/2026'],rotation=10,fontsize=7);b.set_ylim(0,max(changed)*1.4);b.set_ylabel('Số cặp đổi host_id / 1.000 cặp')
    b.set_title('Đổi host_id: 3 → 35 → 37 cặp',loc='left',fontweight='bold')
    b.bar_label(bar,labels=[f'{v}/1.000' for v in changed],padding=3,fontsize=8);b.grid(axis='y',alpha=.2)
    fig.tight_layout(w_pad=2.5);save_figure(fig,figures,'report_time',plt)
    # LLM: 1,000 predictions; multi-label aspect rates are not a partition of sentiment rates.
    fig,(a,b)=plt.subplots(1,2,figsize=(10,2.9),gridspec_kw={'width_ratios':[1,1.3]})
    classes=list(evaluate.CLASS_ORDER)
    bars=a.barh([LABELS[c] for c in classes],[sentiment[c]/len(prediction)*100 for c in classes],color=[BLUE,ORANGE,'#713528'])
    a.invert_yaxis();a.set_xlim(0,110);a.set_xlabel('% trong 1.000 review');a.set_title('64/1.000 review là mixed hoặc negative',loc='left',fontweight='bold')
    a.bar_label(bars,labels=[f'{sentiment[c]} ({number(sentiment[c]/10,1)}%)' for c in classes],padding=3,fontsize=8)
    order=sorted(cfg['llm']['aspects'],key=lambda k:-aspects[k]);vals=[aspects[c] for c in order]
    bars=b.barh([ASPECTS[c] for c in order],vals,color=[ORANGE if i==0 else BLUE for i in range(len(order))]);b.invert_yaxis();b.set_xlim(0,max(vals)*1.25);b.set_xlabel('Review nhắc khía cạnh chê / 1.000 review')
    b.set_title('Tiện nghi dẫn đầu các khía cạnh bị chê',loc='left',fontweight='bold');b.bar_label(bars,labels=[f'{v} ({number(v/10,1)}%)' for v in vals],padding=3,fontsize=8)
    a.grid(axis='x',alpha=.18);b.grid(axis='x',alpha=.18);fig.tight_layout(w_pad=2.5);save_figure(fig,figures,'report_reviews',plt)
    # Confusion matrices share a linear scale; cells display counts to make minority errors visible.
    fig,axes=plt.subplots(1,2,figsize=(8,2.6))
    for ax,kind,title in zip(axes,['baseline','llm'],['Baseline: 95/100 đúng','Gemini: 96/100 đúng']):
        matrix=[[evaluation[kind]['confusion_matrix'][g][p] for p in classes] for g in classes]
        ax.imshow(matrix,cmap='Blues',vmin=0,vmax=90)
        for i,row in enumerate(matrix):
            for j,n in enumerate(row):ax.text(j,i,str(n),ha='center',va='center',color='white' if n>45 else '#111111',fontweight='bold')
        ax.set_xticks(range(3),[LABELS[c] for c in classes],fontsize=8);ax.set_yticks(range(3),[LABELS[c] for c in classes],fontsize=8)
        ax.set_xlabel('Dự đoán');ax.set_ylabel('Nhãn tay');ax.set_title(title,loc='left',fontweight='bold');ax.spines[['top','right','left','bottom']].set_visible(False)
    fig.tight_layout(w_pad=2);save_figure(fig,figures,'report_confusion',plt)
    # Generated LaTeX values/tables eliminate hand-copied numbers from the report.
    macros={'SourceCommit':commit[:12],'SourceCommitFull':commit,'GlobalMedian':number(median_price,2),
            'ValidPrices':number(len(price)),'LLMIssueCount':str(sentiment['mixed']+sentiment['negative']),
            'LLMIssuePct':number((sentiment['mixed']+sentiment['negative'])/len(prediction)*100,1),
            'CacheShortHash':digest(cache_path)[:16], 'CityReviewCount':number(city['review_count']),
            'CityCost':number(costs[1]['estimated_usd'],2),'SampleCost':number(costs[0]['estimated_usd'],3),
            'CityInputTokens':number(costs[1]['input_tokens']),'CityOutputTokens':number(costs[1]['output_tokens']),
            'SampleInputTokens':number(costs[0]['input_tokens']),'SampleOutputTokens':number(costs[0]['output_tokens'])}
    (folder/'values.tex').write_text(''.join('\\newcommand{\\'+k+'}{'+tex(v)+'}\n' for k,v in macros.items()))
    def table(name, records):
        slash, newline = chr(92), chr(10)
        lines = [' & '.join(str(v).replace(slash * 2 + '%', slash + '%') for v in r) + slash * 2
                 for r in records]
        (folder/name).write_text(newline.join(lines) + newline + slash + 'bottomrule' + newline,
                                 encoding='utf-8')
    table('area_rows.tex',[(r['analysis_area'],r['supply'],r['price_n'],number(r['median_price'],2),number(float(r['entire_home_share'])*100,1)+r'\%',number(float(r['multi_listing_host_share'])*100,1)+r'\%') for r in final_market])
    table('calendar_rows.tex',[(r['snapshot'],number(r['available']),number(r['observed']),number(r['coverage']*100,2)+r'\%',number(r['availability']*100,2)+r'\%') for r in temporal])
    table('evaluation_rows.tex',[('Gemini' if name=='llm' else 'Baseline',number(r['summary']['accuracy']*100,1)+r'\%',number(r['summary']['macro_f1'],4),r['summary']['paired_n']) for name,r in evaluation.items()])
    table('class_rows.tex',[('Gemini' if kind=='llm' else 'Baseline',LABELS[c],r['support'],number(r['precision'],3),number(r['recall'],3),number(r['f1'],3)) for kind,data in evaluation.items() for c,r in data['per_class'].items()])
    table('area_guest_rows.tex',[(r['scope'].split(':')[-1],r['sample_n'],number(float(r['value'])*100,2)+r'\%') for r in read_table(source/'kpi_guest.csv') if r['metric']=='area_guest_issue_rate'])
    checks=read_table(root/'reports/checks/check_DSE2049-C01-G10-toronto.csv')
    table('data_rows.tex',[(r['ngay'],number(r['listings_dong']),number(r['calendar_dong']),number(r['reviews_dong']),r['so_cot_listings'],r['so_cot_nan_90'],number(r['thieu_price'])) for r in checks])
    table('cost_rows.tex',[(tex(r['scope']),number(r['n']),number(r['input_tokens']),number(r['output_tokens']),number(r['estimated_usd'],3)) for r in costs])
    missing=read_table(root/'reports/checks/missing_columns.csv'); grouped=defaultdict(list)
    for row in missing:grouped[row['ngay']].append(row['column'])
    (folder/'missing_columns.tex').write_text('\n'.join('\\paragraph{'+snap+'} '+', '.join(r'\path{'+c+'}' for c in names)+'.' for snap,names in grouped.items()))
    # Keep all actual errors machine-readable; the main report only discusses selected short examples.
    from airbnb.io import write_csv
    write_csv(folder/'classification_errors.csv',[{'model':kind,**r} for kind,data in errors.items() for r in data],['model','review_id','gold','predicted','comments'])
    table('error_rows.tex',[(kind,r['review_id'],r['gold'],r['predicted']) for kind,data in errors.items() for r in data])
    # Reuse short exact source excerpts, keeping implementation detail in the supplement.
    snippets={'filter_ids':('src/airbnb/loading.py','    assigned_ids =','        if name =='),
              'cache_guard':('src/airbnb/llm.py','    if not allow_api:', '    results = []'),
              'calendar_exposure':('src/airbnb/calendar.py','    counts: dict','    for row in records:'),
              'review_join':('src/airbnb/pipeline.py','        # Join source','        selected ='),
              'evaluation':('src/airbnb/evaluate.py','    for cls in CLASS_ORDER:', '    macro_f1 =')}
    for name,(path,start,end) in snippets.items():
        content=(root/path).read_text();a=content.index(start);b=content.index(end,a)
        (folder/f'{name}.py').write_text(content[a:b])
    artifact_hashes={str(p.relative_to(root)):digest(p) for p in sorted(figures.glob('*')) if p.suffix in {'.pdf','.png'}}
    (folder/'figure_provenance.json').write_text(json.dumps({'source_commit':commit,'pipeline_metadata_sha256':digest(report_source/'run_metadata.json'),'artifacts':artifact_hashes},indent=2)+'\n')
    print(f'Report assets verified: {len(prediction)} LLM reviews, {len(labels)} labels, city reviews {city["review_count"]}',flush=True)
    if compile_pdf:
        engine=shutil.which('xelatex') or ('/Library/TeX/texbin/xelatex' if Path('/Library/TeX/texbin/xelatex').exists() else None)
        if not engine:raise RuntimeError('Install XeLaTeX/TeX Live or compile the report source on Overleaf with XeLaTeX')
        build=folder/'latex';build.mkdir(exist_ok=True)
        documents = {'Nhom10_InsideAirbnb_Report': root / 'reports'}
        if include_supplement:
            documents['Nhom10_InsideAirbnb_Supplement'] = folder
        for stem, destination in documents.items():
            for attempt in range(2):
                completed=subprocess.run([engine,'-interaction=nonstopmode','-halt-on-error',f'-output-directory={build}',f'{stem}.tex'],cwd=root/'reports',stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
                (build/f'{stem}.console.log').write_text(completed.stdout)
                if completed.returncode:raise RuntimeError(f'XeLaTeX failed; see {build / (stem+".console.log")}')
            shutil.move(build/f'{stem}.pdf', destination/f'{stem}.pdf')
    return result


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config',default=str(ROOT/'configs/toronto.yaml'))
    p.add_argument('--no-download',action='store_true')
    p.add_argument('--skip-pipeline',action='store_true',help='Reuse a verified full real run whose cache hash still matches')
    p.add_argument('--assets-only',action='store_true',help='Generate CSV/figure/LaTeX assets without requiring XeLaTeX')
    p.add_argument('--supplement', action='store_true', help='Also build the supplement under reports/generated/report')
    args=p.parse_args(argv)
    if args.assets_only and args.supplement:
        p.error('--supplement requires PDF compilation')
    produce(args.config, args.skip_pipeline, args.no_download, not args.assets_only, args.supplement)


if __name__=='__main__':
    main()
