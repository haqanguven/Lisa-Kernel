# Black screen and recovery findings, 2026-10-17

User confirmation supersedes any interpretation of sys.boot_completed=1 as usable boot: the physical panel stayed black and the phone later returned to the Mi logo.

The diagnostic kernel ran for more than two minutes with Android services alive. Digital screencap showed a normal lockscreen while the physical screen remained black. That capture contains private notifications and stays local. Power initially reported Dozing/DOZE_SUSPEND; physical key presses briefly woke it, followed by application sleep. Proximity was false. Input wake injection was denied; cmd power wakeup succeeded and requested ON, with a transient committed OFF and screenReady=false. Brightness command did not restore a visible panel. No refresh-rate override or automatic-brightness-mode change was made.

Current persisted diagnostic records contain snapshots at48s and93s, with no kernel panic found in them. Subsequent Restart records identify the old permanent kernel, not the diagnostic kernel. The exact first restart cause is unresolved. ADB restarted during Android startup, ending the first logcat stream; do not claim it captured the final restart.

Recovery: A slot became unbootable with retry count0 after repeated failures. Original known-working TWRP and its verified repack then both failed fastboot boot with Load Error. Rebooting bootloader alone did not fix it. Re-activating the SAME A slot reset unbootable=no/retry7; original TWRP then booted successfully. No image partition was flashed in that recovery operation.

Phone is left in original TWRP. Vendor_a v2 remains applied. Experimental kernel was temporary and is not installed in boot_a. Original full vendor backup remains local. No userdata formatting, new permissive policy, forced module CRCs or further vendor edits were performed.

Remaining work is targeted physical panel/display power/HWC/refresh diagnosis and kernel-module compatibility, not claiming completed stable Android17 support.
