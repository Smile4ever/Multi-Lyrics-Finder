# Product Info
Name "Multi Lyrics Finder"
!define SOURCEDIR "..\build\exe.win-amd64-3.13\"
!define PRODUCT "Multi Lyrics Finder"
!define PRODUCTNOSPACES "MultiLyricsFinder"
!define EXENAME "multi_lyrics_finder.exe"
!define ARP "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCTNOSPACES}"

!ifndef VERSION
    !define VERSION "0.0.0"
!endif
!ifndef SIZE
    !define SIZE 0
!endif

!include "MUI2.nsh"

# Installer details
Outfile "..\build\setup\${PRODUCTNOSPACES}-Setup-${VERSION}.exe"
InstallDir "$PROGRAMFILES64\${PRODUCT}"
RequestExecutionLevel admin
ShowInstDetails show   ; Show installation progress
ShowUninstDetails show ; Show uninstallation progress

# Modern UI Pages
!define MUI_ABORTWARNING  ; Warn users if they cancel installation

; !define MUI_ICON "icon.ico"   ; Set custom installer icon
; !define MUI_UNICON "icon.ico" ; Uninstaller icon

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

#################################
!macro SecSelect SecId
  Push $0
  IntOp $0 ${SF_SELECTED} | ${SF_SELECTED} # Minimum 2 parameters needed, so two times same value
  SectionSetFlags ${SecId} $0
  SectionSetInstTypes ${SecId} 1
  Pop $0
!macroend
 
!define SelectSection '!insertmacro SecSelect'
 
!macro SecUnSelect SecId
  Push $0
  IntOp $0 ${SF_USELECTED} | ${SF_USELECTED} # Minimum 2 parameters needed, so two times same value
  SectionSetFlags ${SecId} $0
  SectionSetText  ${SecId} ""
  Pop $0
!macroend
 
!define UnSelectSection '!insertmacro SecUnSelect'
###################################

Section "Multi Lyrics Finder"
	SectionIn RO
	
    SetOutPath "$INSTDIR"
	
	Call KillProcess
    File /r "${SOURCEDIR}\*"

    WriteUninstaller "$INSTDIR\Uninstall.exe"
	
	SetRegView 64
    WriteRegStr HKLM "${ARP}" "DisplayName" "Multi Lyrics Finder"
	WriteRegStr HKLM "${ARP}" "DisplayVersion" "${VERSION}"
	WriteRegStr HKLM "${ARP}" "URLInfoAbout" "https://github.com/Smile4ever/Multi-Lyrics-Finder"
    WriteRegStr HKLM "${ARP}" "Publisher" "Smile4ever"
	WriteRegDWORD HKLM "${ARP}" "EstimatedSize" "${SIZE}"
	WriteRegStr HKLM "${ARP}" "InstallLocation" "$INSTDIR"
	;WriteRegStr HKLM "${ARP}" "DisplayIcon" ""
    WriteRegStr HKLM "${ARP}" "UninstallString" "$INSTDIR\Uninstall.exe"
SectionEnd

SectionGroup /e "Shortcuts"
	Section "Desktop"
		SetShellVarContext current
		CreateShortcut "$DESKTOP\${PRODUCT}.lnk" "$INSTDIR\${EXENAME}"
	SectionEnd
	
	Section "Start menu"
		SetShellVarContext current
		CreateShortcut "$SMPROGRAMS\${PRODUCT}.lnk" "$INSTDIR\${EXENAME}"
	SectionEnd
SectionGroupEnd

Function .onInstSuccess
	IfSilent +2 ;Skip one line if installer is silent
	Exec "$INSTDIR\${EXENAME}"
FunctionEnd

Function KillProcess
	nsExec::Exec "taskkill /IM ${EXENAME} /F"
	Sleep 500
FunctionEnd

Section "Uninstall"
	Call un.KillProcess

    Delete "$INSTDIR\${EXENAME}"
    Delete "$INSTDIR\Uninstall.exe"
    RMDir /r "$INSTDIR"

    Delete "$DESKTOP\${PRODUCT}.lnk"
    Delete "$SMPROGRAMS\${PRODUCT}.lnk"

	SetRegView 64
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCTNOSPACES}"
SectionEnd

Function un.KillProcess
	nsExec::Exec "taskkill /IM ${EXENAME} /F"
	Sleep 500
FunctionEnd
