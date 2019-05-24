@echo off

setlocal

set PROJ_MAIN_DIR=%~dp0..\..

pushd "%PROJ_MAIN_DIR%"

echo CurrentDIr: %CD%

rem twine upload --repository pypi dist/*

echo !!! Pypi Upload is currently Disabled until the project is stable

echo ProjectUrl: https://pypi.org/project/ezscrape

popd

endlocal
