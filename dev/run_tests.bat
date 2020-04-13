@echo off

setlocal

set PROJ_MAIN_DIR=%~dp0..
set PACKAGE_ROOT=ezscrape

set PYTHONPATH=%PYTHONPATH%;%PACKAGE_ROOT%

rem To see how to loop through multiple Command Line Arguments: https://www.robvanderwoude.com/parameters.php

rem Disable Unwanted tests when run from Travis
if "%1"=="travis-ci" (
    rem add testing exclusions for travis
    set PYTEST_ADDOPTS=-m "(not selenium) and (not proxytest)"
    echo Argument "travis-ci" passed, set "PYTEST_ADDOPTS" env variable
    goto run_tests
)

:local_setup
rem TODO - Different Handling Needed, need to think how user will set it

set CHROME_WEBDRIVER_PATH=%PROJ_MAIN_DIR%\%PACKAGE_ROOT%\webdriver\chromedriver\74.0.3729.6\win32\chromedriver.exe
set CHROME_WEBDRIVER_PATH=%PROJ_MAIN_DIR%\%PACKAGE_ROOT%\webdriver\chromedriver\75.0.3770.90\win32\chromedriver.exe
set CHROME_WEBDRIVER_PATH=%PROJ_MAIN_DIR%\%PACKAGE_ROOT%\webdriver\chromedriver\80.0.3987.106\win32\chromedriver.exe

rem set CHROME_EXEC_PATH=C:\# Eric\Portable Apps\GoogleChromePortable\GoogleChromePortable.exe
set CHROME_EXEC_PATH=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe

echo ChromeDriver path set to "%CHROME_WEBDRIVER_PATH%"
echo CHeck Chrome Driver Path Exists:
dir "%CHROME_WEBDRIVER_PATH%"

echo Chrome path set to "%CHROME_EXEC_PATH%"
echo CHeck Chrome Path Exists:
dir "%CHROME_EXEC_PATH%"

pause

:run_tests
pytest --rootdir="%PROJ_MAIN_DIR%" --cov="%PACKAGE_ROOT%"
set return_code=%errorlevel%
if %return_code% equ 0 (
    echo *** No Issues Found
    goto exit_ok
) else (
    echo *** Some Issues Found
    goto exit_error
)

rem Some pytest resources
rem https://hackingthelibrary.org/posts/2018-02-09-code-coverage/
rem https://code.activestate.com/pypm/pytest-cov/
rem https://docs.pytest.org/en/latest/usage.html
rem http://blog.thedigitalcatonline.com/blog/2018/07/05/useful-pytest-command-line-options/
rem https://www.patricksoftwareblog.com/python-unit-testing-structuring-your-project/

:exit_error
endlocal
echo exit /B 1
exit /B 1

:exit_ok
endlocal
echo exit /B 0
exit /B 0
