# Device boot investigation, 2026-10-16

No successful Android 17 boot has been verified. All device tests used temporary
`fastboot boot`; boot/vendor_boot/dtbo partitions were not flashed and userdata
was not formatted.

## Meow source candidates

The first candidate built successfully both locally and in Actions run
38785113767 (commit 5985f799e18078d488be4b28c6c31ee0ff0866b3).
Its 51 modules passed CRC checks against their own Module.symvers. Structural
BTF validation passed; this did not establish runtime compatibility.

The ROM ramdisk and original TWRP ramdisk both stalled at the Mi logo with the
candidate kernel. The second candidate used upstream lisa_defconfig with BTF,
strict module version checks, root integration disabled and additional boot
logging. It compiled but also stalled with the TWRP ramdisk. It produced no
separate modules; its selected drivers were built in.

The working ROM and TWRP kernels have Image text_offset 0x80000. The original
Meow candidate had zero. A controlled copy changing only this Image header
field was tested; the reported outcome was a black screen or restart, with no
ADB. This is not proof of reaching a particular kernel initialization stage.
The source now records the legacy offset for further diagnosis.

Pstore was empty and /proc/last_kmsg absent. Cached recovery logs and oops
records did not contain either candidate's release name; historical failures
must not be attributed to these tests. LOGFS boot records were also inspected
locally without obtaining a current kernel failure trace. Device logs and
partition backups are not part of this repository.

## Alternative baseline under investigation

The working recovery kernel identifies as 5.4.302-LiFESTEAL_lisa-v2.2-qgki+.
The related public source was located at
https://github.com/AlphaDroid-devices/kernel_xiaomi_lisa, branch lifesteal_clean,
pinned to b54fcd3c1c03b7d4fdb39ccb93b78f026202b123. This is a related kernel
family, not a verified exact source match for that recovery binary.

A separate local baseline build uses the extracted recovery configuration,
disables root integration and LTO, and initially keeps BTF disabled as in the
working recovery. Its immediate purpose is to establish a booting source
baseline before adding Android 17 compatibility changes. It is not an
Android 17 release.

