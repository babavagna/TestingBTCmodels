#!/usr/bin/env python3
"""Format the measured 52-indicator table as real numeric .xls and .xlsx files.

No models are fitted or re-scored. Existing full-precision results are displayed
as percentages with two decimal places. Warnings live outside the numeric cells.
"""
import json,math,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import xlwt,xlrd,xlsxwriter,openpyxl
from btc_lab.data import sha256,write_json,utc_now
from indicator_lab.data import ROOT
from directional_study.run import request
SOURCE=ROOT/'reports/selected_directional/combined.json'
DEST=ROOT/'BTC_DIRECTIONAL_SORTABLE'
COLUMNS=[(5,'up','5m UP'),(5,'down','5m DOWN'),(15,'up','15m UP'),(15,'down','15m DOWN'),(60,'up','1h UP'),(60,'down','1h DOWN')]
HEADERS=['Indicator']+[label for _,_,label in COLUMNS]

def data():
    source=json.loads(SOURCE.read_text());_,ids,_,_=request()
    if len(ids)!=52:raise ValueError('Expected the requested 52 distinct indicator IDs')
    rows=[];counts=[];warnings=[]
    for ident in ids:
        row=[ident];nrow=[ident];wrow=[ident]
        for minutes,direction,_ in COLUMNS:
            matches=[r for r in source['rows'] if r['id']==ident and r['timeframe_minutes']==minutes and r['period']=='retrospective']
            if len(matches)!=1:raise ValueError('Missing/duplicate measured result: '+ident)
            r=matches[0];value=r[direction+'_accuracy'];n=r[direction+'_calls']
            if value is None:
                if n!=0:raise ValueError('Missing accuracy despite nonzero guesses')
                row.append('N/A')
            else:
                if not isinstance(value,(int,float)) or not math.isfinite(value) or not 0<=value<=1 or n==0:raise ValueError('Invalid measured percentage')
                row.append(value)
            nrow.append(n);wrow.append('NO GUESSES' if n==0 else ('FEWER THAN 100 GUESSES' if n<100 else ''))
        rows.append(row);counts.append(nrow);warnings.append(wrow)
    return rows,counts,warnings

def readme():
    return [
      ['How to sort','Accuracy has one row per indicator and six SEPARATE numeric percentage columns. In .xlsx use the header dropdown > Sort Largest to Smallest. In .xls select A1:G53 > Data > Sort, keeping whole rows together and treating the first row as headers.'],
      ['Main columns',', '.join(HEADERS)],
      ['Percentages','Values are real Excel numbers, not text. They retain measured precision and display two decimal places. No slashes or asterisks are inside numeric cells.'],
      ['N/A','This model made no guesses in that direction. N/A stays text, never an invented zero. A genuine 0.00% remains a numeric zero.'],
      ['Small samples','Orange accuracy cells indicate 1–99 guesses: the asterisk from your pasted table. Counts and warnings keeps each direction count and a separate warning. Zero guesses are labeled NO GUESSES.'],
      ['Direction accuracy','UP means correct UP guesses / all UP guesses. DOWN means correct DOWN guesses / all DOWN guesses. These are not actual-move recall or trading win rates.'],
      ['Dates and scope','January–September 2026 retrospective; Binance spot BTC/USDT; next close relative to the current close on matching 5m, 15m and 1h charts. Models were frozen after training 2020–2024 and selecting settings using 2025.'],
      ['Pattern scope','Every eligible candle is scored, including when a candlestick pattern did not appear. The detailed BTC_UP_DOWN_ACCURACY.xlsx workbook has the separate Pattern Events sheet. These forecasts are indicator + trained model, not standalone native TradingView predictions.'],
      ['Example of weak evidence','CORREL 15m DOWN shows 100.00%, from only one correct DOWN guess out of one. Do not interpret that as a reliable success rate.'],
      ['Special formula inputs','CORREL and BETA use BTC high/low series, not another reference market. Native TradingView agreement remains unverified.'],
      ['Accuracy versus profit','Accuracy ignores trading costs. This formatting export does not change models, settings, predictions or the earlier cost assumptions. The full workbook keeps the separate portfolio results.'],
      ['Source','reports/selected_directional/combined.json; every value comes from the verified re-executed forecasts.'],
    ]

def export_xls(rows,counts,warnings):
    path=DEST.with_suffix('.xls');temp=DEST.with_suffix('.tmp.xls');w=xlwt.Workbook()
    head=xlwt.easyxf('font: bold on, colour white; pattern: pattern solid, fore_colour dark_blue; align: wrap on;')
    normal=xlwt.easyxf(num_format_str='0.00%')
    limited=xlwt.easyxf('pattern: pattern solid, fore_colour light_orange;',num_format_str='0.00%')
    wrap=xlwt.easyxf('align: wrap on, vert top;')
    for name,headers,records in [('Accuracy',HEADERS,rows),('Counts and warnings',['Indicator']+[s+' guesses' for _,_,s in COLUMNS]+[s+' warning' for _,_,s in COLUMNS],[n+w[1:] for n,w in zip(counts,warnings)]),('Read Me',['Topic','Explanation'],readme())]:
        s=w.add_sheet(name);s.panes_frozen=True;s.horz_split_pos=1;s.vert_split_pos=1;s.row(0).height=600
        for col,label in enumerate(headers):s.write(0,col,label,head);s.col(col).width=(30 if col==0 else (110 if name=='Read Me' else 24))*256
        for i,row in enumerate(records,1):
            for j,value in enumerate(row):
                style=wrap if name=='Read Me' else xlwt.Style.default_style
                if name=='Accuracy' and j>0 and isinstance(value,(int,float)):style=limited if 0<counts[i-1][j]<100 else normal
                s.write(i,j,value,style)
            if name=='Read Me':s.row(i).height=1200
    w.save(str(temp));temp.replace(path);return path

