"""Reproduce ajustes sobre los arrays y las particiones archivadas, sin reimportar."""
from pathlib import Path
import sys,json,hashlib,argparse,platform
import numpy as np
import sklearn,joblib
from sklearn.metrics import f1_score
from threadpoolctl import threadpool_limits

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('evidence',type=Path,help='Directorio raíz del paquete de evidencias extraído')
parser.add_argument('--output',type=Path,default=Path('replay_result.json'))
a=parser.parse_args();base=a.evidence.resolve()
snapshot=base/'training/source_snapshot';sys.path.insert(0,str(snapshot))
from app.ml.training import build_model,candidates
from app.ml.schema import RunConfig,LABELS
run_dir=base/'training/registry/runs/90709911-241e-4104-988d-40102c02be1c'
r=json.loads((run_dir/'record.json').read_text());config=RunConfig.model_validate(r['config'])
for name,expected in r['environment']['code_sha256'].items():
 path=snapshot/name
 assert hashlib.sha256(path.read_bytes()).hexdigest()==expected, f'Código distinto: {name}'
assert sklearn.__version__==r['environment']['sklearn'],'Se requiere la misma versión de scikit-learn'
data_path=base/'training/registry/datasets'/r['dataset_id']/'features.npz'
assert hashlib.sha256(data_path.read_bytes()).hexdigest()==r['dataset']['features_sha256']
assert hashlib.sha256((run_dir/'partition.npz').read_bytes()).hexdigest()==r['environment']['partition_sha256']
d=np.load(data_path,allow_pickle=False);X,y,groups=d['X'],d['y'],d['groups']
split=np.load(run_dir/'partition.npz',allow_pickle=False)
for left,right in [('train','validation'),('train','test'),('validation','test')]:
 assert not set(groups[split[left]]) & set(groups[split[right]])
pred=json.loads((run_dir/'predictions.json').read_text())
result={'python':platform.python_version(),'sklearn':sklearn.__version__,'selection_unchanged':r['selected_model'],'models':{}}
with threadpool_limits(limits=1):
 for key in ['M1','M2','M3']:
  scores=[]
  for params in candidates(key,config):
   folds=[]
   for i in range(config.folds):
    tr,va=split[f'fold_{i}_train'],split[f'fold_{i}_validation']
    assert not set(groups[tr]) & set(groups[va])
    model=build_model(key,params,config.seed).fit(X[tr],y[tr])
    folds.append(f1_score(y[va],model.predict(X[va]),average='macro',labels=LABELS,zero_division=0))
   scores.append((float(np.mean(folds)),params))
  best=max(scores,key=lambda x:x[0]);assert best[1]==r['models'][key]['params']
  model=build_model(key,best[1],config.seed).fit(X[split['train']],y[split['train']])
  observed=model.predict(X[split['test']]);expected=np.array(pred['predictions'][key])
  assert np.array_equal(observed,expected),f'Predicciones distintas: {key}'
  artifact=run_dir/(key+'.joblib')
  assert hashlib.sha256(artifact.read_bytes()).hexdigest()==r['models'][key]['artifact_sha256']
  # Cargar solo este artefacto de procedencia conocida tras verificar el hash.
  persisted=joblib.load(artifact);assert np.array_equal(persisted.predict(X[split['test']]),expected)
  result['models'][key]={'cv_macro_f1':best[0],'test_macro_f1':float(f1_score(y[split['test']],observed,average='macro',labels=LABELS)),'predictions_exact_match':True}
a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False))
