"""Repack a boot v3 image; preserve its ramdisk and omit obsolete AVB metadata."""
import argparse
import hashlib
import json
import pathlib
import struct


def align(value):
    return (value + 4095) & ~4095


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("original", type=pathlib.Path)
    parser.add_argument("kernel", type=pathlib.Path)
    parser.add_argument("output", type=pathlib.Path)
    args = parser.parse_args()
    original = args.original.read_bytes()
    kernel = args.kernel.read_bytes()
    if original[:8] != b"ANDROID!" or struct.unpack_from("<I", original, 40)[0] != 3:
        raise ValueError("Expected an Android boot header v3")
    if kernel[56:60] != b"ARM\x64":
        raise ValueError("Expected an uncompressed ARM64 kernel Image")
    original_size, ramdisk_size = struct.unpack_from("<II", original, 8)
    ramdisk_start = 4096 + align(original_size)
    ramdisk = original[ramdisk_start:ramdisk_start + ramdisk_size]
    if len(ramdisk) != ramdisk_size:
        raise ValueError("Truncated source ramdisk")
    header = bytearray(original[:4096])
    struct.pack_into("<I", header, 8, len(kernel))
    packed = header + kernel + bytes(align(len(kernel)) - len(kernel))
    packed += ramdisk + bytes(align(len(ramdisk)) - len(ramdisk))
    if len(packed) > len(original):
        raise ValueError("Candidate exceeds the original boot partition size")
    packed += bytes(len(original) - len(packed))
    args.output.write_bytes(packed)
    # Inspect the saved output, rather than only trusting construction.
    saved = args.output.read_bytes()
    saved_size, saved_ramdisk_size = struct.unpack_from("<II", saved, 8)
    saved_ramdisk_start = 4096 + align(saved_size)
    assert saved_size == len(kernel)
    assert saved[4096:4096 + saved_size] == kernel
    assert saved_ramdisk_size == ramdisk_size
    assert saved[saved_ramdisk_start:saved_ramdisk_start + saved_ramdisk_size] == ramdisk
    assert saved[-64:-60] != b"AVBf"
    report = {
        "status": "EXPERIMENTAL_UNFLASHED_NOT_BOOT_VALIDATED",
        "boot_header_version": 3,
        "image_size": len(saved),
        "kernel_size": saved_size,
        "ramdisk_preserved": True,
        "ramdisk_sha256": hashlib.sha256(ramdisk).hexdigest(),
        "boot_sha256": hashlib.sha256(saved).hexdigest(),
        "avb": "Unsigned; original AVB hash/footer not reused",
        "remaining_checks": ["ROM netbpfload 5.10 version guard", "vendor module ABI", "hardware and encrypted userdata boot"]
    }
    args.output.with_suffix(".json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
