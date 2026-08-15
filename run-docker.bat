@echo off
echo ========================================
echo Urban Mobility Analytics - Docker Setup
echo ========================================
echo.
echo Buildiendo imagen Docker...
docker build -t urban-mobility .
echo.
echo Corriendo contenedor...
docker run -p 8501:8501 urban-mobility
echo.
pause
