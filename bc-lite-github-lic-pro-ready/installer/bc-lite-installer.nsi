; BC-Lite NSIS Installer Script
; Assumes PyInstaller-built EXE at dist\BC-Lite.exe

!define APP_NAME "BC-Lite"
!define APP_VERSION "0.2.0"
!define COMPANY_NAME "YourCompany"
!define INSTALL_DIR "$PROGRAMFILES\${COMPANY_NAME}\${APP_NAME}"

OutFile "BC-Lite-Setup-${APP_VERSION}.exe"
InstallDir "${INSTALL_DIR}"
RequestExecutionLevel admin
ShowInstDetails show
ShowUninstDetails show

!include "MUI2.nsh"

!define MUI_ABORTWARNING
!define MUI_ICON "bc-lite.ico"
!define MUI_UNICON "bc-lite.ico"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

Section "Install"
  SetOutPath "$INSTDIR"
  ; Copy main executable (update path if different)
  File "dist\BC-Lite.exe"

  ; Optional: config/docs
  ; File /r "docs\*.*"
  ; File "LICENSE"
  ; File "README.md"

  ; Shortcuts
  CreateDirectory "$SMPROGRAMS\${APP_NAME}"
  CreateShortCut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\BC-Lite.exe"
  CreateShortCut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\BC-Lite.exe"

  ; Uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"

  ; Registry entries (Add/Remove Programs)
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayName" "${APP_NAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString" '"$INSTDIR\Uninstall.exe"'
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayVersion" "${APP_VERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "Publisher" "${COMPANY_NAME}"
SectionEnd

Section "Uninstall"
  Delete "$DESKTOP\${APP_NAME}.lnk"
  Delete "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk"
  RMDir "$SMPROGRAMS\${APP_NAME}"

  Delete "$INSTDIR\BC-Lite.exe"
  Delete "$INSTDIR\Uninstall.exe"
  ; Optionally remove config (comment out if you want to keep user settings)
  ; RMDir /r "$APPDATA\BC-Lite"

  RMDir "$INSTDIR"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
SectionEnd
