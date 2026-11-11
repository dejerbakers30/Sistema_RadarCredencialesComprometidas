"""Motor de Evaluación de Riesgo de Contraseñas (Risk Engine).

Evalúa la debilidad de credenciales y el riesgo asociado a una filtración
utilizando extracción de características y un clasificador de Machine Learning
(LogisticRegression/NaiveBayes) calibrado con patrones de datasets como RockYou.
"""
from __future__ import annotations

import math
import re
from typing import Literal

import numpy as np
from sklearn.linear_model import LogisticRegression

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
    num_lower = sum(c.islower() for c in password)
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
    """Clasificador de riesgo basado en Machine Learning."""

    def __init__(self) -> None:
        self.model = LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42)
        self.classes_ = ["Bajo", "Medio", "Crítico"]
        self._train_initial_model()

    def _train_initial_model(self) -> None:
        """Entrena el modelo base con patrones representativos (RockYou + contraseñas complejas)."""
        # Muestra calibrada de entrenamiento
        # Crítico: Contraseñas débiles típicas de RockYou (longitud corta, alta predictibilidad)
        critical_samples = [
            "123456", "password", "12345678", "qwerty", "12345", "123456789", "football",
            "iloveyou", "admin", "welcome", "monkey", "dragon", "master", "sunshine",
            "letmein", "princess", "solo", "starwars", "pass1", "test123", "hello",
            "secret", "user", "guest", "root", "111111", "aaaaaa", "qwerty123", "123123",
            "charlie", "jordan", "michael", "shadow", "superman", "harley", "trustno1",
            "liverpool", "arsenal", "chelsea", "yellow", "orange", "cookie", "cheese",
            "hunter", "killer", "matrix", "buster", "barbie", "bailey", "system",
        ]

        # Medio: Contraseñas con complejidad moderada pero estructura predecible
        medium_samples = [
            "Summer2023!", "Company123", "P@ssw0rd1", "Barcelona2021", "Password#99",
            "Marzo2024*", "Admin2024$", "SecurePass1", "Welcome2025!", "Empresa2023*",
            "Winter2024#", "Spring2025$", "Fuerza2024!", "Peru2024*#", "Bogota2023!",
            "Santiago2024*", "Quito2025#", "Caracas2024$", "Lima2023!*", "Mexico2024#",
            "Tigre2024!#", "Leon2025$*", "Aguila2023!", "Halcon2024*", "Condor2025#",
        ]

        # Bajo: Contraseñas robustas con alta entropía y longitud
        low_samples = [
            "k9#mP$2vL!9xQ", "Z8!wX9#bLq2@kM", "Tr0ub4dor&3_complex", "9x#Lp!Qz@4mK1$",
            "aB8$kL2!vP9#wX", "correct-horse-battery-staple-99", "xK9!mP$2vL!9xQ8#",
            "vR8#wX9$bLq2@kM4", "7uP#Lq2@kM4!vR8$", "wX9#bLq2@kM4!vR8", "pL9#mP$2vL!9xQ8#",
            "mK4!vR8#wX9$bLq2", "bLq2@kM4!vR8#wX9", "kM4!vR8#wX9$bLq2@", "4!vR8#wX9$bLq2@k",
            "N7#pQ9$vL!2xM8*z", "Y6!rK4#wZ9$bM1&s", "Q9#xL2!vP8$wK3*m", "P8$wK3*mQ9#xL2!v",
        ]

        X: list[list[float]] = []
        y: list[str] = []

        for p in critical_samples:
            X.append(extract_features(p))
            y.append("Crítico")

        for p in medium_samples:
            X.append(extract_features(p))
            y.append("Medio")

        for p in low_samples:
            X.append(extract_features(p))
            y.append("Bajo")

        self.model.fit(np.array(X), np.array(y))

    def evaluate(self, password: str | None) -> RiskLevel:
        """Evalúa una contraseña y retorna su nivel de riesgo: 'Bajo', 'Medio' o 'Crítico'."""
        if not password or not isinstance(password, str):
            return "Crítico"

        pwd = password.strip()
        if len(pwd) == 0:
            return "Crítico"

        # Heurísticas de seguridad deterministas inmediatas
        lower = pwd.lower()
        if len(pwd) < 6:
            return "Crítico"

        if any(re.fullmatch(pat, lower) for pat in COMMON_PATTERNS[:6]):
            return "Crítico"

        features = np.array([extract_features(pwd)])
        prediction = self.model.predict(features)[0]
        return str(prediction)  # type: ignore[return-value]


# Instancia singleton para uso en servicios
risk_engine = RiskEngine()

