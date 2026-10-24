"""Directional precision and recall have different denominators; report both."""
import math
import numpy as np
MIN_DIRECTION_CALLS=100

def interval(correct,total):
    if total==0:return None,None
    z=1.959963984540054;p=correct/total;den=1+z*z/total
    centre=(p+z*z/(2*total))/den
    half=z*math.sqrt(p*(1-p)/total+z*z/(4*total*total))/den
    return max(0.,centre-half),min(1.,centre+half)

def directions(y,probabilities):
    y=np.asarray(y);p=np.asarray(probabilities,dtype=float)
    if y.ndim!=1 or p.shape!=y.shape:raise ValueError('Direction arrays must be matching one-dimensional samples')
    if not np.isfinite(p).all() or ((p<0)|(p>1)).any():raise ValueError('Every scored probability must be finite and between 0 and 1')
    if not np.isin(y,[0,1]).all():raise ValueError('Targets must be binary UP/DOWN; remove flat targets explicitly')
    up=p>=.5;actual_up=y==1;n=len(y)
    tp=int(np.sum(up&actual_up));tn=int(np.sum(~up&~actual_up));fp=int(np.sum(up&~actual_up));fn=int(np.sum(~up&actual_up))
    up_calls=tp+fp;down_calls=tn+fn;ups=tp+fn;downs=tn+fp
    def ratio(a,b):return a/b if b else None
    up_ci=interval(tp,up_calls);down_ci=interval(tn,down_calls);overall_ci=interval(tp+tn,n)
    ur=ratio(tp,ups);dr=ratio(tn,downs)
    return dict(forecasts=n,overall_accuracy=ratio(tp+tn,n),up_accuracy=ratio(tp,up_calls),down_accuracy=ratio(tn,down_calls),up_calls=up_calls,down_calls=down_calls,actual_up_moves=ups,actual_down_moves=downs,up_moves_found=ur,down_moves_found=dr,balanced_accuracy=(ur+dr)/2 if ur is not None and dr is not None else None,predicted_up_share=ratio(up_calls,n),actual_up_share=ratio(ups,n),up_ci_low=up_ci[0],up_ci_high=up_ci[1],down_ci_low=down_ci[0],down_ci_high=down_ci[1],overall_ci_low=overall_ci[0],overall_ci_high=overall_ci[1],few_up_calls=up_calls<MIN_DIRECTION_CALLS,few_down_calls=down_calls<MIN_DIRECTION_CALLS,one_sided_forecasts=(up_calls==0 or down_calls==0),tp=tp,tn=tn,fp=fp,fn=fn)
