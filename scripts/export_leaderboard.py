"""Build a real, auditable Excel workbook from completed, verified research outputs.

This exporter never runs or invents a strategy and never turns a previously seen
holdout into an untouched leaderboard. All numeric results come from saved runs.
"""
import argparse
import json
import math
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import xlsxwriter

from btc_lab.data import DataError, load_verified, sha256, write_json
from btc_lab.robustness import read_audit
from btc_lab.runner import read_current_report
from btc_lab.strategies import ROOT, load_catalog

REPO_URL = 'https://github.com/babavagna/TestingBTCmodels'
SOURCE_URL = 'https://github.com/binance/binance-public-data'
MISSING = 'N/A — not provided or undefined in the saved run'
EXPOSURE = 'Previously inspected; not a genuinely untouched test'
ADAPTATION = 'Hourly long/cash signal adaptation; native bot ROI targets and stoploss omitted'
SHEET_NAMES = ['Read Me', 'All Strategies', 'Top 10', 'Prediction Accuracy', 'Charts',
               'Failed Tests', 'Walk Forward', 'Sensitivity', 'Training Fits', 'Data Sources', 'Chart Data']


def junit_summary(path):
    tree = ET.parse(path)
    cases = list(tree.getroot().iter('testcase'))
    failures = []
    for case in cases:
        for tag in ('failure', 'error'):
            for item in case.findall(tag):
                failures.append(dict(category='Software test', strategy='N/A — software check', period='pytest', status='FAIL',
                                     check=case.attrib.get('classname', '')+'.'+case.attrib.get('name', ''), observed=tag,
                                     required='Test passes', explanation=item.attrib.get('message', '') or (item.text or '')[:2000],
                                     source='reports/test-results.xml'))
    skipped = sum(c.find('skipped') is not None for c in cases)
    failed_cases = sum(c.find('failure') is not None or c.find('error') is not None for c in cases)
    return dict(tests=len(cases), passed=len(cases)-skipped-failed_cases, failed=failed_cases,
                skipped=skipped, failures=failures)


def load_inputs(root):
    """Validate provenance before touching a potentially existing exported file."""
    root = Path(root)
    legacy, legacy_meta = read_current_report(root)
    periods, audit_meta = read_audit(root)
    candles, data_meta = load_verified(root)
    catalog = load_catalog(root/'sources/strategies.json')
    ids = {s['id'] for s in catalog}
    legacy_strategies = legacy[legacy.kind != 'benchmark']
    if set(legacy_strategies.strategy_id) != ids or legacy_strategies.strategy_id.duplicated().any():
        raise DataError('Exploratory results do not contain exactly the tested catalog.')
    if set(periods.period) != {'validation_2025', 'nominal_test_2026'} or periods.duplicated(['strategy_id', 'period']).any():
        raise DataError('Chronological result periods are missing or duplicated.')
    for _, group in periods.groupby('period'):
        if set(group.strategy_id) != ids:
            raise DataError('A strategy is missing from a chronological period.')
    if not legacy_strategies.execution_status.eq('completed').all() or not periods.execution_status.eq('completed').all():
        raise DataError('Unexecuted/failed backtests cannot be presented as tested.')
    for source in catalog:
        if sha256((root/source['local_source']).read_bytes()) != source['source_sha256']:
            raise DataError('A retained original strategy source changed.')
    audit = root/'reports/audit'
    obj = dict(root=root, legacy=legacy_strategies, legacy_meta=legacy_meta, periods=periods,
               audit_meta=audit_meta, candles=candles, data_meta=data_meta, catalog=catalog,
               software=junit_summary(root/'reports/test-results.xml'))
    for key, file in [('verdicts', 'strategy_verdicts.csv'), ('stress', 'sensitivity.csv'),
                      ('walk', 'walk_forward.csv'), ('training', 'training_candidates.csv'),
                      ('robustness', 'robustness_summary.csv'), ('causality', 'causality.csv')]:
        obj[key] = pd.read_csv(audit/file)
    obj['frozen'] = json.loads((audit/'frozen_selection.json').read_text())
    obj['protocol'] = json.loads((audit/'protocol.json').read_text())
    obj['directions'] = pd.read_csv(root/'reports/directional_predictions.csv')
    if set(obj['directions'].strategy_id) != ids or obj['directions'].strategy_id.duplicated().any():
        raise DataError('The directional-capability audit does not match the catalog.')
    return obj


