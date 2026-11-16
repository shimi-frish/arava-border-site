@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
echo Rebuilding the website from Israel_Jordan_Arava_MASTER.qgz ...
echo (Save the project in QGIS first.)
set "PY=%USERPROFILE%\anaconda3\python.exe"
if not exist "%PY%" set "PY=python"
"%PY%" -c "import rasterio, fiona, shapely, lxml" 2>nul
if errorlevel 1 (
  echo Installing required Python packages - first time only...
  "%PY%" -m pip install --user rasterio fiona shapely lxml
)
"%PY%" "_build\update_site.py"
if errorlevel 1 goto failed
where git >nul 2>nul
if errorlevel 1 goto nogit
if exist ".git" goto push
echo Connecting this folder to GitHub (first time only)...
git init -q -b main
git remote add origin https://github.com/shimi-frish/arava-border-site.git
git fetch -q --depth 1 origin main
if errorlevel 1 goto failed
git reset -q --soft origin/main
:push
echo Publishing to GitHub ...
git add -A
git commit -q -m "Update site"
git push -u origin main
if errorlevel 1 goto failed
echo Done. https://shimi-frish.github.io/arava-border-site/ will refresh in 1-2 minutes.
goto end
:nogit
echo Done locally. To publish automatically, install Git for Windows: https://git-scm.com/download/win
goto end
:failed
echo *** Something failed - see the messages above. ***
:end
pause
