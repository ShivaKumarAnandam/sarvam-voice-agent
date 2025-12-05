@echo off
echo ========================================
echo Starting Sarvam Voice Agent Server
echo ========================================
echo.

cd /d "%~dp0"

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Starting server on port 8000...
echo.
echo IMPORTANT: After server starts, open a NEW terminal and run:
echo    ngrok http 8000
echo.
echo Then copy the ngrok HTTPS URL and configure it in Twilio:
echo    https://YOUR-NGROK-URL/voice/incoming
echo.
echo ========================================
echo.

python twilio_server.py

pause
