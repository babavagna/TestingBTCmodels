"""Named assets are authoritative; broker aliases and contract multipliers aren't guessed."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CRYPTO=['BTC','ETH','SOL','NEAR','ZEC','XRP','WLD','HYPE','VVV','ADA','BNB','BCH','DOGE','SUI','AAVE','LTC','UNI','LINK','KSHIB']
OTHER=[('WTI','WTI crude oil','commodity'),('GOLD','Gold','commodity'),('SILVER','Silver','commodity'),('PALLADIUM','Palladium','commodity'),('PLATINUM','Platinum','commodity'),('COPPER','Copper','commodity'),('ALUMINUM','Aluminum','commodity'),('USTECH100','USTECH100 (Nasdaq 100)','index'),('US500','US500 (S&P 500)','index')]

def supplementary_assets():
    rows=[]
    for name in CRYPTO:
        ambiguous=name=='KSHIB';perp=name=='VVV'
        rows.append(dict(id=name,name=name,category='crypto',symbol=None if ambiguous else name+'USDT',provider=None if ambiguous else 'Binance',market_type=None if ambiguous else ('USDT-margined perpetual' if perp else 'spot'),archive_market=None if ambiguous else ('futures/um' if perp else 'spot'),quote_currency='USDT',unit_size=None if ambiguous or perp else 1.,original_dashboard_contract_verified=False,contract_spec_status='Original dashboard specifications absent; exchange live metadata endpoint blocked' if not ambiguous else 'KSHIB scaling/contract identity not supplied',data_enabled=not ambiguous,trading_days_per_year=365,mapping_status='REQUIRES_KSHIB_CONTRACT_IDENTITY' if ambiguous else 'RESEARCH_MARKET_IDENTIFIED',mapping_note='User confirmation needed: KSHIB could be a scaled SHIB symbol or a derivative; no substitution made' if ambiguous else ('VVV spot monthly archive unavailable; actual Binance USDT perpetual researched separately with funding' if perp else 'Named asset on Binance spot USDT; original dashboard venue/lot specifications not supplied')))
    for name,label,category in OTHER:
        rows.append(dict(id=name,name=label,category=category,symbol=None,provider=None,market_type=None,archive_market=None,quote_currency='USD',unit_size=None,original_dashboard_contract_verified=False,contract_spec_status='Original broker symbol, instrument type and contract/lot size not supplied',data_enabled=False,trading_days_per_year=252,mapping_status='REQUIRES_DASHBOARD_BROKER_INSTRUMENT',mapping_note='A CFD, continuous future, spot quote, ETF or cash index cannot be silently substituted for another instrument'))
    # Explicit overrides must document the actual source/contract, never just a name.
    path=ROOT/'sources/multiasset/instrument_overrides.json'
    if path.exists():
        overrides=json.loads(path.read_text())
        for row in rows:
            if row['id'] in overrides:row.update(overrides[row['id']])
    for row in rows:
        row.update(price_role='SUPPLEMENTARY_EXTERNAL_FEED',is_primary_kalshi=False)
    return rows

def supplementary_asset(ident):return next(r for r in supplementary_assets() if r['id']==ident)

def assets():
    path=ROOT/'data/kalshi/markets.json'
    source=json.loads(path.read_text()) if path.exists() else json.loads((ROOT/'sources/multiasset/original_dashboard_markets.json').read_text())
    named=set(CRYPTO)|{x[0] for x in OTHER};rows=[]
    for market in source['markets']:
        ticker=market['ticker'];ident=ticker.removeprefix('KX').removesuffix('PERP').removesuffix('FUTURE')
        category={'Crypto':'crypto','Metals':'commodity','Energy':'commodity','Indices':'index','Equities':'equity'}.get(market.get('asset_class'),'unknown')
        rows.append(dict(id=ident,name=market.get('title',ident),category=category,symbol=ticker,provider='Kalshi',market_type='dated future' if ticker.endswith('FUTURE') else 'perpetual future',market_id=market.get('market_id'),market_version=market.get('market_version'),exchange_index=market.get('exchange_index'),market_status=market.get('status'),quote_currency='USD',contract_size=market.get('contract_size'),underlying_multiplier=market.get('underlying_multiplier'),tick_size=market.get('tick_size'),fractional_trading_enabled=market.get('fractional_trading_enabled'),schedule=market.get('schedule'),original_dashboard_contract_verified=all(k in market for k in ('contract_size','underlying_multiplier','tick_size')),metadata_is_current=bool(source.get('fresh_retrieval')),data_enabled=True,trading_days_per_year=365 if category=='crypto' else 252,price_role='PRIMARY_KALSHI_CONTRACT',is_primary_kalshi=True,requested_by_name=ident in named,discovered_extra=ident not in named,source_url='https://external-api.kalshi.com/trade-api/v2/margin/markets',mapping_status='KALSHI_CONTRACT_IDENTIFIED',contract_spec_status='Current metadata' if source.get('fresh_retrieval') else 'Previously observed dashboard metadata; refresh required'))
    return rows

def asset(ident):return next(r for r in assets() if r['id']==ident or r['symbol']==ident)