def all_records(inputs):
    """Thirty protocol-specific rows; do not merge unlike parameter/warmup runs."""
    rows = []
    cat = {s['id']: s for s in inputs['catalog']}
    val = inputs['periods'].query("period == 'validation_2025'").set_index('strategy_id')
    verdict = inputs['verdicts'].set_index('strategy_id')
    selections = {s['strategy_id']: s for s in inputs['frozen']['selections']}
    directions = inputs['directions'].set_index('strategy_id')
    portfolios = pd.read_csv(inputs['root']/'reports/equity.csv.gz', index_col='timestamp', parse_dates=True)
    for frame, exploratory in [(inputs['legacy'], True), (inputs['periods'], False)]:
        for r in frame.to_dict('records'):
            sid, source = r['strategy_id'], cat[r['strategy_id']]
            lm, p = inputs['legacy_meta'], inputs['protocol']
            start = pd.Timestamp(lm['first_candle'] if exploratory else r['start'])
            stop = pd.Timestamp(lm['last_candle'])+pd.Timedelta(hours=1) if exploratory else pd.Timestamp(r['stop_exclusive'])
            actual = inputs['candles'].loc[(inputs['candles'].index >= start) & (inputs['candles'].index < stop)]
            expected = len(pd.date_range(start, stop, freq='h', inclusive='left'))
            history = selections[sid]
            profile = 'original' if exploratory else r['variant']
            params = inputs['protocol']['candidate_parameters'][sid][profile]
            vpass = bool(val.loc[sid, 'diagnostic_gate_pass'])
            row = dict(strategy=source['title'], strategy_id=sid,
                       evaluation='Exploratory full period (not OOS)' if exploratory else r['period'],
                       execution='COMPLETED — verified saved backtest',
                       return_pct=r['return_pct'], sharpe_ratio=r['sharpe_ratio'], max_drawdown_pct=r['max_drawdown_pct'],
                       profit_factor=r['profit_factor'], win_rate_pct=r['win_rate_pct'], trades=r['trades'],
                       low_trades='CAUTION — fewer than 30 trades' if r['trades'] < 30 else 'Not flagged; count alone does not establish reliability',
                       buy_and_hold_return_pct=r['buy_and_hold_return_pct'],
                       excess_return_pp=r['return_pct']-r['buy_and_hold_return_pct'],
                       oos_validation='N/A — different exploratory protocol' if exploratory else ('PASS — retrospective 2025 gate only' if vpass else 'FAIL — 2025 diagnostic gate'),
                       period_gate='N/A — exploratory' if exploratory else ('PASS — diagnostic only' if r['diagnostic_gate_pass'] else 'FAIL — diagnostic gate'),
                       passed_both='N/A — exploratory' if exploratory else ('YES' if verdict.loc[sid, 'passed_both_period_gates'] else 'NO'),
                       genuinely_unseen='NO — '+EXPOSURE, unseen_rank='NOT ISSUED — prior exposure',
                       accuracy='N/A — no directional forecasts' if not directions.loc[sid, 'forecast_provided'] else MISSING,
                       variant=profile, parameters=json.dumps(params, sort_keys=True),
                       start_utc=start, last_candle_utc=actual.index[-1], liquidation_deadline_utc=stop,
                       first_scored_utc=pd.Timestamp(lm['first_trade_opportunity']) if exploratory else start,
                       train_start_utc='N/A — no local fit' if exploratory else pd.Timestamp(history['fit_first_candle']),
                       train_last_utc='N/A — no local fit' if exploratory else pd.Timestamp(history['fit_last_candle']),
                       fee_per_side=lm['fee_per_side'] if exploratory else p['original_fee'],
                       slippage_per_side=lm['slippage_per_side'] if exploratory else p['slippage_per_side'],
                       initial_cash_usdt=r['initial_cash_usdt'], final_equity_usdt=r['final_equity_usdt'],
                       total_fees_usdt=r['total_fees_usdt'], warmup=lm['warmup_candles'] if exploratory else p['shared_warmup'],
                       candles=len(actual), portfolio_samples=len(portfolios) if exploratory else r['sharpe_hourly_samples'],
                       missing_hours=expected-len(actual), exchange='Binance spot', symbol='BTC/USDT', interval='1h',
                       data_source=SOURCE_URL, archive_base='https://data.binance.vision/data/spot/monthly/klines/BTCUSDT/1h/',
                       github=source['source_url'], source_commit=source['source_commit'], dataset_sha256=inputs['data_meta']['dataset_sha256'],
                       assumptions='All-in long/cash; next adjacent hourly open; no leverage; final-close liquidation; gap signals canceled; positions held; indicator warmup resets after gaps',
                       adaptation=ADAPTATION, unverified='Original authors’ tuning data unknown; live performance unverified; prior exposure prevents genuine untouched validation',
                       artifact='reports/summary.csv' if exploratory else 'reports/audit/period_results.csv')
            rows.append(row)
    return sorted(rows, key=lambda r: (r['evaluation'], r['strategy']))


