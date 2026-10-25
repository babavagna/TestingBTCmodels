"""Export executed multi-asset evidence to sortable, formula-safe Excel/CSV."""
import json,math
from collections import Counter
from pathlib import Path
import numpy as np
import pandas as pd
import xlsxwriter
import xml.etree.ElementTree as ET
from btc_lab.data import sha256,write_json
from full_universe.audit import catalog as source_catalog
from indicator_lab.features import catalog as indicator_catalog
from multiasset.registry import ROOT,assets
from multiasset_report import build,read_json,case_status,case_records,run_directory,current_record
from directional_study.metrics import interval

OUT=ROOT/'reports/multiasset'


def source_inventory():
    rows=[]
    for r in source_catalog():rows.append(dict(candidate_id='SOURCE:'+r['id'],name=r['name'],framework=r['framework'],source_url=r['source_url'],license=r.get('license'),source_path=r.get('source_path'),source_sha256=r.get('source_sha256'),scope='Published signal hooks or documented Jesse translation; native risk management omitted'))
    for r in indicator_catalog():rows.append(dict(candidate_id='INDICATOR:'+r['id'],name=r['name'],framework=r.get('family'),source_url=r['github_url'],license='Retained upstream license; see sources/indicator_provenance.json',scope='Pinned formula + binary logistic readout; not native TradingView parity'))
    return rows


def probability_tables(report):
    rows=[];classes=[];bins=[];thresholds=[]
    for summary in report['summary']:
        for basis in ['trades','quotes']:
            status=case_status(ROOT,summary['asset'],summary['timeframe_minutes'],basis);directory=run_directory(status)
            if not directory:continue
            for model in read_json(directory/'probabilities.json',[]) or []:
                for period in ['validation','retrospective_test']:
                    block=model.get('periods',{}).get(period,{});metrics=block.get('calibrated',{});baseline=block.get('training_frequency_baseline',{})
                    n=metrics.get('observations',0);ci=interval(round(n*metrics['accuracy']),n) if metrics.get('accuracy') is not None else (None,None)
                    p=model.get('historical_snapshot_probabilities') or [None]*3
                    row=dict(asset=summary['asset'],contract=summary['contract'],minutes=summary['timeframe_minutes'],price_basis=basis,threshold=model['threshold'],period=period,status=model['status'],reason=model.get('reason') or model.get('calibration_error'),observations=n,accuracy=metrics.get('accuracy'),balanced_accuracy=metrics.get('balanced_accuracy'),baseline_accuracy=baseline.get('accuracy'),accuracy_ci_low=ci[0],accuracy_ci_high=ci[1],brier=metrics.get('brier'),log_loss=metrics.get('log_loss'),calibration_error=metrics.get('ece'),too_few_forecasts=n<1000,current_status=model.get('current_status'),current_down=None,current_stay=None,current_up=None,historical_down=p[0],historical_stay=p[1],historical_up=p[2],predicted_historical_direction=['DOWN','STAY SIMILAR','UP'][int(np.argmax(p))] if p[0] is not None else None,last_price_as_of=model.get('last_price_as_of'),last_successful_model_update=model.get('last_successful_model_update'),training_end=model.get('training_end'),calibration_end=model.get('calibration_end'),score_start=model.get('dates',{}).get(period,{}).get('start'),score_stop=model.get('dates',{}).get(period,{}).get('stop'),untouched_test=False)
                    # Current values come only from a fresh, calibrated separate buffer.
                    current=current_record(status)
                    if current.get('status')=='CURRENT' and model['threshold']==.001:
                        age=(pd.Timestamp.now(tz='UTC')-pd.Timestamp(current['as_of'])).total_seconds()
                        if 0<=age<=max(summary['timeframe_minutes']*120,600):row.update(current_status='CURRENT',current_down=current['probabilities'][0],current_stay=current['probabilities'][1],current_up=current['probabilities'][2])
                    thresholds.append(row)
                    if model['threshold']==.001:
                        rows.append(row)
                        for cls in metrics.get('classes',[]):classes.append(dict(asset=row['asset'],minutes=row['minutes'],price_basis=basis,period=period,**cls))
                        for b in metrics.get('reliability_bins',[]):bins.append(dict(asset=row['asset'],minutes=row['minutes'],price_basis=basis,period=period,**b))
    return rows,classes,bins,thresholds


