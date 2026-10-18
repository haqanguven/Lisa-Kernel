"""Patch only vendor_a extents in an Android sparse super image, retaining liblp metadata.

Format reference: AOSP system/core/fs_mgr/liblp/include/liblp/metadata_format.h.
Never flashes a device. Original input is opened read-only; output must not exist.
"""
from pathlib import Path
import argparse, bisect, hashlib, json, struct

RAW, FILL, SKIP = 0xCAC1, 0xCAC2, 0xCAC3

class Sparse:
    def __init__(self, path):
        self.path = Path(path)
        self.f = self.path.open('rb')
        self.header = self.f.read(28)
        magic, major, minor, fh, ch, self.block, blocks, count, crc = struct.unpack('<IHHHHIIII', self.header)
        assert (magic, major, fh, ch, crc) == (0xED26FF3A, 1, 28, 12, 0)
        self.size = blocks * self.block
        self.chunks, self.starts = [], []
        pos = 0
        for _ in range(count):
            typ, reserved, nblocks, total = struct.unpack('<HHII', self.f.read(12))
            length = nblocks * self.block
            payload = self.f.tell()
            assert typ in (RAW, FILL, SKIP)
            assert total == 12 + (length if typ == RAW else 4 if typ == FILL else 0)
            self.starts.append(pos)
            self.chunks.append((pos, pos + length, typ, payload))
            self.f.seek(total - 12, 1)
            pos += length
        assert pos == self.size and self.f.tell() == self.path.stat().st_size

    def read(self, start, length):
        assert 0 <= start <= start + length <= self.size
        pieces = []
        while length:
            i = bisect.bisect_right(self.starts, start) - 1
            lo, hi, typ, payload = self.chunks[i]
            n = min(length, hi - start)
            if typ == RAW:
                self.f.seek(payload + start - lo)
                data = self.f.read(n)
            elif typ == FILL:
                self.f.seek(payload)
                word = self.f.read(4)
                offset = (start - lo) % 4
                data = (word * ((n + offset + 3) // 4))[offset:offset + n]
            else:
                data = bytes(n)
            assert len(data) == n
            pieces.append(data)
            start += n
            length -= n
        return b''.join(pieces)

def metadata(image):
    geometry = image.read(4096, 4096)
    magic, size = struct.unpack_from('<II', geometry)
    assert magic == 0x616C4467 and size == 52
    g = bytearray(geometry[:size]); g[8:40] = bytes(32)
    assert hashlib.sha256(g).digest() == geometry[8:40]
    max_size, slots, block = struct.unpack_from('<III', geometry, 40)
    assert block == image.block and 1 <= slots <= 4
    all_maps = []
    metadata_bytes = 12288 + 2 * slots * max_size
    for slot in range(slots * 2):
        blob = image.read(12288 + slot * max_size, max_size)
        magic, major, minor, header_size = struct.unpack_from('<IHHI', blob)
        assert magic == 0x414C5030 and major == 10 and minor <= 2
        header = bytearray(blob[:header_size]); header[12:44] = bytes(32)
        assert hashlib.sha256(header).digest() == blob[12:44]
        table_size = struct.unpack_from('<I', blob, 44)[0]
        tables = blob[header_size:header_size + table_size]
        assert hashlib.sha256(tables).digest() == blob[48:80]
        po, pn, ps = struct.unpack_from('<III', blob, 80)
        eo, en, es = struct.unpack_from('<III', blob, 92)
        assert ps == 52 and es == 24
        parts = {}
        for i in range(pn):
            name, attrs, first, count, group = struct.unpack_from('<36sIIII', tables, po + i * ps)
            name = name.split(b'\0', 1)[0].decode('ascii')
            assert first + count <= en
            extents = []
            for j in range(first, first + count):
                sectors, typ, sector, device = struct.unpack_from('<QIQI', tables, eo + j * es)
                assert typ == 0 and device == 0
                start, length = sector * 512, sectors * 512
                assert start >= metadata_bytes and start + length <= image.size
                extents.append((start, length))
            parts[name] = extents
        all_maps.append(parts)
    assert all(x == all_maps[0] for x in all_maps), 'Metadata slots differ; manual review required'
    return all_maps[0], metadata_bytes

def digest_ranges(image, ranges):
    h = hashlib.sha256()
    for start, length in ranges:
        for offset in range(0, length, 8 * 1024 * 1024):
            h.update(image.read(start + offset, min(8 * 1024 * 1024, length - offset)))
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('source', type=Path)
    ap.add_argument('--vendor', type=Path)
    ap.add_argument('--output', type=Path)
    args = ap.parse_args()
    original = Sparse(args.source)
    parts, meta_end = metadata(original)
    print(json.dumps({'expanded_bytes': original.size, 'partitions': parts}, indent=2), flush=True)
    if not args.vendor:
        return
    assert args.output and not args.output.exists()
    assert args.output.resolve() != args.source.resolve()
    vendor_size = args.vendor.stat().st_size
    assert vendor_size % original.block == 0
    assert sum(n for _, n in parts['vendor_a']) >= vendor_size
    patches, consumed = [], 0
    for start, length in parts['vendor_a']:
        n = min(length, vendor_size - consumed)
        if n:
            assert start % original.block == n % original.block == 0
            patches.append((start, start + n, consumed))
            consumed += n
    assert consumed == vendor_size
    # Reject overlapping logical allocations before changing any bytes.
    physical = sorted((s, s+n, name) for name, ext in parts.items() for s, n in ext if n)
    assert all(a[1] <= b[0] for a, b in zip(physical, physical[1:]))
    chunks = 0
    with args.vendor.open('rb') as replacement, args.output.open('xb') as out:
        out.write(original.header)
        for lo, hi, typ, payload in original.chunks:
            cuts = sorted({lo, hi} | {x for a,b,_ in patches for x in (a,b) if lo < x < hi})
            for a, b in zip(cuts, cuts[1:]):
                patch = next((p for p in patches if p[0] <= a and b <= p[1]), None)
                output_type = RAW if patch else typ
                length = b - a
                out.write(struct.pack('<HHII', output_type, 0, length // original.block,
                                      12 + (length if output_type == RAW else 4 if output_type == FILL else 0)))
                chunks += 1
                if patch:
                    replacement.seek(patch[2] + a - patch[0])
                if output_type == RAW:
                    for offset in range(0, length, 8 * 1024 * 1024):
                        n = min(8 * 1024 * 1024, length - offset)
                        data = replacement.read(n) if patch else original.read(a + offset, n)
                        assert len(data) == n
                        out.write(data)
                elif output_type == FILL:
                    original.f.seek(payload)
                    out.write(original.f.read(4))
        out.seek(20)
        out.write(struct.pack('<I', chunks))
    corrected = Sparse(args.output)
    assert corrected.size == original.size
    assert metadata(corrected) == (parts, meta_end)
    # Independently compare every virtual byte outside vendor replacement ranges,
    # including metadata, unused space and all other logical partitions.
    cursor = 0
    for a, b, _ in sorted(patches) + [(original.size, original.size, 0)]:
        if a > cursor:
            assert digest_ranges(original, [(cursor, a-cursor)]) == digest_ranges(corrected, [(cursor, a-cursor)])
        cursor = b
    expected_vendor = hashlib.sha256(args.vendor.read_bytes()).hexdigest()
    actual_vendor = digest_ranges(corrected, [(a, b-a) for a,b,_ in patches])
    assert actual_vendor == expected_vendor
    report = dict(status='VERIFIED_NOT_DEVICE_FLASHED', vendor_sha256=actual_vendor,
                  unchanged_outside_vendor=True, metadata_unchanged=True,
                  expanded_bytes=corrected.size, output_bytes=args.output.stat().st_size)
    with args.output.open('rb') as f:
        report['sparse_sha256'] = hashlib.file_digest(f, 'sha256').hexdigest()
    args.output.with_suffix('.validation.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2), flush=True)

if __name__ == '__main__':
    main()
