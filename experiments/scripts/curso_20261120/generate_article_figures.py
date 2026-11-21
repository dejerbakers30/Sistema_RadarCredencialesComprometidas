from pathlib import Path
import json,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import argparse
p=argparse.ArgumentParser();p.add_argument('evidence',type=Path);a=p.parse_args();base=a.evidence.resolve();out=base/'figures';out.mkdir(exist_ok=True)
run=json.loads((base/'training/registry/runs/90709911-241e-4104-988d-40102c02be1c/record.json').read_text())
perf=json.loads((base/'performance/summary.json').read_text())
plt.rcParams.update({'font.family':'DejaVu Serif','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'white','savefig.facecolor':'white'})
fig,ax=plt.subplots(figsize=(7.2,3.6));ax.set_xlim(-.1,10.1);ax.set_ylim(-.15,4.15);ax.axis('off')
positions=[(.1,2.35),(3.5,2.35),(6.9,2.35),(6.9,.35),(3.5,.35),(.1,.35)]
texts=[('1 Fuente pública','PWLDS y licencia CC BY 4.0\nMuestreo documentado'),('2 EDA y representación','Ocho características\nGrupos y ambigüedad'),('3 Partición por grupos','Entrenamiento / validación\nPrueba con grupos separados'),('4 Entrenamiento\ny búsqueda','M1 / M2 / M3\nCV interna y 3 ensayos'),('5 Selección\ny congelación','Macro F1 de validación\nSin consultar prueba'),('6 Evaluación y registro','Prueba reservada y artefacto\nVista previa y medición HTTP')]
for (x,y),(title,body) in zip(positions,texts):
 ax.add_patch(FancyBboxPatch((x,y),2.9,1.3,boxstyle='round,pad=.035,rounding_size=.05',facecolor='#f5f7f9',edgecolor='#374151',linewidth=.8))
 ax.text(x+1.45,y+1.0,title,ha='center',va='center',fontweight='bold',fontsize=9.5)
 ax.text(x+1.45,y+.38,body,ha='center',va='center',fontsize=9,linespacing=1.6)
for start,end in [((3.05,3.0),(3.43,3.0)),((6.45,3.0),(6.83,3.0)),((8.35,2.28),(8.35,1.73)),((6.83,1.0),(6.45,1.0)),((3.43,1.0),(3.05,1.0))]:ax.annotate('',xy=end,xytext=start,arrowprops={'arrowstyle':'->','lw':1.2,'color':'#374151'})
fig.tight_layout();fig.savefig(out/'figura1_metodologia.png',dpi=240,bbox_inches='tight');plt.close(fig)
fig,axes=plt.subplots(1,3,figsize=(7.2,2.8),layout='constrained')
labels=['Bajo','Medio','Crítico']
for ax,key in zip(axes,['M1','M2','M3']):
 cm=np.array(run['models'][key]['test']['confusion_matrix']);ax.imshow(cm,cmap='Blues',vmin=0,vmax=max(sum(cm.tolist(),[])))
 ax.set_title(key+' · prueba reservada',fontsize=10,fontweight='bold');ax.set_xticks(range(3),labels);ax.set_yticks(range(3),labels);ax.set_xlabel('Predicción');ax.set_ylabel('Referencia')
 for i in range(3):
  for j in range(3):ax.text(j,i,str(cm[i,j]),ha='center',va='center',color='white' if cm[i,j]>cm.max()*.55 else '#111827',fontsize=10)
fig.savefig(out/'figura2_matrices.png',dpi=260,bbox_inches='tight');plt.close(fig)
fig,ax=plt.subplots(figsize=(7.2,3.6),layout='constrained');x=np.arange(3);width=.3
val=[run['models'][k]['validation']['macro_f1']*100 for k in ['M1','M2','M3']];test=[run['models'][k]['test']['macro_f1']*100 for k in ['M1','M2','M3']]
lo=[t-run['models'][k]['test']['uncertainty']['macro_f1_95_ci'][0]*100 for k,t in zip(['M1','M2','M3'],test)];hi=[run['models'][k]['test']['uncertainty']['macro_f1_95_ci'][1]*100-t for k,t in zip(['M1','M2','M3'],test)]
ax.bar(x-width/2,val,width,label='Validación',color='#a8bdd0');ax.bar(x+width/2,test,width,label='Prueba e IC exploratorio',color='#24557a',yerr=[lo,hi],capsize=4,error_kw={'elinewidth':1})
ax.axhline(run['rule_baseline']['macro_f1']*100,color='#7a6452',linestyle='--',label='Reglas explícitas en prueba')
ax.set_xticks(x,['M1 Logística','M2 Random Forest','M3 Hist. boosting']);ax.set_ylabel('Macro F1 (%)');ax.set_ylim(60,101);ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True);ax.legend(loc='lower right',fontsize=9)
fig.savefig(out/'figura3_comparacion.png',dpi=260,bbox_inches='tight');plt.close(fig)
fig,axes=plt.subplots(1,2,figsize=(7.2,3.3),layout='constrained');threads=[p['threads'] for p in perf]
axes[0].plot(threads,[p['overall']['throughput_rps'] for p in perf],'-o',color='#24557a');axes[0].set_ylabel('Solicitudes por segundo');axes[0].set_xlabel('Usuarios concurrentes');axes[0].set_title('Rendimiento HTTP agregado',fontsize=11)
axes[1].plot(threads,[p['overall']['p95_ms'] for p in perf],'-o',label='API agregada',color='#24557a');axes[1].plot(threads,[p['samplers']['Inferencia_M2_preview']['p95_ms'] for p in perf],'-s',label='Vista previa M2',color='#9a6648');axes[1].set_xlabel('Usuarios concurrentes');axes[1].set_ylabel('Tiempo de respuesta p95 (ms)');axes[1].set_title('Latencia HTTP',fontsize=11);axes[1].legend(fontsize=9)
for ax in axes:ax.set_xticks(threads);ax.grid(alpha=.2)
fig.savefig(out/'figura4_jmeter.png',dpi=260,bbox_inches='tight');plt.close(fig)
print('Cuatro figuras científicas generadas a partir del registro de entrenamiento y los JTL.')
