from streamlit.testing.v1 import AppTest

from btc_lab.strategies import ROOT


def test_dashboard_opens_without_prices_and_does_not_make_up_results(tmp_path, monkeypatch):
    import shutil
    (tmp_path/'sources').mkdir()
    shutil.copy(ROOT/'sources/strategies.json', tmp_path/'sources/strategies.json')
    monkeypatch.setattr('btc_lab.strategies.ROOT', tmp_path)
    app = AppTest.from_file(str(ROOT/'app.py')).run(timeout=30)
    assert not app.exception
    assert app.title[0].value == '₿ Bitcoin Strategy Lab'
    buttons = {button.label: button for button in app.button}
    assert buttons['Run comparison'].disabled
    assert not app.dataframe
    assert any('No historical performance' in text.value for text in app.markdown)
    assert len(app.expander) >= 2


def test_dashboard_displays_saved_real_comparison():
    if not (ROOT/'reports/run.json').exists():
        import pytest
        pytest.skip('No saved real-data comparison to display.')
    app = AppTest.from_file(str(ROOT/'app.py')).run(timeout=30)
    assert not app.exception
    assert len(app.dataframe) == 1
    assert len(app.dataframe[0].value) == 11
    assert any('Missing-hour events' in text.value for text in app.markdown)
