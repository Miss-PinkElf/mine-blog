@echo off
setlocal
set "DIR=%~dp0"

where py >nul 2>&1
if %ERRORLEVEL%==0 (
  py -3 "%DIR%run.py" %*
  exit /b %ERRORLEVEL%
)

where python >nul 2>&1
if %ERRORLEVEL%==0 (
  python "%DIR%run.py" %*
  exit /b %ERRORLEVEL%
)

where node >nul 2>&1
if %ERRORLEVEL%==0 (
  node "%DIR%run.mjs" %*
  exit /b %ERRORLEVEL%
)

echo 错误: 需要 Python 3 或 Node.js
echo   Windows: winget install Python.Python.3.12
echo   或: winget install OpenJS.NodeJS.LTS
exit /b 127
