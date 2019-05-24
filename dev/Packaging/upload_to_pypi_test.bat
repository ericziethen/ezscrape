@echo off

setlocal

set PROJ_MAIN_DIR=%~dp0..\..

pushd "%PROJ_MAIN_DIR%"

echo CurrentDIr: %CD%

twine upload --repository testpypi dist/*

echo ProjectUrl: https://test.pypi.org/project/ezscrape

popd

endlocal
