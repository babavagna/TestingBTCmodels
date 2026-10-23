/* Execute published Zenbot signal hooks on completed hourly candles.
 * No exchange client or native trading daemon is loaded. Source bugs are kept.
 * State-dependent strategies require a coupled execution adapter and fail closed.
 */
const fs=require('fs');
const path=require('path');
const input=JSON.parse(fs.readFileSync(0,'utf8'));
const root=path.resolve(__dirname,'..');
const originalLog=console.log;
console.log=(...args)=>process.stderr.write(args.join(' ')+'\n');
async function main(){
 const strategy=require(path.join(root,input.source_path));
 const options={mode:'sim',verbose:false,period:'1h',period_length:'1h',min_periods:52};
 strategy.getOptions.call({option:(key,desc,type,value)=>{options[key]=value;}});
 options.period='1h';options.period_length='1h';
 const excluded=['period','period_length','threads','neurons_1','neurons_2','depth','min_predict','learns'];
 if(input.factor!==1)for(const key of Object.keys(options)){
  if(typeof options[key]==='number' && !excluded.includes(key)){
   const val=options[key]*input.factor;
   options[key]=Number.isInteger(options[key]) && options[key]>0?Math.max(1,Math.round(val)):val;
  }
 }
 // These sources read native fills/account state. A free-standing signal series
 // cannot reproduce their behavior; do not silently substitute made-up balances.
 if(strategy.name==='neural')throw new Error('UNSUPPORTED_FORECAST_RUNTIME: native predictor forks a cluster and retrains each scoring hour; frozen training/forecast adapter is required before directional accuracy can be measured');
 if(['rsi','sar'].includes(strategy.name))throw new Error('UNSUPPORTED_STATE: source reads native account/trade history; coupled fill-state adapter required');
 // The source starts a cluster worker and does not acknowledge its master hook.
 // Probe it in a real child process with a timeout from the Python adapter.
 const s={options,lookback:[],in_preroll:true,my_trades:[]};
 const en=[],ex=[];
 for(let i=0;i<input.candles.length;i++){
  const row=input.candles[i];
  s.period={time:row[0],period_id:row[0],close_time:row[0]+3599999,open:row[1],high:row[2],low:row[3],close:row[4],volume:row[5]};
  s.signal=null;s.in_preroll=i<input.warmup-1;
  if(strategy.calculate)await strategy.calculate(s);
  await new Promise((resolve,reject)=>{
   const timer=setTimeout(()=>reject(new Error('CALLBACK_TIMEOUT: onPeriod did not finish within 5 seconds')),5000);
   try{strategy.onPeriod(s,()=>{clearTimeout(timer);resolve();});}catch(e){clearTimeout(timer);reject(e);}
  });
  en.push(!s.in_preroll && s.signal==='buy');ex.push(!s.in_preroll && s.signal==='sell');
  s.lookback.unshift(s.period);
 }
 process.stdout.write(JSON.stringify({entry:en,exit:ex,parameters:options}));
}
main().catch(e=>{process.stderr.write(e.stack+'\n');process.exitCode=1;});
