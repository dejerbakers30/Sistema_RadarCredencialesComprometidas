import os
from datetime import datetime, timedelta, timezone

os.environ.setdefault("JWT_SECRET", "test-only-secret-with-at-least-32-characters")
os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://radar:test@localhost:5433/radar_creds")
os.environ.setdefault("HIBP_API_KEY", "test-only-hibp-key")

from app.core.security import (
    compare_challenge, create_refresh_token, decode_token, hash_challenge, is_challenge_valid,
)


def test_mfa_challenge_hash_is_not_reversible_and_compares_constant_time():
    challenge = "challenge-for-test"
    stored = hash_challenge(challenge)
    assert stored != challenge
    assert compare_challenge(challenge, stored)
    assert not compare_challenge("wrong", stored)


def test_refresh_token_contains_version():
    token = create_refresh_token("00000000-0000-0000-0000-000000000001", token_version=4)
    assert decode_token(token)["token_version"] == 4


def test_mfa_challenge_valid_incorrect_and_expired():
    now = datetime.now(timezone.utc)
    stored = hash_challenge("valid")
    assert is_challenge_valid("valid", stored, now + timedelta(minutes=1), now)
    assert not is_challenge_valid("wrong", stored, now + timedelta(minutes=1), now)
    assert not is_challenge_valid("valid", stored, now - timedelta(seconds=1), now)
