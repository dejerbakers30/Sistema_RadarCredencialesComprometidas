from pathlib import Path
import json
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
import argparse
p0=argparse.ArgumentParser();p0.add_argument('evidence',type=Path);args=p0.parse_args();BASE=args.evidence.resolve()
OUT=BASE/'rendered_article'
OUT.mkdir(exist_ok=True)
R=json.loads((BASE/'training/registry/runs/90709911-241e-4104-988d-40102c02be1c/record.json').read_text())
J=json.loads((BASE/'performance/summary.json').read_text())
doc=Document()
sec=doc.sections[0];sec.page_width=Inches(8.2677);sec.page_height=Inches(11.6929)
sec.top_margin=sec.bottom_margin=Inches(.866);sec.left_margin=sec.right_margin=Inches(.945)
sec.header_distance=sec.footer_distance=Inches(.35)
for name in ['Normal','Title','Subtitle','Heading 1','Heading 2','Heading 3','Caption']:
 s=doc.styles[name];s.font.name='Times New Roman';s.font.color.rgb=RGBColor(0,0,0)
 fonts=s._element.get_or_add_rPr().rFonts
 for a in ['ascii','hAnsi','eastAsia','cs']:fonts.set(qn('w:'+a),'Times New Roman')
 for a in ['asciiTheme','hAnsiTheme','eastAsiaTheme','cstheme']:fonts.attrib.pop(qn('w:'+a),None)
 for node in list(s._element.iter(qn('w:pBdr'))):node.getparent().remove(node)
normal=doc.styles['Normal'];normal.font.size=Pt(11)
normal.paragraph_format.space_after=Pt(6);normal.paragraph_format.line_spacing=1.08
normal.paragraph_format.widow_control=True
for name,size in [('Title',16),('Heading 1',13),('Heading 2',11.5)]:
 s=doc.styles[name];s.font.size=Pt(size);s.font.bold=True
 s.paragraph_format.space_before=Pt(11);s.paragraph_format.space_after=Pt(6)
 s.paragraph_format.keep_with_next=True
c=doc.styles['Caption'];c.font.size=Pt(10);c.font.italic=False;c.paragraph_format.space_after=Pt(5)
c.paragraph_format.keep_with_next=True
footer=sec.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=footer.add_run();r.font.size=Pt(9)
fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');r._r.addnext(fld)
doc.core_properties.title='Radar de credenciales comprometidas con entrenamiento reproducible y evaluación multiclase de debilidad de contraseñas'
doc.core_properties.author='Luis Josmell Cruz Esquivel; Álvaro Joseph Paz Romero; Juan Pedro Santos Fernández; Robert Jerry Sánchez Ticona'
doc.core_properties.subject='Caso24 entrenamiento comparativo e integración controlada'
doc.core_properties.keywords='ciberseguridad, entrenamiento, Random Forest, n8n, JMeter'
def p(t,style=None):
 x=doc.add_paragraph(t,style);x.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY if style is None else None
 return x
def h(t,level=1):return doc.add_heading(t,level)
def cap(t):return p(t,'Caption')
def table(title,headers,rows,widths):
 cap(title)
 t=doc.add_table(rows=1, cols=len(headers));t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
 for c,w in zip(t.columns,widths):c.width=Inches(w)
 pr=t._tbl.tblPr;b=OxmlElement('w:tblBorders')
 for edge in ['top','left','bottom','right','insideH','insideV']:
  e=OxmlElement('w:'+edge);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');e.set(qn('w:color'),'D9D9D9');b.append(e)
 pr.append(b)
 for values in [headers]+list(rows):
  cells=t.rows[0].cells if values is headers else t.add_row().cells
  for i,(cell,txt) in enumerate(zip(cells,values)):
   cell.width=Inches(widths[i]);cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
   tcPr=cell._tc.get_or_add_tcPr();m=OxmlElement('w:tcMar')
   for side,v in [('top','65'),('bottom','65'),('left','85'),('right','85')]:
    q=OxmlElement('w:'+side);q.set(qn('w:w'),v);q.set(qn('w:type'),'dxa');m.append(q)
   tcPr.append(m)
   para=cell.paragraphs[0];para.paragraph_format.space_after=Pt(0);para.paragraph_format.line_spacing=1.0
   para.alignment=WD_ALIGN_PARAGRAPH.LEFT if i==0 or len(str(txt))>35 else WD_ALIGN_PARAGRAPH.CENTER
   run=para.add_run(str(txt));run.font.name='Times New Roman';run.font.size=Pt(9.5)
   if values is headers:
    run.bold=True;shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'E8EDF1');tcPr.append(shade)
  trpr=cells[0]._tc.getparent().get_or_add_trPr();ns=OxmlElement('w:cantSplit');trpr.append(ns)
 repeat=OxmlElement('w:tblHeader');t.rows[0]._tr.get_or_add_trPr().append(repeat)
 for row in t.rows[:-1]:
  for cell in row.cells:
   for para in cell.paragraphs:para.paragraph_format.keep_with_next=True
 doc.add_paragraph().paragraph_format.space_after=Pt(0)
 return t
def fig(filename,title,width=6.2):
 para=doc.add_paragraph();para.alignment=WD_ALIGN_PARAGRAPH.CENTER;para.paragraph_format.keep_with_next=True
 run=para.add_run();shape=run.add_picture(str(BASE/'figures'/filename),width=Inches(width))
 shape._inline.docPr.set('descr',title)
 cp=cap(title);cp.paragraph_format.keep_with_next=False

def pct(v):return f'{v*100:.2f}'.replace('.',',')