def failed_records(inputs):
    rows = list(inputs['software']['failures'])
    for r in inputs['periods'].to_dict('records'):
        if not r['diagnostic_gate_pass']:
            reasons = []
            if r['return_pct'] <= 0:
                reasons.append('The strategy lost money.')
            if r['return_pct'] <= r['buy_and_hold_return_pct']:
                reasons.append('It did not beat buying and holding Bitcoin.')
            if r['trades'] < 30:
                reasons.append('Fewer than 30 trades: too little evidence for this check.')
            rows.append(dict(category='Investment validation criterion', strategy=r['strategy'], period=r['period'], status='FAIL',
                             check='Positive net return AND beats same-cost hold AND >=30 trades',
                             observed=f"Return {r['return_pct']:.2f}%; hold {r['buy_and_hold_return_pct']:.2f}%; {r['trades']} trades",
                             required='All three requirements pass', explanation=' '.join(reasons), source='reports/audit/period_results.csv'))
    for r in inputs['verdicts'].to_dict('records'):
        if not r['passed_both_period_gates']:
            rows.append(dict(category='Combined-period criterion', strategy=r['strategy'], period='2025 + Jan–Sep 2026', status='FAIL',
                             check='Pass both chronological diagnostic gates', observed='Did not pass both periods', required='Both periods pass',
                             explanation=r['failure_reasons'], source='reports/audit/strategy_verdicts.csv'))
    rows.extend([
        dict(category='Limitation; not a software failure', strategy='ALL', period='2025 / 2026', status='UNVERIFIED',
             check='Genuinely untouched final test', observed=EXPOSURE, required='Future prices not previously inspected',
             explanation='Earlier project runs already used these dates. Replaying them cannot undo exposure.', source='reports/audit/run.json'),
        dict(category='Missing data; not a software failure', strategy='ALL', period='2020–Sep 2026 source dataset', status='MISSING',
             check='Full hourly coverage', observed=f"{inputs['data_meta']['missing_hours']} missing hours; no invented candles", required='No gaps for complete coverage',
             explanation='All 81 monthly files were verified, but the source contains holes. Exact missing timestamps are in data/manifest.json.', source='data/manifest.json'),
        dict(category='Unverified provenance', strategy='ALL', period='Before this project', status='UNKNOWN',
             check='Original authors’ parameter-training data', observed='Not supplied in retained strategy sources', required='Independent provenance evidence',
             explanation='Published settings could already reflect historical tuning. We cannot certify upstream independence.', source='reports/audit/run.json')])
    return rows


class ExcelReport:
    def __init__(self, path):
        self.book = xlsxwriter.Workbook(path, {'strings_to_formulas': False, 'strings_to_urls': False})
        self.book.set_properties({'title': 'Bitcoin Strategy Lab — verified research workbook', 'author': 'Bitcoin Strategy Lab',
                                  'comments': 'Previously inspected history; no genuine unseen-data ranking. Binance Vision data attribution.'})
        self.sheets = {name: self.book.add_worksheet(name) for name in SHEET_NAMES}
        self.title = self.book.add_format({'bold': True, 'font_size': 20, 'font_color': '#FFFFFF', 'bg_color': '#16324F', 'valign': 'vcenter'})
        self.note = self.book.add_format({'text_wrap': True, 'valign': 'top', 'font_color': '#334155', 'bg_color': '#EFF5F9'})
        self.warn = self.book.add_format({'text_wrap': True, 'bold': True, 'font_color': '#92400E', 'bg_color': '#FEF3C7', 'valign': 'vcenter'})
        self.good = self.book.add_format({'font_color': '#166534', 'bg_color': '#DCFCE7', 'text_wrap': True})
        self.bad = self.book.add_format({'font_color': '#991B1B', 'bg_color': '#FEE2E2', 'text_wrap': True})
        self.na = self.book.add_format({'font_color': '#64748B', 'bg_color': '#F1F5F9', 'text_wrap': True})
        self.fmts = {
            'text': self.book.add_format({'text_wrap': True, 'valign': 'top'}),
            'pct': self.book.add_format({'num_format': '0.00%;[Red]-0.00%', 'font_color': '#1D4ED8', 'valign': 'top'}),
            'rate': self.book.add_format({'num_format': '0.00%', 'font_color': '#1D4ED8', 'valign': 'top'}),
            'ratio': self.book.add_format({'num_format': '0.00;[Red]-0.00', 'font_color': '#1D4ED8', 'valign': 'top'}),
            'money': self.book.add_format({'num_format': '#,##0.00;[Red]-#,##0.00', 'font_color': '#1D4ED8', 'valign': 'top'}),
            'int': self.book.add_format({'num_format': '#,##0', 'font_color': '#1D4ED8', 'valign': 'top'}),
            'date': self.book.add_format({'num_format': 'yyyy-mm-dd hh:mm', 'valign': 'top'}),
            'pp': self.book.add_format({'num_format': '0.00" pp";[Red]-0.00" pp"', 'valign': 'top'}),
        }
        self.header = self.book.add_format({'bold': True, 'text_wrap': True, 'font_color': '#FFFFFF', 'bg_color': '#24576A', 'valign': 'vcenter'})
        for ws in self.sheets.values():
            ws.hide_gridlines(2)
            ws.set_zoom(85)
            ws.set_default_row(30)
            ws.set_tab_color('#24576A')
            ws.set_landscape()
            ws.fit_to_pages(1, 0)
            ws.set_paper(9)
            ws.set_footer('&LBitcoin Strategy Lab — retrospective research&RPage &P of &N')
        self.sheets['Top 10'].set_tab_color('#D97706')
        self.sheets['Failed Tests'].set_tab_color('#DC2626')
        self.sheets['Charts'].set_tab_color('#7C3AED')

    def banner(self, name, title, subtitle, note=''):
        ws = self.sheets[name]
        last_col = 1 if name == 'Read Me' else 9
        ws.merge_range(0, 0, 1, last_col, title, self.title)
        ws.merge_range(2, 0, 3, last_col, subtitle, self.warn)
        ws.merge_range(4, 0, 5, last_col, note or 'Blue numbers are saved calculations. N/A is not zero. All trading timestamps are UTC. No genuinely unseen ranking is issued.', self.note)
        ws.set_column(0, 9, 16)
        return ws

    def value(self, ws, row, col, value, kind='text'):
        if value is None or (not isinstance(value, (list, dict)) and pd.isna(value)):
            ws.write_string(row, col, MISSING, self.na)
        elif kind == 'date' and not isinstance(value, str):
            t = pd.Timestamp(value)
            if t.tzinfo is not None:
                t = t.tz_convert('UTC').tz_localize(None)
            ws.write_datetime(row, col, t.to_pydatetime(), self.fmts['date'])
        elif isinstance(value, (bool, np.bool_)):
            ws.write_string(row, col, 'YES' if value else 'NO', self.fmts['text'])
        elif isinstance(value, (int, float, np.number)):
            if not math.isfinite(float(value)):
                ws.write_string(row, col, MISSING, self.na)
            else:
                ws.write_number(row, col, float(value)/100 if kind == 'pct' else float(value), self.fmts.get(kind, self.fmts['ratio']))
        elif kind == 'url' and str(value).startswith('https://'):
            ws.write_url(row, col, str(value), string=str(value))
        else:
            # Explicit strings prevent spreadsheet formula injection in source text.
            ws.write_string(row, col, str(value), self.na if str(value).startswith(('N/A', 'NOT ISSUED')) else self.fmts['text'])

    def table(self, name, columns, records, *, row=7, table_name=None):
        ws = self.sheets[name]
        for j, (key, label, kind, width) in enumerate(columns):
            ws.set_column(j, j, width)
            ws.write_string(row, j, label, self.header)
        ws.set_row(row, 44)
        for i, record in enumerate(records, row+1):
            for j, (key, _, kind, _) in enumerate(columns):
                self.value(ws, i, j, record.get(key), kind)
            ws.set_row(i, 48 if name == 'All Strategies' else 34)
        if records:
            ws.add_table(row, 0, row+len(records), len(columns)-1,
                         {'name': table_name or name.replace(' ', ''), 'style': 'Table Style Medium 2',
                          'columns': [{'header': c[1], 'header_format': self.header} for c in columns]})
            ws.conditional_format(row+1, 0, row+len(records), len(columns)-1,
                                  {'type': 'text', 'criteria': 'begins with', 'value': 'FAIL', 'format': self.bad})
            ws.conditional_format(row+1, 0, row+len(records), len(columns)-1,
                                  {'type': 'text', 'criteria': 'begins with', 'value': 'PASS', 'format': self.good})
        ws.freeze_panes(row+1, min(2, len(columns)))
        ws.repeat_rows(row)
        ws.print_area(0, 0, row+max(1, len(records)), len(columns)-1)
        return ws


