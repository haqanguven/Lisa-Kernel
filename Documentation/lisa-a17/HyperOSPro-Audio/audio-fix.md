# Lisa audio registration fix — 2026-10-18

User confirmed two-way call audio with temporary build #13, Linux 5.4.302-HyperOSPro. The user also confirms apps open successfully. Wi-Fi/internet, physical display and kernel-version display were previously confirmed. 5G remains under investigation; this is not a complete hardware certification.

The baseline MI2S driver expected a single `qcom,msm-mi2s-lines` property and split RX/TX DAI IDs. Lisa's device tree instead provides separate RX/TX lines and bidirectional IDs. Six MI2S probes failed with EINVAL, preventing sound-card registration. Restoring the official Lisa driver and header bound those devices, but the old link table then requested an absent `msm-dai-q6-mi2s.6`. Restoring the matching Lisa link table resolved registration; controlC0 and playback/capture PCM devices appeared and the HAL opened playback streams.

The exact changes are in `lisa-mi2s-v2.patch`, against pinned LiFESTEAL base `b54fcd3c1c03b7d4fdb39ccb93b78f026202b123`. Three files come from official Xiaomi Lisa commit `57ee2b068000ac79caa7c076d0d9bb1a9260e8a4`:

- techpack/audio/asoc/msm-dai-q6-v2.c
- techpack/audio/asoc/msm-dai-q6-v2.h
- techpack/audio/asoc/msm_dailink.h

The official local bit-count helper is renamed `lisa_mi2s_num_of_bits_set` to avoid a declaration conflict with the newer DSP header. No audio routing settings, firmware, module CRC checks or SELinux policy were bypassed.

Reconstruction: use `../HyperOSPro-Version/reconstruct-miui-display.sh` and its base patch to create the version/display-compatible source, then apply `lisa-mi2s-v2.patch` at that source root. Use the version bundle's build helper, this folder's `kernel.config`, pinned Proton clang13, `TARGET_PRODUCT=lisa`, `DYNAMIC_SINGLE_CHIP=qca6750` and empty make `LOCALVERSION=`. Preserve the existing MIUI display and Wi-Fi corrections.

Boot image SHA-256: `76ecd280d195438e39d4f2e831da6711f56b077e2ffe87d900518c66cc1f2e3a`. Original ROM ramdisk SHA-256: `0dc218f3167e560444634a6a8cf969eb4470bcf452837a3e23bf45ea0a6819ae`. Temporary boot only; the permanent boot partition has not been replaced. Local images and phone logs are not distributed in this repository.
