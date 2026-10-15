#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
CLANG_BIN=${CLANG_BIN:-$ROOT/.toolchains/proton-clang/bin}
OUTPUT=${OUTPUT:-$ROOT/out/lisa-a17}
JOBS=${JOBS:-4}
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$CLANG_BIN
mkdir -p "$OUTPUT"
if [[ ! -f "$ROOT/Makefile" ]]; then
    echo 'The pinned kernel source has not been imported yet. Run the Actions workflow first.' >&2
    exit 1
fi
if [[ ! -f "$OUTPUT/.config" ]]; then
    gzip -dc "$ROOT/configs/lisa_hyperos17.config.gz" > "$OUTPUT/.config"
fi
# Keep BTF, but avoid LTO's large merged debug units on memory-limited hosts.
"$ROOT/scripts/config" --file "$OUTPUT/.config" \
    --disable LTO_CLANG --disable THINLTO --enable LTO_NONE
ARGS=( -C "$ROOT" O="$OUTPUT" ARCH=arm64
    CC="$CLANG_BIN/clang" LD="$CLANG_BIN/ld.lld"
    AR="$CLANG_BIN/llvm-ar" NM="$CLANG_BIN/llvm-nm"
    OBJCOPY="$CLANG_BIN/llvm-objcopy" OBJDUMP="$CLANG_BIN/llvm-objdump"
    STRIP="$CLANG_BIN/llvm-strip" HOSTCC=gcc HOSTCXX=g++
    LLVM_IAS=1 CROSS_COMPILE=aarch64-linux-gnu- PAHOLE="${PAHOLE:-pahole}" )
make "${ARGS[@]}" olddefconfig
mkdir -p "$OUTPUT/tools/bpf/resolve_btfids"
make -C "$ROOT/tools/bpf/resolve_btfids" \
    OUTPUT="$OUTPUT/tools/bpf/resolve_btfids/" HOSTCC=gcc HOSTLD=ld HOSTAR=ar -j"$JOBS"
make "${ARGS[@]}" -j"$JOBS" Image modules
mkdir -p "$OUTPUT/artifacts/modules"
cp "$OUTPUT/arch/arm64/boot/Image" "$OUTPUT/artifacts/Image"
"$CLANG_BIN/llvm-objcopy" --dump-section .BTF="$OUTPUT/artifacts/vmlinux.btf" "$OUTPUT/vmlinux"
python3 "$ROOT/tools/inspect-btf.py" "$OUTPUT/artifacts/vmlinux.btf" "$OUTPUT/artifacts/btf-report.json"
cp "$OUTPUT/.config" "$OUTPUT/artifacts/kernel.config"
cp "$OUTPUT/Module.symvers" "$OUTPUT/artifacts/Module.symvers"
cp "$OUTPUT/modules.builtin" "$OUTPUT/artifacts/modules.builtin"
cp "$OUTPUT/modules.order" "$OUTPUT/artifacts/modules.order"
while IFS= read -r -d '' module_path; do
    relative=${module_path#"$OUTPUT/"}
    mkdir -p "$OUTPUT/artifacts/modules/$(dirname -- "$relative")"
    cp "$module_path" "$OUTPUT/artifacts/modules/$relative"
    "$CLANG_BIN/llvm-strip" --strip-debug "$OUTPUT/artifacts/modules/$relative"
done < <(find "$OUTPUT" -path "$OUTPUT/artifacts" -prune -o -name '*.ko' -print0)
python3 "$ROOT/tools/audit-module-abi.py" "$OUTPUT/Module.symvers" \
    "$OUTPUT/artifacts/modules" "$OUTPUT/artifacts/candidate-module-abi.json"
python3 - "$OUTPUT/artifacts/candidate-module-abi.json" <<'PY'
import json, sys
result = json.load(open(sys.argv[1]))
if result['modules_with_crc_mismatch_or_missing_export']:
    raise SystemExit('Candidate modules failed the symbol CRC audit')
PY
tar -C "$OUTPUT/artifacts" -czf "$OUTPUT/artifacts/modules.tar.gz" modules
sha256sum "$OUTPUT/artifacts/Image" "$OUTPUT/artifacts/modules.tar.gz" \
    "$OUTPUT/artifacts/vmlinux.btf" \
    > "$OUTPUT/artifacts/SHA256SUMS"

