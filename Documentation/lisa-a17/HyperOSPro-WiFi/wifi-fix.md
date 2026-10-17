# HyperOSPro Wi-Fi path correction

Kernel release remains5.4.302-HyperOSPro. This build passes DYNAMIC_SINGLE_CHIP=qca6750 through qcacld's existing Kbuild mechanism. No Wi-Fi firmware content, vendor partition or module-ABI checks were modified.

Observed failure: old built-in driver requested wlan/qca_cld/WCNSS_qcom_cfg.ini. That ROM symlink points to /vendor/etc/wifi/WCNSS_qcom_cfg.ini, which is missing. The ROM contains a valid qca6750 subdirectory/config. Driver probe failed and Android Wi-Fi HAL returned EINVAL while writing its driver-state control. Compiled wlan_hdd_main.o now contains wlan/qca_cld/qca6750/WCNSS_qcom_cfg.ini.

Temporary boot validation: uname5.4.302-HyperOSPro, build#10, boot_completed1; Wi-Fi HAL started, Wi-Fi enabled, wlan0 exists, scan returned13 records. HAL, wificond and supplicant setup failure counters are zero. User connection/internet confirmation is pending; long-term stability and other hardware are not certified. Earlier MIUI-display candidate had one user-reported restart, then a337s successful lock/wake retest. Settings Unavailable remains a separate ROM parser issue.

Build: run reconstruct-miui-display.sh with a NEW source directory. Use supplied kernel.config and build-HyperOSPro.sh with SOURCE, OUTPUT and CLANG_BIN environment variables. Pins are in provenance.json. LOCALVERSION= is explicitly passed to suppress the automatic '+' suffix. BPF compatibility and official Lisa MIUI display integration remain as documented in the parent directory.

Boot SHA256:0f6191a9a011f0915c62b721a7d3cd3b8c033a5a3b13e78e4e20cbce2d582cb9. Original ROM ramdisk SHA256 remains0dc218f3167e560444634a6a8cf969eb4470bcf452837a3e23bf45ea0a6819ae. Unsigned bootv3,201326592bytes. Tested with temporary fastboot boot; no persistent boot write performed. No private network identifiers, raw logs, ROM images or partition backups are published.
