"""Train-only multiclass probabilities, separate calibration, empirical joint outcomes."""
import numpy as np
import pandas as pd
from scipy.special import softmax
from scipy.optimize import minimize,minimize_scalar
import talib
from multiasset.engine import WARMUP
LABELS=['DOWN','STAY SIMILAR','UP'];THRESHOLDS=[.0005,.001,.002]

def targets(d,minutes,threshold=.001):
    step=pd.Timedelta(minutes=minutes);delta=d.close.shift(-1).to_numpy()/d.close.to_numpy()-1
    valid=np.r_[np.diff(d.index.asi8)==step.value,False]&np.isfinite(delta);valid[:min(WARMUP,len(valid))]=False
    y=np.where(delta>threshold,2,np.where(delta< -threshold,0,1)).astype(np.int8)
    return y,valid,d.index+step,d.index+2*step,delta

def split(d,minutes):
    _,valid,decision,end,_=targets(d,minutes);pos=np.flatnonzero(valid)
    if len(pos)<100:raise ValueError(f'Only {len(pos)} adjacent post-warmup targets; need at least 100 for chronological partitions')
    fractions=[0,.50,.60,.75,.85,1.];bounds=[]
    for frac in fractions[:-1]:bounds.append(decision[pos[min(int(len(pos)*frac),len(pos)-1)]])
    bounds.append(end[pos[-1]])
    names=['fit','selection','calibration','validation','retrospective_test'];masks={};dates={}
    for j,name in enumerate(names):
        # Earlier answers cannot finish at the next stage's decision boundary.
        mask=valid&(decision>=bounds[j])&((end<bounds[j+1]) if j<4 else (end<=bounds[j+1]))
        masks[name]=mask;dates[name]=dict(start=bounds[j].isoformat(),stop=bounds[j+1].isoformat(),targets=int(mask.sum()))
    if any((masks[a]&masks[b]).any() for a in names for b in names if a!=b):raise ValueError('Overlapping chronological stages')
    return masks,dates

def features(d):
    c=d.close.to_numpy(float);log=pd.Series(np.log(c),index=d.index);r=log.diff();vol=r.rolling(24).std();scale=vol.replace(0,np.nan)
    out=[r/scale,log.diff(3)/(scale*np.sqrt(3)),log.diff(6)/(scale*np.sqrt(6)),log.diff(12)/(scale*np.sqrt(12)),log.diff(24)/(scale*np.sqrt(24)),np.log(r.rolling(6).std().replace(0,np.nan)/scale),pd.Series(talib.RSI(c,14),index=d.index)/100-.5,(log-log.ewm(span=20,adjust=False).mean())/scale]
    # Zero realized volatility is real data. Scaled return features are then zero;
    # never interpolate missing prices. Preserve NaNs from initial lookbacks.
    zero=vol.eq(0)&np.isfinite(vol)
    for j in [0,1,2,3,4,5,7]:out[j]=out[j].mask(zero,0.)
    return np.column_stack(out)

def fit(x,y,mask,min_rows=256):
    a=np.asarray(x[mask],float);b=np.asarray(y[mask],int)
    if len(b)<min_rows:raise ValueError(f'Only {len(b)} training targets; need {min_rows}')
    counts=np.bincount(b,minlength=3)
    if (counts<10).any():raise ValueError('Insufficient training outcome support: '+str(counts.tolist())+'; need 10 per class')
    if not np.isfinite(a).all():raise ValueError('Missing model features in training')
    mu=a.mean(0);sd=a.std(0);keep=sd>1e-10
    if not keep.any():raise ValueError('All probability features are constant')
    z=np.column_stack([np.ones(len(a)),np.clip((a[:,keep]-mu[keep])/sd[keep],-10,10)]);k=z.shape[1];truth=np.eye(3)[b];ridge=.01
    def objective(w):
        w=w.reshape(3,k);logits=z@w.T;p=softmax(logits,axis=1)
        loss=-np.log(np.clip(p[np.arange(len(b)),b],1e-15,1)).mean()+.5*ridge*np.sum(w[:,1:]**2)
        grad=(p-truth).T@z/len(b);grad[:,1:]+=ridge*w[:,1:]
        return float(loss),grad.ravel()
    opt=minimize(objective,np.zeros(3*k),jac=True,method='L-BFGS-B',options={'maxiter':200,'ftol':1e-10,'gtol':1e-7})
    if not opt.success:raise ValueError('Multiclass optimizer failed: '+str(opt.message))
    return dict(mean=mu.tolist(),scale=sd.tolist(),keep=keep.tolist(),weights=opt.x.reshape(3,k).tolist(),classes=LABELS,training_counts=counts.tolist(),training_rows=len(b),temperature=1.,calibrated=False)

