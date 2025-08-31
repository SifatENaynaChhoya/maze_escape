# PowerShell script to run the refactored 3D Maze Escape game
# Make sure you have Python and PyOpenGL installed

Write-Host "Starting 3D Maze Escape: Hunter's Chase..." -ForegroundColor Green
Write-Host "Make sure the OpenGL folder is available in the parent directory" -ForegroundColor Yellow

# Check if Python is available
try {
    python --version
    Write-Host "Python found. Starting game..." -ForegroundColor Green
    
    # Change to the warp directory and run the main game
    Set-Location $PSScriptRoot
    python main.py
}
catch {
    Write-Host "Error: Python not found or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python and make sure it's in your PATH" -ForegroundColor Red
    Write-Host "You can download Python from: https://www.python.org/downloads/" -ForegroundColor Yellow
}

Write-Host "Press any key to exit..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