p('Radar de credenciales comprometidas con entrenamiento reproducible y evaluación multiclase de debilidad de contraseñas','Title')
p('Luis Josmell Cruz Esquivel¹,* · Álvaro Joseph Paz Romero¹ · Juan Pedro Santos Fernández² · Robert Jerry Sánchez Ticona²')
for text in ['¹ Escuela de Ingeniería de Sistemas, Universidad Nacional de Trujillo, Trujillo, Perú',
 '² Universidad Nacional de Trujillo, Trujillo, Perú',
 'ORCID en orden de autoría: 0009‑0001‑6273‑6844; 0009‑0005‑9014‑9275; 0000‑0002‑8882‑9256; 0000‑0001‑9387‑1945',
 '* Autor de correspondencia: Luis Josmell Cruz Esquivel, GitHub dejerbakers30']:
 x=p(text);x.paragraph_format.space_after=Pt(3)
 for run in x.runs:run.font.size=Pt(9.5)
h('Resumen')
p('La gestión de credenciales expuestas exige distinguir la presencia de una cuenta en una filtración de la debilidad de una contraseña. Este trabajo actualiza un radar basado en FastAPI, React, PostgreSQL y n8n mediante un motor reproducible de entrenamiento e inferencia auxiliar. Se compararon regresión logística, Random Forest y gradient boosting por histogramas sobre 10 000 observaciones de PWLDS, un benchmark público sintético con etiquetas de generación. Las cinco etiquetas originales se agruparon en tres niveles de debilidad. Se preservaron grupos relacionados, se reservaron 7029 observaciones para entrenamiento, 1354 para validación y 1617 para prueba, y se ejecutaron tres candidatos por algoritmo con validación cruzada de tres folds dentro del entrenamiento. Random Forest fue seleccionado por su macro F1 de validación de 95,55 %, antes de abrir la prueba. En esta obtuvo macro F1 de 93,83 %, exactitud de 94,31 % y un intervalo exploratorio por bootstrap de grupos de 85,85–96,66 %. La regla de referencia alcanzó macro F1 de 76,93 %. Las verificaciones locales cubrieron los 15 flujos de n8n con servicios simulados y comprobaron la aceptación de una firma HMAC válida y el rechazo HTTP 401 de una inválida. Apache JMeter registró 7277 solicitudes válidas sin errores HTTP en tres perfiles breves; con 25 usuarios se observaron 194,53 solicitudes/s y p95 global de 55 ms. La mejora acredita trazabilidad experimental y funcionamiento controlado. No demuestra resistencia ante ataques reales, capacidad máxima en producción ni una probabilidad de compromiso. El artefacto sintético permanece disponible para previsualización y bloqueado para activación operativa.')
p('Palabras clave: credenciales expuestas; debilidad de contraseñas; entrenamiento reproducible; clasificación multiclase; n8n; pruebas de carga.')
h('Abstract').paragraph_format.page_break_before=True
p('Managing exposed credentials requires distinguishing account exposure from password weakness. This study updates a FastAPI, React, PostgreSQL and n8n radar with a reproducible training engine and auxiliary inference. Logistic regression, Random Forest and histogram gradient boosting were compared using 10,000 observations from PWLDS, a public synthetic benchmark with generation-based labels. Five source labels were mapped to three weakness levels. Group-preserving partitions contained 7,029 training, 1,354 validation and 1,617 test observations. Three candidates per algorithm were assessed using three-fold cross-validation within the training subset. Random Forest was selected by validation macro F1 before accessing the test set. Its test macro F1 was 93.83%, accuracy was 94.31%, and an exploratory group-bootstrap interval was 85.85–96.66%. A heuristic reference reached 76.93% macro F1. Local integration checks covered 15 n8n workflows with simulated services, including valid HMAC acceptance and HTTP 401 rejection of an invalid signature. Apache JMeter recorded 7,277 valid requests with no HTTP errors across three brief profiles. At 25 users, throughput was 194.53 requests/s and overall p95 was 55 ms. The findings support experimental traceability and controlled functionality, but do not establish effectiveness against real attacks or maximum production capacity. The synthetic artifact is available for preview and cannot be activated for operational decisions.')
doc.paragraphs[-1].paragraph_format.keep_with_next=True
p('Keywords: exposed credentials; password weakness; reproducible training; multiclass classification; n8n; load testing.')

h('1 Introducción')
p('Un radar de credenciales comprometidas busca transformar avisos de exposición en hallazgos correlacionados con un directorio corporativo, acciones de respuesta y registros auditables. La consulta de filtraciones de una dirección de correo informa asociaciones con incidentes conocidos; no entrega por ese hecho la contraseña del usuario [1]. Por ello, la evaluación de composición de una contraseña requiere una entrada distinta y no puede inferirse a partir del correo consultado.')
p('Esta distinción tiene consecuencias para la arquitectura. Una cuenta expuesta, una contraseña estimada como débil y un autenticador confirmado como comprometido representan evidencias diferentes. Las recomendaciones de autenticación de NIST incluyen comprobaciones frente a listas de contraseñas comunes o comprometidas, pero no convierten umbrales locales de longitud o entropía en una probabilidad de ataque [2]. La respuesta a incidentes requiere además decisiones y trazabilidad acordes con el contexto de la organización [3].')
p('La versión anterior del proyecto contenía una discrepancia experimental: el servicio utilizaba una regresión logística multiclase entrenada con ejemplos manuales, mientras un evaluador separado analizaba Random Forest con una tarea binaria. Comparar sus porcentajes no permitía concluir que el modelo evaluado fuera el realmente utilizado por la aplicación. La actualización aborda esa discrepancia mediante un único esquema de variables, un protocolo compartido y la persistencia del mismo artefacto que se evalúa.')
p('El objetivo es implementar y verificar un motor de entrenamiento auxiliar al Caso24, comparar tres algoritmos para una misma tarea y documentar resultados predictivos y de software por separado. Se plantearon tres preguntas: qué desempeño obtienen los modelos bajo particiones comunes y sin grupos compartidos; si la aplicación puede consultar el artefacto seleccionado sin volver a entrenarlo; y qué comportamiento muestran la orquestación y la API bajo verificaciones locales. La contribución se concentra en la trazabilidad del experimento y la integración, con límites explícitos sobre la validez externa.')

