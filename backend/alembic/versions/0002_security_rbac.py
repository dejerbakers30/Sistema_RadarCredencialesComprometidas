"""Add token revocation, MFA challenge state and persisted RBAC permissions."""

from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


PERMISSIONS = {
    "admin": {
        ("dashboard", "read"), ("leaks", "read"), ("leaks", "write"), ("leaks", "export"),
        ("resets", "read"), ("resets", "execute"), ("reports", "read"),
        ("reports", "generate"), ("reports", "schedule"), ("users", "read"),
        ("users", "write"), ("users", "admin"), ("roles", "read"), ("roles", "write"),
        ("audit", "read"), ("audit", "export"), ("sources", "read"),
        ("sources", "write"), ("config", "admin"), ("notifications", "read"),
    },
    "soc_analyst": {
        ("dashboard", "read"), ("leaks", "read"), ("leaks", "write"),
        ("leaks", "export"), ("resets", "read"), ("resets", "execute"),
        ("reports", "read"), ("reports", "generate"), ("audit", "read"),
        ("sources", "read"), ("notifications", "read"),
    },
    "auditor": {
        ("dashboard", "read"), ("leaks", "read"), ("leaks", "export"),
        ("resets", "read"), ("reports", "read"), ("reports", "generate"),
        ("audit", "read"), ("audit", "export"), ("users", "read"),
        ("notifications", "read"),
    },
    "end_user": {
        ("dashboard", "read"), ("notifications", "read"), ("profile", "write"),
    },
}


def upgrade() -> None:
    op.add_column("usuarios", sa.Column("mfa_challenge_hash", sa.String(64), nullable=True))
    op.add_column("usuarios", sa.Column("mfa_challenge_expires_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("usuarios", sa.Column("token_version", sa.Integer(), nullable=False, server_default="0"))

    bind = op.get_bind()
    for role, permissions in PERMISSIONS.items():
        for modulo, accion in permissions:
            bind.execute(
                sa.text("INSERT INTO permisos (modulo, accion) VALUES (:modulo, :accion) "
                        "ON CONFLICT (modulo, accion) DO NOTHING"),
                {"modulo": modulo, "accion": accion},
            )
            bind.execute(
                sa.text("""
                    INSERT INTO rol_permisos (rol_id, permiso_id)
                    SELECT r.id, p.id FROM roles r, permisos p
                    WHERE r.nombre = :rol AND p.modulo = :modulo AND p.accion = :accion
                    ON CONFLICT DO NOTHING
                """),
                {"rol": role, "modulo": modulo, "accion": accion},
            )

    # Serializa escritores de la cadena dentro de la transacción actual.
    op.execute("""
    CREATE OR REPLACE FUNCTION audit_log_chain() RETURNS TRIGGER AS $$
    DECLARE prev_hash TEXT;
    BEGIN
        PERFORM pg_advisory_xact_lock(hashtextextended('radar:audit_log_chain', 0));
        SELECT hash_actual INTO prev_hash FROM audit_log ORDER BY id DESC LIMIT 1;
        NEW.hash_anterior := COALESCE(prev_hash, 'GENESIS');
        NEW.hash_actual := encode(digest(
            COALESCE(NEW.ts::text,'') || COALESCE(NEW.usuario_email::text,'') ||
            COALESCE(NEW.modulo,'') || COALESCE(NEW.accion,'') ||
            COALESCE(NEW.resultado,'') || COALESCE(NEW.hash_anterior,''),
            'sha256'), 'hex');
        RETURN NEW;
    END; $$ LANGUAGE plpgsql;
    """)


def downgrade() -> None:
    op.execute("DELETE FROM rol_permisos rp USING roles r WHERE rp.rol_id = r.id AND r.nombre IN ('admin','soc_analyst','auditor','end_user')")
    op.drop_column("usuarios", "token_version")
    op.drop_column("usuarios", "mfa_challenge_expires_at")
    op.drop_column("usuarios", "mfa_challenge_hash")