DEFINITIONS=[
 ('Scope','39 Kalshi contracts: 28 requested names plus 11 discovered in the original dashboard. 247 candidate implementations = 100 source strategies + 147 indicator readouts. These are not 247 independent ideas.'),
 ('Primary prices','Only actual Kalshi per-contract observations support primary results. Binance observations are supplementary; never a substitute for Kalshi contract prices.'),
 ('Dates','Target January 2020–September 2026. Retrieved primary histories begin in 2026. Earlier years do not exist in these retrieved contract histories. Exact dates and missing data are listed per contract.'),
 ('Short history','512 observed bars warm up indicators. Remaining valid targets: first 50% fit, next 10% choose parameters, next 15% calibrate probabilities, next 10% validation, last 15% retrospective test. Answers crossing earlier boundaries are purged.'),
 ('Test honesty','All historical 2026 comparisons are retrospective, not a new untouched experiment. No fully validated financial top 10 exists. Missing funding, financing, rollover, liquidation and historical session/specification data prevent that claim.'),
 ('Trading costs','10,000 USD; 0.10% fee plus 0.05% slippage on EVERY side. Whole-contract sizing when required by metadata. Unleveraged long/cash signal projection; original bot risk rules are not reproduced.'),
 ('Quote-only inputs','Observed bid/ask midpoint closes are marked separately. They support only formulas that need closes. No artificial open/high/low/volume is created and no financial backtest is run on quote-only data.'),
 ('Net return','How much the starting money changed after modeled fees/slippage. +20% turns 100 into 120. Missing derivative costs can change this result.'),
 ('Sharpe','Average daily gain compared with how bumpy daily gains are, scaled to one year (365 crypto, 252 other markets). A high value from a short sample can be misleading.'),
 ('Sortino','Like Sharpe, but counts only downward bumps as risk. N/A when there are no downward observations to divide by.'),
 ('Maximum drawdown','Largest fall from an earlier account high. A 30% drawdown means 100 fell to 70. Only observed candle closes are measured.'),
 ('Profit factor','Money from winning trades divided by money lost on losing trades. Above 1 means gains outweighed losses. N/A if there are no losing-trade dollars.'),
 ('Trade win rate','Share of completed buy/sell pairs that made money after costs. A big loss can outweigh many small wins. Fewer than 30 trades is flagged.'),
 ('Buy and hold','Buy once and sell at the same scoring end, with the same costs and whole-contract sizing. This is the comparison yardstick.'),
 ('Directional accuracy','Correct next-candle UP/DOWN forecasts divided by forecasts scored. Exact flat closes are excluded in binary scores. Trading entries/exits are not forecasts; their accuracy is N/A.'),
 ('UP/DOWN precision','UP precision: among UP guesses, how many were right? DOWN precision: among DOWN guesses, how many were right? Separate numeric columns let you sort each.'),
 ('Recall','Of all actual UP moves, how many did the model find? DOWN recall asks the same question for falls. Precision and recall have different denominators.'),
 ('STAY SIMILAR','Three-class model uses next-close movement within −0.10% to +0.10%. Threshold sensitivity repeats ±0.05% and ±0.20%. A quiet market can make always guessing STAY appear accurate; compare the baseline and balanced accuracy.'),
 ('Baseline','The most frequent class in training predicts every held-out candle. Compare on the same eligible rows. High raw accuracy alone does not establish useful prediction.'),
 ('Confidence interval','An uncertainty range around a measured percentage. Wilson ranges are descriptive: nearby candles can be correlated, and trying many models creates lucky winners.'),
 ('Brier/log loss','Scores for probability quality; smaller is better. Log loss strongly penalizes confident wrong predictions. Three-class Brier sums squared errors across all three classes.'),
 ('Calibration','A model that says 60% should succeed about 60 times out of 100 similar cases. Temperature is fitted only on a separate earlier calibration segment. Calibration is not guaranteed in later markets.'),
 ('Joint outcomes','When selected indicators agree, count what actually happened after their joint historical configuration. Do not multiply individual accuracy percentages or treat correlated indicators as independent votes.'),
 ('Freshness','September historical snapshots are not current in October. Current probability cells remain N/A until a separate recent buffer is retrieved and a fresh calibrated model output is checked.'),
 ('Walk forward','Repeatedly learn on earlier observations, then score later ones. Small folds can fail for lack of history; failures remain visible.'),
 ('Sensitivity','Fixed parameter neighbors are selected before held-out scoring. Fee stresses halve/double fees and double fees plus slippage. Parameter selection records and earlier-fold results are retained.'),
 ('Cheating checks','Past-prefix and future-mutation checks look for later prices changing earlier signals. Known leaking original sources remain quarantined. Finite checks cannot prove the absence of every possible bias.'),
 ('Duplicates','Exact sampled training signal duplicates and very high correlations are recorded. Repeated signals are not counted as independent evidence.'),
 ('N/A','Missing, undefined, insufficient or unverified. N/A is never silently converted to a real zero.'),
 ('Workbook access','GitHub does not preview Excel. Open the workbook page, choose Download raw file, then open the downloaded .xlsx in Excel or LibreOffice. Do not save a GitHub HTML page with an Excel extension.'),
 ('Original dashboard','This repository adds tabs to its existing Streamlit lab. The separate hosted Perpetual Edge Site project was inspected read-only; it was not deployed or modified by this task.'),
]