h('2 Fundamento y trabajos relacionados')
p('Los medidores de contraseñas aproximan dificultad de adivinación o aplican criterios de composición; su salida depende del modelo de amenaza y de los datos utilizados. zxcvbn constituye una referencia práctica de estimación basada en patrones [4]. El presente estudio usa ocho características agregadas y etiquetas sintéticas, de modo que no evalúa equivalencia con el número de intentos de un atacante ni sustituye una comprobación de contraseña comprometida.')
p('Random Forest permite representar relaciones no lineales mediante conjuntos de árboles [5]. La regresión logística aporta una referencia regularizada y el boosting por histogramas ofrece otro mecanismo no lineal dentro de la misma biblioteca. Las tres familias están implementadas en scikit-learn [6]. Elegirlas permite comparar complejidad y desempeño sin añadir infraestructura de aprendizaje profundo para una entrada tabular de ocho dimensiones.')
p('La separación por grupos y el ajuste del preprocesamiento dentro de cada fold reducen formas concretas de fuga de información [7,8]. Sin embargo, una partición correcta no valida por sí misma las etiquetas. PWLDS ofrece datos sintéticos con niveles de generación y licencia abierta [9]; resulta útil para ejercitar el motor y comparar algoritmos bajo una referencia compartida, pero exige reconocer los sesgos del generador y del muestreo.')

h('3 Materiales y métodos')
h('Diseño y unidad de análisis',2)
p('Se realizó un estudio aplicado de desarrollo tecnológico con evaluación computacional controlada, ejecutada el 20 de noviembre de 2026. La unidad predictiva fue una observación de contraseña sintética representada por un vector numérico. La población accesible estuvo formada por los prefijos muestreados de cinco archivos públicos de PWLDS, no por usuarios de la Universidad ni por credenciales corporativas reales. La variable objetivo fue el nivel de debilidad de referencia en las clases Bajo, Medio y Crítico. No hubo seguimiento temporal ni etiquetas de toma de cuentas.')
p('La predicción puede apoyar una revisión educativa o una política auxiliar de calidad de contraseñas cuando existan datos autorizados. En esta evaluación no se conectó a una decisión real de contención. Los nombres Bajo, Medio y Crítico designan clases de debilidad y no probabilidades operativas. La exposición del correo se determina por la fuente de filtraciones, mientras la respuesta se gobierna por la evidencia y la política del radar.')
h('Arquitectura y separación de funciones',2)
p('La solución conserva FastAPI para la API, React para el panel, PostgreSQL para usuarios, hallazgos y auditoría, y n8n para la orquestación. El laboratorio incorpora validación de datasets, EDA, configuración individual de M1–M3, seguimiento de ejecuciones, comparación y registro de artefactos. Los trabajos largos se ejecutan en un proceso separado y un bloqueo limita las ejecuciones simultáneas. La cancelación y el presupuesto se comprueban entre ajustes; no interrumpen instantáneamente un ajuste interno.')
p('El evaluador y la aplicación utilizan el mismo constructor de modelos y el mismo orden de variables. Se persisten el pipeline o estimador, su hash, el esquema y la versión de la biblioteca. La inferencia de previsualización recibe únicamente ocho características, verifica el artefacto y no reentrena por petición. Los modelos sintéticos no pueden activarse como modelo operativo. Sin un artefacto autorizado activo, el motor mantiene su alternativa explícita de reglas. Un resultado auxiliar de debilidad baja no convierte automáticamente una exposición confirmada en falso positivo.')

fig('figura1_metodologia.png','Figura 1. Secuencia del experimento desde la procedencia de los datos hasta la inferencia verificada. La selección se congela antes de evaluar la prueba final.')
h('Fuente de datos y muestreo',2)
p('Se utilizó PWLDS de Infinitode Pty Ltd, con atribución y licencia CC BY 4.0 [9,10], fijando el commit c16f18d080e41b54da727445d0505f2c74d53f6a. Se leyó un prefijo de 50 000 registros de cada uno de cinco archivos y se seleccionaron 2000 observaciones por archivo mediante muestreo reservoir, con semilla 20261120 más el identificador de clase. El marco accesible fue, por tanto, de 250 000 registros y la muestra fue de 10 000. No se afirma un muestreo aleatorio del repositorio completo: la restricción a prefijos puede introducir sesgo de orden.')
p('Las etiquetas originales se mapearon antes del entrenamiento: 0 y 1 a Crítico, 2 a Medio, y 3 y 4 a Bajo. El mapeo invierte la orientación de fortaleza para expresar debilidad y produce 4000, 2000 y 4000 observaciones, respectivamente. Las etiquetas proceden del proceso sintético de generación; no fueron asignadas por expertos ni por resultados de ataques. Se conservaron características, clases e identificadores opacos. No se guardaron cadenas de contraseña en las evidencias del estudio.')
h('EDA y representación de las observaciones',2)
p('El EDA verificó el esquema, finitud, rangos, coherencia de proporciones y distribución por clase. No hubo imputación ni eliminación de observaciones para mejorar las métricas. Se conservaron 113 vectores de características asociados a más de una etiqueta, ya que contraseñas distintas pueden compartir las ocho características. Se registraron 6739 repeticiones de vectores respecto de 3261 vectores únicos; esta cifra no equivale a 6739 contraseñas duplicadas. La longitud varió entre 2 y 32 caracteres, con media 12,3588, y la entropía empírica entre 0,5033 y 5,0000 bits, con media 3,0949.')
table('Tabla 1. Características comunes de entrada', ['Variable','Definición'],[
 ('length','Número de caracteres'),('entropy','Entropía de Shannon de las frecuencias de caracteres de la cadena'),
 ('digits_ratio','Proporción de caracteres numéricos'),('uppercase_ratio','Proporción de mayúsculas'),
 ('symbols_ratio','Proporción de símbolos'),('common_pattern','Indicador de coincidencia con el repertorio local de patrones'),
 ('only_letters_or_digits','Indicador de cadena solo alfabética o solo numérica'),('num_symbols','Número de símbolos')],[1.55,4.8])
