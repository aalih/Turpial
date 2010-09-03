;--------------------------------
;Include Modern UI

  !include "MUI.nsh"

;--------------------------------
;General

  ;Name and file
  Name "Turpial"
  OutFile "turpial-setup.exe"

  ;Default installation folder
  InstallDir "$PROGRAMFILES\Turpial"
 
  ;Get installation folder from registry if available
  InstallDirRegKey HKLM "Software\Turpial" ""

;--------------------------------
;Interface Settings

  !define MUI_ABORTWARNING

;--------------------------------
;Pages

  !insertmacro MUI_PAGE_WELCOME
  !insertmacro MUI_PAGE_LICENSE "COPYING"
  !insertmacro MUI_PAGE_COMPONENTS
  !insertmacro MUI_PAGE_DIRECTORY
  !insertmacro MUI_PAGE_INSTFILES
 
  !insertmacro MUI_UNPAGE_WELCOME
  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES
  !insertmacro MUI_UNPAGE_FINISH
;--------------------------------
;Languages
 
  !insertmacro MUI_LANGUAGE "English"

;--------------------------------
;Installer Sections

InstType "Full"

Section "Package" SecMain
  
  SectionIn 1 RO
  SetOutPath "$INSTDIR"
 
  File "COPYING"
  File "AUTHORS"
  File "Changelog"
  File "Readme.rst"
  File "dist\*.exe"
  File "dist\*.pyd"
  File "dist\*.zip"
  File "dist\python*.dll"

  CreateShortCut "$INSTDIR\turpial.lnk" "$INSTDIR\main.exe"
  CreateShortCut "$INSTDIR\turpial (DEBUG).lnk" "$INSTDIR\main.exe" "-d"

  SetOutPath "$INSTDIR\data"
  File /r "dist\data\*"

  SetOutPath "$INSTDIR\etc"
  File /r "dist\etc\*"

  SetOutPath "$INSTDIR\lib"
  File /r "dist\lib\*"
  File /x python*.dll "dist\*.dll"

  SetOutPath "$INSTDIR\share"
  File /r "dist\share\*"
   
  ;Store installation folder
  WriteRegStr HKLM "Software\Turpial" "" $INSTDIR
 
  ;Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"
 
  SetOutPath "$SMPROGRAMS\Turpial\"
  CopyFiles "$INSTDIR\turpial.lnk" "$SMPROGRAMS\Turpial\"
  CopyFiles "$INSTDIR\turpial (DEBUG).lnk" "$SMPROGRAMS\Turpial\"
  CopyFiles "$INSTDIR\turpial.lnk" "$DESKTOP\"
  Delete "$INSTDIR\turpial.lnk" 
  CreateShortCut "$SMPROGRAMS\Turpial\Uninstall.lnk" "$INSTDIR\Uninstall.exe"

SectionEnd
;--------------------------------
;Descriptions

  ;Language strings
  LangString DESC_SecMain ${LANG_ENGLISH} "Main Package"

  ;Assign language strings to sections
  !insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecMain} $(DESC_Main)
  !insertmacro MUI_FUNCTION_DESCRIPTION_END

;--------------------------------
;Uninstaller Section

Section "Uninstall" 

  Delete "$INSTDIR\*.*"

  Delete "$DESKTOP\turpial.lnk"
  Delete "$SMPROGRAMS\Turpial\turpial.lnk"
  Delete "$SMPROGRAMS\Turpial\Uninstall.lnk"

  RMDir  "$SMPROGRAMS\Turpial\"

  RMDir /r "$INSTDIR\etc\"   
  RMDir /r "$INSTDIR\lib\"
  RMDir /r "$INSTDIR\share\"
  RMDIR /r "$INSTDIR\data\"

  RMDir "$INSTDIR"

  DeleteRegKey /ifempty HKLM "Software\Turpial"

SectionEnd 
