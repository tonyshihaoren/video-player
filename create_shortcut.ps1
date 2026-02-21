$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\VideoPlayer.lnk")
$Shortcut.TargetPath = "C:\Users\Administrator\Desktop\全能播放器\dist\全能播放器.exe"
$Shortcut.WorkingDirectory = "C:\Users\Administrator\Desktop\全能播放器\dist"
$Shortcut.Description = "Video Player with AB Loop"
$Shortcut.IconLocation = "C:\Users\Administrator\Desktop\全能播放器\dist\全能播放器.exe,0"
$Shortcut.Save()
Write-Host "Shortcut created successfully!"
