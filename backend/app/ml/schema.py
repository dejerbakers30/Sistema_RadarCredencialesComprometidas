from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

FEATURES = (
    "length", "entropy", "digits_ratio", "uppercase_ratio", "symbols_ratio",
    "common_pattern", "only_letters_or_digits", "num_symbols",
)
SCHEMA_VERSION = "password-features-v1"
LABELS = ("Bajo", "Medio", "Crítico")


class Provenance(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source: str = Field(min_length=5, max_length=300)
    license: str = Field(min_length=3, max_length=200)
    label_method: str = Field(min_length=15, max_length=500)
    kind: Literal["synthetic", "heuristic", "expert"]
    authorized: Literal[True]


class LogisticConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    C: float = Field(default=1.0, ge=0.001, le=100)
    max_iter: int = Field(default=500, ge=50, le=2000)
    tol: float = Field(default=0.0001, ge=0.000001, le=0.01)


class ForestConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    n_estimators: int = Field(default=100, ge=20, le=300)
    max_depth: int = Field(default=12, ge=2, le=30)
    min_samples_leaf: int = Field(default=2, ge=1, le=20)


class BoostingConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    max_iter: int = Field(default=100, ge=20, le=300)
    learning_rate: float = Field(default=0.1, ge=0.01, le=0.3)
    max_leaf_nodes: int = Field(default=15, ge=3, le=63)
    l2_regularization: float = Field(default=1.0, ge=0, le=10)


class RunConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    seed: int = Field(default=42, ge=0, le=2**31 - 1)
    folds: int = Field(default=3, ge=2, le=5)
    trials: int = Field(default=3, ge=1, le=8)
    max_seconds: int = Field(default=600, ge=30, le=1800)
    m1: LogisticConfig = Field(default_factory=LogisticConfig)
    m2: ForestConfig = Field(default_factory=ForestConfig)
    m3: BoostingConfig = Field(default_factory=BoostingConfig)


class StartRun(BaseModel):
    model_config = ConfigDict(extra="forbid")
    dataset_id: str
    config: RunConfig = Field(default_factory=RunConfig)


MODEL_CARDS = [
    {"id": "M1", "name": "Regresión logística", "initial": LogisticConfig().model_dump(),
     "fixed": {"solver": "lbfgs", "class_weight": "balanced", "scaling": "StandardScaler"},
     "search": {"C": [0.01, 0.1, 1.0, 10.0], "tol": [0.0001, 0.001]},
     "stop": "Convergencia tol o max_iter. Ensayos sin convergencia se descartan.",
     "reason": "Referencia interpretable y regularizada para ocho variables numéricas."},
    {"id": "M2", "name": "Random Forest", "initial": ForestConfig().model_dump(),
     "fixed": {"max_features": "sqrt", "class_weight": "balanced", "n_jobs": 1},
     "search": {"max_depth": [6, 12, 20], "min_samples_leaf": [1, 2, 5],
                "n_estimators": [50, 100, 200]},
     "stop": "Termina al construir n_estimators árboles; sin épocas ni early stopping.",
     "reason": "Captura relaciones no lineales; comparable con el evaluador histórico."},
    {"id": "M3", "name": "Histogram Gradient Boosting", "initial": BoostingConfig().model_dump(),
     "fixed": {"class_weight": "balanced", "early_stopping": False},
     "search": {"learning_rate": [0.03, 0.1, 0.2], "max_leaf_nodes": [7, 15, 31],
                "l2_regularization": [0.0, 1.0, 5.0], "max_iter": [50, 100, 200]},
     "stop": "max_iter. Sin partición interna aleatoria que rompa los grupos.",
     "reason": "Boosting eficiente sin añadir otra biblioteca; complejidad acotada."},
]
