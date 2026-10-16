# LiFESTEAL persistent boot diagnostics, 2026-10-16

Patch lifesteal-clean-logdiagnostic.patch applies only to AlphaDroid-devices/kernel_xiaomi_lisa at b54fcd3c1c03b7d4fdb39ccb93b78f026202b123. It includes the scoped uname option and ARM64 alignment. It is an alternative to lifesteal-clean-a17.patch, not an additional patch for the Meow source in this branch.

The recovery-derived config enables MTD, MTD_BLOCK2MTD and MTD_OOPS. BTF and LTO remain disabled. Existing Lisa boot arguments already target /dev/block/sda17, an oops log partition of 16MiB with 2MiB erase/record blocks. Built-in block2mtd now resolves Android /dev/block/name paths before device nodes/rootfs exist. The mtdoops maximum is raised from 8 to 16MiB.

The opt-in mtdoops.boot_snapshot=45 parameter schedules at most two snapshots at that interval after the backend attaches. Default zero disables it. It enables dump_oops only when opted in, never induces a panic, and stores records through the existing log backend. This is diagnostic code and should be disabled/removed for normal releases.

TWRP validation: new diagnostic kernel booted, backend attached at 1.7s and snapshot1 was written at48s. A readback contained the current release and snapshot marker.

ROM validation: a current 48s snapshot identifies 5.4.302-lisa-a17-logdiagnostic+, Android init first and second stages, system/vendor mounting, and vold waiting repeatedly for keystore2 while mounting encrypted userdata. Numerous existing ROM modules fail module_layout CRC checks. These are current records, unlike the older cached HyperOSPro logs. Built-in drivers mean module rejection alone does not establish the cause of the storage wait. No kernel panic or netbpfload execution was seen in this current snapshot. Android boot is still unverified.

A second temporary boot uses the same kernel with printk.devkmsg=on in the boot header to obtain init messages previously rate limited. Its result is pending. Boot/vendor_boot/dtbo/data were not flashed or formatted. The diagnostic backend writes only to the existing oops log partition. Raw device logs, user data, and partition backups are kept local.
