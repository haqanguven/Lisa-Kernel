# First visible MIUI-display boot (2026-10-17)

Status: EXPERIMENTAL, UNSTABLE. The user saw the physical lockscreen/home screen for the first time with this candidate, then reported freezing and restarting. This is not a stable release. Restart cause awaits persistent kernel logs. No permanent boot partition write was performed. Vendor_a V2 label fixes remain installed.

Kernel: 5.4.302-lisa-miui-display+. ADB confirmed sys.boot_completed=1 and bootanim stopped at uptime83s. /dev/mi_display/disp_feature now exists. ROM displayfeature.default.so references that device and panel_info; the previous AOSP-oriented display source lacked those interfaces. Restoring the official Lisa display stack coincided with restored physical output; this does not establish which individual change was necessary.

Base: AlphaDroid-devices/kernel_xiaomi_lisa, b54fcd3c1c03b7d4fdb39ccb93b78f026202b123.
Display overlay: MiCode/Xiaomi_Kernel_OpenSource, lisa-r-oss, 57ee2b068000ac79caa7c076d0d9bb1a9260e8a4.
Keep the base techpack/display/Makefile and config directory for built-in linkage. Copy the official include/drm/mi_disp_notifier.h. Touch copied sources to avoid stale objects. All selected drivers are built in; do not force incompatible vendor module CRCs.

This directory contains source reconstruction script, base patch, exact kernel.config and packer. Invoke reconstruction with a NEW source directory. Build Image with Proton clang13 commit9fb011b183fe7e69b04b873ef6533b4b077e3c5e, ARCH=arm64 TARGET_PRODUCT=lisa LLVM_IAS=1 CROSS_COMPILE=aarch64-linux-gnu-, CC=clang LD=ld.lld and matching LLVM tools. HOSTCC=gcc HOSTCXX=g++. Use a separate O=directory and copy kernel.config as .config, then olddefconfig and -j6 Image. Root integrations, BTF and LTO are disabled in this candidate. The scoped netbpfload compatibility and persistent diagnostic patches remain.

Boot image SHA256: 6efcb24397d4c0b0a330396467990f96c3479096131e95f6b7b04869267fbde0.
Image size47034880 bytes; boot image201326592 bytes. Original ROM ramdisk is byte-identical, SHA256 0dc218f3167e560444634a6a8cf969eb4470bcf452837a3e23bf45ea0a6819ae. Unsigned repack, temporary fastboot boot only.

Before this driver change, a reversible MIUI screen_optimize_mode1->3 test changed effective mode258->257 but the physical panel stayed black. Restored mode1/color258 and shell WRITE_SETTINGS AppOp default, independently verified. No settings permission change remains.

Private logs, screenshots, ROM images and partition backups are not included in this repository. Root repository source/workflow still represents the earlier Meow experiment; use this directory's reconstruction instructions for this candidate.
