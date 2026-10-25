import json
import unittest
import numpy as np
from scipy.special import expit
from indicator_lab.data import load
from indicator_lab.features import catalog, features
from live_signal_server import closed_rows, direction, infer, IDS_15

class LiveTests(unittest.TestCase):
    def test_closed_only(self):
        rows=[[0,1,1,1,1,1,299999],[300000,1,1,1,1,1,599999]]
        self.assertEqual(closed_rows(rows,300000),rows[:1])
    def test_direction_boundary_and_missing(self):
        self.assertEqual(direction(.5),'UP'); self.assertEqual(direction(.499),'DOWN')
        self.assertIsNone(direction(float('nan'))); self.assertIsNone(direction(None))
    def test_15m_closed_only(self):
        rows=[[0,1,1,1,1,1,899999],[900000,1,1,1,1,1,1799999]]
        self.assertEqual(closed_rows(rows,900000,900000),rows[:1])
    def test_original_model_parity_full_history(self):
        from pathlib import Path
        for tf, ids in [(5, None),(15, IDS_15)]:
            d,_=load(tf); frozen=json.loads(Path(f'reports/predictions/frozen_{tf}m.json').read_text())
            result=infer(d,frozen,ids) if ids else infer(d,frozen)
            self.assertEqual(len(result),26 if tf==15 else 35)
            lookup={r['id']:r for r in catalog()}
            for r in result:
                e=frozen['models'][r['id']]; m=e['profiles'][e['selected_profile']]['model']
                x=features(lookup[r['id']],d,e['selected_profile'])[-1]
                keep=np.array(m['keep'],bool)
                z=np.clip((x[keep]-np.array(m['mean'])[keep])/np.array(m['scale'])[keep],-10,10)
                p=float(expit(m['weights'][0]+z@np.array(m['weights'][1:])))
                self.assertAlmostEqual(r['p_up'],p,places=12)
            short=infer(d.iloc[:100],frozen,ids) if ids else infer(d.iloc[:100],frozen)
            self.assertTrue(all(r['direction'] is None for r in short))
if __name__=='__main__':unittest.main()
