"""Binance's official public spot archives, with mandatory SHA-256 validation."""
import hashlib
import io
import json
import re
import time
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

BASE_URL = 'https://data.binance.vision/data/spot/monthly/klines/BTCUSDT/1h'
PRICE_COLUMNS = ['open', 'high', 'low', 'close', 'volume']


class DataError(ValueError):
    pass


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
    temp.replace(path)


def month_range(start, end):
    if not re.fullmatch(r'\d{4}-\d{2}', start) or not re.fullmatch(r'\d{4}-\d{2}', end):
        raise DataError('Use month dates like 2020-01 and 2026-09.')
    a, b = pd.Period(start, freq='M'), pd.Period(end, freq='M')
    if a > b:
        raise DataError('Start month must be before end month.')
    return [str(p) for p in pd.period_range(a, b, freq='M')]


def fetch(url):
    # HTTPS verification remains on. Retry only temporary server failures.
    for attempt in range(3):
        try:
            request = urllib.request.Request(url, headers={'User-Agent': 'BitcoinStrategyLab/0.1'})
            with urllib.request.urlopen(request, timeout=30) as response:
                return response.read()
        except urllib.error.HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt == 2:
                raise
            time.sleep(attempt + 1)


def verify_archive(blob, checksum_text, filename):
    fields = checksum_text.decode('ascii').strip().split()
    if len(fields) != 2 or not re.fullmatch(r'[0-9a-fA-F]{64}', fields[0]):
        raise DataError('The published checksum has an unexpected format.')
    if fields[1].lstrip('*') != filename:
        raise DataError('The checksum belongs to a different archive.')
    digest = sha256(blob)
    if digest.lower() != fields[0].lower():
        raise DataError(f'Checksum mismatch for {filename}; the file will not be used.')
    return digest


def parse_archive(blob, month):
    filename = f'BTCUSDT-1h-{month}.csv'
    with zipfile.ZipFile(io.BytesIO(blob)) as archive:
        if archive.namelist() != [filename]:
            raise DataError('Unexpected files inside the price archive.')
        if archive.getinfo(filename).file_size > 20_000_000:
            raise DataError('Hourly month archive is unexpectedly large.')
        table = pd.read_csv(archive.open(filename), header=None)
    if table.shape[1] != 12 or table.empty:
        raise DataError('Expected Binance 12-column kline data.')
    raw_time = pd.to_numeric(table[0], errors='raise').to_numpy(dtype=np.int64)
    # Binance spot archives changed milliseconds -> microseconds in January 2025.
    ns = np.where(raw_time >= 100_000_000_000_000, raw_time * 1000, raw_time * 1_000_000)
    frame = table.iloc[:, 1:6].copy()
    frame.columns = PRICE_COLUMNS
    frame = frame.astype(float)
    frame.index = pd.DatetimeIndex(pd.to_datetime(ns, utc=True), name='timestamp')
    validate_prices(frame, contiguous=False)
    if any(frame.index.strftime('%Y-%m') != month):
        raise DataError(f'Archive timestamps do not belong to {month}.')
    return frame


def validate_prices(frame, contiguous=True):
    if frame.empty or not set(PRICE_COLUMNS).issubset(frame.columns):
        raise DataError('No valid OHLCV price rows were found.')
    if not isinstance(frame.index, pd.DatetimeIndex) or frame.index.tz is None:
        raise DataError('Price timestamps must include a UTC timezone.')
    if not frame.index.is_unique or not frame.index.is_monotonic_increasing:
        raise DataError('Prices have duplicate or out-of-order timestamps.')
    if (frame.index != frame.index.floor('h')).any():
        raise DataError('Each candle must start exactly on an hour.')
    values = frame[PRICE_COLUMNS].to_numpy(dtype=float)
    if not np.isfinite(values).all() or (frame[PRICE_COLUMNS[:4]] <= 0).any().any() or (frame.volume < 0).any():
        raise DataError('Prices must be finite and positive, and volume cannot be negative.')
    if ((frame.high < frame[['open', 'close', 'low']].max(axis=1)) |
        (frame.low > frame[['open', 'close', 'high']].min(axis=1))).any():
        raise DataError('A candle has inconsistent high/low prices.')
    gaps = frame.index.to_series().diff().dropna() != pd.Timedelta(hours=1)
    if contiguous and gaps.any():
        raise DataError('There are missing hours. No prices were invented. Select a continuous date range using --start/--end; see data/manifest.json.')


