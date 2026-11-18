"""Script de aprovisionamiento de datos para pruebas de rendimiento en JMeter.
Crea el usuario 'tester@radar.local' (con rol admin y sin MFA) y asegura que existan
registros en 'leak_hits' para que los endpoints de consulta y contención tengan datos reales.
"""
import hashlib
import os
import sys
from datetime import datetime, timezone, timedelta
from uuid import uuid4

# Asegurar cwd y path al backend
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
os.chdir(backend_dir)
sys.path.insert(0, backend_dir)

from sqlalchemy import select, func
from app.core.security import hash_password
from app.db.models.user import Role, Usuario
from app.db.models.source import Fuente
from app.db.models.leak import LeakHit, LeakEstado, LeakSeveridad
from app.db.session import session_scope

TESTER_EMAIL = "tester@radar.local"
TESTER_PASSWORD = "TesterPassword123!"


def setup_data():
    with session_scope() as db:
        print("[*] Verificando roles y usuario tester...")
        # 1. Obtener rol admin
        admin_role = db.execute(select(Role).where(Role.nombre == "admin")).scalar_one_or_none()
        if not admin_role:
            print("[!] Error: Rol 'admin' no encontrado. Ejecuta las migraciones de Alembic.")
            return

        # 2. Verificar/crear usuario tester
        user = db.execute(select(Usuario).where(Usuario.email == TESTER_EMAIL)).scalar_one_or_none()
        if not user:
            user = Usuario(
                email=TESTER_EMAIL,
                nombre="JMeter Performance Tester",
                rol_id=admin_role.id,
                password_hash=hash_password(TESTER_PASSWORD),
                activo=True,
                mfa_enabled=False
            )
            db.add(user)
            print(f" [+] Usuario creado: {TESTER_EMAIL} / {TESTER_PASSWORD}")
        else:
            # Asegurar que esté activo, rol admin y sin MFA
            user.activo = True
            user.mfa_enabled = False
            user.rol_id = admin_role.id
            user.password_hash = hash_password(TESTER_PASSWORD)
            print(f" [*] Usuario actualizado con password estándar: {TESTER_EMAIL}")

        # 3. Verificar/crear fuente
        fuente = db.execute(select(Fuente).limit(1)).scalar_one_or_none()
        if not fuente:
            fuente = Fuente(
                nombre="HIBP Integration",
                tipo="hibp",
                activa=True
            )
            db.add(fuente)
            db.flush()
            print(" [+] Fuente de prueba creada.")

        # 4. Verificar filtraciones de prueba
        leak_count = db.execute(select(func.count(LeakHit.id))).scalar() or 0
        print(f" [*] Registros de filtraciones actuales en BD: {leak_count}")
        if leak_count < 15:
            print(f" [*] Insertando 15 filtraciones de prueba para banco de JMeter...")
            ahora = datetime.now(timezone.utc)
            severidades = [LeakSeveridad.baja, LeakSeveridad.media, LeakSeveridad.alta, LeakSeveridad.critica]
            estados = [LeakEstado.nuevo, LeakEstado.contenido, LeakEstado.falso_positivo]
            
            for i in range(15):
                h = hashlib.sha256(f"test-leak-sample-{i}-{uuid4()}".encode()).hexdigest()
                leak = LeakHit(
                    email_corporativo=f"empleado{i+1}@empresa.com",
                    breach_origen=f"TestBreach_2026_{i % 3}",
                    breach_dominio=f"servicio{i % 4}.com",
                    fecha_deteccion=ahora - timedelta(days=i),
                    severidad=severidades[i % len(severidades)],
                    fuente_id=fuente.id,
                    datos_expuestos=["Passwords", "Email addresses"],
                    estado=estados[i % len(estados)],
                    hash_canonico=h,
                    score_riesgo="Crítico" if i % 2 == 0 else "Bajo"
                )
                db.add(leak)
            print(" [+] 15 filtraciones de prueba agregadas con éxito.")

        print("\n[OK] Base de datos lista para pruebas de rendimiento con JMeter.")
        print(f"Credenciales configuradas:\n - Email: {TESTER_EMAIL}\n - Password: {TESTER_PASSWORD}")


if __name__ == "__main__":
    setup_data()
