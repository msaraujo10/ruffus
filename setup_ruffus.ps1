# Setup Ruffus - Python Global (Cripto/Bybit)
# Execute este script para instalar dependências globais

Write-Host "🧠 RUFFUS Setup - Instalando dependências globais" -ForegroundColor Cyan
Write-Host ""

# Verificar se Python está disponível
$pythonCmd = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python não encontrado no PATH global" -ForegroundColor Red
    Write-Host "Instale Python ou adicione ao PATH" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Python encontrado: $pythonCmd" -ForegroundColor Green
Write-Host ""

# Instalar pip upgrade
Write-Host "📦 Atualizando pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip

# Instalar dependências
Write-Host "📦 Instalando dependências..." -ForegroundColor Cyan
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Setup completo!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Próximos passos:" -ForegroundColor Cyan
    Write-Host "  1. Execute: python main.py" -ForegroundColor White
    Write-Host "  2. Ou use: .\run_ruffus.ps1" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "❌ Erro durante instalação" -ForegroundColor Red
    exit 1
}
