"""Evaluación auxiliar de debilidad con características v1 y artefactos registrados."""
from __future__ import annotations

import logging
import math
import re
from typing import Literal

logger = logging.getLogger(__name__)

RiskLevel = Literal["Bajo", "Medio", "Crítico"]

COMMON_PATTERNS = [
    r"12345",
    r"password",
    r"qwerty",
    r"admin",
    r"letmein",
    r"welcome",
    r"iloveyou",
    r"monkey",
    r"dragon",
    r"football",
    r"baseball",
    r"abc123",
    r"pass(word)?",
    r"(\d)\1{2,}",  # Dígitos repetidos 111, 222
    r"([a-zA-Z])\1{2,}",  # Letras repetidas aaa, bbb
]


def shannon_entropy(s: str) -> float:
    """Calcula la entropía de Shannon de una cadena."""
    if not s:
        return 0.0
    length = len(s)
    freq = {}
    for c in s:
        freq[c] = freq.get(c, 0) + 1
    return -sum((count / length) * math.log2(count / length) for count in freq.values())


def extract_features(password: str) -> list[float]:
    """Extrae vector de características numéricas para el modelo de ML."""
    if not password:
        return [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0]

    length = float(len(password))
    entropy = shannon_entropy(password)

    num_digits = sum(c.isdigit() for c in password)
    num_upper = sum(c.isupper() for c in password)
    num_symbols = sum(not c.isalnum() for c in password)

    digits_ratio = num_digits / length
    uppercase_ratio = num_upper / length
    symbols_ratio = num_symbols / length

    # Detección de patrones comunes estilo RockYou
    lower_pwd = password.lower()
    has_common_pattern = 1.0 if any(re.search(pat, lower_pwd) for pat in COMMON_PATTERNS) else 0.0
    is_only_numbers_or_letters = 1.0 if (password.isdigit() or password.isalpha()) else 0.0

    return [
        length,
        entropy,
        digits_ratio,
        uppercase_ratio,
        symbols_ratio,
        has_common_pattern,
        is_only_numbers_or_letters,
        float(num_symbols),
    ]


class RiskEngine:
    """Estima debilidad; nunca decide si una exposición es un falso positivo.

    Sin artefacto registrado utiliza reglas explícitas. No entrena al importar.
    """

    def evaluate(self, password: str | None) -> RiskLevel:
        if not isinstance(password, str) or not password or len(password) > 256:
            return "Crítico"
        features = extract_features(password)
        try:
            from app.ml.inference import predict_features
            prediction = predict_features(features)
            if prediction in ("Bajo", "Medio", "Crítico"):
                return prediction
        except Exception:  # noqa: BLE001 - fallo de artefacto no debe interrumpir la evaluación
            logger.warning("Artefacto de debilidad no disponible; se aplican reglas conservadoras")
        if len(password) < 8 or features[5]:
            return "Crítico"
        if len(password) >= 14 and features[1] >= 3:
            return "Bajo"
        return "Medio"


risk_engine = RiskEngine()