p('La entropía calculada describe la distribución interna de caracteres de una cadena; no es una medida directa de seguridad criptográfica ni de resistencia a un atacante con diccionarios. Las características de composición tampoco identifican toda la similitud semántica entre variantes. Esa restricción afecta a la interpretación de los grupos y del desempeño.')
h('Grupos y particiones independientes',2)
p('Se identificaron familias por la huella de la cadena normalizada con casefold y se unieron adicionalmente los grupos cuyos vectores eran idénticos. Los identificadores importados se transformaron con HMAC y una sal aleatoria; el dataset consolidado produjo 3259 grupos. Se buscaron 120 particiones candidatas por grupos, con semilla de base 42, para aproximar 70/15/15 y conservar las tres clases. La elección de partición minimizó desviaciones de tamaño y proporción de clases, sin consultar predicciones ni desempeño de los modelos. Se priorizó la integridad del grupo sobre porcentajes exactos.')
table('Tabla 2. Partición efectiva conservada para todos los algoritmos',['Conjunto','Filas','Grupos','Bajo','Medio','Crítico'],[
 (name,R['partition'][k]['rows'],R['partition'][k]['groups'],R['partition'][k]['classes']['Bajo'],R['partition'][k]['classes']['Medio'],R['partition'][k]['classes']['Crítico'])
 for name,k in [('Entrenamiento 70,29 %','train'),('Validación 13,54 %','validation'),('Prueba 16,17 %','test')]],[2.05,.85,.85,.85,.85,.9])
p('Dentro de las 7029 filas de entrenamiento se aplicó StratifiedGroupKFold con tres folds, barajado y semilla 42 [7]. Los índices de folds y de los tres conjuntos se guardaron. Ningún grupo se compartió entre entrenamiento, validación y prueba ni entre las partes de cada fold. Una nueva importación puede cambiar las huellas saladas y, por ello, la partición sorteada; la reproducción exacta usa los arrays consolidados y los índices archivados, no una importación nueva que asuma identidad de particiones.')
h('Parametrización de los tres modelos',2)
p('M1, M2 y M3 son identificadores de tres algoritmos para la misma tarea. Parametrizar significa fijar los hiperparámetros y las condiciones del ajuste; no equivale a los coeficientes, divisiones de árboles o valores de hojas que el algoritmo aprende. Se utilizó scikit-learn 1.9.1, semilla 42 y ponderación de clases balanced. La tabla 3 separa la configuración inicial del espacio de búsqueda; los valores finalmente seleccionados se presentan en resultados.')
table('Tabla 3. Condiciones iniciales y búsqueda discreta',['Modelo','Configuración inicial','Valores candidatos'],[
 ('M1 Regresión logística','C=1; max_iter=500; tol=0,0001; solver=lbfgs; penalización L2; StandardScaler','C: 0,01; 0,1; 1; 10.\ntol: 0,0001; 0,001.'),
 ('M2 Random Forest','100 árboles; profundidad 12; mínimo 2 por hoja; max_features=sqrt; n_jobs=1','Árboles: 50; 100; 200.\nProfundidad: 6; 12; 20.\nHoja: 1; 2; 5.'),
 ('M3 Boosting por histogramas','100 iteraciones; tasa 0,1; 15 hojas; L2=1; early_stopping=False','Iteraciones: 50; 100; 200.\nTasa: 0,03; 0,1; 0,2.\nHojas: 7; 15; 31.\nL2: 0; 1; 5.')],[1.2,2.65,2.5])
