# Set the current directory variable
$currentDir = Get-Location

# Create a virtual environment named 'venv'
if (Test-Path -Path "venv") {
    Write-Host "Virtual environment 'venv' already exists."
} else {
    Write-Host "Creating virtual environment 'venv'..."
    python -m venv venv
}

# Activate the virtual environment
$activateScript = Join-Path -Path $currentDir -ChildPath "venv\Scripts\Activate.ps1"
if (Test-Path -Path $activateScript) {
    Write-Host "Activating virtual environment..."
    . $activateScript
} else {
    Write-Host "Activation script not found. Please ensure the virtual environment was created successfully."
    exit 1
}

# Ensure the script is running as administrator
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "Restarting script as administrator..."
    Start-Process powershell "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

# Define the path to the venv python executable
$venvPython = Join-Path -Path $currentDir -ChildPath "venv\Scripts\python.exe"

# Update pip to the latest version BEFORE installing requirements
Write-Host "Updating pip to the latest version..."
& $venvPython -m pip install --upgrade pip

# Install required packages
$requirementsFile = Join-Path -Path $currentDir -ChildPath "requirements.txt"
if (Test-Path -Path $requirementsFile) {
    Write-Host "Installing required packages from $requirementsFile..."
    & $venvPython -m pip install -r $requirementsFile
} else {
    Write-Host "Requirements file not found: $requirementsFile"
}

# Run the main script
$mainScript = Join-Path -Path $currentDir -ChildPath "main.py"
if (Test-Path -Path $mainScript) {
    Write-Host "Running main script: $mainScript"
    & $venvPython $mainScript
} else {
    Write-Host "Main script not found: $mainScript"
}