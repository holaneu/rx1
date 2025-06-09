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
    exit /b 1
)

echo.
echo ✅ Confirmed. Proceeding with overwrite...

echo.
echo ================================
echo  Syncing main with latest dev...
echo ================================

git checkout dev
git pull origin dev

IF %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to update dev branch. Aborting.
    exit /b 1
)

git checkout main
git reset --hard dev
git push origin main --force

IF %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to push to main. Aborting.
    exit /b 1
)

git checkout dev

echo.
echo ✅ Main successfully synced with dev.
echo ✅ You're now back on dev branch.