p('M1 usa escalado ajustado únicamente dentro del pipeline de cada fold y en el reajuste final sobre entrenamiento. La regularización controla la magnitud de los coeficientes. M2 no requiere escalado y limita la complejidad mediante profundidad y tamaño de hojas. M3 tampoco requiere escalado y combina tasa, número de iteraciones y regularización. Se deshabilitó su parada anticipada para no introducir una partición interna aleatoria que ignore los grupos [11]. No se incluyó remuestreo sintético ni selección automática de variables.')
p('M1 termina al converger conforme a la tolerancia o al alcanzar 500 iteraciones; un aviso de no convergencia invalida ese ensayo. M2 termina al construir el número configurado de árboles, sin épocas ni parada anticipada. M3 termina en el máximo de iteraciones. El estudio admite tres ensayos por modelo y un presupuesto global de 1200 s, comprobado entre ajustes; una cancelación o fallo impide publicar la ejecución como completada. No se aplicó pruning ni se anunció reanudación de un estudio de optimización que no está implementada.')
h('Optimización y congelación de la selección',2)
p('Se empleó una búsqueda aleatoria discreta reproducible de bajo presupuesto, sin incorporar otra dependencia de optimización. El primer candidato fue la configuración inicial y los dos siguientes se obtuvieron del producto cartesiano barajado del espacio de cada modelo, evitando duplicados. Cada candidato se evaluó con los mismos tres folds y se conservó el mayor promedio de macro F1. Se ejecutaron 27 ajustes de validación cruzada, más un reajuste de cada ganador sobre las 7029 observaciones de entrenamiento.')
p('Los tres modelos reajustados se compararon una sola vez sobre validación. La regla de selección fue el mayor macro F1, con desempate en el orden M1, M2, M3. Se congeló M2 el 20 de noviembre a las 18:42:51,699 de Lima; la prueba se abrió a las 18:42:51,705. Solo después se calcularon las métricas finales de los tres algoritmos. No se reajustó con validación ni se sustituyó al ganador según la prueba. El artefacto guardado es exactamente el evaluado y utilizado en previsualización.')
h('Métricas e incertidumbre',2)
p('La métrica principal fue macro F1, promedio no ponderado de los F1 de Bajo, Medio y Crítico, para que la clase Medio no quedara dominada por las otras dos. Se calcularon precisión, sensibilidad y F1 por clase, matriz de confusión y balanced accuracy. Como medidas complementarias se registraron average precision macro uno contra el resto, ROC AUC macro, Brier multiclase definido como el promedio de la suma de errores cuadrados de las tres probabilidades, y pérdida logarítmica. No se calibraron probabilidades ni se interpretaron como riesgo de ataque.')
p('El intervalo exploratorio de macro F1 se estimó con 200 remuestreos bootstrap de los grupos de prueba, con reposición, conservando todas las filas de cada grupo y semilla 42. Se usaron percentiles 2,5 y 97,5. Se conservaron predicciones pareadas de los modelos, pero no se realizó una prueba inferencial de superioridad. Los folds dependientes no se trataron como réplicas independientes. Se añadieron dos referencias: predicción de la clase mayoritaria y una regla fija que devuelve Crítico si longitud < 8 o hay patrón común, Bajo si longitud ≥ 14 y entropía ≥ 3, y Medio en el resto. La regla es local y no se atribuye a NIST.')
h('Verificación de la orquestación',2)
p('Se utilizaron n8n 2.46.6, un directorio de identidades .test, endpoints locales de HIBP e IdP, y Mailpit para capturar notificaciones. Los 15 flujos se ejecutaron manualmente o como subflujos y permanecieron sin programación activa. W01–W03 cubrieron recolección, correlación y contención simulada con entradas positivas. W04 procesó un reintento pendiente y actualizó el estado de contención. W08 verificó HMAC SHA 256 sobre los bytes originales del cuerpo; se contrastaron una firma válida y una inválida. W12 se ejercitó con un evento de error inyectado y después se restauró su Error Trigger original; esa prueba no valida el disparo automático en producción.')
p('Las correcciones de integración incluyeron referencias de subflujos compatibles con la instancia, sincronización de ambas respuestas del IdP antes de evaluar W04, y una respuesta HTTP 401 para una firma inválida. Los intentos de diagnóstico fallidos se conservaron separados de las ejecuciones finales válidas. Las acciones de reset y revocación se dirigieron exclusivamente a fixtures. No se probaron en esta ronda todas las ramas de agotamiento, fallos permanentes o caída de servicios externos.')
h('Protocolo de carga HTTP',2)
p('Se ejecutó Apache JMeter 5.6.3 en modo no gráfico y se conservaron los registros JTL [12]. Se midieron tres perfiles de 5, 15 y 25 usuarios, con duración configurada de 20 s, rampa de 3 s y pausa constante de 100 ms antes de cada solicitud. Cada bucle incluyó salud, disponibilidad, resumen del panel, consulta paginada de hallazgos y previsualización de M2. Las peticiones protegidas usaron un JWT temporal de solo lectura; la obtención del token y el inicio de sesión quedaron fuera de la medición. Se usaron 500 vectores numéricos del benchmark para la previsualización.')
p('Se definió error como muestra HTTP fallida o con estado distinto de 200. El tiempo de respuesta se tomó del campo elapsed, no del tiempo hasta el primer byte. Los percentiles se calcularon por interpolación lineal sobre las muestras de cada perfil. El rendimiento se obtuvo como número de solicitudes dividido entre el tiempo desde el inicio de la primera hasta el fin de la última respuesta. Se excluyó un preflight con cero muestras debido a incompatibilidad del motor de scripts con Java 26; el plan definitivo evitó ese componente y exigió JTL no vacíos.')
p('La API tuvo un trabajador y no hubo entrenamiento concurrente durante las mediciones. API, base de datos y generador de carga compartieron una laptop Intel Core i5 11320H a 3,20 GHz, ocho procesadores lógicos y aproximadamente 14,9 GiB de RAM. Se emplearon Python 3.14.4, NumPy 2.5.4, joblib 1.6.0 y Java 26.0.2. Los perfiles breves no incluyeron TLS, latencia de Internet, contenciones n8n por solicitud ni recuperación de fallos. La pausa limita la tasa ofrecida; no se buscó un punto de saturación.')
h('Registro y reproducibilidad',2)
p('La ejecución se identificó como 90709911-241e-4104-988d-40102c02be1c. El paquete experimental conserva manifiesto de procedencia y licencia, CSV derivado, arrays sin cadenas de contraseña, particiones, ensayos, predicciones, tres artefactos y sus hashes. El código base corresponde al commit 9d0510bceebc4ce0ccd1e00b8d3e7baffe6b59c4 con modificaciones locales; una instantánea de las fuentes de entrenamiento permite verificar su correspondencia con los hashes del registro. El paquete de evidencias no contiene contraseñas de acceso, tokens de integración ni los cuerpos privados de ejecución de n8n. La persistencia de modelos requiere cargar únicamente artefactos de confianza y mantener compatibilidad de dependencias [13].')

