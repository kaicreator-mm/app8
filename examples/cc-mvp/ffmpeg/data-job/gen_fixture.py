"""V04-FFMPEG-004 deterministic fixture generator (stdlib only, no target execution).

Generates a byte-deterministic raw gray8 video: 4 frames of 64x48.
Byte layout per frame f (0-based), row y, column x:
  y == 0  : byte(x) = (f + x) & 0xFF            (frame-tag row, frame identity)
  y >= 1  : byte = (x*31 + y*17 + f*53) & 0xFF
Frame size = 64*48 = 3072 bytes; file = 4*3072 = 12288 bytes.
"""
import hashlib
import pathlib

W, H, F = 64, 48, 4
out = pathlib.Path(__file__).resolve().parent / "fixture"
out.mkdir(exist_ok=True)
buf = bytearray()
for f in range(F):
    for y in range(H):
        for x in range(W):
            if y == 0:
                buf.append((f + x) & 0xFF)
            else:
                buf.append((x * 31 + y * 17 + f * 53) & 0xFF)
p = out / "input_gray8_64x48_f4.raw"
p.write_bytes(bytes(buf))
data = p.read_bytes()
print("file=", p)
print("size=", len(data))
print("sha256=", hashlib.sha256(data).hexdigest())
