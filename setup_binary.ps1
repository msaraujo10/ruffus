# Setup Ruffus Binary - Virtual Environment (Bullex)
# Execute este script para instalar dependências no venv

Write-Host "🧠 RUFFUS-BINARY Setup - Instalando no venv" -ForegroundColor Cyan
Write-Host ""

# Criar venv se não existir
if (-not (Test-Path ".venv")) {
    Write-Host "📦 Criando ambiente virtual..." -ForegroundColor Cyan
    python -m venv .venv
}

# Ativar venv
Write-Host "🔌 Ativando venv..." -ForegroundColor Cyan
& ".\.venv\Scripts\Activate.ps1"

# Instalar pip upgrade
Write-Host "📦 Atualizando pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip

# Instalar dependências
Write-Host "📦 Instalando dependências..." -ForegroundColor Cyan
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Setup BINARY completo!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Próximos passos:" -ForegroundColor Cyan
    Write-Host "  1. Execute: python -m apps.ruffus_binary" -ForegroundColor White
    Write-Host "  2. Ou use: .\venv\Scripts\activate e depois python -m apps.ruffus_binary" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "❌ Erro durante instalação" -ForegroundColor Red
    exit 1
}
