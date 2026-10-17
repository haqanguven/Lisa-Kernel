#!/usr/bin/env bash
set -euo pipefail
SOURCE=${SOURCE:?Set SOURCE to the reconstructed kernel source}
OUTPUT=${OUTPUT:?Set OUTPUT to a build directory}
CLANG_BIN=${CLANG_BIN:?Set CLANG_BIN to pinned Proton clang bin}
bundle=$(cd -- "$(dirname -- "$0")" && pwd)
mkdir -p "$OUTPUT"
cp "$bundle/kernel.config" "$OUTPUT/.config"
export PATH="$CLANG_BIN:$PATH"
args=(-C "$SOURCE" O="$OUTPUT" ARCH=arm64 TARGET_PRODUCT=lisa DYNAMIC_SINGLE_CHIP=qca6750 LOCALVERSION= CC="$CLANG_BIN/clang" LD="$CLANG_BIN/ld.lld" AR="$CLANG_BIN/llvm-ar" NM="$CLANG_BIN/llvm-nm" OBJCOPY="$CLANG_BIN/llvm-objcopy" OBJDUMP="$CLANG_BIN/llvm-objdump" STRIP="$CLANG_BIN/llvm-strip" HOSTCC=gcc HOSTCXX=g++ LLVM_IAS=1 CROSS_COMPILE=aarch64-linux-gnu-)
make "${args[@]}" olddefconfig
make "${args[@]}" -j6 Image
