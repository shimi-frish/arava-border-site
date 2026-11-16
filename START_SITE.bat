@echo off
rem Opens the site through a small local web server (needed only for previewing CSV/MD/TXT files).
cd /d "%~dp0"
set PY=python
where python >nul 2>nul || set PY="%USERPROFILE%\anaconda3\python.exe"
start "" http://localhost:8765/index.html
%PY% -m http.server 8765