h('4 Resultados')
h('Comparación predictiva bajo un protocolo común',2)
rows=[]
for k in ['M1','M2','M3']:
 m=R['models'][k];ci=m['test']['uncertainty']['macro_f1_95_ci']
 rows.append((k,pct(m['cv_macro_f1']),pct(m['validation']['macro_f1']),pct(m['test']['macro_f1']),pct(ci[0])+'–'+pct(ci[1]),f"{m['training_seconds']:.3f}".replace('.',',')))
table('Tabla 4. Macro F1 por etapa e intervalo exploratorio en prueba',['Modelo','CV %','Validación %','Prueba %','IC 95 % prueba','Tiempo s'],rows,[.7,.85,1, .9,1.9,1])
p('Los tiempos incluyen búsqueda, ajustes y mediciones previas a la prueba dentro de cada bloque de modelo; no representan únicamente un ajuste final. No hubo ensayos sin convergencia en la ejecución completada. Los tres modelos conservaron como mejor candidato su configuración inicial dentro del presupuesto de tres ensayos: esto no implica optimalidad global. La ejecución completa tardó aproximadamente '+f"{R['elapsed_seconds']:.2f}".replace('.',',')+' s, incluyendo la evaluación final y el bootstrap.')
p('M2 alcanzó el mejor macro F1 de validación, 95,55 %, y fue seleccionado conforme al criterio congelado. Su macro F1 de prueba fue 93,83 %, frente a 88,43 % de M1 y 94,94 % de M3. El mayor valor de prueba de M3 se reporta como resultado descriptivo, sin modificar retrospectivamente la selección. Los intervalos exploratorios se superponen y no sustentan una afirmación de superioridad estadística. La referencia mayoritaria obtuvo 18,67 % y la regla fija 76,93 % de macro F1.')
fig('figura3_comparacion.png','Figura 2. Comparación de macro F1 de validación y prueba. Las barras de incertidumbre corresponden al bootstrap de grupos en prueba y no a réplicas independientes de entrenamiento.')
p('La diferencia entre M2 y la regla fue de 16,90 puntos porcentuales de macro F1 en este benchmark. Esa diferencia caracteriza la reproducción de etiquetas sintéticas mediante relaciones de composición y patrones. No demuestra una mejora de igual magnitud en detección de filtraciones, prevención de intrusiones o reducción de incidentes.')
h('Errores del artefacto seleccionado',2)
table('Tabla 5. Desempeño de M2 por clase en prueba',['Clase','Precisión %','Sensibilidad %','F1 %','Soporte'],[
 (k,pct(R['models']['M2']['test']['per_class'][k]['precision']),pct(R['models']['M2']['test']['per_class'][k]['recall']),pct(R['models']['M2']['test']['per_class'][k]['f1-score']),int(R['models']['M2']['test']['per_class'][k]['support'])) for k in ['Bajo','Medio','Crítico']],[1.3,1.4,1.4,1.2,1.05])
p('De 629 observaciones Crítico, M2 clasificó 581 correctamente, 42 como Medio y 6 como Bajo. La precisión de Crítico fue 100 % dentro de esta muestra, mientras su sensibilidad fue 92,37 %; por tanto, no corresponde afirmar ausencia de omisiones. De 609 observaciones Bajo, 38 se elevaron a Medio. La clase Medio concentró el menor valor de precisión, 82,34 %, debido a las asignaciones procedentes de las otras dos clases.')
fig('figura2_matrices.png','Figura 3. Matrices de confusión de los tres modelos sobre las mismas 1617 observaciones. Las filas representan la clase de referencia y las columnas la predicción.')
p('M2 obtuvo exactitud de 94,31 %, balanced accuracy de 94,85 %, average precision macro de 0,9847 y ROC AUC macro de 0,9943. El Brier multiclase fue 0,0749 y la pérdida logarítmica 0,1465. Estas métricas probabilísticas describen ajuste a las clases de referencia y no calibración frente a ataques. El artefacto ocupó 2 151 169 bytes. El tiempo de predicción y probabilidades en lote fue 0,0146 ms por fila, una medición distinta del tiempo HTTP de la aplicación.')
h('Integración de artefactos y flujos',2)
p('La previsualización de la aplicación utilizó el M2 persistido en la ejecución seleccionada, conservando el orden del esquema password-features-v1 y verificando su hash. La activación operativa del dataset sintético permaneció bloqueada. El panel permite consultar procedencia, clases, particiones, ensayos, métricas y artefactos mediante temas claro y oscuro. La suite de backend finalizó con 34 pruebas satisfactorias; la verificación previa del frontend incluyó 12 pruebas y construcción de la aplicación.')
table('Tabla 6. Evidencia de integración final en n8n',['Flujos','Caso verificado','Ejecución representativa'],[
 ('W01 W02 W03','Recolección positiva, correlación y contención con IdP simulado','1442; 1444; 1446'),
 ('W04','Reintento pendiente con reset y revocación exitosos','1466'),
 ('W05 W06','Notificación al usuario y alerta al administrador','1430; 1433'),
 ('W07','Verificación de la cadena de auditoría','1419'),
 ('W08','HMAC válido aceptado y firma inválida rechazada con HTTP 401','1468; 1471'),
 ('W09 W10 W11','Reporte por correo local, sincronización y salud de fuente simulada','1458; 1437; 1459'),
 ('W12','Formateo, alerta y auditoría de evento inyectado','1461'),
 ('W13 W14 W15','Auditoría, hash canónico y notificación local','1426; 1424; 1428')],[1.05,3.75,1.55])
