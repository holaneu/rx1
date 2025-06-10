@echo off
echo.
echo ============================================
echo  !!! WARNING !!!
echo  You are about to OVERWRITE the main branch
echo  with the current state of the dev branch.
echo ============================================
echo.

set /p confirm=!!! Are you really sure? Type "overwrite" to proceed: 

if /I not "%confirm%"=="overwrite" (
    echo.
    echo ❌ Aborted: You did not type "overwrite".
    pause
    exit /b 1
)

echo.
echo Confirmed. Proceeding with overwrite...

echo.
echo ================================
echo  Syncing main with latest dev...
echo ================================
echo.

REM Ensure dev is up to date with remote
git checkout dev

echo.
git fetch origin
echo.
git reset --hard origin/dev
echo.

IF %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to update dev branch. Aborting.
    pause
    exit /b 1
)

echo.
git checkout main
echo.
git reset --hard dev
echo.
git push origin main --force

IF %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to push to main. Aborting.
    pause
    exit /b 1
)

echo.
git checkout dev

echo.
echo Main successfully synced with latest dev.
echo.
echo You're now back on dev branch.
echo.

pause
