"""Arranque local de demostración; todas las integraciones de salida son fixtures."""
from pathlib import Path
import os,signal,subprocess,sys,time
from dotenv import dotenv_values

ROOT=Path(__file__).resolve().parents[1]
if not (ROOT/'backend').exists():
 ROOT=Path('/run/media/pandaman/Datos1/UNT/4to AÑO/VIII/Software II/3raunidad/Sistema_RadarCredencialesComprometidas')
env=os.environ.copy()
env.update({k:v for k,v in dotenv_values(ROOT/'backend/.env').items() if v is not None})
n8n={k:v for k,v in dotenv_values(ROOT/'n8n/.env').items() if v is not None}
secret=n8n.get('IDP_HMAC_SECRET')
service=n8n.get('RADAR_SERVICE_TOKEN')
if not secret or not service:raise SystemExit('Falta la configuración privada de sandbox en n8n/.env')
runtime=ROOT/'backend/runtime/course_lab';runtime.mkdir(parents=True,exist_ok=True,mode=0o700)
env.update({'IDP_HMAC_SECRET':secret,'IDP_WEBHOOK_HMAC_SECRET':secret,'N8N_SERVICE_TOKEN':service,
 'IDP_WEBHOOK_URL':'http://127.0.0.1:9000/idp','IDP_PROVIDER':'generic_webhook',
 'HIBP_BASE_URL':'http://127.0.0.1:9000/hibp','SMTP_HOST':'127.0.0.1','SMTP_PORT':'1025',
 'SMTP_USE_TLS':'false','REDIS_REQUIRED':'false','BACKEND_SCHEDULER_COLLECT_ENABLED':'false',
 'REPORTS_STORAGE_PATH':str(runtime/'reports'),'FIXTURE_EVIDENCE_DIR':str(runtime/'fixture_evidence'),
 'CORS_ORIGINS':'["http://localhost:5173","http://127.0.0.1:5173"]'})
children=[]
def stop(*_):
 for child in children:
  if child.poll() is None:child.terminate()
 for child in children:
  try:child.wait(timeout=10)
  except subprocess.TimeoutExpired:child.kill()
 raise SystemExit(0)
signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
for name,cmd in [('fixtures',[sys.executable,str(ROOT/'n8n/fixtures/local_sandbox.py')]),
                 ('api',[sys.executable,'-m','uvicorn','app.main:app','--host','0.0.0.0','--port','8000'])]:
 log=(runtime/(name+'.log')).open('a');os.chmod(runtime/(name+'.log'),0o600)
 child=subprocess.Popen(cmd,cwd=ROOT/'backend',env=env,stdout=log,stderr=subprocess.STDOUT)
 children.append(child)
print('Laboratorio local: API 8000, fixtures 9000; salidas dirigidas a sandbox. Ctrl+C para detener.',flush=True)
while True:
 if any(c.poll() is not None for c in children):
  print('Un servicio terminó; revisa backend/runtime/course_lab/*.log',flush=True);stop()
 time.sleep(1)
