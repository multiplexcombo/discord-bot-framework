# Check if script execution is allowed, and guide the user if not
if ((Get-ExecutionPolicy) -eq 'Restricted') {
    Write-Host "Script execution is disabled on this system."
    Write-Host "To enable script execution, run PowerShell as Administrator and execute:"
    Write-Host "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned"
    Write-Host "For more information, see: https://go.microsoft.com/fwlink/?LinkID=135170"
    exit 1
}

# Create a Python virtual environment if it doesn't exist
$venvDir = "C:\Users\Administrator\Documents\GitHub\casino-bot\venv"
if (-not (Test-Path $venvDir)) {
    Write-Host "Creating Python virtual environment..."
    python.exe -m venv $venvDir
}

# Activate the Python virtual environment for the casino-bot project
$venvPath = "C:\Users\Administrator\Documents\GitHub\casino-bot\venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    try {
        & $venvPath
    } catch {
        Write-Host "Could not activate the virtual environment. Script execution may be disabled on this system."
        Write-Host "To enable script execution, run PowerShell as Administrator and execute:"
        Write-Host "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned"
        Write-Host "For more information, see: https://go.microsoft.com/fwlink/?LinkID=135170"
    }
} else {
    Write-Host "Virtual environment activation script not found at $venvPath"
}

# Upgrade pip to the latest version
Write-Host "Upgrading pip to the latest version..."
pip install --upgrade pip

# Install required Python packages
$requirementsFile = "C:\Users\Administrator\Documents\GitHub\casino-bot\requirements.txt"
if (Test-Path $requirementsFile) {
    Write-Host "Installing required Python packages..."
    pip install -r $requirementsFile
} else {
    Write-Host "Requirements file not found at $requirementsFile"
}

# Run the casino-bot script
$scriptPath = "C:\Users\Administrator\Documents\GitHub\casino-bot\main.py"
if (Test-Path $scriptPath) {
    Write-Host "Running casino-bot script..."
    python.exe $scriptPath
} else {
    Write-Host "Casino-bot script not found at $scriptPath"
}