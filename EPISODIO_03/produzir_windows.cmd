@echo off
setlocal
pushd "%~dp0.."
set PYTHONUTF8=1
where py >nul 2>nul
if errorlevel 1 (
    python EPISODIO_03\produzir_windows.py %*
) else (
    py -3.12 EPISODIO_03\produzir_windows.py %*
)
set CLAREIRA_RESULT=%ERRORLEVEL%
popd
exit /b %CLAREIRA_RESULT%
