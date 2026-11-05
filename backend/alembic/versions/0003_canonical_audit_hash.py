"""Keep audit hash calculation in the application canonical implementation."""

from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    CREATE OR REPLACE FUNCTION audit_log_chain() RETURNS TRIGGER AS $$
    BEGIN
        PERFORM pg_advisory_xact_lock(hashtextextended('radar:audit_log_chain', 0));
        IF NEW.hash_anterior IS NULL THEN
            SELECT hash_actual INTO NEW.hash_anterior
            FROM audit_log ORDER BY id DESC LIMIT 1;
            NEW.hash_anterior := COALESCE(NEW.hash_anterior, 'GENESIS');
        END IF;
        RETURN NEW;
    END; $$ LANGUAGE plpgsql;
    """)


def downgrade() -> None:
    op.execute("""
    CREATE OR REPLACE FUNCTION audit_log_chain() RETURNS TRIGGER AS $$
    BEGIN
        PERFORM pg_advisory_xact_lock(hashtextextended('radar:audit_log_chain', 0));
        SELECT hash_actual INTO NEW.hash_anterior FROM audit_log ORDER BY id DESC LIMIT 1;
        NEW.hash_anterior := COALESCE(NEW.hash_anterior, 'GENESIS');
        NEW.hash_actual := encode(digest(
            COALESCE(NEW.ts::text,'') || COALESCE(NEW.usuario_email::text,'') ||
            COALESCE(NEW.modulo,'') || COALESCE(NEW.accion,'') ||
            COALESCE(NEW.resultado,'') || COALESCE(NEW.hash_anterior,''),
            'sha256'), 'hex');
        RETURN NEW;
    END; $$ LANGUAGE plpgsql;
    """)
