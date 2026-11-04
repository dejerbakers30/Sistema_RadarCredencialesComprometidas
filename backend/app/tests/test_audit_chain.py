from datetime import datetime, timezone
from app.db.models.audit import AuditLog
from app.services.audit import verify_chain, write_audit


def test_chain_ok(db):
    for i in range(5):
        write_audit(db, modulo="test", accion=f"a{i}", resultado="ok")
    db.commit()
    result = verify_chain(db)
    assert result["ok"] is True
    assert result["broken"] == []


def test_chain_detects_tampering(db):
    write_audit(db, modulo="test", accion="a1", resultado="ok")
    write_audit(db, modulo="test", accion="a2", resultado="ok")
    db.commit()
    # Manipulación directa
    row = db.query(AuditLog).first()
    row.accion = "MANIPULADO"
    db.commit()
    result = verify_chain(db)
    assert result["ok"] is False
