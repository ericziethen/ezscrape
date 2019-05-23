@echo off

setlocal

rem This selfwrapper calls itself again to avoid closing the command window when exiting
IF "%selfWrapped%"=="" (
  REM this is necessary so that we can use "exit" to terminate the batch file,
  REM and all subroutines, but not the original cmd.exe
  SET selfWrapped=true
  %ComSpec% /s /c ""%~0" %*"
  GOTO :EOF
)

set PROJ_MAIN_DIR=%~dp0..

set TEST_SERVER_DIR=%PROJ_MAIN_DIR%\tests\TestServerContent

python -m http.server --directory "%TEST_SERVER_DIR%" --bind localhost 8000

goto exit_ok

:exit_error
endlocal
exit /B 1

:exit_ok
endlocal
exit /B 0
