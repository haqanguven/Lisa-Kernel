# Persistent boot repair — 2026-10-18

Two normal boot tests completed successfully after repair: sys.boot_completed=1, boot animation stopped, release 5.4.302-HyperOSPro. No temporary fastboot boot command was used for either test.

Read-only inspection found boot_a still contained the original 5.4.289 kernel, while its ramdisk SHA-256 exactly matched the confirmed #13 image. Vendor inspection and runtime AVC logs found libdmabufheap.so labeled vendor_file; SurfaceFlinger could not read it, failed to load OpenGL ES and restarted repeatedly.

The original boot_a (201326592 bytes) and current vendor_a (1439657984 bytes) were backed up locally before repair. The known audio-working #13 image was written permanently to boot_a. Entire partition readback SHA-256 matched 76ecd280d195438e39d4f2e831da6711f56b077e2ffe87d900518c66cc1f2e3a. Vendor V2 was restored and its image-length readback matched e147bd27e5f26c95377ffd9c7230e1220d518e611b7434ff8376b98186ddaf6b. Both libdmabufheap files were verified as same_process_hal_file in recovery, and runtime /dev/ion is ion_device.

The first normal reboot completed at uptime64s. A second normal adb reboot also completed at uptime68s with the expected kernel and labels. This resolves the observed boot failure in these tests. Longer-term stability and all hardware are not certified. Actual 5G remains unresolved.

Only active-slot boot_a and vendor_a were written for this repair; no slot_b, system_ext, modem, EFS or userdata changes. The earlier 'temporary kernel only' notes describe historical work and no longer describe the current boot_a state. Backups and phone logs remain local.
