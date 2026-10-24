"""Directional denominators and missing evidence must never be confused."""
import json
import numpy as np
import pytest
from directional_study.metrics import directions,interval
from directional_study.run import request

def test_up_and_down_precision_have_their_own_denominators():
    r=directions([1,1,0,0,1],[.9,.1,.7,.3,.8])
    assert r['up_calls']==3 and r['down_calls']==2
    assert r['up_accuracy']==pytest.approx(2/3)
    assert r['down_accuracy']==.5
    assert r['overall_accuracy']==.6
    assert r['up_moves_found']==pytest.approx(2/3)
    assert r['down_moves_found']==.5
    assert r['balanced_accuracy']==pytest.approx((2/3+.5)/2)
    assert r['tp']+r['tn']+r['fp']+r['fn']==r['forecasts']

def test_no_down_guesses_means_down_accuracy_na_not_perfect():
    r=directions([1,0,1],[.6,.7,.8])
    assert r['down_accuracy'] is None and r['down_ci_low'] is None and r['down_ci_high'] is None
    assert r['down_moves_found']==0 and r['one_sided_forecasts']
    assert r['up_accuracy']==pytest.approx(2/3)

def test_no_pattern_events_means_no_event_accuracy():
    r=directions([],[])
    assert r['forecasts']==0 and r['overall_accuracy'] is None
    assert r['up_accuracy'] is None and r['down_accuracy'] is None

def test_zero_accuracy_is_a_real_score_when_calls_exist():
    r=directions([0,0],[.6,.9])
    assert r['up_accuracy']==0 and r['up_calls']==2
    assert r['up_ci_high']>0 and r['up_ci_low']==0

def test_probability_threshold_and_rare_direction_warning():
    r=directions([1,0],[.5,.49])
    assert r['overall_accuracy']==1 and r['up_calls']==r['down_calls']==1
    assert r['few_up_calls'] and r['few_down_calls']

@pytest.mark.parametrize('y,p',[([1],[np.nan]),([1],[1.2]),([2],[.4]),([1,0],[.5])])
def test_invalid_or_unscored_labels_cannot_be_silently_measured(y,p):
    with pytest.raises(ValueError):directions(y,p)

def test_user_duplicates_are_preserved_but_not_recounted_as_tests():
    original,ids,counts,known=request()
    assert len(original)==90 and len(ids)==52 and len(set(ids))==52
    assert sum(counts.values())==90 and sum(known[n]['pattern'] for n in ids)==35
    assert counts['EOM']==4 and counts['CDLDRAGONFLYDOJI']==4
