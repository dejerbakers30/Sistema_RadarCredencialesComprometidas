import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Activity, ArrowDownToLine, ArrowRight, BrainCircuit, Check, ChevronRight, Database,
  FlaskConical, GitBranch, Loader2, Play, ShieldCheck, SlidersHorizontal, Square, Upload } from "lucide-react";
import { api, extractErrorMessage } from "@/lib/api";
import { useCan } from "@/hooks/useCan";
import "./training.css";

type Config = { seed: number; folds: number; trials: number; max_seconds: number;
  m1: { C: number; max_iter: number; tol: number };
  m2: { n_estimators: number; max_depth: number; min_samples_leaf: number };
  m3: { max_iter: number; learning_rate: number; max_leaf_nodes: number; l2_regularization: number } };
type Provenance = { source: string; license: string; label_method: string; kind: string };
type Dataset = { id: string; created_at: string; rows: number; groups: number; duplicates: number; ambiguous_feature_vectors?: number;
  source_sha256: string; provenance: Provenance; classes: Record<string, number>;
  features: { name: string; min: number; max: number; mean: number; std: number }[] };
type Metric = { macro_f1: number; balanced_accuracy: number; confusion_matrix: number[][];
  labels: string[]; pr_auc_macro_ovr: number; roc_auc_macro_ovr: number;
  brier_multiclass: number; log_loss: number; latency_ms_per_row_batch: number;
  uncertainty?: { macro_f1_95_ci: number[] }; per_class: Record<string, { precision: number; recall: number; "f1-score": number; support: number }> };
type ModelResult = { cv_macro_f1: number; train: Metric; validation: Metric; test?: Metric;
  params: Record<string, number>; training_seconds: number; artifact_bytes: number;
  artifact_sha256: string; trials: { trial: number; macro_f1?: number; status: string; fold_scores: number[] }[] };
type Run = { id: string; dataset_id: string; created_at: string; status: string; phase: string;
  progress: number; selected_model?: string; config: Config; models?: Record<string, ModelResult>;
  partition?: Record<string, { rows: number; groups: number; ratio: number }>;
  baseline?: Metric; rule_baseline?: { macro_f1: number; definition: string };
  limitations?: string[]; frozen_at?: string; test_opened_at?: string;
  environment?: Record<string, string | number>; dataset?: Dataset };
type Card = { id: string; name: string; initial: Record<string, number>; search: Record<string, number[]>;
  fixed: Record<string, unknown>; stop: string; reason: string };
type Overview = { models: Card[]; features: string[]; labels: string[]; datasets: Dataset[]; runs: Run[];
  task: string; research_status: string; active: { mode: string; run_id: string | null; selected_model?: string; kind?: string } };

const initialConfig: Config = { seed: 42, folds: 3, trials: 3, max_seconds: 600,
  m1: { C: 1, max_iter: 500, tol: 0.0001 },
  m2: { n_estimators: 100, max_depth: 12, min_samples_leaf: 2 },
  m3: { max_iter: 100, learning_rate: 0.1, max_leaf_nodes: 15, l2_regularization: 1 } };
const bounds: Record<string, [number, number, number]> = {
  C: [0.001, 100, 0.001], tol: [0.000001, 0.01, 0.000001],
  max_iter: [50, 2000, 1], n_estimators: [20, 300, 1], max_depth: [2, 30, 1],
  min_samples_leaf: [1, 20, 1], learning_rate: [0.01, 0.3, 0.01],
  max_leaf_nodes: [3, 63, 1], l2_regularization: [0, 10, 0.1],
};
const tabs = [
  { id: "data", label: "Datos y EDA", icon: Database },
  { id: "models", label: "Modelos y particiones", icon: SlidersHorizontal },
  { id: "runs", label: "Ejecuciones", icon: Activity },
  { id: "results", label: "Comparación", icon: FlaskConical },
  { id: "registry", label: "Registro", icon: ShieldCheck },
];
const kindName: Record<string, string> = { synthetic: "Sintéticos · solo verificación", heuristic: "Etiquetas heurísticas", expert: "Etiquetas de expertos" };
const statusName: Record<string, string> = { queued: "En cola", running: "Entrenando", completed: "Completado", failed: "Fallido", cancelled: "Cancelado", timed_out: "Tiempo agotado", interrupted: "Interrumpido" };
const activeRun = (run: Run) => ["running", "queued"].includes(run.status);
const pct = (n?: number) => n === undefined ? "—" : `${(100 * n).toFixed(1)} %`;
const date = (s: string) => new Date(s).toLocaleString("es-PE");

