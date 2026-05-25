!define APPNAME "FinacialSim"
!define APPVERSION "1.0.0"
!define APPDIR "FinacialSim"
!define GTK_INSTALLER "GTK3-runtime-3.24.31-ts-win64.exe"

OutFile "..\dist\FinacialSim-Setup-${APPVERSION}.exe"
InstallDir "$PROGRAMFILES64\${APPDIR}"
RequestExecutionLevel admin
Name "${APPNAME}"

Page directory
Page instfiles

; Check if GTK3 runtime is already present
Function CheckGTK
  IfFileExists "$SYSDIR\libgtk-3-0.dll" gtk_ok
  ; GTK3 not found - silently install bundled runtime
  ; Place GTK3-runtime-3.24.31-ts-win64.exe next to the installer before running makensis
  IfFileExists "$EXEDIR\${GTK_INSTALLER}" run_gtk
    DetailPrint "WARNING: GTK3 runtime installer not found. WeasyPrint PDF generation may not work."
    Goto gtk_ok
  run_gtk:
    DetailPrint "Installing GTK3 runtime..."
    ExecWait '"$EXEDIR\${GTK_INSTALLER}" /S' $0
    DetailPrint "GTK3 runtime install exit code: $0"
  gtk_ok:
FunctionEnd

Section "Install"
  Call CheckGTK

  SetOutPath "$INSTDIR"
  File /r "..\dist\${APPDIR}\*.*"

  CreateDirectory "$SMPROGRAMS\${APPDIR}"
  CreateShortcut "$SMPROGRAMS\${APPDIR}\${APPNAME}.lnk" "$INSTDIR\FinacialSim.exe"
  CreateShortcut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\FinacialSim.exe"

  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" "$INSTDIR\uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "${APPVERSION}"
  WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

Section "Uninstall"
  Delete "$DESKTOP\${APPNAME}.lnk"
  RMDir /r "$SMPROGRAMS\${APPDIR}"
  RMDir /r "$INSTDIR"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
SectionEnd
