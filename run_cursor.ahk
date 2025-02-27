^!r::  ; Ctrl + Alt + R to run the Python script
    ; Set the path to your Python script
    script_path := ""
    ; Run the Python script using pythonw.exe so it runs in the background without a console window
    Run, python "%script_path%"
return

^!p::  ; Ctrl + Alt + P to send the F12 key (toggles pause/resume in the Python script)
    Send, {F12}
return
