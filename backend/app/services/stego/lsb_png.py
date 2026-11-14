"""LSB steganography in PNG (Unit 2 Crypto Lab)."""

from __future__ import annotations

import struct
from io import BytesIO

from PIL import Image

MAGIC = b"SR1\0"
HEADER_SIZE = 8  # magic(4) + length(4)


def capacity_bits(image: Image.Image) -> int:
    rgb = image.convert("RGB")
    w, h = rgb.size
    return w * h * 3


def capacity_bytes(image: Image.Image) -> int:
    return capacity_bits(image) // 8


def _bytes_to_bits(data: bytes) -> list[int]:
    bits: list[int] = []
    for byte in data:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
    return bits


def _bits_to_bytes(bits: list[int]) -> bytes:
    out = bytearray()
    for i in range(0, len(bits) - 7, 8):
        value = 0
        for bit in bits[i : i + 8]:
            value = (value << 1) | bit
        out.append(value)
    return bytes(out)


def embed_payload(cover_png: bytes, payload: bytes) -> tuple[bytes, int, int]:
    """
    Hide payload in PNG LSBs.
    Returns (stego_png_bytes, capacity_bits, payload_bits).
    """
    image = Image.open(BytesIO(cover_png)).convert("RGB")
    cap_bits = capacity_bits(image)
    framed = MAGIC + struct.pack(">I", len(payload)) + payload
    need_bits = len(framed) * 8
    if need_bits > cap_bits:
        raise ValueError(
            f"Payload too large for cover image: need {need_bits} bits, capacity {cap_bits}"
        )

    bits = _bytes_to_bits(framed)
    pixels = list(image.getdata())
    flat: list[int] = []
    for r, g, b in pixels:
        flat.extend([r, g, b])

    for i, bit in enumerate(bits):
        flat[i] = (flat[i] & 0xFE) | bit

    new_pixels = [
        (flat[i], flat[i + 1], flat[i + 2]) for i in range(0, len(flat), 3)
    ]
    stego = Image.new("RGB", image.size)
    stego.putdata(new_pixels)

    buf = BytesIO()
    stego.save(buf, format="PNG", optimize=False)
    return buf.getvalue(), cap_bits, need_bits


def extract_payload(stego_png: bytes) -> bytes:
    """Recover payload bytes from a stego PNG produced by embed_payload."""
    image = Image.open(BytesIO(stego_png)).convert("RGB")
    pixels = list(image.getdata())
    flat: list[int] = []
    for r, g, b in pixels:
        flat.extend([r, g, b])

    header_bits = [flat[i] & 1 for i in range(HEADER_SIZE * 8)]
    header = _bits_to_bytes(header_bits)
    if header[:4] != MAGIC:
        raise ValueError("Stego magic header not found")
    payload_len = struct.unpack(">I", header[4:8])[0]
    if payload_len < 0 or payload_len > capacity_bytes(image):
        raise ValueError("Invalid stego payload length")

    total_bits = (HEADER_SIZE + payload_len) * 8
    if total_bits > len(flat):
        raise ValueError("Stego payload exceeds image capacity")
    all_bits = [flat[i] & 1 for i in range(total_bits)]
    framed = _bits_to_bytes(all_bits)
    return framed[HEADER_SIZE : HEADER_SIZE + payload_len]