def download(root, start='2020-01', end='2026-09', fetcher=fetch):
    root = Path(root)
    data_dir = root / 'data'
    raw_dir = data_dir / 'raw'
    raw_dir.mkdir(parents=True, exist_ok=True)
    months = month_range(start, end)
    report = dict(exchange='Binance spot', symbol='BTCUSDT', interval='1h', timezone='UTC',
                  requested_start_month=start, requested_end_month=end, checked_at=utc_now(),
                  source_documentation='https://github.com/binance/binance-public-data',
                  attribution='Binance Vision', dataset_license='CC BY-NC-SA 4.0 plus Binance Vision Dataset Terms',
                  status='downloading', months=[])
    frames = []
    try:
        for month in months:
            name = f'BTCUSDT-1h-{month}.zip'
            url = f'{BASE_URL}/{name}'
            item = dict(month=month, archive_url=url, checksum_url=url+'.CHECKSUM')
            report['months'].append(item)
            try:
                checksum_text = fetcher(url + '.CHECKSUM')
            except urllib.error.HTTPError as exc:
                if exc.code != 404:
                    raise
                item.update(status='unavailable', reason='Published checksum returned HTTP 404; no unchecked prices used.')
                print(f'{month}: unavailable (HTTP 404)', flush=True)
                continue
            cache = raw_dir / name
            blob = cache.read_bytes() if cache.exists() else fetcher(url)
            digest = verify_archive(blob, checksum_text, name)
            frame = parse_archive(blob, month)
            if not cache.exists():
                cache.write_bytes(blob)
            item.update(status='verified', sha256=digest, rows=len(frame),
                        first_candle=frame.index[0].isoformat(), last_candle=frame.index[-1].isoformat())
            frames.append(frame)
            print(f'{month}: {len(frame)} real candles, checksum verified', flush=True)
        if not frames:
            raise DataError('None of the requested months were available. No backtest was run.')
        frame = pd.concat(frames)
        validate_prices(frame, contiguous=False)
        first = pd.Timestamp(months[0]+'-01', tz='UTC')
        last_month = pd.Period(months[-1], freq='M')
        stop = pd.Timestamp(str(last_month+1)+'-01', tz='UTC')
        expected = pd.date_range(first, stop, freq='h', inclusive='left')
        missing = expected.difference(frame.index)
        output = data_dir / 'btcusdt_1h.csv.gz'
        temp = data_dir / 'btcusdt_1h.tmp.gz'
        frame.to_csv(temp, compression={'method': 'gzip', 'mtime': 0})
        temp.replace(output)
        report.update(status='complete' if len(missing) == 0 else 'partial', rows=len(frame),
                      actual_first_candle=frame.index[0].isoformat(), actual_last_candle=frame.index[-1].isoformat(),
                      expected_rows=len(expected), missing_hours=len(missing),
                      missing_timestamps=[t.isoformat() for t in missing],
                      dataset_path='data/btcusdt_1h.csv.gz', dataset_sha256=sha256(output.read_bytes()))
        write_json(data_dir / 'manifest.json', report)
        return report
    except Exception as exc:
        report.update(status='blocked', error=f'{type(exc).__name__}: {exc}')
        # Keep a previous successful manifest/data pair intact on a failed refresh.
        write_json(data_dir / 'download_attempt.json', report)
        raise DataError(f'Download stopped: {exc}. See data/download_attempt.json. Existing verified data was preserved.') from exc


def load_verified(root):
    root = Path(root)
    path, manifest_path = root/'data/btcusdt_1h.csv.gz', root/'data/manifest.json'
    if not path.exists() or not manifest_path.exists():
        raise DataError('Real prices are not installed yet. Run the Download prices step first.')
    manifest = json.loads(manifest_path.read_text())
    if manifest['status'] not in ('complete', 'partial') or sha256(path.read_bytes()) != manifest['dataset_sha256']:
        raise DataError('The price file no longer matches its verified manifest. Download it again.')
    if (manifest.get('exchange'), manifest.get('symbol'), manifest.get('interval')) != ('Binance spot', 'BTCUSDT', '1h'):
        raise DataError('Only the shared Binance spot BTC/USDT 1-hour dataset is accepted.')
    frame = pd.read_csv(path, index_col='timestamp', parse_dates=['timestamp'])
    frame.index = pd.to_datetime(frame.index, utc=True)
    validate_prices(frame, contiguous=False)
    if len(frame) != manifest['rows']:
        raise DataError('Price row count does not match its manifest.')
    return frame, manifest
