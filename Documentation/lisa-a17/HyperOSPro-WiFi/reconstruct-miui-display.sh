#!/usr/bin/env bash
# Reconstruct the source used for the first physical-display boot.
set -euo pipefail
bundle=$(cd -- "$(dirname -- "$0")" && pwd)
dest=${1:?Usage: reconstruct-miui-display.sh NEW_SOURCE_DIRECTORY}
test ! -e "$dest"
git clone --depth 1 --branch lifesteal_clean https://github.com/AlphaDroid-devices/kernel_xiaomi_lisa.git "$dest"
git -C "$dest" fetch --depth 1 origin b54fcd3c1c03b7d4fdb39ccb93b78f026202b123
git -C "$dest" checkout --detach b54fcd3c1c03b7d4fdb39ccb93b78f026202b123
git -C "$dest" apply "$bundle/base-a17-diagnostics.patch"
official=$(mktemp -d)
trap 'rm -rf -- "$official"' EXIT
git clone --depth 1 --filter=blob:none --sparse --branch lisa-r-oss https://github.com/MiCode/Xiaomi_Kernel_OpenSource.git "$official/source"
git -C "$official/source" fetch --depth 1 origin 57ee2b068000ac79caa7c076d0d9bb1a9260e8a4
git -C "$official/source" checkout --detach 57ee2b068000ac79caa7c076d0d9bb1a9260e8a4
git -C "$official/source" sparse-checkout set techpack/display include/drm
cp "$dest/techpack/display/Makefile" "$official/Makefile"
cp -a "$dest/techpack/display/config" "$official/config"
cp -a "$official/source/techpack/display/." "$dest/techpack/display/"
cp "$official/Makefile" "$dest/techpack/display/Makefile"
cp -a "$official/config/." "$dest/techpack/display/config/"
cp "$official/source/include/drm/mi_disp_notifier.h" "$dest/include/drm/mi_disp_notifier.h"
find "$dest/techpack/display" -type f -exec touch {} +
printf 'Source ready. Use supplied kernel.config and pinned Proton toolchain; see first-visible-boot.md.\n'