p('Los identificadores corresponden a la instancia local y permiten localizar los registros depurados. Una ejecución de rechazo HMAC aparece como exitosa en n8n porque completó correctamente la rama HTTP 401; no significa que la firma se aceptara. La cobertura funcional no constituye una estimación de tasa de éxito con réplicas ni una medición de disponibilidad de servicios reales. Las notificaciones se capturaron en el entorno local.')
h('Comportamiento de la API con JMeter',2)
table('Tabla 7. Solicitudes HTTP observadas por perfil de carga',['Usuarios','Muestras','Errores','Media ms','p95 ms','p99 ms','Solicitudes s'],[
 (x['threads'],x['overall']['n'],0,f"{x['overall']['mean_ms']:.2f}".replace('.',','),f"{x['overall']['p95_ms']:.0f}",f"{x['overall']['p99_ms']:.2f}".replace('.',','),f"{x['overall']['throughput_rps']:.2f}".replace('.',',')) for x in J],[.65,.85,.65,1.05,.8,.9,1.45])
p('Se conservaron 7277 solicitudes válidas y todas devolvieron HTTP 200. El perfil de 25 usuarios produjo 3857 muestras en una ventana efectiva de 19,827 s, con media global de 19,64 ms, p95 de 55 ms y rendimiento de 194,53 solicitudes/s. Para la previsualización de M2, los p95 fueron 19,00 ms, 30,85 ms y 75,90 ms con 5, 15 y 25 usuarios, respectivamente. La mayor latencia de la inferencia respecto a salud y disponibilidad es coherente con una operación adicional, aunque el experimento no aísla causalmente cada componente del tiempo.')
fig('figura4_jmeter.png','Figura 4. Rendimiento y p95 de respuesta bajo tres perfiles locales breves. El p95 global mezcla cinco tipos de solicitud; el de previsualización considera únicamente la inferencia HTTP de M2.')
p('El crecimiento de la tasa y de los percentiles al aumentar usuarios describe el rango observado bajo la pausa y la duración fijadas. No se midió capacidad máxima, estabilidad prolongada ni tasa de incidentes evitados. Cero errores en esta ventana no equivale a garantía de disponibilidad futura.')

h('5 Discusión')
p('La mejora principal respecto al motor previo consiste en establecer correspondencia verificable entre datos, protocolo, modelo evaluado y artefacto consultado por la aplicación. La selección entre tres familias se realiza con una tarea multiclase común y con preprocesamiento encapsulado. El conjunto de validación cumple una función diferente de la validación cruzada, y la prueba no interviene en el criterio de selección. Esto corrige una ambigüedad del evaluador histórico, pero no convierte automáticamente el benchmark en evidencia sobre cuentas comprometidas.')
p('El modelo aprende etiquetas definidas por un generador. Su buen resultado puede reflejar regularidades de ese generador, como longitud, composición o patrones, más que dificultad de adivinación frente a un adversario. Los 113 vectores con etiquetas múltiples exponen además una pérdida de información de la representación: un clasificador determinista de ocho variables no distingue todas las cadenas que comparten esa representación. Conservar esas observaciones evita mejorar artificialmente el resultado eliminando casos difíciles.')
p('La agrupación reduce contaminación por cadenas normalizadas y por vectores idénticos, pero no garantiza independencia de todas las variantes semánticas ni de las familias del generador. La muestra restringida a prefijos, la orientación lingüística de la fuente y la ausencia de un conjunto externo impiden generalizar a la población corporativa objetivo. Los intervalos bootstrap reflejan variación entre los grupos observados, condicionada al conjunto y al modelo entrenado; no incluyen incertidumbre de una nueva fuente ni de todo el proceso de selección.')
p('M3 presentó una prueba superior a M2 en 1,11 puntos porcentuales de macro F1. Elegir M3 a partir de ese resultado reutilizaría la prueba para seleccionar. Se conserva M2 y se registra la diferencia para una futura réplica independiente. El presupuesto de tres candidatos por algoritmo es deliberadamente modesto y no permite afirmar que se alcanzaron hiperparámetros óptimos ni una comparación exhaustiva de familias.')
p('Los resultados actuales tampoco se comparan directamente con la exactitud de 99,20 % del evaluador binario del manuscrito anterior. Cambiaron la fuente, el etiquetado, las clases y los grupos. Tampoco las latencias HTTP actuales sustituyen tiempos históricos de flujos completos que incluían esperas deliberadas y llamadas a otros servicios. Un estudio antes y después requiere conservar tarea, población y protocolo, o justificar explícitamente el cambio de estimando.')
p('La integración mostró defectos reparables que no eran visibles en la métrica predictiva: referencias de subflujos incompatibles, evaluación prematura de respuestas paralelas y verificación de HMAC sobre una reconstrucción del JSON. Las verificaciones posteriores documentan las rutas corregidas en el sandbox. Aun así, se requieren pruebas adicionales de reintento agotado, errores permanentes y disparo automático del manejador de errores antes de establecer cobertura de fallos de producción.')
p('Las mediciones JMeter aportan evidencia de respuesta de la API e inferencia de previsualización durante aproximadamente un minuto agregado de perfiles cortos. No acreditan un sistema resistente a ataques de denegación de servicio ni un servicio operativo de alta disponibilidad. Se necesitan réplicas de mayor duración, aislamiento del generador, pruebas de autenticación y medición con integraciones autorizadas. Del mismo modo, no se ha cuantificado una reducción de carga de analistas o de incidentes atribuible al componente de aprendizaje.')

