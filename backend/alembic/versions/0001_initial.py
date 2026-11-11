"""initial schema

Revision ID: 0001
Revises:
Create Date: 2025-01-01 00:00:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "citext"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    # ---------- Roles, permisos, usuarios ----------
    op.create_table(
        "roles",
        sa.Column("id", sa.SmallInteger, primary_key=True),
        sa.Column("nombre", sa.String(50), unique=True, nullable=False),
        sa.Column("descripcion", sa.Text),
    )
    op.create_table(
        "permisos",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("modulo", sa.String(50), nullable=False),
        sa.Column("accion", sa.String(50), nullable=False),
        sa.UniqueConstraint("modulo", "accion", name="uq_permiso_modulo_accion"),
    )
    op.create_table(
        "rol_permisos",
        sa.Column("rol_id", sa.SmallInteger, sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("permiso_id", sa.Integer, sa.ForeignKey("permisos.id", ondelete="CASCADE"), primary_key=True),
    )
    op.create_table(
        "usuarios",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("email", postgresql.CITEXT, unique=True, nullable=False),
        sa.Column("nombre", sa.String(200), nullable=False),
        sa.Column("rol_id", sa.SmallInteger, sa.ForeignKey("roles.id"), nullable=False),
        sa.Column("activo", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("idp_subject", sa.String(255)),
        sa.Column("password_hash", sa.String(255)),
        sa.Column("mfa_secret", sa.String(255)),
        sa.Column("mfa_enabled", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("ultimo_login", sa.DateTime(timezone=True)),
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("actualizado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_usuarios_email_activo", "usuarios", ["email"], postgresql_where=sa.text("activo"))
    op.create_index("idx_usuarios_rol", "usuarios", ["rol_id"])

    # ---------- Fuentes y dominios ----------
    op.create_table(
        "fuentes",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("nombre", sa.String(50), unique=True, nullable=False),
        sa.Column("tipo", sa.String(20), nullable=False),
        sa.Column("endpoint", sa.Text),
        sa.Column("api_key_ref", sa.String(200)),
        sa.Column("activa", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("rate_limit_rps", sa.Numeric(6, 2), server_default="0.5"),
        sa.Column("ultima_consulta", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "dominios_monitoreados",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("dominio", sa.String(200), unique=True, nullable=False),
        sa.Column("organizacion", sa.String(200)),
        sa.Column("activo", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("verificado_hibp", sa.Boolean, nullable=False, server_default=sa.false()),
    )

    # ---------- Enums ----------
    op.execute("CREATE TYPE leak_estado AS ENUM ('nuevo','contenido','resuelto','falso_positivo')")
    op.execute("CREATE TYPE leak_severidad AS ENUM ('baja','media','alta','critica')")
    op.execute("CREATE TYPE reset_metodo AS ENUM ('automatico','manual')")
    op.execute("CREATE TYPE reset_resultado AS ENUM ('exitoso','fallido','pendiente','reintento')")

    # ---------- Leak hits ----------
    op.create_table(
        "leak_hits",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("email_corporativo", postgresql.CITEXT, nullable=False),
        sa.Column("usuario_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("usuarios.id", ondelete="SET NULL")),
        sa.Column("breach_origen", sa.String(200), nullable=False),
        sa.Column("breach_dominio", sa.String(200)),
        sa.Column("fecha_breach", sa.Date),
        sa.Column("fecha_deteccion", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("severidad", postgresql.ENUM("baja", "media", "alta", "critica", name="leak_severidad", create_type=False), nullable=False, server_default="media"),
        sa.Column("fuente_id", sa.Integer, sa.ForeignKey("fuentes.id"), nullable=False),
        sa.Column("fuente_detalle", sa.String(200)),
        sa.Column("datos_expuestos", postgresql.ARRAY(sa.Text)),
        sa.Column("estado", postgresql.ENUM("nuevo", "contenido", "resuelto", "falso_positivo", name="leak_estado", create_type=False), nullable=False, server_default="nuevo"),
        sa.Column("fecha_contencion", sa.DateTime(timezone=True)),
        sa.Column("hash_canonico", sa.String(64), unique=True, nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("actualizado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_leak_email", "leak_hits", ["email_corporativo"])
    op.create_index("idx_leak_estado", "leak_hits", ["estado"])
    op.create_index("idx_leak_fecha_det_desc", "leak_hits", [sa.text("fecha_deteccion DESC")])
    op.create_index("idx_leak_severidad", "leak_hits", ["severidad"])

    # ---------- Resets ----------
    op.create_table(
        "resets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("leak_hit_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("leak_hits.id", ondelete="CASCADE"), nullable=False),
        sa.Column("usuario_ejecutor", postgresql.UUID(as_uuid=True), sa.ForeignKey("usuarios.id")),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("metodo", postgresql.ENUM("automatico", "manual", name="reset_metodo", create_type=False), nullable=False),
        sa.Column("resultado", postgresql.ENUM("exitoso", "fallido", "pendiente", "reintento", name="reset_resultado", create_type=False), nullable=False, server_default="pendiente"),
        sa.Column("idp_respuesta", postgresql.JSONB),
        sa.Column("intentos", sa.SmallInteger, nullable=False, server_default="1"),
        sa.Column("proximo_intento", sa.DateTime(timezone=True)),
        sa.Column("error_detalle", sa.Text),
    )
    op.create_index("idx_resets_leak", "resets", ["leak_hit_id"])
    op.create_index("idx_resets_pendientes", "resets", ["resultado", "proximo_intento"])

    # ---------- Notificaciones ----------
    op.create_table(
        "notificaciones",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("leak_hit_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("leak_hits.id", ondelete="CASCADE")),
        sa.Column("destinatario", postgresql.CITEXT, nullable=False),
        sa.Column("canal", sa.String(20), nullable=False),
        sa.Column("plantilla", sa.String(50)),
        sa.Column("enviado_en", sa.DateTime(timezone=True)),
        sa.Column("estado", sa.String(20), nullable=False, server_default="pendiente"),
        sa.Column("error_detalle", sa.Text),
    )

    # ---------- Caché HIBP ----------
    op.create_table(
        "hibp_cache",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("cache_key", sa.String(128), unique=True, nullable=False),
        sa.Column("payload", postgresql.JSONB, nullable=False),
        sa.Column("consultado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("expira_en", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("idx_hibp_cache_expira", "hibp_cache", ["expira_en"])

    # ---------- Auditoría ----------
    op.create_table(
        "audit_log",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("tz", sa.String(50), nullable=False, server_default="UTC"),
        sa.Column("usuario_id", sa.String(36)),
        sa.Column("usuario_email", postgresql.CITEXT),
        sa.Column("modulo", sa.String(50), nullable=False),
        sa.Column("accion", sa.String(50), nullable=False),
        sa.Column("entidad", sa.String(50)),
        sa.Column("entidad_id", sa.String(64)),
        sa.Column("resultado", sa.String(20), nullable=False),
        sa.Column("ip_origen", postgresql.INET),
        sa.Column("user_agent", sa.Text),
        sa.Column("detalle", postgresql.JSONB),
        sa.Column("hash_anterior", sa.String(64)),
        sa.Column("hash_actual", sa.String(64), nullable=False),
    )
    op.create_index("idx_audit_modulo_ts", "audit_log", ["modulo", "ts"])
    op.create_index("idx_audit_usuario_ts", "audit_log", ["usuario_email", "ts"])

    # Triggers de inmutabilidad y encadenamiento
    op.execute("""
    CREATE OR REPLACE FUNCTION audit_log_chain() RETURNS TRIGGER AS $$
    DECLARE prev_hash TEXT;
    BEGIN
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
    op.execute("""
    CREATE TRIGGER trg_audit_chain BEFORE INSERT ON audit_log
    FOR EACH ROW EXECUTE FUNCTION audit_log_chain();
    """)
    op.execute("""
    CREATE OR REPLACE FUNCTION audit_log_inmutable() RETURNS TRIGGER AS $$
    BEGIN
        RAISE EXCEPTION 'audit_log es inmutable: % no permitido', TG_OP;
    END; $$ LANGUAGE plpgsql;
    """)
    op.execute("""
    CREATE TRIGGER trg_audit_no_update BEFORE UPDATE OR DELETE ON audit_log
    FOR EACH ROW EXECUTE FUNCTION audit_log_inmutable();
    """)

    # ---------- Reportes ----------
    op.create_table(
        "reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("tipo", sa.String(20), nullable=False),
        sa.Column("formato", sa.String(10), nullable=False),
        sa.Column("periodo_desde", sa.Date, nullable=False),
        sa.Column("periodo_hasta", sa.Date, nullable=False),
        sa.Column("generado_por", postgresql.UUID(as_uuid=True), sa.ForeignKey("usuarios.id")),
        sa.Column("generado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("ruta_archivo", sa.String(500), nullable=False),
        sa.Column("hash_archivo", sa.String(64), nullable=False),
    )

    # ---------- Configuración ----------
    op.create_table(
        "configuracion",
        sa.Column("clave", sa.String(100), primary_key=True),
        sa.Column("valor", postgresql.JSONB, nullable=False),
        sa.Column("descripcion", sa.Text),
        sa.Column("actualizado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ---------- Seed de roles ----------
    op.execute("""
        INSERT INTO roles (nombre, descripcion) VALUES
        ('admin','Administrador total'),
        ('soc_analyst','Analista SOC'),
        ('auditor','Auditor de solo lectura'),
        ('end_user','Usuario final')
    """)


def downgrade() -> None:
    op.drop_table("configuracion")
    op.drop_table("reports")
    op.execute("DROP TRIGGER IF EXISTS trg_audit_no_update ON audit_log")
    op.execute("DROP FUNCTION IF EXISTS audit_log_inmutable()")
    op.execute("DROP TRIGGER IF EXISTS trg_audit_chain ON audit_log")
    op.execute("DROP FUNCTION IF EXISTS audit_log_chain()")
    op.drop_table("audit_log")
    op.drop_table("hibp_cache")
    op.drop_table("notificaciones")
    op.drop_table("resets")
    op.drop_table("leak_hits")
    op.execute("DROP TYPE IF EXISTS reset_resultado")
    op.execute("DROP TYPE IF EXISTS reset_metodo")
    op.execute("DROP TYPE IF EXISTS leak_severidad")
    op.execute("DROP TYPE IF EXISTS leak_estado")
    op.drop_table("dominios_monitoreados")
    op.drop_table("fuentes")
    op.drop_table("usuarios")
    op.drop_table("rol_permisos")
    op.drop_table("permisos")
    op.drop_table("roles")
