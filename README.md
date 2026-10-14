# Lisa Kernel: experimental Android 17 compatibility

Kernel work for Xiaomi 11 Lite 5G NE (`lisa`) and a HyperOS Android 17 port.

**Experimental: no successful device boot has been verified.** The actual
kernel remains Linux 5.4.302. Existing ROM modules have incompatible symbol
CRCs and must not be treated as compatible replacement drivers.

## Source and changes

The source is pinned to MeowKernel commit
`240b4a2e8265ce2100024a4e94b596b35a2d6afe` from
[MirahSyakilla/android_kernel_xiaomi_lisa](https://github.com/MirahSyakilla/android_kernel_xiaomi_lisa).
That source already contains BPF ring buffer and other BPF backports; their
authors retain credit and copyrights.

Local changes select Lisa hardware, enable BPF/BTF options, remove unavailable
KernelSU build integration, and adapt BTF generation for modern pahole.
`CONFIG_ANDROID_NETBPFLOAD_COMPAT` reports `5.10.248` only to `netbpfload`, so
Android 17's numerical version check can reach real BPF feature checks.
This does not upgrade Linux and does not prove all ROM BPF objects will load.

## Build

The Actions workflow imports the pinned full kernel source on the first run,
applies the patch, and records it as a new commit without overwriting divergent
remote work. It then builds Image and matching modules. Until that import
completes, this repository contains the pinned source reference, patch, config,
and build tools rather than the complete source tree.

On a Linux build host with clang/LLVM 14, GCC, binutils, flex, bison, libssl-dev,
cpio, and pahole installed:

```sh
CLANG_BIN=/usr/lib/llvm-14/bin ./build-lisa.sh
```

BTF generation can require more than 8 GB of memory; provision sufficient RAM
and swap. Outputs are under `out/lisa-a17/`.

The workflow uploads Image, built modules, configuration, Module.symvers, and
build logs as artifacts. It does not upload device backups or private logs,
flash a device, or publish a boot-tested release.

`tools/pack-experimental-boot.py` can repack a local original boot v3 image with
Image while preserving its ramdisk. Its output is unsigned and requires AVB,
driver ABI, BPF loading, and encrypted userdata checks before installation.
`tools/audit-module-abi.py` compares actual imported module CRCs with
Module.symvers; changing vermagic or disabling checks is not an ABI fix.

The imported kernel source retains its original license files. Kernel changes
are distributed under the applicable Linux kernel GPL-2.0 license.
