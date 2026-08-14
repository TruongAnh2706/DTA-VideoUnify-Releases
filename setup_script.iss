; =========================================================
; DTA VideoUnify Pro - Inno Setup 6 Installer Script
; Phát triển bởi DTA Studio - Chủ quản: Đức Trường
; Email: ductruong.onl@gmail.com | Zalo/SĐT: 0962775506
; Website: https://dta-studio.vercel.app/
; Portable Relative Paths Fix for GitHub Actions CI/CD
; =========================================================

#define MyAppName "DTA VideoUnify Pro"
#define MyAppVersion "2.3.3"
#define MyAppPublisher "DTA Studio - Đức Trường"
#define MyAppURL "https://dta-studio.vercel.app/"
#define MyAppExeName "DTA_VideoUnify_Pro.exe"
#define MySourceDir "."

[Setup]
AppId={{DTA-VIDEOUNIFY-PRO-ENTERPRISE-2026}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\DTA Studio\{#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
DefaultGroupName=DTA Studio\{#MyAppName}
AllowNoIcons=yes
LicenseFile=
OutputDir={#MySourceDir}\Output
OutputBaseFilename=DTA_VideoUnify_Pro_Setup
SetupIconFile={#MySourceDir}\logo.ico
WizardStyle=modern
SolidCompression=yes
Compression=lzma2/ultra64
PrivilegesRequired=lowest

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "{#MySourceDir}\dist\DTA_VideoUnify_Pro\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#MySourceDir}\logo.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#MySourceDir}\logo.png"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"; IconIndex: 0
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"; IconIndex: 0; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
