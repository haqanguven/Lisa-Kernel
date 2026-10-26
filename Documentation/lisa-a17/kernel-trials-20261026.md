# Lisa Android 17 kernel trials — 2026-10-26

Device: Xiaomi 11 Lite 5G NE (`lisa`), Android 17, active slot `_a`.

## Device state

The phone is booted to the lock/home screen with the original ROM kernel:

```
5.4.302-HyperOSPro #1 SMP PREEMPT Tue, 13 Oct 2026 11:44:11 +0300
```

The current `boot_a` was not written during these trials. Its verified local backup is
`C:\\Users\\Hakan\\Desktop\\Lisa-Kernel-20261026\\boot-oncesi-yedek.img`
(SHA-256 `135855390f0b3ed97e4f30a5e24b556f072be3ea14c0ce04db55c79330aa788d`).

## Temporary boot attempts

- LiFESTEAL baseline build `#13`: fastboot temporary boot left a black screen.
- MeowKernel Android 17 build `#12`: fastboot accepted the image, but the next ADB session reported the original `#1` kernel and Android returned to the lock/home screen. A successful boot of #12 was not verified.

No permanent boot write was performed. Local images and verification data remain in
`C:\\Users\\Hakan\\Desktop\\Lisa-Kernel-20261026`.

## ROM module ABI audit

The current ROM's `/vendor/lib/modules` was pulled locally and compared with each candidate's `Module.symvers`. All 334 module files had at least one symbol CRC mismatch for both candidates.

| Kernel candidate | Candidate `module_layout` CRC | ROM module CRC | Mismatched modules |
|---|---:|---:|---:|
| MeowKernel #12 | `0xb5ecb734` | `0x1e5b7ab7` | 334 / 334 |
| LiFESTEAL #13 | `0xe59a5ac0` | `0x1e5b7ab7` | 334 / 334 |

This ABI difference is a strong reason not to install either candidate against the current vendor modules. It likely explains the failed boot path, but the exact early-boot failure was not captured; `/sys/fs/pstore` was empty after recovery.

## Next required input

The next kernel build needs the source tree and build configuration that produced the currently working `ylmzer@lisa-builder` kernel, or a verified matching kernel source and vendor module set. The ROM package and local WSL build folders contain no matching `Module.symvers`. Do not flash the #12 or #13 candidate permanently based on these trials.
