"""Seed Crypto Lab volume + sample cover PNG + sample anomalies (Phase 8).

Usage (from repo root or backend/, with DATABASE_URL set):

    python -m app.scripts.seed_crypto_lab
    python -m app.scripts.seed_crypto_lab --crypto 8000 --auth 400 --attacks 120 --run-anomalies
"""

from __future__ import annotations

import argparse
from io import BytesIO
from pathlib import Path

from PIL import Image

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.enums import UserRole
from app.models.user import User
from app.services.analytics_service import AnalyticsService
from app.services.anomaly.anomaly_service import AnomalyService


def ensure_cover_png(path: Path, *, width: int = 256, height: int = 256) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.stat().st_size > 0:
        return path
    image = Image.new("RGB", (width, height), color=(32, 96, 128))
    # Subtle gradient so LSB demos look less flat
    pixels = image.load()
    assert pixels is not None
    for y in range(height):
        for x in range(width):
            pixels[x, y] = (
                (32 + (x * 40) // width) % 256,
                (96 + (y * 60) // height) % 256,
                128,
            )
    buf = BytesIO()
    image.save(buf, format="PNG")
    path.write_bytes(buf.getvalue())
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed Crypto Lab analytics volume")
    parser.add_argument("--crypto", type=int, default=8000, help="crypto_operations rows")
    parser.add_argument("--auth", type=int, default=400, help="auth failure security_logs")
    parser.add_argument("--attacks", type=int, default=120, help="attack_experiments rows")
    parser.add_argument("--hours", type=int, default=72, help="time span for timestamps")
    parser.add_argument(
        "--run-anomalies",
        action="store_true",
        help="Run anomaly detector after seeding (auth_burst expected)",
    )
    parser.add_argument(
        "--cover",
        type=str,
        default="",
        help="Optional path for demo cover PNG (default: STEGO_DIRECTORY/cover_demo.png)",
    )
    args = parser.parse_args()

    stego_dir = Path(settings.STEGO_DIRECTORY)
    if not stego_dir.is_absolute():
        # Prefer repo-root uploads/stego when launched from backend/
        candidates = [Path.cwd() / stego_dir, Path.cwd().parent / stego_dir]
        for candidate in candidates:
            try:
                candidate.mkdir(parents=True, exist_ok=True)
                stego_dir = candidate.resolve()
                break
            except OSError:
                continue
    cover_path = Path(args.cover) if args.cover else stego_dir / "cover_demo.png"
    cover = ensure_cover_png(cover_path)
    print(f"Cover PNG ready: {cover} ({cover.stat().st_size} bytes)")

    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.role == UserRole.ADMIN.value).first()
        if not admin:
            raise SystemExit("No admin user found. Run: python -m app.scripts.seed")
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

        if args.run_anomalies:
            created = AnomalyService(db).run_detection(
                admin=admin,
                hours=max(args.hours, 24),
                auth_burst_threshold=20,
            )
            types = sorted({e.anomaly_type for e in created})
            print(f"Anomalies created={len(created)} types={types}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