def write_workbook(path,tables,report):
    temp=path.with_suffix('.building.xlsx')
    book=xlsxwriter.Workbook(temp,{'strings_to_formulas':False,'strings_to_urls':False,'nan_inf_to_errors':False})
    title=book.add_format({'bold':True,'font_size':15,'font_color':'#153b55'})
    warning=book.add_format({'text_wrap':True,'font_color':'#8b260c'})
    percent=book.add_format({'num_format':'0.00%'});number=book.add_format({'num_format':'0.000'});integer=book.add_format({'num_format':'0'})
    rates={'net_return','max_drawdown','win_rate','buy_hold_return','excess_vs_buy_hold','directional_accuracy','accuracy','balanced_accuracy','baseline_accuracy','training_majority_baseline_accuracy','up_precision','up_recall','down_precision','down_recall','fee','slippage','fee_per_side','slippage_per_side','threshold','return_value','brier','ece','calibration_error','accuracy_ci_low','accuracy_ci_high','historical_down','historical_stay','historical_up','current_down','current_stay','current_up','precision','recall','mean_confidence','up_precision_ci_low','up_precision_ci_high','down_precision_ci_low','down_precision_ci_high','lift_block_ci_low','lift_block_ci_high','accuracy_lift_vs_train_majority'}
    for name,rows in tables.items():
        sheet=book.add_worksheet(name);sheet.write(0,0,name,title);sheet.merge_range(1,0,2,7,'Retrospective research. Funding/financing/rollover unverified; no fully validated financial ranking. N/A means missing or undefined.',warning);sheet.set_row(1,28)
        if not rows:sheet.write(4,0,'No eligible results. See Coverage, Failed Tests and Read Me.');continue
        columns=list(dict.fromkeys(k for row in rows for k in row))
        data=[]
        for row in rows:
            values=[]
            for key in columns:
                value=row.get(key)
                if isinstance(value,(dict,list,tuple)):value=json.dumps(value,sort_keys=True,ensure_ascii=False)
                if value is None or isinstance(value,float) and not math.isfinite(value):value='N/A'
                if isinstance(value,str) and len(value)>32767:value=value[:32720]+' [Full content retained in JSON]'
                values.append(value)
            data.append(values)
        defs=[]
        for j,key in enumerate(columns):
            fmt=number if key in ['sharpe','sortino','profit_factor','log_loss','brier'] else percent if key in rates else None
            defs.append({'header':key,'format':fmt} if fmt else {'header':key})
            sheet.set_column(j,j,22 if key not in ['reason','explanation','source_url','source_error'] else 65)
        result=sheet.add_table(4,0,4+len(data),len(columns)-1,{'data':data,'columns':defs,'style':'Table Style Medium 2','name':'ResearchTable'+str(len(book.worksheets()))})
        if result!=0:raise RuntimeError('Excel table could not be written: '+name)
        sheet.freeze_panes(5,2)
        for j,key in enumerate(columns):
            if key in ['net_return','directional_accuracy','accuracy']:sheet.conditional_format(5,j,4+len(data),j,{'type':'3_color_scale'})
    chart_sheet=book.add_worksheet('Charts');chart_sheet.write(0,0,'Actual saved retrospective equity curves; funding omitted',title)
    location=3;chart_count=0
    for spec in assets():
        for minutes in [5,15,60]:
            status=case_status(ROOT,spec['id'],minutes,'trades');records=[r for r in case_records(status) if r.get('executed') and r.get('periods',{}).get('retrospective_test',{}).get('curve')]
            if not records:continue
            # Alphabetical comparison, not a selection of historical winners.
            records=sorted(records,key=lambda r:r['name'].lower())[:3];dates=records[0]['periods']['retrospective_test']['curve']['date']
            chart_sheet.write_row(location,0,['UTC date']+[r['name'] for r in records]);chart_sheet.write_column(location+1,0,dates)
            chart=book.add_chart({'type':'line'})
            for col,r in enumerate(records,1):
                values=r['periods']['retrospective_test']['curve']['equity'];chart_sheet.write_column(location+1,col,values)
                chart.add_series({'name':['Charts',location,col],'categories':['Charts',location+1,0,location+len(dates),0],'values':['Charts',location+1,col,location+len(values),col]})
            chart.set_title({'name':f'{spec["id"]} {minutes}m · first 3 alphabetically'});chart.set_y_axis({'name':'USD, fees/slippage only'});chart_sheet.insert_chart(location,6,chart);location+=max(18,len(dates)+3);chart_count+=1
    if not chart_count:chart_sheet.write(3,0,'No completed traded-price equity curves are available.')
    book.close();temp.replace(path)


