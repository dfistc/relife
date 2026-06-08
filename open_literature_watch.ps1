$ErrorActionPreference = "SilentlyContinue"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = "C:\Users\22203\AppData\Local\Python\pythoncore-3.14-64\python.exe"
$Edge = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
$Port = 8000

$serverReady = Test-NetConnection -ComputerName 127.0.0.1 -Port $Port `
    -InformationLevel Quiet -WarningAction SilentlyContinue

if (-not $serverReady -and (Test-Path -LiteralPath $Python)) {
    Start-Process -FilePath $Python `
        -ArgumentList "-m", "http.server", "$Port", "--bind", "127.0.0.1" `
        -WorkingDirectory $ProjectRoot `
        -WindowStyle Hidden

    for ($attempt = 0; $attempt -lt 20; $attempt++) {
        Start-Sleep -Milliseconds 250
        $serverReady = Test-NetConnection -ComputerName 127.0.0.1 -Port $Port `
            -InformationLevel Quiet -WarningAction SilentlyContinue
        if ($serverReady) { break }
    }
}

if (Test-Path -LiteralPath $Python) {
    Start-Process -FilePath $Python `
        -ArgumentList "`"$ProjectRoot\scripts\update_literature.py`"" `
        -WorkingDirectory $ProjectRoot `
        -WindowStyle Hidden `
        -Wait
}

$cacheBuster = [DateTimeOffset]::Now.ToUnixTimeSeconds()
$url = "http://127.0.0.1:$Port/index.html?v=$cacheBuster"

if (Test-Path -LiteralPath $Edge) {
    Start-Process -FilePath $Edge -ArgumentList $url
} else {
    Start-Process $url
}
