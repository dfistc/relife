$ErrorActionPreference = "SilentlyContinue"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = "C:\Users\22203\AppData\Local\Python\pythoncore-3.14-64\python.exe"
$Port = 8001

$serverReady = Test-NetConnection -ComputerName 127.0.0.1 -Port $Port `
    -InformationLevel Quiet -WarningAction SilentlyContinue

if (-not $serverReady -and (Test-Path -LiteralPath $Python)) {
    Start-Process -FilePath $Python `
        -ArgumentList "-m", "http.server", "$Port", "--bind", "0.0.0.0" `
        -WorkingDirectory $ProjectRoot `
        -WindowStyle Hidden
    Start-Sleep -Seconds 1
}

$cacheBuster = [DateTimeOffset]::Now.ToUnixTimeSeconds()
Start-Process "http://127.0.0.1:$Port/index.html?v=$cacheBuster"