def export_xlsx(rows,counts,warnings):
    path=DEST.with_suffix('.xlsx');temp=DEST.with_suffix('.tmp.xlsx');w=xlsxwriter.Workbook(temp,{'strings_to_formulas':False,'strings_to_urls':False})
    pct=w.add_format({'num_format':'0.00%'});limited=w.add_format({'num_format':'0.00%','bg_color':'#FCE4D6'});wrap=w.add_format({'text_wrap':True,'valign':'top'})
    for name,headers,records in [('Accuracy',HEADERS,rows),('Counts and warnings',['Indicator']+[s+' guesses' for _,_,s in COLUMNS]+[s+' warning' for _,_,s in COLUMNS],[n+w[1:] for n,w in zip(counts,warnings)]),('Read Me',['Topic','Explanation'],readme())]:
        s=w.add_worksheet(name);s.freeze_panes(1,1);s.set_column(0,0,30);s.set_column(1,len(headers)-1,24)
        s.add_table(0,0,len(records),len(headers)-1,{'name':{'Accuracy':'DirectionalAccuracy','Counts and warnings':'DirectionEvidence','Read Me':'ReadingInstructions'}[name],'columns':[{'header':h} for h in headers],'style':'Table Style Medium 2'})
        for i,row in enumerate(records,1):
            for j,value in enumerate(row):
                fmt=wrap if name=='Read Me' else None
                if name=='Accuracy' and j>0 and isinstance(value,(int,float)):fmt=limited if 0<counts[i-1][j]<100 else pct
                s.write(i,j,value,fmt)
                if name=='Accuracy' and j>0:s.write_comment(i,j,f'{counts[i-1][j]:,} guesses. '+('No guesses: no accuracy.' if counts[i-1][j]==0 else ('Fewer than 100 guesses; original asterisk warning.' if counts[i-1][j]<100 else 'Measured directional precision; not a profit measure.')))
            if name=='Read Me':s.set_row(i,65)
        if name=='Read Me':s.set_column(1,1,125,wrap)
    w.close();temp.replace(path);return path

def verify(paths,rows,counts):
    counts_numeric=counts_na=0
    for path in paths:
        if path.suffix=='.xls':
            b=xlrd.open_workbook(path);s=b.sheet_by_name('Accuracy')
            assert s.nrows==53 and s.ncols==7
            assert s.row_values(0)==HEADERS
            actual=[s.row_values(i) for i in range(1,53)]
            for i,row in enumerate(rows,1):
                for j,value in enumerate(row[1:],1):assert s.cell_type(i,j)==(xlrd.XL_CELL_TEXT if value=='N/A' else xlrd.XL_CELL_NUMBER)
        else:
            b=openpyxl.load_workbook(path,data_only=True);s=b['Accuracy']
            assert s.max_row==53 and s.max_column==7 and 'DirectionalAccuracy' in s.tables
            assert [v.value for v in s[1]]==HEADERS
            actual=[list(row) for row in s.iter_rows(min_row=2,values_only=True)]
            b.close()
        for expected,found in zip(rows,actual):
            for a,e in zip(found,expected):
                if isinstance(e,float):assert abs(a-e)<1e-14
                else:assert a==e
        # Both directions of sorting can use numbers directly, without parsing.
        for j in range(1,7):
            numeric=[r[j] for r in actual if isinstance(r[j],(int,float))]
            assert sorted(numeric,reverse=True)[0]==max(numeric)
    for row in rows:
        counts_numeric+=sum(isinstance(v,(int,float)) for v in row[1:]);counts_na+=sum(v=='N/A' for v in row[1:])
    assert counts_numeric+counts_na==312
    return dict(rows=52,accuracy_columns=6,numeric_accuracy_cells=counts_numeric,na_cells=counts_na,both_formats_reopened=True,all_cells_match_measured_source=True,xlsx_sort_filter_table=True,xls_numeric_data_sort=True,small_sample_cells=sum(0<v<100 for row in counts for v in row[1:]))

def main():
    rows,counts,warnings=data();paths=[export_xls(rows,counts,warnings),export_xlsx(rows,counts,warnings)];checks=verify(paths,rows,counts)
    write_json(ROOT/'reports/selected_directional/sortable_export.json',dict(created_at=utc_now(),source=str(SOURCE.relative_to(ROOT)),source_sha256=sha256(SOURCE.read_bytes()),export_script_sha256=sha256(Path(__file__).read_bytes()),verification=checks,files=[dict(path=str(p.relative_to(ROOT)),bytes=p.stat().st_size,sha256=sha256(p.read_bytes())) for p in paths]))
    print(checks)
    for p in paths:print(p,p.stat().st_size,'bytes')
if __name__=='__main__':main()
