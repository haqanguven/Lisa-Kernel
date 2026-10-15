"""Compare the ROM's ELF module symbol CRCs with a candidate Module.symvers."""
import argparse
import json
import pathlib
import struct


def module_versions(path):
    data = path.read_bytes()
    if data[:6] != b"\x7fELF\x02\x01":
        raise ValueError(f"Not a little-endian ELF64 module: {path}")
    offset = struct.unpack_from("<Q", data, 40)[0]
    size, count, string_index = struct.unpack_from("<HHH", data, 58)
    headers = [struct.unpack_from("<IIQQQQIIQQ", data, offset + i * size) for i in range(count)]
    strings_header = headers[string_index]
    strings = data[strings_header[4]:strings_header[4] + strings_header[5]]
    versions = {}
    for header in headers:
        name = strings[header[0]:].split(b"\0", 1)[0]
        if name != b"__versions":
            continue
        section = data[header[4]:header[4] + header[5]]
        if len(section) % 64:
            raise ValueError(f"Unexpected module version record size: {path}")
        for record in range(0, len(section), 64):
            crc = struct.unpack_from("<Q", section, record)[0]
            symbol = section[record + 8:record + 64].split(b"\0", 1)[0].decode("ascii")
            versions[symbol] = crc
    return versions


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("symvers", type=pathlib.Path)
    parser.add_argument("modules", type=pathlib.Path)
    parser.add_argument("output", type=pathlib.Path)
    args = parser.parse_args()
    candidate = {}
    for line in args.symvers.read_text().splitlines():
        fields = line.split()
        if len(fields) >= 2:
            candidate[fields[1]] = int(fields[0], 16)
    results = []
    for path in sorted(args.modules.rglob("*.ko")):
        versions = module_versions(path)
        mismatches = [
            {"symbol": symbol, "rom_crc": f"0x{crc:08x}",
             "candidate_crc": None if symbol not in candidate else f"0x{candidate[symbol]:08x}"}
            for symbol, crc in versions.items() if candidate.get(symbol) != crc
        ]
        results.append({"module": str(path.relative_to(args.modules)),
                        "checked_symbols": len(versions), "mismatches": mismatches})
    incompatible = sum(bool(result["mismatches"]) for result in results)
    report = {"modules_checked": len(results), "modules_with_crc_mismatch_or_missing_export": incompatible,
              "candidate_module_layout_crc": candidate.get("module_layout"), "results": results}
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Checked {len(results)} ROM modules; {incompatible} have mismatched or missing symbol CRCs.")


if __name__ == "__main__":
    main()