def raw_columns(frame):
    columns = []
    for key in frame.columns:
        if key.endswith('_pct') or key in ('fee_per_side', 'slippage_per_side'):
            kind = 'pct' if key.endswith('_pct') else 'rate'
        elif key.endswith('_pp'):
            kind = 'pp'
        elif pd.api.types.is_numeric_dtype(frame[key]) and not pd.api.types.is_bool_dtype(frame[key]):
            kind = 'int' if key in ('trades', 'sharpe_hourly_samples') else 'ratio'
        else:
            kind = 'text'
        columns.append((key, key.replace('_', ' ').title(), kind, 22 if kind != 'text' else 34))
    return columns


def build_workbook(inputs, path):
    report = ExcelReport(path)
    records = all_records(inputs)
    now = datetime.now(timezone.utc)
    sw = inputs['software']
    rm = report.banner('Read Me', 'BITCOIN STRATEGY LAB | Excel research report',
                       'NO VERIFIED UNSEEN TOP 10 — 2025 and Jan–Sep 2026 were already inspected. This is a report of executed historical research, not a recommendation.',
                       f"Prepared {now.astimezone(ZoneInfo('Asia/Amman')):%Y-%m-%d %H:%M} Asia/Amman. All trading dates below use UTC. Data and derived output: Binance Vision, CC BY-NC-SA 4.0 plus saved dataset terms.")
    intro = [
        ('Start here', 'All Strategies contains 30 executed result rows: 10 strategies x 3 protocols. Filter Evaluation to separate the exploratory full period, 2025 validation and 2026 nominal test. Rows are alphabetical, not ranked.'),
        ('Top 10', 'No eligible unseen entries. The sheet explains exclusions for all ten strategies; an empty genuine leaderboard is intentional, not missing work.'),
        ('Prediction Accuracy', 'Ten trading rules, zero next-hour forecast models. Accuracy is N/A for every strategy; trade win rate is a different measurement.'),
        ('Charts', 'Native Excel charts use verified values on Chart Data. They illustrate retrospective results, not future probabilities.'),
        ('Failed Tests', 'Separates software outcomes from failed investment criteria and data/provenance limitations.'),
        ('Supporting sheets', 'Walk Forward: 30 held-out-from-fit yearly evaluations. Sensitivity: 200 cost/parameter runs. Training Fits: 120 training-only scores. Data Sources: all 81 archive/checksum URLs and source fingerprints.'),
        ('Software checks at export', f"{sw['tests']} tests recorded: {sw['passed']} passed, {sw['failed']} failed, {sw['skipped']} skipped. Source: reports/test-results.xml. A failed investment gate is not a software test error."),
        ('Chronological protocol', 'Training: 2020–2024, final hour purged. Validation: 2025. Nominal final test: Jan–Sep 2026, already seen previously. Parameters frozen before the audit’s validation/test scores; no retuning on those scores.'),
        ('Out-of-sample meaning', 'Selection-out-of-sample means excluded from the current fit. It does NOT mean genuinely untouched after prior project exposure. PASS means the retrospective 2025 gate passed; it cannot establish independent future performance.'),
        ('Investment gate', 'Positive net return AND beats the same-cost buy-and-hold reference AND at least 30 completed trades. One strategy passed 2025, a different one passed 2026; none passed both.'),
        ('Fees and execution', 'Base: 0.10% fee + 0.05% slippage PER SIDE on buys and sells. Start 10,000 USDT; all-in long/cash; next adjacent hourly open; no leverage. Remaining position liquidated at the last close with costs.'),
        ('Warmup and positions', 'Chronological audit: shared 300-candle warmup, past-only context, fresh cash and no inherited positions per evaluation. Earlier exploratory run: 200-candle warmup. Do not combine unlike protocols.'),
        ('Missing data', f"{inputs['data_meta']['rows']:,} real hourly candles across 2020–Sep 2026; {inputs['data_meta']['missing_hours']} missing hours in 15 gaps. No filling. Gaps cancel pending signals and reset warmup; existing positions remain held. 2025/2026 evaluation windows themselves have no missing hours."),
        ('Unverified items', 'True untouched independence is unavailable; original authors’ tuning/training history is unknown; live trading performance is unverified; source URLs were retained from verified snapshots, not re-queried for this export.'),
        ('Adaptation limits', ADAPTATION+'. Constant slippage, no partial fills, no lot rounding. Close-based drawdown misses intrabar and missing-hour losses.'),
        ('Net return', 'Total gain/loss after costs over the full named period, NOT annual return. +50% turns 100 into 150; -50% turns 100 into 50.'),
        ('Sharpe ratio', 'Average hourly portfolio return divided by sample standard deviation, scaled by sqrt(8760). Cash earns 0%; idle hours and entry costs included. Changes spanning missing hours excluded. Higher usually means more reward for bumpiness, not guaranteed safety.'),
        ('Maximum drawdown', 'Worst recorded drop from an earlier account high. A 77% drawdown turns a 100 peak into about 23 before any recovery.'),
        ('Profit factor', 'Winning-trade dollars divided by losing-trade dollars after costs. Below 1 means losses outweighed gains. N/A means no losing-trade denominator or no trades; zero can be a real measured value.'),
        ('Win rate and trades', 'Win rate is the fraction of completed buy/sell pairs that made money. Many small wins can be outweighed by large losses. Fewer than 30 trades is flagged, not a formal statistical threshold.'),
        ('Hold benchmark and excess', 'Buy once at the same protocol start and sell at the end with the same costs. Excess return is strategy return minus hold return, in percentage points (pp).'),
        ('Stress cases', 'Three predeclared parameter profiles x three fees per period, plus doubled fee/slippage. Profiles change numeric settings jointly, not one at a time. Scenarios are not independent trials or probabilities, and do not select a new winner.'),
        ('Sources and license', SOURCE_URL+' | Data terms: '+REPO_URL+'/blob/main/sources/BINANCE_DATASET_TERMS.md'),
    ]
    report.table('Read Me', [('topic', 'Topic / sheet', 'text', 30), ('detail', 'Explanation', 'text', 115)],
                 [dict(topic=k, detail=v) for k, v in intro], table_name='Guide')
    rm.set_row(8, 58)
    rm.activate()
    for index, name in enumerate(SHEET_NAMES[1:]):
        rm.write_url(35+index, 0, f"internal:'{name}'!A1", string='Open '+name)

    report.banner('All Strategies', 'ALL TESTED STRATEGIES | protocol-specific results',
                  '30 rows, 10 distinct strategies. Every row is a completed saved backtest. Prior exposure prevents genuinely unseen ranks. Filter Evaluation before comparing.',
                  'Percentages are real numeric Excel percentages. N/A is explicit. Expand/scroll right for dates, assumptions and immutable GitHub links. Different parameter/warmup protocols remain separate.')
    specs = [
        ('strategy','Strategy','text',32), ('evaluation','Evaluation','text',34), ('execution','Execution status','text',40), ('return_pct','Net return','pct',15),
        ('sharpe_ratio','Sharpe','ratio',12), ('max_drawdown_pct','Max drawdown','pct',16), ('profit_factor','Profit factor','ratio',20),
        ('win_rate_pct','Win rate','pct',15), ('trades','Completed trades','int',13), ('low_trades','Trade-count flag','text',30),
        ('buy_and_hold_return_pct','Buy-and-hold return','pct',18), ('excess_return_pp','Excess vs hold (pp)','pp',18),
        ('oos_validation','OOS validation: 2025 gate','text',38), ('period_gate','This period gate','text',26),
        ('passed_both','Passed both 2025 + 2026 gates','text',22), ('genuinely_unseen','Genuinely untouched?','text',40),
        ('unseen_rank','Unseen rank','text',30), ('accuracy','Next-hour prediction accuracy','text',34),
        ('github','Original GitHub strategy URL','url',55), ('variant','Parameter profile','text',20),
        ('parameters','Actual settings used','text',50), ('start_utc','First input candle UTC','date',22),
        ('last_candle_utc','Last input candle UTC','date',22), ('first_scored_utc','Scoring starts UTC','date',22),
        ('liquidation_deadline_utc','Final close deadline UTC','date',22), ('train_start_utc','Training starts UTC','date',25),
        ('train_last_utc','Last training candle UTC','date',25), ('fee_per_side','Trading fee per side','rate',18),
        ('slippage_per_side','Slippage per side','rate',18), ('initial_cash_usdt','Initial cash (USDT)','money',20),
        ('final_equity_usdt','Final equity (USDT)','money',20), ('total_fees_usdt','Total fees (USDT)','money',18),
        ('warmup','Warmup candles','int',16), ('candles','Available input candles','int',20),
        ('portfolio_samples','Scored portfolio samples','int',22), ('missing_hours','Missing input hours','int',18),
        ('exchange','Exchange','text',20), ('symbol','Pair','text',14), ('interval','Candle interval','text',14),
        ('data_source','Historical data documentation','url',52), ('archive_base','Official monthly archive base','url',60),
        ('assumptions','Trading assumptions','text',62), ('adaptation','Source adaptation','text',60),
        ('unverified','Missing / unverified information','text',65), ('source_commit','Strategy source commit','text',45),
        ('dataset_sha256','Verified dataset SHA-256','text',68), ('strategy_id','Strategy ID','text',20),
        ('artifact','Saved metric source','text',40)]
    ws = report.table('All Strategies', specs, records)
    ws.set_column(20, len(specs)-1, 24, None, {'level': 1})

    report.banner('Top 10', 'TOP 10 | no eligible unseen entries',
                  'NO GENUINE UNSEEN RANKING ISSUED. All candidate test dates were previously examined; no strategy passed both period gates.',
                  'The table below explains exclusions for all ten strategies. It is alphabetical and is NOT a top-ten ranking. No rank is fabricated.')
    decisions = []
    for r in inputs['verdicts'].sort_values('strategy').to_dict('records'):
        decisions.append(dict(strategy=r['strategy'], rank='NOT ISSUED', eligible='NO', reason='Previously inspected holdout; '+r['failure_reasons'],
                              passed_both='YES' if r['passed_both_period_gates'] else 'NO',
                              github=next(s['source_url'] for s in inputs['catalog'] if s['id']==r['strategy_id'])))
    report.table('Top 10', [('strategy','Strategy considered','text',35), ('rank','Genuine unseen rank','text',24),
                            ('eligible','Eligible?','text',12), ('passed_both','Passed both gates?','text',20),
                            ('reason','Why excluded / unverified','text',100), ('github','GitHub source','url',65)], decisions)

    report.banner('Prediction Accuracy', 'PREDICTION ACCURACY | no forecast models',
                  'No next-hour up/down forecasts were supplied by these strategies. Accuracy is N/A for every rule; zero models were scored.',
                  'Trade win rate is not forecast accuracy. N/A is not 0%. Scored forecasts = 0 means no forecasts were evaluated.')
    prediction_rows = []
    for r in inputs['directions'].sort_values('strategy').to_dict('records'):
        prediction_rows.append(dict(strategy=r['strategy'], trading_status=r['trading_backtest_status'],
                                    forecast='NO' if not r['forecast_provided'] else 'YES', accuracy='N/A — no directional forecasts',
                                    count=r['scored_forecasts'], status='NOT APPLICABLE — no model forecasts', reason=r['reason'],
                                    horizon='N/A — no forecast horizon supplied', dates='N/A — prediction evaluation not executed',
                                    github=next(s['source_url'] for s in inputs['catalog'] if s['id']==r['strategy_id'])))
    report.table('Prediction Accuracy', [('strategy','Strategy','text',36), ('trading_status','Trading backtest','text',22),
                                        ('forecast','Provides forecasts?','text',18), ('accuracy','Directional accuracy','text',38),
                                        ('count','Forecasts scored','int',16), ('status','Prediction evaluation','text',42),
                                        ('reason','Reason','text',70), ('horizon','Forecast horizon','text',38),
                                        ('dates','Prediction test dates','text',42), ('github','GitHub source','url',60)], prediction_rows)

    failures = failed_records(inputs)
    report.banner('Failed Tests', 'FAILED CHECKS | keep software and investment criteria separate',
                  f"Software: {sw['failed']} failed / {sw['tests']} recorded tests. Investment criteria have failures. Missing/unknown items are separately typed limitations.",
                  'A strategy can run correctly and still lose money. FAIL below does not automatically mean a software bug. MISSING/UNKNOWN/UNVERIFIED are not invented test failures.')
    report.table('Failed Tests', [('category','Category','text',32), ('strategy','Strategy','text',34), ('period','Period','text',28),
                                 ('status','Status','text',18), ('check','Check','text',70), ('observed','Observed result','text',65),
                                 ('required','Requirement','text',48), ('explanation','Simple explanation','text',100),
                                 ('source','Evidence file','text',45)], failures)

    for name, key, subtitle in [('Walk Forward', 'walk', '30 yearly evaluations excluded from each fit; previously inspected history, not untouched validation.'),
                                ('Sensitivity', 'stress', '200 executed parameter/cost cases; diagnostics only, not a search for a new winner.'),
                                ('Training Fits', 'training', '120 executed training-only candidate scores. Training performance is NOT out-of-sample performance.')]:
        frame = inputs[key].copy()
        report.banner(name, name.upper()+' | executed audit records', subtitle,
                      'Percent metrics are numeric Excel percentages. Fees and slippage display as Excel percentages: 0.10% per side corresponds to 0.001 in the underlying CSV. N/A stays explicit. Source: reports/audit/.')
        if key == 'training':
            frame.insert(1, 'strategy', frame.strategy_id.map({s['id']: s['title'] for s in inputs['catalog']}))
        report.table(name, raw_columns(frame), frame.to_dict('records'))

    report.banner('Data Sources', 'DATA SOURCES | official archives and verified fingerprints',
                  f"Binance spot BTC/USDT 1h, UTC: {inputs['data_meta']['rows']:,} candles; {inputs['data_meta']['missing_hours']} missing hours. Source coverage is partial.",
                  'Each archive was checksum-verified at download. Endpoints were not re-queried for Excel export. A matching checksum proves the download matches the published file, not that exchange records are error-free. Data: CC BY-NC-SA 4.0 plus Binance dataset terms.')
    source_rows = [dict(month=r['month'], status=r['status'], rows=r.get('rows'), first=r.get('first_candle'), last=r.get('last_candle'),
                        archive=r['archive_url'], checksum=r['checksum_url'], digest=r.get('sha256'),
                        evidence='SHA-256 checked during saved download; URL live availability not rechecked') for r in inputs['data_meta']['months']]
    report.table('Data Sources', [('month','Month','text',14), ('status','Saved verification','text',20), ('rows','Actual candles','int',16),
                                 ('first','First UTC candle','text',28), ('last','Last UTC candle','text',28),
                                 ('archive','Official archive URL','url',80), ('checksum','Published checksum URL','url',85),
                                 ('digest','Verified archive SHA-256','text',70), ('evidence','Verification scope','text',75)], source_rows)
    build_charts(report, inputs)
    report.book.close()
    return dict(strategy_count=len(inputs['catalog']), result_rows=len(records), eligible_top_10=0,
                forecast_models_scored=0, software_tests={k: v for k, v in sw.items() if k != 'failures'},
                sheets=SHEET_NAMES, created_at_utc=now.isoformat())


