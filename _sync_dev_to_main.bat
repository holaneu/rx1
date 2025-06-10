@echo off
setlocal

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
    echo Aborted: You did not type "overwrite".
    pause
    exit /b 1
)

echo.
echo Confirmed. Proceeding...

echo.
echo === Step 1: Checkout dev ===
git checkout dev
IF %ERRORLEVEL% NEQ 0 (
    echo Failed to checkout dev.
    pause
    exit /b 1
)

echo.
echo === Step 2: Fetch origin and reset dev to origin/dev ===
git fetch origin
IF %ERRORLEVEL% NEQ 0 (
    echo Failed to fetch from origin.
    pause
    exit /b 1
)

git reset --hard origin/dev
IF %ERRORLEVEL% NEQ 0 (
    echo Failed to reset dev to origin/dev.
    pause
    exit /b 1
)

echo.
echo === Step 3: Checkout main ===
git checkout main
IF %ERRORLEVEL% NEQ 0 (
    echo Failed to checkout main.
    pause
    exit /b 1
)

echo.
echo === Step 4: Reset main to local dev ===
git reset --hard dev
IF %ERRORLEVEL% NEQ 0 (
    echo Failed to reset main to dev.
    pause
    exit /b 1
)

echo.
echo === Step 5: Force push main to origin ===
git push origin main --force
IF %ERRORLEVEL% NEQ 0 (
    echo Failed to push main to origin.
    pause
    exit /b 1
)

echo.
echo === Step 6: Switch back to dev ===
git checkout dev
IF %ERRORLEVEL% NEQ 0 (
    echo Failed to switch back to dev.
    pause
    exit /b 1
)

echo.
echo ✅ Main successfully synced with dev.
echo ✅ You are now back on dev branch.
pause
