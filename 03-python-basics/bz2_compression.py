from __future__ import annotations

import bz2
import gzip
import lzma
import zlib
from dataclasses import dataclass
from tempfile import TemporaryDirectory
from pathlib import Path
from typing import Callable


DATA = (
    b"Donec rhoncus quis sapien sit amet molestie. Fusce scelerisque vel augue "
    b"nec ullamcorper. Nam rutrum pretium placerat. Aliquam vel tristique lorem, "
    b"sit amet cursus ante. In interdum laoreet mi, sit amet ultrices purus "
    b"pulvinar a. Nam gravida euismod magna, non varius justo tincidunt feugiat. "
    b"Aliquam pharetra lacus non risus vehicula rutrum. Maecenas aliquam leo "
    b"felis. Pellentesque semper nunc sit amet nibh ullamcorper, ac elementum "
    b"dolor luctus. Curabitur lacinia mi ornare consectetur vestibulum. "
) * 100


@dataclass(frozen=True)
class Codec:
    name: str
    extension: str
    compress: Callable[[bytes], bytes]
    decompress: Callable[[bytes], bytes]
    typical_use: str


CODECS = [
    Codec(
        name="gzip",
        extension=".gz",
        compress=lambda data: gzip.compress(data, compresslevel=6, mtime=0),
        decompress=gzip.decompress,
        typical_use="General-purpose files, logs, HTTP content encoding",
    ),
    Codec(
        name="bz2",
        extension=".bz2",
        compress=lambda data: bz2.compress(data, compresslevel=9),
        decompress=bz2.decompress,
        typical_use="Better ratio than gzip on some text, but slower",
    ),
    Codec(
        name="lzma/xz",
        extension=".xz",
        compress=lambda data: lzma.compress(data, preset=6),
        decompress=lzma.decompress,
        typical_use="High compression ratio, slower and more memory-hungry",
    ),
    Codec(
        name="zlib",
        extension=".zlib",
        compress=lambda data: zlib.compress(data, level=6),
        decompress=zlib.decompress,
        typical_use="Protocols and in-memory payloads, not a common file format",
    ),
]


def compare_in_memory(data: bytes) -> None:
    print("In-memory compression")
    print("-" * 88)
    print(f"{'module':<10} {'size':>8} {'ratio':>8}  {'round-trip':<10}  use case")

    for codec in CODECS:
        compressed = codec.compress(data)
        restored = codec.decompress(compressed)
        ratio = len(data) / len(compressed)
        print(
            f"{codec.name:<10} "
            f"{len(compressed):>8} "
            f"{ratio:>8.2f}  "
            f"{str(restored == data):<10}  "
            f"{codec.typical_use}"
        )


def write_compressed_files(data: bytes) -> None:
    print("\nFile APIs")
    print("-" * 88)

    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        paths = {
            "gzip": temp_path / "sample.txt.gz",
            "bz2": temp_path / "sample.txt.bz2",
            "lzma": temp_path / "sample.txt.xz",
        }

        with gzip.open(paths["gzip"], "wb", compresslevel=6) as file:
            file.write(data)

        with bz2.open(paths["bz2"], "wb", compresslevel=9) as file:
            file.write(data)

        with lzma.open(paths["lzma"], "wb", preset=6) as file:
            file.write(data)

        readers = {
            "gzip": gzip.open,
            "bz2": bz2.open,
            "lzma": lzma.open,
        }

        for name, path in paths.items():
            with readers[name](path, "rb") as file:
                restored = file.read()
            print(
                f"{name:<10} {path.name:<16} "
                f"{path.stat().st_size:>8} bytes  "
                f"round-trip={restored == data}"
            )


def stream_with_zlib(data: bytes) -> None:
    print("\nzlib streaming")
    print("-" * 88)

    compressor = zlib.compressobj(level=6)
    compressed_parts = []

    for start in range(0, len(data), 128):
        compressed_parts.append(compressor.compress(data[start : start + 128]))
    compressed_parts.append(compressor.flush())

    compressed = b"".join(compressed_parts)
    restored = zlib.decompress(compressed)

    print(f"compressed size: {len(compressed)} bytes")
    print(f"round-trip matches original: {restored == data}")


if __name__ == "__main__":
    compare_in_memory(DATA)
    write_compressed_files(DATA)
    stream_with_zlib(DATA)
