from concurrent.futures import ThreadPoolExecutor
from ipaddress import IPv4Address

import pytest
from sqlalchemy.exc import DBAPIError

from app.db.models.audit import AuditLog
from app.db.session import SessionLocal
from app.services.audit import normalize_ip, verify_chain, write_audit


@pytest.mark.parametrize(
    ("value", "expected"),
    [("127.0.0.1", "127.0.0.1"), (IPv4Address("127.0.0.1"), "127.0.0.1"), ("::1", "::1"), ("8.8.8.8", "8.8.8.8"),
     ("testclient", None), ("", None), (None, None)],
)
def test_normalize_ip(value, expected):
    assert normalize_ip(value) == expected


def test_chain_ok(db):
    for i in range(5):
        write_audit(db, modulo="test", accion=f"a{i}", resultado="ok")
    db.commit()
    result = verify_chain(db)
    assert result["ok"] is True
    assert result["broken"] == []


def test_chain_rejects_update_and_delete(db):
    write_audit(db, modulo="test", accion="a1", resultado="ok")
    write_audit(db, modulo="test", accion="a2", resultado="ok")
    db.commit()
    row = db.query(AuditLog).first()
    row.accion = "MANIPULADO"
    with pytest.raises(DBAPIError):
        db.commit()
    db.rollback()
    with pytest.raises(DBAPIError):
        db.delete(row)
        db.commit()
    db.rollback()


def test_chain_serializes_concurrent_writers(db):
    def write(index):
        session = SessionLocal()
        try:
            write_audit(session, modulo="concurrency", accion=f"a{index}", resultado="ok")
            session.commit()
        finally:
            session.close()

    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(write, range(2)))
    assert verify_chain(db)["ok"] is True
