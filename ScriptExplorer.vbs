Dim dir, pythonw, cmd
Set fso  = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

dir     = fso.GetParentFolderName(WScript.ScriptFullName)
pythonw = "C:\Users\desig\AppData\Local\Programs\Python\Python311\pythonw.exe"
cmd     = """" & pythonw & """ """ & dir & "\main.py"""

shell.CurrentDirectory = dir
shell.Run cmd, 1, False
