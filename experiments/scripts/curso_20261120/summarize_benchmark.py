from pathlib import Path
import csv,json,math,collections
import argparse
p=argparse.ArgumentParser();p.add_argument('directory',type=Path);a=p.parse_args();base=a.directory.resolve()
def quantile(values,q):
 values=sorted(values);n=len(values);point=(n-1)*q;lo=int(point);hi=math.ceil(point);return values[lo]*(hi-point)+values[hi]*(point-lo) if hi!=lo else values[lo]
def stats(rows):
 elapsed=[float(r['elapsed']) for r in rows]
 start=min(int(r['timeStamp']) for r in rows);end=max(int(r['timeStamp'])+float(r['elapsed']) for r in rows)
 errors=sum(r['success'].lower()!='true' for r in rows)
 return {'n':len(rows),'errors':errors,'error_rate':errors/len(rows),'mean_ms':sum(elapsed)/len(elapsed),'p50_ms':quantile(elapsed,.5),'p95_ms':quantile(elapsed,.95),'p99_ms':quantile(elapsed,.99),'wall_seconds':(end-start)/1000,'throughput_rps':len(rows)/((end-start)/1000)}
results=[]
for file in sorted(base.glob('load_*.jtl'),key=lambda f:int(f.stem.split('_')[1])):
 rows=list(csv.DictReader(file.open()));groups=collections.defaultdict(list)
 for row in rows:groups[row['label']].append(row)
 results.append({'threads':int(file.stem.split('_')[1]),'overall':stats(rows),'samplers':{name:stats(group) for name,group in groups.items()},'http_codes':dict(collections.Counter(r['responseCode'] for r in rows))})
(base/'summary.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
