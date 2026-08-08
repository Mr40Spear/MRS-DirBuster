# MRS DIRB PRO - Windows Kurulum Scripti
# PowerShell olarak çalıştırın

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║     MRS DIRB PRO - Kurulum Wizard v2.0                   ║" -ForegroundColor Magenta  
Write-Host "║     Windows için Otomatik Kurulum                        ║" -ForegroundColor Magenta
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
Write-Host ""

# Python kontrolü
Write-Host "[*] Python kontrol ediliyor..." -ForegroundColor Cyan

$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[X] Python bulunamadi! Lutfen Python 3.8+ yukleyin." -ForegroundColor Red
    Write-Host "    https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

Write-Host "[+] $pythonVersion bulundu" -ForegroundColor Green

# Pip kontrolü
Write-Host "[*] pip kontrol ediliyor..." -ForegroundColor Cyan

$pipVersion = pip --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[X] pip bulunamadi!" -ForegroundColor Red
    exit 1
}

Write-Host "[+] pip bulundu" -ForegroundColor Green

# Gerekli kütüphaneler
$packages = @(
    "aiohttp",
    "rich",
    "argparse"
)

Write-Host ""
Write-Host "[*] Gerekli kutuphaneler yukleniyor..." -ForegroundColor Cyan
Write-Host ""

foreach ($package in $packages) {
    Write-Host "    [>] $package yukleniyor..." -ForegroundColor Yellow -NoNewline
    
    $result = pip install $package --quiet 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host " [OK]" -ForegroundColor Green
    } else {
        Write-Host " [HATA]" -ForegroundColor Red
        Write-Host "        $result" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "[+] Kurulum tamamlandi!" -ForegroundColor Green
Write-Host "══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "Kullanim:" -ForegroundColor Cyan
Write-Host "  python mrs_dirb_pro.py https://example.com" -ForegroundColor White
Write-Host "  python mrs_dirb_pro.py https://example.com -w wordlist.txt -t 100" -ForegroundColor White
Write-Host "  python mrs_dirb_pro.py https://example.com -m stealth -x .php,.html" -ForegroundColor White
Write-Host ""
Write-Host "Yardim icin:" -ForegroundColor Cyan
Write-Host "  python mrs_dirb_pro.py --help" -ForegroundColor White
Write-Host ""
