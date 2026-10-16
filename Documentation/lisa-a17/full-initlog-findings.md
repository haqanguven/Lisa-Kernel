# Current full init log findings, 2026-10-16

The temporary ROM image with printk.devkmsg=on yielded a current mtdoops record (sequence3), identifying 5.4.302-lisa-a17-logdiagnostic+ and the 48s snapshot marker.

Correction to earlier uncertainty: init parsed keystore2.rc, started keystore2 at9.419s (pid825); it was not simply absent from init configuration. Vold still waited for its Binder service. Qualcomm vendor.keymaster-4-1 repeatedly received SIGABRT. Current SELinux AVCs deny TEE and keymaster read access to /dev/ion, labeled generic device.

Read-only inspection found no /dev/ion context entry in the ROM's platform, system_ext, product, vendor or ODM file contexts. Platform policy defines ion_device; mapping30.0 associates ion_device_30_0 with it, and vendor TEE policy already grants that type access. The prepared ROM patch adds only the missing /dev/ion -> ion_device context; it neither disables SELinux nor adds broad allow rules. It targets a verified labeling defect but has not been installed or boot-tested and does not establish the cause of every keymaster failure.

ROM module_layout CRC mismatches remain. They must be resolved with a matching kernel/module set, not forced CRCs. No netbpfload execution appears before the storage wait in this snapshot, so Android17 BPF support has not been runtime-validated.

The device is back in original working TWRP5.4.302-LiFESTEAL_lisa-v2.2-qgki+. No boot/vendor_boot/dtbo partition writes or userdata formatting occurred. Experimental mtdoops logging wrote the existing oops log partition only. Raw logs and binary partition backups remain local.

Next work requires integrating and validating the narrow file-context correction in a separately prepared ROM vendor image or supported ROM overlay, while preserving EROFS metadata, SELinux contexts and AVB/partition constraints. This repository remains experimental; no Android boot success is claimed.
