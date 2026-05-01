Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
baseDir = fso.GetParentFolderName(WScript.ScriptFullName)
pythonw = shell.ExpandEnvironmentStrings("%LOCALAPPDATA%") & "\Programs\Python\Python312\pythonw.exe"
If Not fso.FileExists(pythonw) Then
  pythonw = shell.ExpandEnvironmentStrings("%LOCALAPPDATA%") & "\Programs\Python\Python311\pythonw.exe"
End If
If Not fso.FileExists(pythonw) Then
  pythonw = "pythonw.exe"
End If
Set link = shell.CreateShortcut(baseDir & "\工资时钟.lnk")
link.TargetPath = pythonw
link.Arguments = """" & baseDir & "\salary_clock.py" & """"
link.WorkingDirectory = baseDir
link.WindowStyle = 1
link.Description = "工资时钟"
link.Save
