"""Check raw BTF layout and type kinds against this kernel's format limits."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("btf", type=Path)
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    raw = args.btf.read_bytes()
    magic, version, flags, header_len, type_off, type_len, str_off, str_len = struct.unpack_from("<HBBIIIII", raw)
    if magic != 0xEB9F or version != 1 or flags or header_len < 24:
        raise ValueError("Unsupported BTF header")
    if any(raw[24:header_len]):
        raise ValueError("Nonzero header extension unsupported by this kernel")
    start, end = header_len + type_off, header_len + type_off + type_len
    strings = raw[header_len + str_off:header_len + str_off + str_len]
    if end > header_len + str_off or len(strings) != str_len or not strings:
        raise ValueError("Invalid section bounds")
    if strings[0] or strings[-1] or str_len - 1 > 0xFFFFFF:
        raise ValueError("Invalid string table")
    counts = Counter()
    required = {name: [] for name in ("bpf_ctx_convert", "udp_sock", "sock", "task_struct", "bpf_map", "bpf_prog", "inode", "file")}
    cursor = start
    total = 0
    while cursor < end:
        name_off, info, size = struct.unpack_from("<III", raw, cursor)
        kind, vlen = (info >> 24) & 31, info & 65535
        if kind not in range(1, 16):
            raise ValueError(f"Unsupported BTF kind {kind}")
        if name_off >= str_len:
            raise ValueError("Invalid type name offset")
        name_end = strings.find(b"\0", name_off)
        name = strings[name_off:name_end].decode("utf-8")
        extra = {1: 4, 3: 12, 4: vlen * 12, 5: vlen * 12, 6: vlen * 8,
                 13: vlen * 8, 14: 4, 15: vlen * 12}.get(kind, 0)
        cursor += 12 + extra
        counts[kind] += 1
        total += 1
        if name in required and kind == 4:
            required[name].append(total)
    if cursor != end or total > 0xFFFFF:
        raise ValueError("Invalid type table bounds or count")
    if any(not ids for ids in required.values()):
        raise ValueError(f"Missing required struct types: {required}")
    report = {"status": "STRUCTURAL_CHECK_ONLY_NOT_RUNTIME_VERIFIED",
              "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw),
              "header_len": header_len, "types": total, "kind_counts": dict(counts),
              "required_struct_ids": required}
    args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

