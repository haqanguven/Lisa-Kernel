from pathlib import Path
import struct
import zipfile
import json
import sys


def dex_api(path):
    references, definitions, parents = set(), set(), {}
    with zipfile.ZipFile(path) as archive:
        for entry in archive.namelist():
            if not entry.endswith('.dex'):
                continue
            data = archive.read(entry)

            def u32(offset):
                return struct.unpack_from('<I', data, offset)[0]

            def uleb(offset):
                value, shift = 0, 0
                while True:
                    byte = data[offset]
                    offset += 1
                    value |= (byte & 127) << shift
                    if byte < 128:
                        return value, offset
                    shift += 7

            strings = []
            for i in range(u32(56)):
                _, offset = uleb(u32(u32(60) + i * 4))
                strings.append(data[offset:data.index(0, offset)].decode('utf-8', errors='replace'))
            types = [strings[u32(u32(68) + i * 4)] for i in range(u32(64))]
            protos = []
            for i in range(u32(72)):
                _, result, parameters = struct.unpack_from('<III', data, u32(76) + i * 12)
                args = [] if not parameters else [types[struct.unpack_from('<H', data, parameters + 4 + j * 2)[0]] for j in range(u32(parameters))]
                protos.append('(' + ''.join(args) + ')' + types[result])
            methods = []
            for i in range(u32(88)):
                owner, proto, name = struct.unpack_from('<HHI', data, u32(92) + i * 8)
                methods.append((types[owner], strings[name] + protos[proto]))
            references.update(methods)
            for i in range(u32(96)):
                base = u32(100) + i * 32
                owner, parent, offset = types[u32(base)], u32(base + 8), u32(base + 24)
                parents[owner] = None if parent == 0xffffffff else types[parent]
                if not offset:
                    continue
                counts = []
                for _ in range(4):
                    count, offset = uleb(offset)
                    counts.append(count)
                for _ in range(counts[0] + counts[1]):
                    _, offset = uleb(offset)
                    _, offset = uleb(offset)
                for count in counts[2:]:
                    index = 0
                    for _ in range(count):
                        diff, offset = uleb(offset)
                        index += diff
                        _, offset = uleb(offset)
                        _, offset = uleb(offset)
                        definitions.add(methods[index])
    return references, definitions, parents


root = Path(__file__).resolve().parent
candidate = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else root / 'stock-lisa-reference/QtiTelephony-stock.apk'
refs, candidate_definitions, stock_parents = dex_api(candidate)
library = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else root.parent / 'attempt-lifesteal-a17/extphonelib-current.jar'
_, current, current_parents = dex_api(library)


def resolves(owner, signature):
    seen = set()
    while owner and owner not in seen:
        if (owner, signature) in current:
            return True
        seen.add(owner)
        owner = current_parents.get(owner)
    return False


external = sorted((owner, signature) for owner, signature in refs if owner.startswith('Lcom/qti/extphone/') and owner not in stock_parents)
inherited = [owner + '->' + signature for owner, signature in external if signature == 'asBinder()Landroid/os/IBinder;']
missing = [owner + '->' + signature for owner, signature in external if signature != 'asBinder()Landroid/os/IBinder;' and not resolves(owner, signature)]
result = {'candidate': str(candidate.relative_to(root)), 'scope': 'Referenced extphonelib method signatures only; not full runtime/API compatibility. AIDL asBinder is inherited from framework IInterface.', 'references_checked': len(external), 'framework_inherited': inherited, 'missing': missing}
stubs = [owner for owner, parent in stock_parents.items() if parent == 'Lcom/qti/extphone/IExtPhone$Stub;']
required = sorted(signature for owner, signature in current if owner == 'Lcom/qti/extphone/IExtPhone;')
result['current_binder_methods_not_implemented_by_candidate'] = {
    owner: [signature for signature in required if (owner, signature) not in candidate_definitions and signature != 'asBinder()Landroid/os/IBinder;' and not resolves(stock_parents[owner], signature)]
    for owner in stubs
}
(candidate.parent / 'extphonelib-api-audit.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result, indent=2))
