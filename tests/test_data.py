import hashlib
import io
import json
import urllib.error
import zipfile

import pandas as pd
import pytest

from btc_lab.data import DataError, download, load_verified, month_range, parse_archive, sha256, validate_prices, verify_archive


def archive(month='2020-01', rows=744, unit='ms'):
    dates = pd.date_range(month+'-01', periods=rows, freq='h', tz='UTC')
    output = io.StringIO()
    for t in dates:
        epoch = t.value // (1000 if unit == 'us' else 1_000_000)
        output.write(f'{epoch},100,102,98,101,10,{epoch},1000,1,5,500,0\n')
    blob = io.BytesIO()
    with zipfile.ZipFile(blob, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr(f'BTCUSDT-1h-{month}.csv', output.getvalue())
    return blob.getvalue()


def fetcher(blob):
    def get(url):
        if url.endswith('.CHECKSUM'):
            filename = url.rsplit('/', 1)[-1].removesuffix('.CHECKSUM')
            return f'{sha256(blob)}  {filename}'.encode()
        return blob
    return get


@pytest.mark.parametrize(('month', 'unit'), [('2020-01', 'ms'), ('2025-01', 'us')])
def test_real_archive_format_timestamp_units(month, unit):
    frame = parse_archive(archive(month, rows=3, unit=unit), month)
    assert frame.index[0] == pd.Timestamp(month+'-01', tz='UTC')
    assert frame.index[1]-frame.index[0] == pd.Timedelta(hours=1)
    assert frame.close.iloc[0] == 101


def test_checksum_mismatch_rejected():
    with pytest.raises(DataError, match='mismatch'):
        verify_archive(b'broken', f'{"0"*64}  prices.zip'.encode(), 'prices.zip')


def test_wrong_checksum_filename_rejected():
    with pytest.raises(DataError, match='different'):
        verify_archive(b'', f'{sha256(b"")}  other.zip'.encode(), 'prices.zip')


def test_download_manifest_and_reload(tmp_path):
    blob = archive()
    report = download(tmp_path, '2020-01', '2020-01', fetcher(blob))
    assert report['status'] == 'complete'
    assert report['rows'] == 744
    assert report['missing_hours'] == 0
    assert report['months'][0]['sha256'] == sha256(blob)
    frame, manifest = load_verified(tmp_path)
    assert len(frame) == 744
    assert manifest['dataset_sha256'] == sha256((tmp_path/'data/btcusdt_1h.csv.gz').read_bytes())


def test_cached_archives_are_reverified(tmp_path):
    blob = archive()
    download(tmp_path, '2020-01', '2020-01', fetcher(blob))
    raw = tmp_path/'data/raw/BTCUSDT-1h-2020-01.zip'
    raw.write_bytes(b'tampered')
    with pytest.raises(DataError, match='mismatch'):
        download(tmp_path, '2020-01', '2020-01', fetcher(blob))
    # Last valid dataset remains usable; failure cannot overwrite its manifest.
    assert len(load_verified(tmp_path)[0]) == 744


def test_changed_cleaned_prices_rejected(tmp_path):
    download(tmp_path, '2020-01', '2020-01', fetcher(archive()))
    path = tmp_path/'data/btcusdt_1h.csv.gz'
    path.write_bytes(path.read_bytes()+b'bad')
    with pytest.raises(DataError, match='manifest'):
        load_verified(tmp_path)


def test_unavailable_month_not_filled_or_called_complete(tmp_path):
    blob = archive()
    def get(url):
        if '2020-02' in url:
            raise urllib.error.HTTPError(url, 404, 'Not Found', None, None)
        return fetcher(blob)(url)
    report = download(tmp_path, '2020-01', '2020-02', get)
    assert report['status'] == 'partial'
    assert report['missing_hours'] == 29*24
    assert report['months'][1]['status'] == 'unavailable'
    assert report['actual_last_candle'] == '2020-01-31T23:00:00+00:00'


def test_access_denial_not_mislabeled_as_missing_history(tmp_path):
    def denied(url):
        raise urllib.error.HTTPError(url, 403, 'Forbidden', None, None)
    with pytest.raises(DataError, match='403'):
        download(tmp_path, '2020-01', '2020-01', denied)
    assert not (tmp_path/'data/manifest.json').exists()
    assert json.loads((tmp_path/'data/download_attempt.json').read_text())['status'] == 'blocked'


def test_gaps_duplicates_and_bad_ohlc_rejected(candles):
    with pytest.raises(DataError, match='missing'):
        validate_prices(candles.drop(candles.index[3]))
    with pytest.raises(DataError, match='duplicate'):
        validate_prices(pd.concat([candles.iloc[:1], candles]))
    broken = candles.copy()
    broken.iloc[5, broken.columns.get_loc('high')] = 0
    with pytest.raises(DataError):
        validate_prices(broken)


def test_month_range_crosses_years_and_is_inclusive():
    assert month_range('2020-12', '2021-02') == ['2020-12', '2021-01', '2021-02']
    with pytest.raises(DataError):
        month_range('2026-09', '2020-01')
