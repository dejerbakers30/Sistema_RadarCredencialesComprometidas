import argparse
import sys
from sqlalchemy import select
from app.core.security import hash_password
from app.db.models.user import Role, Usuario
from app.db.session import session_scope
from app.services.audit import verify_chain


def create_admin(email: str, password: str) -> None:
    with session_scope() as db:
        # Verificar si el usuario ya existe
        existing = db.execute(select(Usuario).where(Usuario.email == email)).scalar_one_or_none()
        if existing:
            print(f"Error: El usuario {email} ya existe.")
            sys.exit(1)

        # Obtener el rol de admin
        rol = db.execute(select(Role).where(Role.nombre == 'admin')).scalar_one_or_none()
        if not rol:
            print("Error: El rol 'admin' no existe en la base de datos. Ejecuta las migraciones primero.")
            sys.exit(1)

        # Crear el usuario
        user = Usuario(
            email=email,
            nombre="Administrador",
            rol_id=rol.id,
            password_hash=hash_password(password),
            activo=True
        )
        db.add(user)
        print(f"✅ Usuario administrador {email} creado correctamente.")


def check_chain() -> None:
    with session_scope() as db:
        result = verify_chain(db)
        if result["ok"]:
            print(f"✅ Cadena de auditoría íntegra. Total registros: {result['total']}")
        else:
            print(f"❌ Cadena de auditoría rota en los IDs: {result['broken']}")
            sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Radar de Credenciales CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    parser_admin = subparsers.add_parser("create-admin", help="Crea un usuario administrador")
    parser_admin.add_argument("--email", required=True)
    parser_admin.add_argument("--password", required=True)

    parser_chain = subparsers.add_parser("verify-chain", help="Verifica la integridad de la bitácora")

    args = parser.parse_args()

    if args.command == "create-admin":
        create_admin(args.email, args.password)
    elif args.command == "verify-chain":
        check_chain()


if __name__ == "__main__":
    main()
