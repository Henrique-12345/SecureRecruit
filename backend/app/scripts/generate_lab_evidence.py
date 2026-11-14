"""Generate JSON artifacts for Unit 2 Phase 8 evidence (no screenshots).

Run from backend/:

    DATABASE_URL=... PYTHONPATH=. python -m app.scripts.generate_lab_evidence
"""

from __future__ import annotations

import base64
import json
from datetime import datetime, timezone
from pathlib import Path

from app.core.enums import CryptoAlgorithm
from app.services.crypto import custom_cipher
from app.services.crypto.attacks import brute_force, differential, statistical
from app.services.crypto.key_service import derive_key
from app.services.crypto.metrics import avalanche_score, statistical_report
from app.services.stego import lsb_png
from PIL import Image
from io import BytesIO


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    # backend/app/scripts/ -> repo root
    return here.parents[3]


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {path}")


def main() -> None:
    out_dir = _repo_root() / "docs/security/evidence/unidade-2/artifacts"
    out_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()

    key = derive_key(algorithm=CryptoAlgorithm.CUSTOM_SPN.value)
    plaintext = b"SecureRecruit Phase 8 evidence payload"
    ciphertext = custom_cipher.encrypt(plaintext, key.key)
    recovered = custom_cipher.decrypt(ciphertext, key.key)
    _write(
        out_dir / "01-encrypt-decrypt-spn.json",
        {
            "generated_at": now,
            "algorithm": "custom_spn",
            "roundtrip_ok": recovered == plaintext,
            "plaintext_len": len(plaintext),
            "ciphertext_b64": base64.b64encode(ciphertext).decode("ascii"),
            "key_fingerprint": key.fingerprint,
            "note": "Key material is not persisted; fingerprint only.",
        },
    )

    k2 = derive_key(algorithm=CryptoAlgorithm.CUSTOM_SPN.value)
    _write(
        out_dir / "01-different-keys.json",
        {
            "generated_at": now,
            "same_plaintext": True,
            "ciphertexts_differ": custom_cipher.encrypt(plaintext, key.key)
            != custom_cipher.encrypt(plaintext, k2.key),
            "fingerprint_a": key.fingerprint[:16],
            "fingerprint_b": k2.fingerprint[:16],
        },
    )

    # Cover + stego
    cover_img = Image.new("RGB", (128, 128), color=(40, 90, 130))
    buf = BytesIO()
    cover_img.save(buf, format="PNG")
    cover_bytes = buf.getvalue()
    stego_bytes, capacity, used = lsb_png.embed_payload(cover_bytes, ciphertext)
    extracted = lsb_png.extract_payload(stego_bytes)
    stego_path = out_dir / "02-stego-demo.png"
    stego_path.write_bytes(stego_bytes)
    cover_path = out_dir / "02-cover-demo.png"
    cover_path.write_bytes(cover_bytes)
    _write(
        out_dir / "02-stego-roundtrip.json",
        {
            "generated_at": now,
            "capacity_bits": capacity,
            "payload_bits": used,
            "extract_matches_ciphertext": extracted == ciphertext,
            "cover_file": cover_path.name,
            "stego_file": stego_path.name,
        },
    )

    diff = differential.run_differential(plaintext=plaintext, key=key.key)
    score_d, label_d = differential.effectiveness_from_differential(diff)
    _write(
        out_dir / "03-attack-differential.json",
        {
            "generated_at": now,
            "avalanche_score": diff.avalanche_score,
            "hamming_bits": diff.hamming_bits,
            "effectiveness_score": score_d,
            "label": label_d,
        },
    )

    bf = brute_force.run_truncated_brute_force(
        plaintext=plaintext,
        ciphertext=ciphertext,
        full_key=key.key,
        searchable_bits=10,
        max_attempts=2**10,
    )
    score_b, label_b = brute_force.effectiveness_from_bf(bf)
    _write(
        out_dir / "03-attack-brute-force.json",
        {
            "generated_at": now,
            "found": bf.found,
            "attempts": bf.attempts,
            "keyspace_size": bf.keyspace_size,
            "elapsed_ms": bf.elapsed_ms,
            "estimated_full_keyspace_years": bf.estimated_full_keyspace_years,
            "effectiveness_score": score_b,
            "label": label_b,
        },
    )

    st = statistical.run_statistical(ciphertext)
    score_s, label_s = statistical.effectiveness_from_statistical(st)
    _write(
        out_dir / "03-attack-statistical.json",
        {
            "generated_at": now,
            "report": st.report,
            "effectiveness_score": score_s,
            "label": label_s,
        },
    )

    flipped = bytearray(plaintext)
    flipped[0] ^= 1
    c2 = custom_cipher.encrypt(bytes(flipped), key.key)
    _write(
        out_dir / "04-avalanche.json",
        {
            "generated_at": now,
            "avalanche_score": avalanche_score(ciphertext, c2),
            "statistical": statistical_report(ciphertext),
        },
    )

    index = {
        "generated_at": now,
        "phase": 8,
        "artifacts": sorted(p.name for p in out_dir.glob("*.json")),
        "images": sorted(p.name for p in out_dir.glob("*.png")),
        "note": "Screenshots da UI devem ser adicionados nas pastas 01–06.",
    }
    _write(out_dir / "00-index.json", index)


if __name__ == "__main__":
    main()
