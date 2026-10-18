@echo off
cd /d "%~dp0"
set fastboot=bin\windows\fastboot.exe
if not exist "%fastboot%" (
 echo Fastboot not found.
 pause
 exit /B 1
)
echo Waiting for device...
set device=
for /f "tokens=2" %%A in ('%fastboot% getvar product 2^>^&1 ^| findstr "\<product:"') do set device=%%A
if "%device%" equ "" (
 echo Your device could not be detected.
 pause
 exit /B 1
)
echo Your device: %device%
if "%device%" neq "lisa" (
 echo Compatible devices: lisa
 pause
 exit /B 1
)


rem Validate every input BEFORE writing any partition.
if not exist "images\abl.img" (
 echo Missing image: images\abl.img
 pause
 exit /B 1
)
if not exist "images\aop.img" (
 echo Missing image: images\aop.img
 pause
 exit /B 1
)
if not exist "images\bluetooth.img" (
 echo Missing image: images\bluetooth.img
 pause
 exit /B 1
)
if not exist "images\cpucp.img" (
 echo Missing image: images\cpucp.img
 pause
 exit /B 1
)
if not exist "images\devcfg.img" (
 echo Missing image: images\devcfg.img
 pause
 exit /B 1
)
if not exist "images\dsp.img" (
 echo Missing image: images\dsp.img
 pause
 exit /B 1
)
if not exist "images\dtbo.img" (
 echo Missing image: images\dtbo.img
 pause
 exit /B 1
)
if not exist "images\featenabler.img" (
 echo Missing image: images\featenabler.img
 pause
 exit /B 1
)
if not exist "images\hyp.img" (
 echo Missing image: images\hyp.img
 pause
 exit /B 1
)
if not exist "images\imagefv.img" (
 echo Missing image: images\imagefv.img
 pause
 exit /B 1
)
if not exist "images\keymaster.img" (
 echo Missing image: images\keymaster.img
 pause
 exit /B 1
)
if not exist "images\modem.img" (
 echo Missing image: images\modem.img
 pause
 exit /B 1
)
if not exist "images\qupfw.img" (
 echo Missing image: images\qupfw.img
 pause
 exit /B 1
)
if not exist "images\shrm.img" (
 echo Missing image: images\shrm.img
 pause
 exit /B 1
)
if not exist "images\tz.img" (
 echo Missing image: images\tz.img
 pause
 exit /B 1
)
if not exist "images\uefisecapp.img" (
 echo Missing image: images\uefisecapp.img
 pause
 exit /B 1
)
if not exist "images\vbmeta.img" (
 echo Missing image: images\vbmeta.img
 pause
 exit /B 1
)
if not exist "images\vbmeta_system.img" (
 echo Missing image: images\vbmeta_system.img
 pause
 exit /B 1
)
if not exist "images\xbl.img" (
 echo Missing image: images\xbl.img
 pause
 exit /B 1
)
if not exist "images\xbl_config.img" (
 echo Missing image: images\xbl_config.img
 pause
 exit /B 1
)
if not exist "images\boot.img" (
 echo Missing image: images\boot.img
 pause
 exit /B 1
)
if not exist "images\vendor_boot.img" (
 echo Missing image: images\vendor_boot.img
 pause
 exit /B 1
)
if not exist "images\cust.img" (
 echo Missing image: images\cust.img
 pause
 exit /B 1
)
if not exist "images\super.img" (
 echo Missing image: images\super.img
 pause
 exit /B 1
)
powershell.exe -NoProfile -Command "if ((Get-FileHash -LiteralPath 'images\boot.img' -Algorithm SHA256).Hash -ne '76ecd280d195438e39d4f2e831da6711f56b077e2ffe87d900518c66cc1f2e3a') { exit 1 }"
if errorlevel 1 (
 echo Image verification failed. Nothing was flashed.
 pause
 exit /B 1
)
powershell.exe -NoProfile -Command "if ((Get-FileHash -LiteralPath 'images\super.img' -Algorithm SHA256).Hash -ne 'd3a1cc0c240627d0d9a2c34dda76b3392db9f5900a5970c3c9f88a9be87286d8') { exit 1 }"
if errorlevel 1 (
 echo Image verification failed. Nothing was flashed.
 pause
 exit /B 1
)

echo Your device will be flashed and the data partition will be formatted.
echo You will lose your apps, settings and files on internal storage.
echo Continue if you are flashing HyperOSPro Rom for the first time or downgrading.
set /p choice=Do you want to continue? [y/N] 
if /i "%choice%" neq "y" exit /B 0

echo ##############################################################
echo Please wait. The device will reboot once flashing is complete.
echo ##############################################################
%fastboot% set_active a
if errorlevel 1 goto flash_error
%fastboot% flash abl_ab images\abl.img
if errorlevel 1 goto flash_error
%fastboot% flash aop_ab images\aop.img
if errorlevel 1 goto flash_error
%fastboot% flash bluetooth_ab images\bluetooth.img
if errorlevel 1 goto flash_error
%fastboot% flash cpucp_ab images\cpucp.img
if errorlevel 1 goto flash_error
%fastboot% flash devcfg_ab images\devcfg.img
if errorlevel 1 goto flash_error
%fastboot% flash dsp_ab images\dsp.img
if errorlevel 1 goto flash_error
%fastboot% flash dtbo_ab images\dtbo.img
if errorlevel 1 goto flash_error
%fastboot% flash featenabler_ab images\featenabler.img
if errorlevel 1 goto flash_error
%fastboot% flash hyp_ab images\hyp.img
if errorlevel 1 goto flash_error
%fastboot% flash imagefv_ab images\imagefv.img
if errorlevel 1 goto flash_error
%fastboot% flash keymaster_ab images\keymaster.img
if errorlevel 1 goto flash_error
%fastboot% flash modem_ab images\modem.img
if errorlevel 1 goto flash_error
%fastboot% flash qupfw_ab images\qupfw.img
if errorlevel 1 goto flash_error
%fastboot% flash shrm_ab images\shrm.img
if errorlevel 1 goto flash_error
%fastboot% flash tz_ab images\tz.img
if errorlevel 1 goto flash_error
%fastboot% flash uefisecapp_ab images\uefisecapp.img
if errorlevel 1 goto flash_error
%fastboot% flash vbmeta_ab images\vbmeta.img
if errorlevel 1 goto flash_error
%fastboot% flash vbmeta_system_ab images\vbmeta_system.img
if errorlevel 1 goto flash_error
%fastboot% flash xbl_ab images\xbl.img
if errorlevel 1 goto flash_error
%fastboot% flash xbl_config_ab images\xbl_config.img
if errorlevel 1 goto flash_error
%fastboot% flash boot_ab images\boot.img
if errorlevel 1 goto flash_error
%fastboot% flash vendor_boot_ab images\vendor_boot.img
if errorlevel 1 goto flash_error
%fastboot% flash cust images\cust.img
if errorlevel 1 goto flash_error
%fastboot% flash super images\super.img
if errorlevel 1 goto flash_error
%fastboot% erase metadata
if errorlevel 1 goto flash_error
%fastboot% erase userdata
if errorlevel 1 goto flash_error
%fastboot% reboot
if errorlevel 1 goto flash_error
exit /B 0
:flash_error
echo Flash command failed. Installation stopped; no further partitions were written.
pause
exit /B 1
