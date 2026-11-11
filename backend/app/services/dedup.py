import hashlib
from datetime import date


def canonical_hash(email: str, breach: str, fecha_breach: date | None) -> str:
    payload = f"{email.lower().strip()}|{breach.strip()}|{fecha_breach or 'sin_fecha'}"
    return hashlib.sha256(payload.encode()).hexdigest()
