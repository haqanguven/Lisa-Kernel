# Lisa Android 17 vendor policy fix

## Device and scope

Tested on Xiaomi 11 Lite 5G NE (Lisa), HyperOSPro Android 17
(`OS4.0.5.0.XPCCNXM`, API 37) with vendor SDK 30. The running kernel is
`5.4.302-A17-HyperOSPro`. The fix changes vendor SELinux metadata; no kernel
source or boot image change was needed.

## Changes

- Map only `ro.vendor.audio.soundfx.type` to
  `vendor_exported_system_prop`. On this Android 17 build MiSound runs in
  `platform_app_36`, while the vendor policy's `vendor_audio_prop` read
  allowance covered `platform_app_30_0`. MiSound therefore could not read the
  value `mi`, selected an unavailable Dirac effect, and crashed while building
  the empty effect list.
- Allow Binder `call` and `transfer` between processes in
  `hal_vibrator_default`. The two vibrator HAL processes share that domain;
  both permissions were denied, so vibration requests failed in dispatch.

The exact additions are in
[`patches/lisa-a17-hyperospro-vendor-policy.patch`](../../patches/lisa-a17-hyperospro-vendor-policy.patch).
Apply them to the matching extracted `vendor_a` tree. Property contexts used
when rebuilding the image must include the platform, system_ext, product, and
vendor context rules so existing SELinux labels are retained.

## Device verification

- Only `vendor_a` was written; `super.img` and the kernel image were untouched.
- Android 17 booted with the same kernel release.
- MiSound read `ro.vendor.audio.soundfx.type=mi`; the sound effects activity
  opened and AudioFlinger reported the MiSound effect.
- `vibrator_manager` reported its vibrator capabilities and effects.
  `cmd vibrator_manager synced oneshot 160 200` completed with `FINISHED`,
  and physical vibration was confirmed on the phone.

## Tested image

The resulting 1,360,674,816-byte `vendor_a` image has SHA-256:

`2216A97A8A33F946222C36AD6BFB6CAAEC3047E67F389604D2E75F291B03670B`

The binary is kept in the user's local Desktop folder
`Lisa-Son-Duzeltmeler/vendor_a.img`; it is not stored in this source repository.