async function download(path: string, name: string) {
  const { data } = await api.get(path, { responseType: "blob" });
  const url = URL.createObjectURL(data);
  const anchor = document.createElement("a"); anchor.href = url; anchor.download = name; anchor.click();
  URL.revokeObjectURL(url);
}

export default function Training() {
  const canAdmin = useCan("admin", "config");
  const client = useQueryClient();
  const [tab, setTab] = useState("data");
  const [datasetId, setDatasetId] = useState("");
  const [selectedId, setSelectedId] = useState("");
  const [config, setConfig] = useState<Config>(initialConfig);
  const [file, setFile] = useState<File | null>(null);
  const [provenance, setProvenance] = useState<Provenance>({ source: "", license: "", label_method: "", kind: "heuristic" });
  const [authorized, setAuthorized] = useState(false);
  const [notice, setNotice] = useState("");
  const overview = useQuery({ queryKey: ["training"], queryFn: async () => (await api.get<Overview>("/training/overview")).data,
    refetchInterval: (q) => q.state.data?.runs.some(activeRun) ? 2000 : 10000 });
  const data = overview.data;
  const chosenId = selectedId || data?.runs[0]?.id;
  const runQuery = useQuery({ queryKey: ["training-run", chosenId], enabled: !!chosenId,
    queryFn: async () => (await api.get<Run>(`/training/runs/${chosenId}`)).data,
    refetchInterval: (q) => q.state.data && activeRun(q.state.data) ? 2000 : false });
  const run = runQuery.data;
  const chosenDatasetId = datasetId || data?.datasets[0]?.id || "";
  const dataset = data?.datasets.find((d) => d.id === chosenDatasetId);
  const busy = data?.runs.some(activeRun);
  const mutation = useMutation({ mutationFn: async (task: () => Promise<unknown>) => task(),
    onSuccess: () => { client.invalidateQueries({ queryKey: ["training"] }); client.invalidateQueries({ queryKey: ["training-run"] }); },
  });
  const perform = (task: () => Promise<unknown>) => { setNotice(""); mutation.mutate(task); };

  const upload = async () => {
    if (!file) return;
    const body = new FormData(); body.append("file", file);
    body.append("provenance", JSON.stringify({ ...provenance, authorized }));
    const result = await api.post<Dataset>("/training/datasets", body, { headers: { "Content-Type": "multipart/form-data" } });
    setDatasetId(result.data.id); setNotice("Dataset validado e importado. No se conservaron identificadores originales.");
  };
  const start = async () => {
    const result = await api.post<Run>("/training/runs", { dataset_id: chosenDatasetId, config });
    setSelectedId(result.data.id); setTab("runs"); setNotice("Entrenamiento iniciado en un proceso independiente.");
  };

  if (overview.isPending) return <div className="ml-loading" role="status"><Loader2 className="animate-spin" /> Conectando con el laboratorio…</div>;
  if (overview.isError || !data) return <div className="ml-lab"><div className="ml-alert" role="alert">No se pudo cargar el laboratorio. {extractErrorMessage(overview.error)} <button onClick={() => overview.refetch()}>Reintentar</button></div></div>;

  return <div className="ml-lab">
    <div className="ml-eyebrow"><span className="ml-live-dot" /> RADAR / INTELIGENCIA APLICADA <span className="ml-version">CASO 24</span></div>
    <section className="ml-hero">
      <div className="ml-hero-copy"><span className="ml-kicker">Laboratorio de modelos</span><h1>De los datos<br />a la <span>evidencia.</span></h1>
        <p>Configura, entrena y compara tres modelos de debilidad de credenciales. Cada resultado conserva su origen, su partición y el artefacto evaluado.</p>
        <div className="ml-hero-actions"><button className="ml-button ml-button-primary" onClick={() => setTab("models")}><SlidersHorizontal size={16} /> Configurar experimento <ArrowRight size={16} /></button><span className="ml-subtle">M1 · M2 · M3 / comparación reproducible</span></div>
      </div>
      <div className="ml-orbit" aria-hidden="true"><div className="ml-orbit-ring" /><div className="ml-orbit-ring ml-orbit-ring-inner" /><div className="ml-orbit-core"><BrainCircuit size={44} strokeWidth={1.3} /></div><span className="ml-node ml-node-one">M1 <i /></span><span className="ml-node ml-node-two">M2 <i /></span><span className="ml-node ml-node-three">M3 <i /></span><span className="ml-orbit-caption">UN PROTOCOLO · TRES PERSPECTIVAS</span></div>
    </section>
    <div className="ml-stats"><Stat label="Datasets disponibles" value={String(data.datasets.length)} detail="Procedencia y hash registrados" /><Stat label="Modelos por experimento" value="03" detail="Logística · Forest · Boosting" /><Stat label="Ejecuciones completas" value={String(data.runs.filter((r) => r.status === "completed").length)} detail="Métricas obtenidas por ejecución" /><Stat label="Modelo en inferencia" value={data.active.selected_model || "Reglas"} detail={data.active.mode === "registered" ? "Artefacto registrado activo" : data.active.mode === "invalid_artifact" ? "Artefacto inválido · reglas conservadoras" : "Sin modelo entrenado activo"} /></div>
    <div className="ml-scope"><ShieldCheck size={18} /><p><strong>Alcance de la IA.</strong> Estima debilidad de contraseñas; una contraseña fuerte no descarta una filtración. La detección y la contención mantienen su política independiente.</p></div>
    <nav className="ml-tabs" aria-label="Secciones del laboratorio">{tabs.map(({ id, label, icon: Icon }) => <button key={id} aria-current={tab === id ? "page" : undefined} className={tab === id ? "is-active" : ""} onClick={() => setTab(id)}><Icon size={16} />{label}</button>)}</nav>
    {mutation.isError && <div className="ml-alert" role="alert">{extractErrorMessage(mutation.error)}</div>}
    {notice && <div className="ml-notice" role="status"><Check size={16} />{notice}</div>}
    {!canAdmin && <p className="ml-subtle">Modo consulta. Importar datos, entrenar y cambiar el modelo activo requiere permiso de administración de configuración.</p>}

    {tab === "data" && <div className="ml-columns">
      <section className="ml-panel"><PanelTitle number="01" title="Datos con trazabilidad" description="CSV de características numéricas, sin contraseñas ni correos." />
        <div className="ml-panel-body"><button className="ml-button ml-button-secondary" onClick={() => perform(() => download("/training/template", "plantilla-caracteristicas.csv"))}><ArrowDownToLine size={15} /> Descargar plantilla CSV</button>
          <form className="ml-form" onSubmit={(e) => { e.preventDefault(); perform(upload); }}>
            <label className="ml-upload"><Upload size={22} /><strong>Selecciona tu dataset</strong><span>CSV UTF-8 · máximo 3 MB · 90–20000 filas</span><input type="file" accept=".csv,text/csv" disabled={!canAdmin} required onChange={(e) => setFile(e.target.files?.[0] ?? null)} /></label>
            <label>Origen y versión<input minLength={5} maxLength={300} required value={provenance.source} onChange={(e) => setProvenance({ ...provenance, source: e.target.value })} placeholder="Fuente autorizada y versión de la colección" /></label>
            <div className="ml-form-grid"><label>Licencia o autorización<input required minLength={3} maxLength={200} value={provenance.license} onChange={(e) => setProvenance({ ...provenance, license: e.target.value })} placeholder="Condiciones de uso" /></label><label>Tipo de evidencia<select value={provenance.kind} onChange={(e) => setProvenance({ ...provenance, kind: e.target.value })}>{Object.entries(kindName).map(([value, name]) => <option key={value} value={value}>{name}</option>)}</select></label></div>
            <label>Cómo se obtuvieron las etiquetas<textarea required minLength={15} maxLength={500} value={provenance.label_method} onChange={(e) => setProvenance({ ...provenance, label_method: e.target.value })} placeholder="Criterios, responsables y limitaciones del etiquetado" /></label>
            <label className="ml-checkbox"><input type="checkbox" required checked={authorized} onChange={(e) => setAuthorized(e.target.checked)} />Confirmo la autorización de uso y que el CSV no contiene contraseñas, correos ni identificadores personales.</label>
            <button className="ml-button ml-button-primary" disabled={!canAdmin || mutation.isPending || !file || !authorized}><Upload size={15} /> Validar e importar</button>
          </form>
        </div>
      </section>
      <section className="ml-panel"><PanelTitle number="02" title="Exploración del dataset" description="Calidad y distribución antes de entrenar." /><div className="ml-panel-body">
        <label className="ml-field">Dataset<select value={chosenDatasetId} onChange={(e) => setDatasetId(e.target.value)}><option value="" disabled>Selecciona un dataset</option>{data.datasets.map((d) => <option key={d.id} value={d.id}>{d.provenance.source} · {d.rows} filas</option>)}</select></label>
        {!dataset ? <Empty title="La evidencia empieza aquí" text="Importa un dataset autorizado para ver su distribución. No hay resultados precargados." /> : <>
          <span className={`ml-badge ${dataset.provenance.kind === "synthetic" ? "ml-badge-warn" : ""}`}>{kindName[dataset.provenance.kind]}</span>
          <div className="ml-mini-stats"><span><strong>{dataset.rows}</strong> observaciones</span><span><strong>{dataset.groups}</strong> grupos</span><span><strong>{dataset.duplicates}</strong> vectores repetidos</span></div>
          <p className="ml-subtle">{dataset.ambiguous_feature_vectors ?? 0} vectores comparten más de una etiqueta. Se conservan para reflejar la ambigüedad de estas características; las repeticiones de vectores no equivalen a contraseñas duplicadas.</p>
          <h3>Distribución de clases</h3><div className="ml-distribution">{data.labels.map((label, i) => <div key={label}><div><span>{label}</span><strong>{dataset.classes[label]}</strong></div><div className="ml-bar"><span style={{ width: pct(dataset.classes[label] / dataset.rows), background: ["#10b981", "#d97706", "#e0526d"][i] }} /></div></div>)}</div>
          <div className="ml-table-scroll"><table className="ml-table"><caption>Características del dataset</caption><thead><tr><th>Variable</th><th>Mín.</th><th>Media</th><th>Máx.</th><th>Desv.</th></tr></thead><tbody>{dataset.features.map((f) => <tr key={f.name}><td className="ml-mono">{f.name}</td><td>{f.min.toFixed(2)}</td><td>{f.mean.toFixed(2)}</td><td>{f.max.toFixed(2)}</td><td>{f.std.toFixed(2)}</td></tr>)}</tbody></table></div>
          <details className="ml-details"><summary>Procedencia y limitaciones</summary><p>{dataset.provenance.label_method}</p><p>Licencia: {dataset.provenance.license}</p><p className="ml-mono">SHA-256 {dataset.source_sha256}</p><p>Se unen grupos con vectores idénticos. No se garantiza detectar todas las variantes semánticas: group_id debe identificar familias relacionadas desde el origen.</p></details>
        </>}
      </div></section>
    </div>}

    {tab === "models" && <>
      <section className="ml-panel"><PanelTitle number="01" title="Un protocolo compartido" description="La independencia de los grupos tiene prioridad sobre los porcentajes exactos." /><div className="ml-panel-body">
        <div className="ml-pipeline">{["Datos y EDA", "Grupos y partición", "CV y búsqueda", "Selección", "Prueba final", "Registro"].map((step, i) => <span key={step}><i>{i + 1}</i>{step}{i < 5 && <ChevronRight size={14} />}</span>)}</div>
        <div className="ml-split"><span style={{ flex: 70 }}>70 %<small>Entrenamiento y CV interna</small></span><span style={{ flex: 15 }}>15 %<small>Validación</small></span><span style={{ flex: 15 }}>15 %<small>Prueba</small></span></div>
        <p className="ml-subtle">La búsqueda usa solo folds del entrenamiento. La validación elige entre M1, M2 y M3; la prueba se abre después de congelar esa decisión. Los tamaños finales se muestran por ejecución.</p>
        <div className="ml-form-grid ml-config-global"><label>Dataset<select value={chosenDatasetId} onChange={(e) => setDatasetId(e.target.value)}><option value="" disabled>Importa primero un dataset</option>{data.datasets.map((d) => <option key={d.id} value={d.id}>{d.provenance.source}</option>)}</select></label><NumberField label="Semilla" value={config.seed} min={0} max={2147483647} onChange={(seed) => setConfig({ ...config, seed })} /><NumberField label="Folds por grupos" value={config.folds} min={2} max={5} onChange={(folds) => setConfig({ ...config, folds })} /><NumberField label="Ensayos por modelo" value={config.trials} min={1} max={8} onChange={(trials) => setConfig({ ...config, trials })} /><NumberField label="Presupuesto en segundos" value={config.max_seconds} min={30} max={1800} onChange={(max_seconds) => setConfig({ ...config, max_seconds })} /></div>
      </div></section>
      <div className="ml-model-grid">{data.models.map((card) => <section className="ml-panel ml-model-card" key={card.id}><div className="ml-model-head"><span>{card.id}</span><BrainCircuit size={20} /></div><h2>{card.name}</h2><p>{card.reason}</p><span className="ml-badge">Configuración inicial propuesta</span><div className="ml-form">
        {Object.entries(config[card.id.toLowerCase() as "m1" | "m2" | "m3"]).map(([key, value]) => {
          const [min, max, step] = card.id === "M3" && key === "max_iter" ? [20, 300, 1] : bounds[key];
          return <NumberField key={key} label={key} value={value} min={min} max={max} step={step} onChange={(v) => setConfig({ ...config, [card.id.toLowerCase()]: { ...config[card.id.toLowerCase() as "m1" | "m2" | "m3"], [key]: v } })} />;
        })}</div><div className="ml-stop"><strong>Condición de parada</strong><p>{card.stop}</p></div><details className="ml-details"><summary>Parámetros fijos y búsqueda</summary><p className="ml-mono">{JSON.stringify(card.fixed)}</p>{Object.entries(card.search).map(([key, values]) => <p key={key}><strong>{key}</strong>: {values.join(" · ")}</p>)}</details></section>)}</div>
      <div className="ml-run-footer"><div><strong>Comparación mediante búsqueda aleatoria acotada</strong><p>El primer ensayo usa tus valores. El resto explora el espacio documentado con la misma semilla. Cancelación y presupuesto se comprueban entre ajustes.</p></div><button className="ml-button ml-button-primary" disabled={!canAdmin || !dataset || busy || mutation.isPending} onClick={() => perform(start)}>{busy ? <Loader2 size={16} className="animate-spin" /> : <Play size={16} />} {busy ? "Hay un entrenamiento activo" : "Entrenar los tres modelos"}</button></div>
    </>}

    {tab === "runs" && <div className="ml-columns ml-columns-runs"><section className="ml-panel"><PanelTitle number="01" title="Historial de ejecuciones" description="Una ejecución activa por servidor." /><div className="ml-panel-body">{!data.runs.length ? <Empty title="Sin entrenamientos todavía" text="Configura tus datos y modelos para iniciar la primera ejecución." /> : <div className="ml-run-list">{data.runs.map((r) => <button key={r.id} className={chosenId === r.id ? "is-selected" : ""} onClick={() => setSelectedId(r.id)}><span><strong className="ml-mono">{r.id.slice(0, 8)}</strong><small>{date(r.created_at)}</small></span><span className={`ml-badge ${r.status === "completed" ? "ml-badge-success" : ""}`}>{statusName[r.status] || r.status}</span></button>)}</div>}</div></section>
      <section className="ml-panel"><PanelTitle number="02" title="Seguimiento del experimento" description="Se conserva el modelo activo si un entrenamiento falla." /><div className="ml-panel-body">{runQuery.isError ? <div role="alert" className="ml-alert">No se pudo leer la ejecución. <button onClick={() => runQuery.refetch()}>Reintentar</button></div> : !run ? <Empty title="Selecciona una ejecución" text="Aquí aparecerán el progreso y las particiones realmente utilizadas." /> : <>
        <div className="ml-run-heading"><div><span className="ml-badge">{statusName[run.status]}</span><h3>{run.phase}</h3></div><span className="ml-progress-value">{run.progress} %</span></div>
        <progress aria-label="Progreso del entrenamiento" value={run.progress} max={100} />
        <p className="ml-subtle ml-mono">{run.id}</p>
        {run.dataset && <p className="ml-badge">{kindName[run.dataset.provenance.kind]}</p>}
        {run.partition && <div className="ml-table-scroll"><table className="ml-table"><caption>Particiones reales</caption><thead><tr><th>Conjunto</th><th>Filas</th><th>Grupos</th><th>Proporción</th></tr></thead><tbody>{Object.entries(run.partition).map(([name, split]) => <tr key={name}><td>{name}</td><td>{split.rows}</td><td>{split.groups}</td><td>{pct(split.ratio)}</td></tr>)}</tbody></table></div>}
        <div className="ml-actions">{activeRun(run) && <button className="ml-button ml-button-secondary" disabled={!canAdmin || mutation.isPending} onClick={() => perform(async () => { await api.post(`/training/runs/${run.id}/cancel`); setNotice("Cancelación solicitada; se aplicará entre ajustes."); })}><Square size={14} /> Solicitar cancelación</button>}{run.status === "completed" && <button className="ml-button ml-button-primary" onClick={() => setTab("results")}><FlaskConical size={16} /> Ver comparación</button>}</div>
        <details className="ml-details"><summary>Entorno y configuración reproducible</summary><pre>{JSON.stringify({ config: run.config, environment: run.environment }, null, 2)}</pre></details>
      </>}</div></section></div>}

    {tab === "results" && <section className="ml-panel"><PanelTitle number="03" title="Resultados medidos" description="El modelo se selecciona por validación, antes de abrir la prueba final." /><div className="ml-panel-body">
      <RunSelect runs={data.runs.filter((r) => r.status === "completed")} value={chosenId || ""} onChange={setSelectedId} />
      {!run?.models || run.status !== "completed" ? <Empty title="Aún no hay una comparación final" text="Selecciona una ejecución completada. Las métricas se generan durante el entrenamiento, nunca se precargan." /> : <>
        <p className="ml-evidence"><FlaskConical size={16} />{kindName[run.dataset?.provenance.kind || "heuristic"]} · La interpretación depende de la validez de las etiquetas.</p>
        <div className="ml-table-scroll"><table className="ml-table"><caption>Macro F1 por conjunto y recursos</caption><thead><tr><th>Modelo</th><th>CV interna</th><th>Entrenamiento</th><th>Validación</th><th>Prueba</th><th>Tiempo</th><th>Artefacto</th></tr></thead><tbody>{Object.entries(run.models).map(([id, m]) => <tr key={id} className={run.selected_model === id ? "ml-champion" : ""}><td><strong>{id}</strong>{run.selected_model === id && <span className="ml-badge">Seleccionado</span>}</td><td>{pct(m.cv_macro_f1)}</td><td>{pct(m.train.macro_f1)}</td><td>{pct(m.validation.macro_f1)}</td><td>{pct(m.test?.macro_f1)}</td><td>{m.training_seconds.toFixed(2)} s</td><td>{(m.artifact_bytes / 1024).toFixed(1)} KB</td></tr>)}</tbody></table></div>
        <p className="ml-subtle">Baseline de clase mayoritaria: {pct(run.baseline?.macro_f1)} · Reglas explícitas: {pct(run.rule_baseline?.macro_f1)}.</p>
        <p className="ml-subtle">{run.rule_baseline?.definition}</p>
        <div className="ml-model-grid">{Object.entries(run.models).map(([id, m]) => <section className="ml-result-card" key={id}><div className="ml-model-head"><span>{id}</span><span className="ml-subtle">PRUEBA FINAL</span></div><h3>Macro F1 <strong>{pct(m.test?.macro_f1)}</strong></h3><p className="ml-subtle">IC 95 % por grupos: {m.test?.uncertainty?.macro_f1_95_ci.map((v) => pct(v)).join(" – ") || "No disponible"}</p>
          {m.test && <><div className="ml-confusion"><table><caption>Matriz de confusión · filas reales / columnas predichas</caption><thead><tr><th scope="col">Real / pred.</th>{m.test.labels.map((l) => <th scope="col" key={l}>{l}</th>)}</tr></thead><tbody>{m.test.confusion_matrix.map((row, i) => <tr key={i}><th scope="row">{m.test!.labels[i]}</th>{row.map((v, j) => <td className={i === j ? "ml-correct" : ""} key={j}>{v}</td>)}</tr>)}</tbody></table></div><dl className="ml-metric-list"><div><dt>Balanced accuracy</dt><dd>{pct(m.test.balanced_accuracy)}</dd></div><div><dt>PR-AUC macro OvR</dt><dd>{m.test.pr_auc_macro_ovr.toFixed(3)}</dd></div><div><dt>ROC-AUC macro OvR</dt><dd>{m.test.roc_auc_macro_ovr.toFixed(3)}</dd></div><div><dt>Brier multiclase</dt><dd>{m.test.brier_multiclass.toFixed(3)}</dd></div><div><dt>Log loss</dt><dd>{m.test.log_loss.toFixed(3)}</dd></div><div><dt>Inferencia por fila en lote</dt><dd>{m.test.latency_ms_per_row_batch.toFixed(3)} ms</dd></div></dl>
            <details className="ml-details"><summary>Métricas por clase y ensayos</summary><div className="ml-table-scroll"><table className="ml-table"><thead><tr><th>Clase</th><th>Precision</th><th>Recall</th><th>F1</th></tr></thead><tbody>{m.test.labels.map((label) => <tr key={label}><td>{label}</td><td>{pct(m.test!.per_class[label].precision)}</td><td>{pct(m.test!.per_class[label].recall)}</td><td>{pct(m.test!.per_class[label]["f1-score"])}</td></tr>)}</tbody></table></div><pre>{JSON.stringify({ selected_params: m.params, trials: m.trials }, null, 2)}</pre></details></>}
        </section>)}</div>
        <div className="ml-actions"><button className="ml-button ml-button-secondary" onClick={() => perform(() => download(`/training/runs/${run.id}/export`, `experimento-${run.id}.json`))}><ArrowDownToLine size={16} /> Exportar evidencia JSON</button><button className="ml-button ml-button-primary" onClick={() => setTab("registry")}>Revisar artefacto <ArrowRight size={16} /></button></div>
        <ul className="ml-limitations">{run.limitations?.map((limitation) => <li key={limitation}>{limitation}</li>)}</ul>
      </>}
    </div></section>}

    {tab === "registry" && <section className="ml-panel"><PanelTitle number="04" title="Registro y modelo activo" description="El artefacto evaluado conserva su preprocesamiento al entrar en inferencia." /><div className="ml-panel-body"><div className="ml-registry-status"><ShieldCheck size={32} /><div><span className="ml-kicker">Inferencia actual</span><h3>{data.active.mode === "registered" ? `${data.active.selected_model} · artefacto registrado` : "Reglas conservadoras de debilidad"}</h3><p className="ml-subtle">{data.active.run_id || "No hay un modelo entrenado activo."}</p></div>{data.active.run_id && <button className="ml-button ml-button-secondary" disabled={!canAdmin || mutation.isPending} onClick={() => perform(async () => { await api.post("/training/deactivate"); setNotice("Se activaron las reglas conservadoras."); })}>Volver a reglas</button>}</div>
      <RunSelect runs={data.runs.filter((r) => r.status === "completed")} value={chosenId || ""} onChange={setSelectedId} />
      {run?.status === "completed" && run.models && run.selected_model ? <><div className="ml-artifact"><span className="ml-badge">{run.selected_model} · seleccionado por validación</span><h3>{run.id}</h3><p className="ml-mono">SHA-256 {run.models[run.selected_model].artifact_sha256}</p><p>Selección congelada: {run.frozen_at && date(run.frozen_at)}<br />Prueba abierta: {run.test_opened_at && date(run.test_opened_at)}</p><p className="ml-subtle">Las etiquetas heurísticas permiten reproducir criterios de debilidad; su rendimiento no demuestra eficacia frente a ataques reales. Los datos sintéticos no pueden activarse.</p><button className="ml-button ml-button-primary" disabled={!canAdmin || mutation.isPending || run.dataset?.provenance.kind === "synthetic" || data.active.run_id === run.id} onClick={() => perform(async () => { await api.post(`/training/runs/${run.id}/activate`); setNotice("Artefacto verificado y activado. La política de contención permanece independiente."); })}><ShieldCheck size={16} />{data.active.run_id === run.id ? "Modelo activo" : "Activar artefacto evaluado"}</button></div></> : <Empty title="Registro listo para tu primer modelo" text="Una ejecución completada genera el artefacto y su hash. Activarlo exige permiso de administración y datos no sintéticos." />}
    </div></section>}
    <footer className="ml-footer"><GitBranch size={14} /> Protocolo trazable · PostgreSQL conserva la auditoría · Evidencia para investigación, sin conclusiones fabricadas.</footer>
  </div>;
}

