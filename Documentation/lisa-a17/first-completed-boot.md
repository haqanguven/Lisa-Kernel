# First completed Android 17 boot, 2026-10-17

A temporary boot of the LiFESTEAL diagnostic kernel with vendor label correction v2 reached Android on the physical Lisa device.

Observed through ADB:
- Linux 5.4.302-lisa-a17-logdiagnostic+.
- Android17, SDK37, HyperOS fingerprint OS4.0.2.0.XPCCNXM.
- SurfaceFlinger, zygote and keystore2 running.
- Userdata mounted and launcher activity present.
- Later sys.boot_completed=1 and service.bootanim.exit=1.

ADB subsequently disappeared. The user's screen confirmation and long-term stability are pending. Two child-process SIGABRT entries named init were observed but not attributed. This is a verified completed boot, not a full hardware/stability certification.

## Exact working inputs
Source: AlphaDroid-devices/kernel_xiaomi_lisa, lifesteal_clean, b54fcd3c1c03b7d4fdb39ccb93b78f026202b123.
Apply patches/lifesteal-clean-logdiagnostic.patch to that source ONLY.
This branch's root source is still the earlier Meow experiment and is not the source of the booted binary.

Boot image: boot-rom-full-initlog.img SHA256 4d9e33cea5f58775232a7bdc1ec7f2aa3338a24d8c1a98f912a2db28b48d8d0b.
Uses original ROM ramdisk and printk.devkmsg=on, with the tested diagnostic kernel/config.
Kernel built with pinned ProtonClang13, recovery-derived config, LTO/BTF/root integration disabled.
The scoped netbpfload uname option does not upgrade Linux to5.10.

Vendor v2: vendor-graphics-fixed-v2.img SHA256 e147bd27e5f26c95377ffd9c7230e1220d518e611b7434ff8376b98186ddaf6b.
Size1350279168, partition1439657984. EROFS format needs Linux5.4.
Added ION context rule and libdmabufheap.so context rule. Changed security.selinux xattr of both lib/libdmabufheap.so and lib64/libdmabufheap.so to u:object_r:same_process_hal_file:s0, preserving all binary contents. A file-context rule alone is insufficient for these existing read-only EROFS files; the inode xattrs must also be corrected.
Re-extraction verified all5056 entries against expected data, ownership, permissions, timestamps, symlinks and xattrs with zero unexpected differences.

The prior ION-only vendor fix removed ION AVCs and allowed storage/boot progress. That current log also confirmed Android bpfloader and hyper_bpfloader exited status0 and bpf.progs_loaded=1. SurfaceFlinger then repeatedly aborted with libdmabufheap.so generic vendor_file AVCs; v2 addressed that specific label.

## Device state and remaining work
Vendor_a v2 was written with user authorization and read back with matching hash. Original vendor backup remains local. Kernel was booted temporarily: boot_a was NOT flashed. Reboot therefore does not preserve the experimental kernel.
No userdata formatting, super resizing, CRC forcing, or SELinux permissive mode was used.
Module ABI mismatches remain in logs; verify hardware, radio/Wi-Fi/audio/camera/fingerprint and suspend before normal use. Boot snapshots are diagnostic and write only to existing oops log partition when enabled.
Do not distribute this as a stable Android17 kernel. ROM/kernel binaries and raw device logs remain local; this repository contains patches and findings.
