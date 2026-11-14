"""Seed synthetic Crypto Lab volume for analytics / dashboard demos.

Usage (from backend/, with DATABASE_URL set):

    python -m app.scripts.seed_crypto_lab
    python -m app.scripts.seed_crypto_lab --crypto 5000 --auth 500 --attacks 100
"""

from __future__ import annotations

import argparse

from app.core.database import SessionLocal
from app.core.enums import UserRole
from app.models.user import User
from app.services.analytics_service import AnalyticsService


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed Crypto Lab analytics volume")
    parser.add_argument("--crypto", type=int, default=2000, help="crypto_operations rows")
    parser.add_argument("--auth", type=int, default=300, help="auth failure security_logs")
    parser.add_argument("--attacks", type=int, default=80, help="attack_experiments rows")
    parser.add_argument("--hours", type=int, default=72, help="time span for timestamps")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.role == UserRole.ADMIN.value).first()
        if not admin:
            raise SystemExit("No admin user found. Run app.scripts.seed first.")
        result = AnalyticsService(db).seed_load(
            admin=admin,
            crypto_events=args.crypto,
            auth_failures=args.auth,
            attack_events=args.attacks,
            hours_span=args.hours,
        )
        print(
            f"Seeded crypto={result['crypto_operations']} "
            f"auth_fail={result['auth_failures']} "
            f"attacks={result['attack_experiments']} "
            f"total={result['total']}"
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