function Stat({ label, value, detail }: { label: string; value: string; detail: string }) { return <div className="ml-stat"><span>{label}</span><strong>{value}</strong><small>{detail}</small></div>; }
function PanelTitle({ number, title, description }: { number: string; title: string; description: string }) { return <div className="ml-panel-title"><span>{number}</span><div><h2>{title}</h2><p>{description}</p></div></div>; }
function Empty({ title, text }: { title: string; text: string }) { return <div className="ml-empty"><Database size={28} strokeWidth={1.2} /><h3>{title}</h3><p>{text}</p></div>; }
function NumberField({ label, value, min, max, step = 1, onChange }: { label: string; value: number; min: number; max: number; step?: number; onChange: (v: number) => void }) { return <label className="ml-field">{label}<input type="number" required min={min} max={max} step={step} value={value} onChange={(e) => { const v = Number(e.target.value); if (Number.isFinite(v)) onChange(v); }} /></label>; }
function RunSelect({ runs, value, onChange }: { runs: Run[]; value: string; onChange: (v: string) => void }) { return <label className="ml-field ml-run-select">Ejecución<select value={runs.some((r) => r.id === value) ? value : ""} onChange={(e) => onChange(e.target.value)}><option value="" disabled>Selecciona una ejecución completada</option>{runs.map((r) => <option key={r.id} value={r.id}>{r.id.slice(0, 8)} · {date(r.created_at)}</option>)}</select></label>; }