def logits(model,x):
    mu=np.asarray(model['mean']);sd=np.asarray(model['scale']);keep=np.asarray(model['keep'],bool)
    z=np.column_stack([np.ones(len(x)),np.clip((x[:,keep]-mu[keep])/sd[keep],-10,10)])
    return z@np.asarray(model['weights']).T

def calibrate(model,x,y,mask):
    b=np.asarray(y[mask],int);z=logits(model,x[mask]);counts=np.bincount(b,minlength=3)
    if len(b)<100 or (counts<3).any():raise ValueError(f'Calibration needs 100 rows and 3 examples per class; got n={len(b)}, counts={counts.tolist()}')
    def loss(t):return float(-np.log(np.clip(softmax(z/t,axis=1)[np.arange(len(b)),b],1e-15,1)).mean())
    opt=minimize_scalar(loss,bounds=(.5,5.),method='bounded',options={'xatol':1e-6})
    temperature=float(opt.x) if opt.success and loss(opt.x)<loss(1.) else 1.
    result=dict(model);result.update(temperature=temperature,calibrated=True,calibration_rows=len(b),calibration_counts=counts.tolist(),calibration_log_loss_before=loss(1.),calibration_log_loss_after=loss(temperature));return result

def predict(model,x,calibrated=True):return softmax(logits(model,x)/(model['temperature'] if calibrated else 1.),axis=1)

def metrics(y,p):
    y=np.asarray(y,int);p=np.asarray(p,float);n=len(y)
    if n==0:return dict(observations=0,accuracy=None,brier=None,log_loss=None,ece=None,balanced_accuracy=None)
    if p.shape!=(n,3) or not np.isfinite(p).all() or not np.allclose(p.sum(1),1,rtol=0,atol=1e-10):raise ValueError('Invalid probability simplex')
    guessed=p.argmax(1);hit=guessed==y;truth=np.eye(3)[y];rows=[];recalls=[]
    for k,label in enumerate(LABELS):
        actual=y==k;calls=guessed==k;tp=int((actual&calls).sum());total=int(actual.sum());called=int(calls.sum())
        recall=tp/total if total else None;recalls.append(recall)
        rows.append(dict(label=label,actual=total,predicted=called,correct=tp,precision=tp/called if called else None,recall=recall))
    confidence=p.max(1);bins=[];ece=0.
    for j in range(10):
        mask=(confidence>=j/10)&((confidence<(j+1)/10) if j<9 else (confidence<=1));count=int(mask.sum())
        if count:
            acc=float(hit[mask].mean());avg=float(confidence[mask].mean());ece+=count/n*abs(acc-avg);bins.append(dict(lower=j/10,upper=(j+1)/10,observations=count,accuracy=acc,mean_confidence=avg))
    return dict(observations=n,accuracy=float(hit.mean()),balanced_accuracy=float(np.mean(recalls)) if all(v is not None for v in recalls) else None,brier=float(np.mean(np.sum((p-truth)**2,axis=1))),log_loss=float(-np.log(np.clip(p[np.arange(n),y],1e-15,1)).mean()),ece=float(ece),classes=rows,reliability_bins=bins,too_few_forecasts=n<1000)

def joint_outcomes(votes,y,selected,current,min_matches=100):
    votes=np.asarray(votes);y=np.asarray(y,int);current=np.asarray(current)
    if votes.ndim!=2 or len(y)!=len(votes):raise ValueError('Bad historical agreement dimensions')
    selected=np.asarray(selected,int)
    if len(selected) and (selected.min()<0 or selected.max()>=votes.shape[1]):raise ValueError('Unknown indicator selected')
    if len(current)!=votes.shape[1]:raise ValueError('Current vote/model identity mismatch')
    if len(selected) and (current[selected]<0).any():return dict(status='MISSING_CURRENT_INDICATOR',observations=0,probabilities=None)
    mask=np.ones(len(y),bool) if not len(selected) else np.all(votes[:,selected]==current[selected],axis=1)
    count=int(mask.sum());classes=np.bincount(y[mask],minlength=3)
    return dict(status='EMPIRICAL_JOINT_ESTIMATE' if count>=min_matches else 'INSUFFICIENT_JOINT_SAMPLE',observations=count,counts=classes.tolist(),probabilities=(classes/count).tolist() if count>=min_matches else None,method='Actual matching joint calibration outcomes; no independence assumption',selection_is_exploratory=True)
