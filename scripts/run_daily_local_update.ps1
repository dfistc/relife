$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Python = "C:\Users\22203\AppData\Local\Python\pythoncore-3.14-64\python.exe"
$LogDir = Join-Path $ProjectRoot "logs"
$LogFile = Join-Path $LogDir "daily-update.log"

New-Item -ItemType Directory -Path $LogDir -Force | Out-Null

"[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Starting literature search" |
    Out-File -LiteralPath $LogFile -Append -Encoding utf8

& $Python (Join-Path $ProjectRoot "scripts\update_literature.py") *>> $LogFile

if ($LASTEXITCODE -ne 0) {
    "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Search failed with exit code $LASTEXITCODE" |
        Out-File -LiteralPath $LogFile -Append -Encoding utf8
    exit $LASTEXITCODE
}

"[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Search completed" |
    Out-File -LiteralPath $LogFile -Append -Encoding utf8
