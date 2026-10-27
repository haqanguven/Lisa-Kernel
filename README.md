# Lisa Kernel: experimental Android 17 compatibility

Kernel work for Xiaomi 11 Lite 5G NE (`lisa`) and a HyperOS Android 17 port.

**Experimental: this kernel has booted on Lisa with the HyperOSPro Android 17 port.**
That single-device boot does not establish full-ROM stability. The kernel
remains Linux 5.4.302. Existing ROM modules have incompatible symbol CRCs and
must not be treated as compatible replacement drivers.

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

The full pinned kernel source is imported, including upstream tracked files
matched by its own ignore rules. The Actions workflow builds Image and matching
modules from this repository.

On a Linux build host with the pinned Proton clang/LLVM 13, GCC, binutils, flex, bison, libssl-dev,
cpio, and pahole installed:

```sh
CLANG_BIN=/path/to/proton-clang/bin PAHOLE=/path/to/pahole-1.32 ./build-lisa.sh
```

BTF remains enabled. LTO is disabled to avoid large merged debug units during
BTF generation on memory-limited hosts. The workflow builds pahole 1.32, pinned
to `fa725d687ce3a712ef296b46bc63ea57ef466014`, with its pinned libbpf submodule.
Provision sufficient RAM and swap. Outputs are under `out/lisa-a17/`.

The Linux v5.10 `resolve_btfids` host tool is included with an ELF-only parser
adaptation and the duplicate-name counting fix from Linux v5.15. The host BTF
reader accepts only zero-filled header extensions, and its BTF UAPI header is
synchronized with this kernel. Unresolved BTF IDs remain fatal. The build also
checks generated BTF type kinds and required kernel structures; these are
structural checks, not a substitute for the runtime kernel verifier.

The Actions workflow fetches Proton clang commit
`9fb011b183fe7e69b04b873ef6533b4b077e3c5e` from
[kdrag0n/proton-clang](https://github.com/kdrag0n/proton-clang), matching the
toolchain used for the local compilation.

The workflow uploads Image, built modules, configuration, Module.symvers, and
build logs as artifacts. It does not upload device backups or private logs,
flash a device, or publish a boot-tested release.

A separate device test verified the vendor policy adjustments required for
MiSound and vibration on the Android 17 Lisa port. These are vendor_a policy
changes, not kernel changes. See
[the device test notes](Documentation/devices/lisa-android17-vendor-policy.md)
and [the vendor policy patch](patches/lisa-a17-hyperospro-vendor-policy.patch).
The tested 1.36 GB vendor_a image is kept outside the repository; the notes
include its SHA-256.

`tools/pack-experimental-boot.py` can repack a local original boot v3 image with
Image while preserving its ramdisk. Its output is unsigned and requires AVB,
driver ABI, BPF loading, and encrypted userdata checks before installation.
`tools/audit-module-abi.py` compares actual imported module CRCs with
Module.symvers; changing vermagic or disabling checks is not an ABI fix.

The imported kernel source retains its original license files. Kernel changes
are distributed under the applicable Linux kernel GPL-2.0 license.

