from pathlib import Path
import os,sys,json,subprocess,urllib.request,csv,time,platform,hashlib
from dotenv import dotenv_values
from uuid import uuid4
import argparse
p=argparse.ArgumentParser();p.add_argument('--project',type=Path,required=True);p.add_argument('--evidence',type=Path,required=True);p.add_argument('--jmeter-home',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
root=a.project.resolve();base=a.evidence.resolve()/'performance'

os.environ.update({k:v for k,v in dotenv_values(root/'backend/.env').items() if v is not None});sys.path.insert(0,str(root/'backend'))
from sqlalchemy import select
from app.db.session import SessionLocal
from app.db.models.user import Usuario,Role
from app.core.security import create_access_token
out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
with SessionLocal() as db:
 role=db.execute(select(Role).where(Role.nombre=='auditor')).scalar_one()
 user=Usuario(email=f'course-bench-{uuid4().hex[:8]}@example.test',nombre='JMeter controlled fixture',rol_id=role.id)
 db.add(user);db.commit();db.refresh(user);identifier=user.id
 token=create_access_token(str(user.id),'auditor')
env=os.environ.copy()
property_fd=os.memfd_create('radar-bench-private-properties',0)
os.write(property_fd,('bench_token='+token+'\n').encode())
headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'}
try:
 with (base/'jmeter_features.csv').open() as stream:values=next(csv.DictReader(stream))
 features=[float(v) for v in values.values()]
 run_id='90709911-241e-4104-988d-40102c02be1c'
 request=urllib.request.Request(f'http://127.0.0.1:8000/api/v1/training/runs/{run_id}/predict',data=json.dumps({'features':features}).encode(),headers=headers,method='POST')
 result=json.load(urllib.request.urlopen(request,timeout=15));assert result['preview'] and result['model_id']=='M2'
 for path in ['/health','/ready','/api/v1/dashboard/summary?dias=30','/api/v1/leaks?limit=20']:
  with urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8000'+path,headers=headers),timeout=15) as response:assert response.status==200
 print('Preflight: API, consultas autenticadas e inferencia M2 disponibles.',flush=True)
 java_version=subprocess.run(['java','-version'],capture_output=True,text=True).stderr.splitlines()[0]
 metadata={'date':time.strftime('%Y-%m-%d'),'timezone':'America/Lima','tool':'Apache JMeter 5.6.3','java':java_version,'python':sys.version.split()[0],'platform':platform.platform(),'cpu':platform.processor() or platform.machine(),'logical_cpus':os.cpu_count(),'memory_bytes':os.sysconf('SC_PAGE_SIZE')*os.sysconf('SC_PHYS_PAGES'),'profile':{'threads':[5,15,25],'duration_seconds':20,'ramp_up_seconds':3,'pause_per_request_ms':100,'http_timeout_ms':10000,'samplers':5,'api_workers':1,'auth':'read-only fixture JWT, login excluded','training_during_load':False,'selected_run':run_id,'preview_only':True},'jmx_sha256':hashlib.sha256((base/'radar_course_benchmark.jmx').read_bytes()).hexdigest()}
 (out/'metadata.json').write_text(json.dumps(metadata,indent=2))
 jmeter=a.jmeter_home.resolve()/'bin/ApacheJMeter.jar'
 for threads in [5,15,25]:
  stem='load_'+str(threads)
  os.lseek(property_fd,0,os.SEEK_SET)
  args=['java','-Xms256m','-Xmx768m','-jar',str(jmeter),'-q','/proc/self/fd/'+str(property_fd),'-n','-t',str(base/'radar_course_benchmark.jmx'),'-l',str(out/(stem+'.jtl')),'-j',str(out/(stem+'.log')),f'-Jthreads={threads}','-Jduration=20','-Jrampup=3','-Jfeaturecsv='+str(base/'jmeter_features.csv'),'-Jjmeter.save.saveservice.output_format=csv','-Jjmeter.save.saveservice.response_data=false','-Jjmeter.save.saveservice.samplerData=false','-Jjmeter.save.saveservice.requestHeaders=false','-Jjmeter.save.saveservice.responseHeaders=false']
  with (out/(stem+'-console.txt')).open('w') as log:result=subprocess.run(args,cwd=out,env=env,stdout=log,stderr=subprocess.STDOUT,pass_fds=(property_fd,))
  print(json.dumps({'threads':threads,'exit_code':result.returncode,'raw_jtl':str(out/(stem+'.jtl'))}),flush=True)
  if result.returncode:raise SystemExit('JMeter no completó el perfil; revisar el registro local.')
  with (out/(stem+'.jtl')).open() as raw:
   if len(list(csv.DictReader(raw))) == 0:raise SystemExit('JMeter no produjo muestras; la ejecución no se considera válida.')
finally:
 os.close(property_fd)
 with SessionLocal() as db:
  user=db.get(Usuario,identifier);user.activo=False;db.commit()
 print('Identidad temporal de benchmark desactivada; no se guardó su token.',flush=True)
