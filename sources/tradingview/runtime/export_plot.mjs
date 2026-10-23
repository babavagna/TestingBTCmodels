import fs from 'node:fs';
import {PineTS} from 'pinets';
const [source,datafile,plot,outfile]=process.argv.slice(2);
const ctx=await new PineTS(JSON.parse(fs.readFileSync(datafile,'utf8')),'BTCUSDT','60').run(fs.readFileSync(source,'utf8'));
fs.writeFileSync(outfile,JSON.stringify(ctx.plots[plot].data.map(x=>x.value)));
