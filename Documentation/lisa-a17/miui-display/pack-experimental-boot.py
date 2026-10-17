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
    parser.add_argument("--append-cmdline", default="")
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
    if args.append_cmdline:
        command = header[44:1580].split(b"\0", 1)[0]
        addition = args.append_cmdline.encode("ascii")
        if any(byte in addition for byte in (0, 10, 13)):
            raise ValueError("Command line must not contain NUL or newlines")
        command = command + (b" " if command else b"") + addition
        if len(command) >= 1536:
            raise ValueError("Command line exceeds boot v3 header capacity")
        header[44:1580] = command.ljust(1536, b"\0")
    assert len(header) == 4096
    struct.pack_into("<I", header, 8, len(kernel))
    packed = header + kernel + bytes(align(len(kernel)) - len(kernel))
    packed += ramdisk + bytes(align(len(ramdisk)) - len(ramdisk))
    if len(packed) > len(original):
        raise ValueError("Candidate exceeds the original boot partition size")
    packed += bytes(len(original) - len(packed))
    args.output.write_bytes(packed)
    # Inspect the saved output, rather than only trusting construction.
    saved = args.output.read_bytes()
    assert len(saved) == len(original)
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
        "header_cmdline": saved[44:1580].split(b"\0", 1)[0].decode("ascii"),
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
