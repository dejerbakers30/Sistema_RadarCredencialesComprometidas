from pathlib import Path
from xml.etree import ElementTree as E
import csv,json
import argparse
p=argparse.ArgumentParser();p.add_argument('evidence',type=Path);a=p.parse_args();base=a.evidence.resolve()/'performance'
run='90709911-241e-4104-988d-40102c02be1c'
root=E.Element('jmeterTestPlan',version='1.2',properties='5.0',jmeter='5.6.3');outer=E.SubElement(root,'hashTree')
plan=E.SubElement(outer,'TestPlan',guiclass='TestPlanGui',testclass='TestPlan',testname='Radar Curso API e inferencia de vista previa')
def prop(node,name,value,tag='stringProp'):E.SubElement(node,tag,name=name).text=str(value)
prop(plan,'TestPlan.comments','Experimento local de lectura e inferencia exploratoria; no ejecuta contención ni entrenamiento.')
h=E.SubElement(outer,'hashTree')
headers=E.SubElement(h,'HeaderManager',guiclass='HeaderPanel',testclass='HeaderManager',testname='Cabeceras sin persistir secretos')
col=E.SubElement(headers,'collectionProp',name='HeaderManager.headers')
for name,value in [('Content-Type','application/json'),('Authorization',"Bearer ${__P(bench_token,)}")]:
 item=E.SubElement(col,'elementProp',name=name,elementType='Header');prop(item,'Header.name',name);prop(item,'Header.value',value)
E.SubElement(h,'hashTree')
csvset=E.SubElement(h,'CSVDataSet',guiclass='TestBeanGUI',testclass='CSVDataSet',testname='Características públicas derivadas')
for key,val in {'filename':'${__P(featurecsv)}','fileEncoding':'UTF-8','variableNames':'length,entropy,digits_ratio,uppercase_ratio,symbols_ratio,common_pattern,only_letters_or_digits,num_symbols','delimiter':',','shareMode':'shareMode.all'}.items():prop(csvset,key,val)
for key,val in {'ignoreFirstLine':'true','quotedData':'true','recycle':'true','stopThread':'false'}.items():prop(csvset,key,val,'boolProp')
E.SubElement(h,'hashTree')
tg=E.SubElement(h,'ThreadGroup',guiclass='ThreadGroupGui',testclass='ThreadGroup',testname='Lectura SOC y clasificación sin contención')
prop(tg,'ThreadGroup.on_sample_error','continue');controller=E.SubElement(tg,'elementProp',name='ThreadGroup.main_controller',elementType='LoopController',guiclass='LoopControlPanel',testclass='LoopController',testname='Loop')
prop(controller,'LoopController.loops','-1');prop(controller,'LoopController.continue_forever','false','boolProp')
for k,v in {'ThreadGroup.num_threads':'${__P(threads,5)}','ThreadGroup.ramp_time':'${__P(rampup,3)}','ThreadGroup.duration':'${__P(duration,20)}','ThreadGroup.delay':'0'}.items():prop(tg,k,v)
prop(tg,'ThreadGroup.scheduler','true','boolProp');prop(tg,'ThreadGroup.same_user_on_next_iteration','true','boolProp')
th=E.SubElement(h,'hashTree');timer=E.SubElement(th,'ConstantTimer',guiclass='ConstantTimerGui',testclass='ConstantTimer',testname='Pausa fija por solicitud');prop(timer,'ConstantTimer.delay','100');E.SubElement(th,'hashTree')
endpoints=[('Salud','GET','/health'),('Disponibilidad','GET','/ready'),('Dashboard','GET','/api/v1/dashboard/summary?dias=30'),('Filtraciones','GET','/api/v1/leaks?limit=20'),('Inferencia_M2_preview','POST',f'/api/v1/training/runs/{run}/predict')]
for name,method,path in endpoints:
 node=E.SubElement(th,'HTTPSamplerProxy',guiclass='HttpTestSampleGui',testclass='HTTPSamplerProxy',testname=name,enabled='true')
 for k,v in {'HTTPSampler.domain':'127.0.0.1','HTTPSampler.port':'8000','HTTPSampler.protocol':'http','HTTPSampler.path':path,'HTTPSampler.method':method,'HTTPSampler.contentEncoding':'UTF-8','HTTPSampler.connect_timeout':'3000','HTTPSampler.response_timeout':'10000'}.items():prop(node,k,v)
 for k,v in {'HTTPSampler.follow_redirects':'false','HTTPSampler.use_keepalive':'true'}.items():prop(node,k,v,'boolProp')
 args=E.SubElement(node,'elementProp',name='HTTPsampler.Arguments',elementType='Arguments');ac=E.SubElement(args,'collectionProp',name='Arguments.arguments')
 if method=='POST':
  prop(node,'HTTPSampler.postBodyRaw','true','boolProp');arg=E.SubElement(ac,'elementProp',name='',elementType='HTTPArgument');prop(arg,'HTTPArgument.always_encode','false','boolProp');prop(arg,'Argument.metadata','=')
  values=','.join('${'+key+'}' for key in ['length','entropy','digits_ratio','uppercase_ratio','symbols_ratio','common_pattern','only_letters_or_digits','num_symbols'])
  prop(arg,'Argument.value','{"features":['+values+']}')
 st=E.SubElement(th,'hashTree')
 assertion=E.SubElement(st,'ResponseAssertion',guiclass='AssertionGui',testclass='ResponseAssertion',testname='HTTP 200 obligatorio')
 strings=E.SubElement(assertion,'collectionProp',name='Asserion.test_strings');prop(strings,'200','200');prop(assertion,'Assertion.test_field','Assertion.response_code');prop(assertion,'Assertion.test_type','8','intProp');prop(assertion,'Assertion.assume_success','false','boolProp');E.SubElement(st,'hashTree')
E.indent(root,space='  ');E.ElementTree(root).write(base/'radar_course_benchmark.jmx',encoding='UTF-8',xml_declaration=True)
with (base.parent/'data/features.csv').open() as src,(base/'jmeter_features.csv').open('w',newline='') as dest:
 reader=csv.reader(src);header=next(reader)[:8];writer=csv.writer(dest);writer.writerow(header)
 for i,row in enumerate(reader):
  if i>=500:break
  writer.writerow(row[:8])
print('Plan JMeter sin credenciales incrustadas preparado; solo lectura y predicción exploratoria.')
