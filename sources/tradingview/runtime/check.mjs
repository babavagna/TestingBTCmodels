// Offline compatibility probe only. A successful probe is not a backtest.
import {PineTS} from 'pinets';
import fs from 'node:fs';
const [file,datafile]=process.argv.slice(2);
try {
 const p=new PineTS(JSON.parse(fs.readFileSync(datafile,'utf8')),'BTCUSDT','60');
 const ctx=await p.run(fs.readFileSync(file,'utf8'));
 const plots=Object.entries(ctx.plots).map(([name,v])=>({name,points:v.data.length,finite:v.data.filter(x=>typeof x.value==='number'&&Number.isFinite(x.value)).length}));
 console.log(JSON.stringify({status:'compatibility_probe_completed_only',plots}));
} catch(e){console.log(JSON.stringify({status:'runtime_failed',error:String(e.message).slice(0,1800)}));}