def build_charts(report, inputs):
    ws = report.banner('Charts', 'CHARTS | retrospective comparisons, not predictions',
                       'All ten strategies are included alphabetically. No genuinely unseen ranking is implied. Parameter settings were selected on training only.',
                       'Charts use actual recorded figures. Daily equity takes the last recorded hourly close each UTC day; no prices are invented. All chart source cells are visible on Chart Data.')
    report.banner('Chart Data', 'CHART DATA | transparent source cells', 'Chart values come from verified chronological CSVs. Numeric percentages are stored as fractions for Excel.',
                  'The buy-and-hold drawdown is computed from its saved recorded equity with initial cash included as an equity peak. Daily lines use recorded end-of-day portfolio values.')
    cat = sorted(inputs['catalog'], key=lambda s:s['title'])
    val = inputs['periods'].query("period == 'validation_2025'").set_index('strategy_id')
    test = inputs['periods'].query("period == 'nominal_test_2026'").set_index('strategy_id')
    risk = inputs['robustness'].query("period == 'nominal_test_2026'").set_index('strategy_id')
    eq = pd.read_csv(inputs['root']/'reports/audit/period_equity.csv.gz', index_col='timestamp', parse_dates=True)
    test_eq = eq[[f"nominal_test_2026_{s['id']}" for s in cat]+['nominal_test_2026_buy_and_hold']].dropna(how='all')
    bh = test_eq['nominal_test_2026_buy_and_hold'].dropna()
    peaks = np.maximum.accumulate(np.r_[10000.0, bh.to_numpy()])[1:]
    bh_dd = float(-(bh.to_numpy()/peaks-1).min()*100)
    rows = []
    for s in cat:
        sid = s['id']
        rows.append(dict(strategy=s['title'], val=val.loc[sid,'return_pct'], test=test.loc[sid,'return_pct'], dd=test.loc[sid,'max_drawdown_pct'],
                         low=risk.loc[sid,'fee_low_return_pct'], base=risk.loc[sid,'fee_base_return_pct'],
                         high=risk.loc[sid,'fee_high_return_pct'], double=risk.loc[sid,'double_cost_return_pct']))
    stress = inputs['stress'].query("period == 'nominal_test_2026'")
    def hold(fee, slip):
        values = stress.loc[(stress.fee_per_side == fee)&(stress.slippage_per_side == slip),'buy_and_hold_return_pct'].unique()
        if len(values) != 1:
            raise DataError('Matching-cost buy-and-hold benchmarks are inconsistent.')
        return float(values[0])
    rows.append(dict(strategy='Buy and hold (reference)', val=float(val.buy_and_hold_return_pct.iloc[0]), test=float(test.buy_and_hold_return_pct.iloc[0]), dd=bh_dd,
                     low=hold(.0005,.0005), base=hold(.001,.0005), high=hold(.002,.0005), double=hold(.002,.001)))
    columns = [('strategy','Strategy','text',38), ('val','2025 return','pct',18), ('test','2026 return','pct',18), ('dd','2026 max drawdown','pct',20),
               ('low','Fee 0.05%','pct',18), ('base','Fee 0.10%','pct',18), ('high','Fee 0.20%','pct',18), ('double','Fee 0.20% + slip 0.10%','pct',26)]
    cd = report.table('Chart Data', columns, rows, table_name='ChartMetrics')
    daily = test_eq.resample('D').last().dropna(how='all')
    labels = [s['title'] for s in cat]+['Buy and hold (reference)']
    row0 = 25
    cd.write_string(row0,0,'UTC candle day (last recorded close)',report.header)
    cd.set_row(row0,44)
    for j,label in enumerate(labels,1):
        cd.write_string(row0,j,label,report.header)
        cd.set_column(j,j,24)
    for i,(date,series) in enumerate(daily.iterrows(),row0+1):
        report.value(cd,i,0,date,'date')
        for j,value in enumerate(series,1):
            report.value(cd,i,j,value,'money')
    cd.print_area(0,0,row0+len(daily),len(labels))
    colors = ['#2563EB','#E11D48','#059669','#9333EA','#D97706','#0891B2','#DB2777','#4F46E5','#65A30D','#64748B','#111827']
    def bars(title, series, anchor, y_axis):
        chart=report.book.add_chart({'type':'bar'})
        for idx,(col,label,color) in enumerate(series):
            chart.add_series({'name':label,'categories':['Chart Data',8,0,18,0],
                              'values':['Chart Data',8,col,18,col], 'fill':{'color':color}, 'border':{'none':True}})
        chart.set_title({'name':title,'name_font':{'size':13}})
        chart.set_x_axis({'name':y_axis,'num_format':'0%','major_gridlines':{'visible':True}})
        chart.set_y_axis({'reverse':True,'num_font':{'size':9}})
        chart.set_legend({'position':'bottom'} if len(series)>1 else {'none':True})
        chart.set_size({'width':920,'height':540})
        chart.set_style(10)
        ws.insert_chart(anchor,chart)
    bars('2025 validation vs 2026 nominal test — not untouched',[(1,'2025 validation','#2563EB'),(2,'Jan–Sep 2026','#D97706')],'B8','Net return after costs')
    bars('2026 maximum drawdown — lower is better',[(3,'Recorded max drawdown','#B91C1C')],'Q8','Drop from earlier account high')
    bars('2026 fee/slippage sensitivity — frozen training settings',[(4,'Fee 0.05%','#059669'),(5,'Fee 0.10%','#2563EB'),(6,'Fee 0.20%','#D97706'),(7,'Fee 0.20% + slip 0.10%','#B91C1C')],'B24','Net return after costs')
    line=report.book.add_chart({'type':'line'})
    for j,label in enumerate(labels,1):
        line.add_series({'name':label,'categories':['Chart Data',row0+1,0,row0+len(daily),0],
                         'values':['Chart Data',row0+1,j,row0+len(daily),j],
                         'line':{'color':colors[j-1],'width':2.25 if j==len(labels) else 1.25}})
    line.set_title({'name':'2026 recorded daily portfolio value — all strategies and hold'})
    line.set_x_axis({'date_axis':True,'num_format':'mmm yyyy'})
    line.set_y_axis({'name':'USDT; each begins with 10,000','num_format':'#,##0'})
    line.set_legend({'position':'bottom','font':{'size':8}})
    line.set_size({'width':920,'height':540})
    ws.insert_chart('Q24',line)
    ws.set_column(0,30,10)
    ws.print_area(0,0,38,30)


