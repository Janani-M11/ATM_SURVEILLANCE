# PowerShell Script to Change PostgreSQL Password Without Current Password
# This script temporarily modifies pg_hba.conf to allow password-free access

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PostgreSQL Password Reset Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "WARNING: This script requires Administrator privileges!" -ForegroundColor Red
    Write-Host "Please run PowerShell as Administrator and try again." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    pause
    exit
}

# Find pg_hba.conf file
$possiblePaths = @(
    "C:\Program Files\PostgreSQL\17\data\pg_hba.conf",
    "C:\Program Files\PostgreSQL\16\data\pg_hba.conf",
    "C:\Program Files\PostgreSQL\15\data\pg_hba.conf",
    "C:\Program Files\PostgreSQL\14\data\pg_hba.conf",
    "C:\Program Files (x86)\PostgreSQL\17\data\pg_hba.conf",
    "C:\Program Files (x86)\PostgreSQL\16\data\pg_hba.conf"
)

$pgHbaPath = $null
foreach ($path in $possiblePaths) {
    if (Test-Path $path) {
        $pgHbaPath = $path
        break
    }
}

if (-not $pgHbaPath) {
    Write-Host "ERROR: Could not find pg_hba.conf file" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please locate it manually. Common locations:" -ForegroundColor Yellow
    Write-Host "C:\Program Files\PostgreSQL\[VERSION]\data\pg_hba.conf" -ForegroundColor Cyan
    pause
    exit
}

Write-Host "Found pg_hba.conf: $pgHbaPath" -ForegroundColor Green
Write-Host ""

# Backup the file
$backupPath = "$pgHbaPath.backup"
Copy-Item $pgHbaPath $backupPath -Force
Write-Host "Backup created: $backupPath" -ForegroundColor Green
Write-Host ""

# Read the file
$content = Get-Content $pgHbaPath
$modified = $false

# Modify the file
$newContent = $content | ForEach-Object {
    if ($_ -match "host\s+all\s+all\s+127\.0\.0\.1/32\s+scram-sha-256") {
        $modified = $true
        $_ -replace "scram-sha-256", "trust"
    } else {
        $_
    }
}

if (-not $modified) {
    Write-Host "WARNING: Could not find the line to modify." -ForegroundColor Yellow
    Write-Host "You may need to edit the file manually." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Look for: host    all    all    127.0.0.1/32    scram-sha-256" -ForegroundColor Cyan
    Write-Host "Change to: host    all    all    127.0.0.1/32    trust" -ForegroundColor Green
} else {
    # Write modified content
    $newContent | Set-Content $pgHbaPath -Encoding UTF8
    Write-Host "Modified pg_hba.conf to use 'trust' authentication" -ForegroundColor Green
    Write-Host ""
}

# Find PostgreSQL service
$services = Get-Service | Where-Object { $_.Name -like "*postgres*" }
if ($services.Count -eq 0) {
    Write-Host "WARNING: Could not find PostgreSQL service" -ForegroundColor Yellow
    Write-Host "Please restart PostgreSQL manually" -ForegroundColor Yellow
} else {
    Write-Host "PostgreSQL services found:" -ForegroundColor Cyan
    $services | ForEach-Object { Write-Host "  - $($_.Name) ($($_.Status))" -ForegroundColor White }
    Write-Host ""
    
    $restart = Read-Host "Do you want to restart PostgreSQL service now? (Y/N)"
    if ($restart -eq "Y" -or $restart -eq "y") {
        foreach ($service in $services) {
            Write-Host "Restarting $($service.Name)..." -ForegroundColor Cyan
            Restart-Service -Name $service.Name -Force
            Write-Host "Service restarted" -ForegroundColor Green
        }
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Connect to PostgreSQL (no password needed now):" -ForegroundColor White
Write-Host "   psql -U postgres" -ForegroundColor Green
Write-Host ""
Write-Host "2. Change the password:" -ForegroundColor White
Write-Host "   ALTER USER postgres WITH PASSWORD 'your_new_password';" -ForegroundColor Green
Write-Host ""
Write-Host "3. Exit psql:" -ForegroundColor White
Write-Host "   \q" -ForegroundColor Green
Write-Host ""
Write-Host "4. Restore pg_hba.conf:" -ForegroundColor Yellow
Write-Host "   Copy $backupPath to $pgHbaPath" -ForegroundColor Cyan
Write-Host "   Or change 'trust' back to 'scram-sha-256' manually" -ForegroundColor Cyan
Write-Host "   Then restart PostgreSQL service" -ForegroundColor Cyan
Write-Host ""
Write-Host "5. Update your .env file with the new password" -ForegroundColor Yellow
Write-Host ""

$newPassword = Read-Host "Enter new password for postgres user"
if ($newPassword) {
    Write-Host ""
    Write-Host "Attempting to change password..." -ForegroundColor Cyan
    
    $psqlPath = "C:\Program Files\PostgreSQL\17\bin\psql.exe"
    $psqlPaths = @(
        "C:\Program Files\PostgreSQL\17\bin\psql.exe",
        "C:\Program Files\PostgreSQL\16\bin\psql.exe",
        "C:\Program Files\PostgreSQL\15\bin\psql.exe"
    )
    
    foreach ($path in $psqlPaths) {
        if (Test-Path $path) {
            $psqlPath = $path
            break
        }
    }
    
    if (Test-Path $psqlPath) {
        $sql = "ALTER USER postgres WITH PASSWORD '$newPassword';"
        & $psqlPath -U postgres -c $sql
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Password changed successfully!" -ForegroundColor Green
            Write-Host ""
            Write-Host "Don't forget to:" -ForegroundColor Yellow
            Write-Host "1. Restore pg_hba.conf (change 'trust' back to 'scram-sha-256')" -ForegroundColor Cyan
            Write-Host "2. Restart PostgreSQL service" -ForegroundColor Cyan
            Write-Host "3. Update .env file: DB_PASSWORD=$newPassword" -ForegroundColor Cyan
        } else {
            Write-Host "Failed to change password. Please try manually using psql." -ForegroundColor Red
        }
    } else {
        Write-Host "psql.exe not found. Please run manually:" -ForegroundColor Yellow
        Write-Host "psql -U postgres" -ForegroundColor Green
        Write-Host "ALTER USER postgres WITH PASSWORD '$newPassword';" -ForegroundColor Green
    }
}

Write-Host ""
pause