h('6 Conclusiones')
p('Se integró un motor de entrenamiento reproducible que compara regresión logística, Random Forest y boosting por histogramas bajo un único esquema, grupos conservados y separación entre optimización, selección y prueba. Random Forest fue seleccionado por validación y alcanzó macro F1 de prueba de 93,83 % en 1617 observaciones de un benchmark público sintético. El mismo artefacto se consultó desde la aplicación sin reentrenamiento y con trazabilidad de versión y hash.')
p('La orquestación se verificó mediante casos controlados de los 15 flujos de n8n y la API registró 7277 solicitudes JMeter sin errores HTTP en los perfiles evaluados. Estos hallazgos sostienen el funcionamiento local y la separación entre evaluación predictiva y operacional. La principal limitación es que las etiquetas representan niveles sintéticos de debilidad. Una validación independiente y autorizada, con etiquetas pertinentes al objetivo operativo y cobertura de fallos, es necesaria antes de activar el modelo para decisiones reales o afirmar mejoras frente a ataques.')
h('Disponibilidad de datos y código')
p('La fuente pública es PWLDS [9], distribuida con licencia CC BY 4.0 [10]. El paquete experimental conserva únicamente representaciones derivadas, etiquetas y huellas opacas, junto con manifiestos y registros reproducibles. El código se basa en el repositorio del radar [14] con modificaciones locales identificadas por hashes; no se atribuye al commit público base la totalidad de esta actualización. Los archivos JTL, el plan JMX y los resúmenes depurados acompañan la versión de evaluación.')
h('Consideraciones éticas y asistencia de herramientas')
p('No se consultaron cuentas corporativas reales ni se ejecutaron cambios de credenciales sobre identidades reales durante esta actualización. Las salidas de integración se dirigieron a fixtures y al correo local. Se utilizó asistencia de OpenAI Codex para modificaciones de software, análisis de registros y apoyo a la redacción. Los resultados numéricos proceden de ejecuciones conservadas; la revisión científica, la autoría y la aprobación de la versión remitida corresponden a los autores.')
h('Referencias')
refs=[
 'Have I Been Pwned. API v3. Documentación de consultas de cuentas, dominios y contraseñas. https://haveibeenpwned.com/API/v3. Consulta: 20 de noviembre de 2026.',
 'National Institute of Standards and Technology. Digital Identity Guidelines Authentication and Authenticator Management. NIST SP 800-63B-4, 2025. https://doi.org/10.6028/NIST.SP.800-63B-4.',
 'National Institute of Standards and Technology. Incident Response Recommendations and Considerations for Cybersecurity Risk Management A CSF 2.0 Community Profile. NIST SP 800-61 Rev. 3, 2025. https://doi.org/10.6028/NIST.SP.800-61r3.',
 'Wheeler DL. zxcvbn: Low-Budget Password Strength Estimation. 25th USENIX Security Symposium, 2016. https://www.usenix.org/conference/usenixsecurity16/technical-sessions/presentation/wheeler.',
 'Breiman L. Random Forests. Machine Learning. 2001;45:5–32. https://doi.org/10.1023/A:1010933404324.',
 'Pedregosa F, Varoquaux G, Gramfort A, et al. Scikit-learn: Machine Learning in Python. Journal of Machine Learning Research. 2011;12:2825–2830. https://jmlr.org/papers/v12/pedregosa11a.html.',
 'scikit-learn developers. StratifiedGroupKFold. Documentación 1.9.1. https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedGroupKFold.html. Consulta: 20 de noviembre de 2026.',
 'scikit-learn developers. Common pitfalls and recommended practices. https://scikit-learn.org/stable/common_pitfalls.html. Consulta: 20 de noviembre de 2026.',
 'Infinitode Pty Ltd. PWLDS. Dataset sintético de niveles de fortaleza de contraseñas, 2024. Commit c16f18d080e41b54da727445d0505f2c74d53f6a. https://github.com/Infinitode/PWLDS/tree/c16f18d080e41b54da727445d0505f2c74d53f6a.',
 'Creative Commons. Attribution 4.0 International. https://creativecommons.org/licenses/by/4.0/. Consulta: 20 de noviembre de 2026.',
 'scikit-learn developers. HistGradientBoostingClassifier. Documentación 1.9.1. https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.HistGradientBoostingClassifier.html. Consulta: 20 de noviembre de 2026.',
 'Apache Software Foundation. Apache JMeter User Manual Listeners. https://jmeter.apache.org/usermanual/listeners.html. Consulta: 20 de noviembre de 2026.',
 'scikit-learn developers. Model persistence. https://scikit-learn.org/stable/model_persistence.html. Consulta: 20 de noviembre de 2026.',
 'Cruz Esquivel LJ y colaboradores. Sistema Radar Credenciales Comprometidas. Repositorio de software. https://github.com/dejerbakers30/Sistema_RadarCredencialesComprometidas. Versión base identificada en el registro experimental.'
]
for i,t in enumerate(refs,1):
 x=p(f'[{i}] {t}');x.alignment=WD_ALIGN_PARAGRAPH.LEFT;x.paragraph_format.line_spacing=1.0;x.paragraph_format.space_after=Pt(5)
 for run in x.runs:run.font.size=Pt(9.5)
file=OUT/'Articulo_Radar_Caso24_Entrenamiento_Actualizado.docx';doc.save(file)
print(file)
print('paragraphs',len(doc.paragraphs),'tables',len(doc.tables),'words',sum(len(x.text.split()) for x in doc.paragraphs))
