"""Muestreo reproducible del prefijo público de PWLDS; no conserva contraseñas."""
from pathlib import Path
from urllib.request import urlopen,Request
import sys,csv,io,hashlib,json,random,re,concurrent.futures
import argparse
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--project',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
root=args.project.resolve()/'backend';sys.path.insert(0,str(root))
from app.services.risk_engine import extract_features
from app.ml.schema import FEATURES
out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
repo='https://api.github.com/repos/Infinitode/PWLDS'
commit='c16f18d080e41b54da727445d0505f2c74d53f6a'
files=['pwlds_very_weak.csv','pwlds_weak.csv','pwlds_average.csv','pwlds_strong.csv','pwlds_very_strong.csv']
limit=50000;sample=2000

def fetch(pair):
 category,name=pair
 url=f'https://raw.githubusercontent.com/Infinitode/PWLDS/{commit}/{name}'
 rng=random.Random(20261120+category);reservoir=[];sha=hashlib.sha256();seen=0;invalid=0
 with urlopen(url,timeout=60) as response:
  raw=response.readline();sha.update(raw);header=next(csv.reader([raw.decode('utf-8-sig')]))
  if header!=['Password','Strength_Level']:raise ValueError('Cabecera inesperada: '+name)
  while seen<limit:
   raw=response.readline()
   if not raw:break
   sha.update(raw);seen+=1
   row=next(csv.reader([raw.decode('utf-8')]))
   if len(row)!=2:invalid+=1;continue
   password=row[0]
   if row[1]!=str(category):raise ValueError('Etiqueta inesperada: '+name)
   if not password or len(password)>256:invalid+=1;continue
   # Una firma opaca conserva familias tras casefold, sin exportar el valor original.
   group=hashlib.sha256(password.casefold().encode()).hexdigest()
   values=extract_features(password)
   result=(values,['Crítico','Crítico','Medio','Bajo','Bajo'][category],group)
   eligible=seen-invalid
   if len(reservoir)<sample:reservoir.append(result)
   else:
    j=rng.randrange(eligible)
    if j<sample:reservoir[j]=result
 return reservoir,{'file':name,'url':url,'observed_rows':seen,'invalid':invalid,'sample_rows':len(reservoir),'prefix_sha256':sha.hexdigest(),'original_class':category}

with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:parts=list(pool.map(fetch,enumerate(files)))
records=[row for rows,_ in parts for row in rows]
with (out/'features.csv').open('w',newline='') as stream:
 writer=csv.writer(stream);writer.writerow([*FEATURES,'label','group_id'])
 for values,label,group in records:writer.writerow([*values,label,group])
manifest={'dataset':'PWLDS','author':'Infinitode Pty Ltd','license':'CC BY 4.0','license_url':'https://creativecommons.org/licenses/by/4.0/','repository':'https://github.com/Infinitode/PWLDS','commit':commit,'sampling':'Reservoir sample of 2000 per original class from at most the first 50000 rows per file, seed 20261120+class; not a random sample of all 15 million records.','mapping':{'0':'Crítico','1':'Crítico','2':'Medio','3':'Bajo','4':'Bajo'},'files':[meta for _,meta in parts],'features_sha256':hashlib.sha256((out/'features.csv').read_bytes()).hexdigest()}
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
(out/'provenance.json').write_text(json.dumps({'source':'PWLDS Infinitode '+commit[:12]+' sampled prefixes','license':'CC BY 4.0; Infinitode Pty Ltd 2024; https://creativecommons.org/licenses/by/4.0/','label_method':'Source five generation-based strength labels mapped 0/1=Crítico, 2=Medio, 3/4=Bajo. Public synthetic benchmark; not expert judgement or observed account compromise. Reservoir 2000 per source class within first 50000 rows, seed 20261120+class.','kind':'synthetic','authorized':True},ensure_ascii=False))
(out/'config.json').write_text(json.dumps({'seed':42,'folds':3,'trials':3,'max_seconds':1200}))
print(json.dumps({'commit':commit,'rows':len(records),'files':manifest['files']},ensure_ascii=False))