def export(root=ROOT, output=None):
    root=Path(root)
    output=Path(output or root/'reports/Bitcoin_Strategy_Leaderboard.xlsx')
    inputs=load_inputs(root)
    output.parent.mkdir(parents=True,exist_ok=True)
    temp=output.with_name(output.stem+'.tmp.xlsx')
    try:
        summary=build_workbook(inputs,temp)
        temp.replace(output)
    finally:
        if temp.exists():
            temp.unlink()
    paths=[root/'data/manifest.json',root/'sources/strategies.json',root/'reports/run.json',root/'reports/summary.csv',root/'reports/test-results.xml',root/'reports/directional_predictions.csv']
    paths += [p for p in sorted((root/'reports/audit').iterdir()) if p.is_file()]
    summary.update(file=output.name,workbook_sha256=sha256(output.read_bytes()),exporter_sha256=sha256(Path(__file__).read_bytes()),
                   input_sha256={str(p.relative_to(root)):sha256(p.read_bytes()) for p in paths},
                   verification='Source report code/data/output fingerprints checked before export; no strategies or forecasts invented.')
    write_json(output.with_suffix('.json'),summary)
    return summary


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,default=None)
    args=p.parse_args()
    result=export(output=args.output)
    print(f"Created {result['file']}: {result['strategy_count']} strategies, {result['result_rows']} protocol rows, {len(result['sheets'])} sheets.")
    print('No eligible genuinely unseen top-10 entries; directional accuracy is N/A for all current rules.')


if __name__=='__main__':
    main()
