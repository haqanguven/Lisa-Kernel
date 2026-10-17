# IMS/SMS investigation — 2026-10-18

User confirms calls work but SMS cannot be sent or received on LTE/NR after the IMS-only trial. In a controlled 3G/2G automatic-mode test, incoming SMS was user-confirmed and the RIL NEW_SMS to GsmInboundSmsHandler delivery path was observed. This isolates a network-mode/IMS interoperability problem; it does not prove a complete causal fix.

The original Android 17 IMS factory has no HIDL fallback; Lisa advertises vendor IMS HIDL 1.7. A genuine Xiaomi-signed Android 16 IMS client was tested alone. Its 134 shared-library method references resolve, but runtime success was not established. No signature checks or SELinux protections were bypassed.

Initial trials retained stale PackageManager metadata because the image preserved old package timestamps. One-second changes to the old timestamp were insufficient. Updating both APK and package directory to the current build time caused normal parsing: the new minSdk/targetSdk and HIDL-wrapper dependency appeared, and the missing-class crash stopped. Nevertheless SMS still failed while calls worked. Therefore this is a FAILED IMS trial, not a working fix.

Rollback: the complete original system_ext partition was first restored and its full SHA-256 matched the backup. To refresh package parsing on rollback, a verified image with ALL ORIGINAL FILE CONTENTS and only two updated mtimes (IMS APK and its directory) was then written. Its 2131 entries match the expected original content and metadata except those two timestamps. Image size 781828096; SHA-256 6c2e0adafdf3f34093e5773785f36c09d37a67626fc4a3bc581c2750397f77d8; device readback matched. The raw original backup remains available locally. Temporary sound-confirmed kernel build #13 is booting; 3G is the intended temporary SMS workaround pending final post-rollback checks.

No modem/EFS/NV/vbmeta/permanent boot writes, no application data reset, no parser cache deletion. Actual 5G and LTE SMS remain unresolved. Private radio logs, proprietary binaries and backups are kept local.
