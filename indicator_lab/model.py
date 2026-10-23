"""Training-only scaling and a fixed, regularized logistic forecast readout."""
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import expit
RIDGE=.01
BURN=2048

def targets(d,minutes):
    ix=d.index;step=pd.Timedelta(minutes=minutes)
    delta=d.close.shift(-1).to_numpy()-d.close.to_numpy()
    adjacent=np.r_[np.diff(ix.asi8)==step.value,False]
    valid=adjacent & np.isfinite(delta) & (delta!=0)
    valid[:BURN]=False
    # Features for candle opening t arrive at t+step; target is next close t+2step.
    return (delta>0).astype(np.int8),valid,ix+step,ix+2*step

def period_mask(d,minutes,valid,start,stop,fit=False):
    _,_,decision,end=targets(d,minutes)
    start=pd.Timestamp(start,tz='UTC');stop=pd.Timestamp(stop,tz='UTC')
    # A target completing at midnight belongs to the preceding period for scoring.
    # Fits purge that boundary label strictly, so it cannot touch the next period.
    return valid & (decision>=start) & ((end<stop) if fit else (end<=stop))

def fit(x,y,mask):
    a=x[mask];b=y[mask].astype(float)
    if len(b)<1000:raise ValueError('Fewer than 1000 valid training targets')
    if not np.isfinite(a).all():raise ValueError('Non-finite feature in training')
    if len(np.unique(b))<2:raise ValueError('Training outcomes contain only one class')
    mu=a.mean(axis=0);sd=a.std(axis=0);keep=sd>1e-10
    if not keep.any():raise ValueError('All training features are constant: no learned indicator forecast')
    z=np.clip((a[:,keep]-mu[keep])/sd[keep],-10,10)
    # Use all available training observations, no random split or future scaling.
    def loss(w):
        t=w[0]+z@w[1:];q=expit(t);r=q-b
        value=np.mean(np.logaddexp(0,t)-b*t)+.5*RIDGE*np.dot(w[1:],w[1:])
        grad=np.r_[r.mean(),z.T@r/len(b)+RIDGE*w[1:]]
        return value,grad
    init=np.zeros(z.shape[1]+1);init[0]=np.log(b.mean()/(1-b.mean()))
    opt=minimize(loss,init,jac=True,method='L-BFGS-B',options={'maxiter':200,'ftol':1e-11,'gtol':1e-7})
    if not opt.success:raise ValueError('Optimizer did not converge: '+str(opt.message))
    return dict(mean=mu.tolist(),scale=sd.tolist(),keep=keep.tolist(),weights=opt.x.tolist(),training_samples=len(b),training_up_rate=float(b.mean()),objective=float(opt.fun),iterations=int(opt.nit),ridge=RIDGE)

def predict(model,x):
    mu=np.array(model['mean']);sd=np.array(model['scale']);keep=np.array(model['keep'],bool);w=np.array(model['weights'])
    z=np.clip((x[:,keep]-mu[keep])/sd[keep],-10,10)
    return expit(w[0]+z@w[1:])