def export():
    report=build();OUT.mkdir(parents=True,exist_ok=True)
    audit=read_json(OUT/'audit.json',{}) or {}
    evidence={(r['asset'],r['minutes'],r['basis'],r['candidate_id'],r['period']):r for r in audit.get('paired_prediction_evidence',[])}
    for row in report['results']:
        e=evidence.get((row['asset'],row['timeframe_minutes'],row['price_basis'],row['candidate_id'],row['period']))
        if e:
            for key in ['accuracy_lift_vs_train_majority','lift_block_ci_low','lift_block_ci_high','daily_hac_se','pvalue','independent_day_blocks','holm_adjusted_pvalue_global','multiplicity_family_size','limited_chronological_gate','independent_untouched_validation']:row[key]=e[key]
    probabilities,classes,bins,thresholds=probability_tables(report)
    executed_ids={r['candidate_id'] for r in report['results'] if r['executed']}
    report['counts']=dict(asset_timeframes=117,candidate_case_records=sum(r['attempted_trade_methods']+r['attempted_quote_methods'] for r in report['summary']),completed_trade_replays=sum(r['completed_trade_methods'] for r in report['summary']),completed_quote_forecasters=sum(r['completed_quote_forecasters'] for r in report['summary']),unique_executed_source_strategies=sum(x.startswith('SOURCE:') for x in executed_ids),unique_executed_indicator_readouts=sum(x.startswith('INDICATOR:') for x in executed_ids),fully_validated_financial_strategies=0,failed_or_blocked_candidates=len(report['failures']),calibrated_main_models=sum(m['status']=='FITTED_AND_CALIBRATED' for m in report['probability_models']))
    secondary=[]
    for p in sorted((ROOT/'data/multiasset').glob('*/manifest.json')):
        m=read_json(p,{}) or {}
        for d in m.get('datasets',[]):secondary.append(dict(asset=p.parent.name,provider=m['asset']['provider'],price_role='SUPPLEMENTARY_ONLY_NOT_KALSHI',**d))
    completed=[r for r in report['results'] if r['executed']]
    tables={'Read Me':[dict(term=k,explanation=v) for k,v in DEFINITIONS],'Coverage':report['summary'],'All Strategies':completed,'Top 10':[dict(status='NO FULLY VALIDATED FINANCIAL RANKS',reason='Missing verified derivative costs and independent test evidence. Sortable exploratory results are in All Strategies; no historical winner is promoted as validated.')],'Prediction Accuracy':[r for r in completed if r['directional_accuracy'] is not None],'Three Outcome Models':probabilities,'Class Precision Recall':classes,'Calibration Bins':bins,'Stay Sensitivity':thresholds,'Walk Forward':report['walk_forward'],'Fee Parameter Sensitivity':report['robustness'],'Monthly':report['monthly'],'Annual':report['annual'],'Data Sources':report['data_sources'],'Contract Specs':assets(),'Source Catalog':source_inventory(),'Failed Tests':report['failures'],'Signal Correlations':report['correlations'],'Supplementary Data':secondary}
    tables.update({'Data Integrity':audit.get('data_integrity',[]),'Paired Accuracy Evidence':audit.get('paired_prediction_evidence',[]),'Causality Checks':audit.get('causality_checks',[]),'Parameter Selection':audit.get('parameter_selection',[])})
    test_path=OUT/'test-results.xml'
    if test_path.exists():
        suite=ET.parse(test_path).getroot();suites=[suite] if suite.tag=='testsuite' else list(suite.findall('testsuite'))
        tables['Software Tests']=[dict(status='EXECUTED',**{key:sum(int(s.get(key,0)) for s in suites) for key in ['tests','failures','errors','skipped']},evidence='reports/multiasset/test-results.xml',command='.venv/bin/python -m pytest -q tests test_live_signal_server.py --junitxml=reports/multiasset/test-results.xml')]
    else:tables['Software Tests']=[dict(status='NO_SAVED_FULL_SUITE_LOG_YET',reason='No software test pass is invented. Earlier focused tests have separate logs.')]
    for key,file in [('summary','coverage'),('results','primary_results'),('failures','failed_tests'),('monthly','monthly'),('annual','annual'),('robustness','robustness'),('walk_forward','walk_forward'),('correlations','signal_correlations')]:
        data=report[key];frame=pd.DataFrame(data)
        for c in frame:
            if frame[c].map(lambda v:isinstance(v,(dict,list))).any():frame[c]=frame[c].map(lambda v:json.dumps(v,sort_keys=True) if isinstance(v,(dict,list)) else v)
        temp=OUT/(file+'.tmp.csv');frame.to_csv(temp,index=False);temp.replace(OUT/(file+'.csv'))
    pd.DataFrame(probabilities).to_csv(OUT/'probability_models.csv',index=False)
    # Detailed rows already live in CSV and immutable per-case JSON. Keep the
    # dashboard summary small enough for GitHub as the universe expands.
    compact={key:report[key] for key in ['updated_at','primary_venue','named_assets','discovered_contracts','summary','counts','limitations','fully_validated_financial_ranking']}
    compact['detailed_files']={'results':'primary_results.csv','probabilities':'probability_models.csv','failures':'failed_tests.csv','audit':'audit.json','cases':'primary/'}
    write_json(OUT/'summary.json',compact)
    path=ROOT/'KALSHI_MULTI_ASSET_RESEARCH.xlsx';write_workbook(path,tables,report)
    manifest=dict(created_at=report['updated_at'],workbook=str(path.relative_to(ROOT)),workbook_sha256=sha256(path.read_bytes()),report_sha256=sha256((OUT/'summary.json').read_bytes()),sheet_rows={k:len(v) for k,v in tables.items()},counts=report['counts'],charts='Alphabetical strategy comparisons from actual saved account curves',fully_validated_ranks=0)
    write_json(OUT/'workbook_manifest.json',manifest)
    lines=['# Kalshi multi-asset research','',f'Generated {report["updated_at"]}. These are executed retrospective studies, not independently validated live trading models.','',json.dumps(report['counts'],indent=2),'','The requested 28 names expand to 39 actual Kalshi contracts after inspecting the original dashboard. The asset headings in the request had inconsistent category counts; the named assets and the additional original contracts are preserved.','', 'Kalshi per-contract prices are primary. Binance data is supplementary. Derivative funding/financing, rollover, historical liquidation rules and historical session/specification changes are unverified, so **there is no fully validated financial winner or top 10**.','', 'Trade replays project published entries/exits into unleveraged long/cash decisions. They do not reproduce native stops, targets, shorts or leverage. Bid/ask midpoint close-only models are listed separately and never receive a trading return.','', 'Target dates are January 2020 through September 2026. Actual retrieved Kalshi contract observations start in 2026. Short histories use chronological fit, selection, calibration, validation and retrospective-test stages; no unavailable older prices are invented. All exact scoring dates appear in the CSV and workbook.','', 'September model snapshots are historical in October. No current probability is claimed without a fresh separate inference buffer. Individual binary accuracy excludes exact flats; the three-class model includes a STAY band of ±0.10%.','', '## All assets and chart timeframes','', '| Asset | Chart | Traded bars | Quote closes | Completed trade methods | Completed quote models | Source status |','|---|---:|---:|---:|---:|---:|---|']
    for r in report['summary']:lines.append(f"| {r['asset']} | {r['timeframe_minutes']}m | {r['trade_candles']} | {r['quote_closes']} | {r['completed_trade_methods']} | {r['completed_quote_forecasters']} | {r['source_status']} |")
    lines+=['','Exact source failures, missing fields, insufficient sample sizes and quarantined code appear in `coverage.csv`, `failed_tests.csv`, the workbook and the per-case JSON checkpoints. Failed cases have no invented metrics.','', '## Actual three-outcome prediction results','', 'The following are held-out chronological retrospective scores of the calibrated ±0.10% STAY models. They are separate from binary indicator accuracy and trade win rate. Price bases are never pooled. Snapshot probabilities are historical, not current.','', '| Asset | Chart | Price basis | Forecasts | Accuracy | Training-majority baseline | Balanced accuracy | Historical DOWN / STAY / UP |','|---|---:|---|---:|---:|---:|---:|---|']
    def show(value):return 'N/A' if value is None else f'{value:.2%}'
    for p in probabilities:
        if p['period']=='retrospective_test' and p['status']=='FITTED_AND_CALIBRATED':lines.append(f"| {p['asset']} | {p['minutes']}m | {p['price_basis']} | {p['observations']} | {show(p['accuracy'])} | {show(p['baseline_accuracy'])} | {show(p['balanced_accuracy'])} | {show(p['historical_down'])} / {show(p['historical_stay'])} / {show(p['historical_up'])} |")
    lines+=['', 'These are model/asset/timeframe tests, not a claim of thousands of independent strategies. Trying many methods can find lucky percentages. The paired-evidence sheets include day-block uncertainty and a global Holm multiple-comparison adjustment. Short validation periods do not support a validated prediction winner.','', 'Order-book depth, partial fills and execution price rounding to the tick are not reproduced. Available whole-contract sizes are respected. Funding, financing, liquidation and historical contract changes remain missing; reported returns are explicitly limited to fees/slippage.','', '## Access and reproduce','', '- Open the repository dashboard with `bash run_dashboard.sh`; choose the Multi-asset timeframe and the contract tab. Existing BTC studies remain available below.','- Download `KALSHI_MULTI_ASSET_RESEARCH.xlsx` with GitHub’s **Download raw file** button; GitHub itself does not preview workbooks.','- Resume collection: `.venv/bin/python -m multiasset.kalshi --workers 3 --max-windows 240`.','- Resume research: `OPENBLAS_NUM_THREADS=1 .venv/bin/python -m multiasset.pipeline --workers 4`.','- Refresh separate current buffers: `.venv/bin/python -m scripts.refresh_kalshi_current`.','- Audit executed results: `.venv/bin/python -m scripts.audit_multiasset_results`.','- Export actual checkpoints: `.venv/bin/python -m scripts.export_multiasset`.','- Software tests: `.venv/bin/python -m pytest -q tests test_live_signal_server.py`.','', 'The existing separate Perpetual Edge public Site was inspected read-only. New tabs belong to this repository’s Streamlit dashboard; no external Site deployment is claimed.','', '## Metrics in plain language','']
    for term,explanation in DEFINITIONS[6:]:lines.append(f'**{term}:** {explanation}\n')
    (OUT/'REPORT.md').write_text('\n'.join(lines).rstrip()+'\n')
    print(json.dumps(manifest,indent=2))
    return manifest

if __name__=='__main__':export()
