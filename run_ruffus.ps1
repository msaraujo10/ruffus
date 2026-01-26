# Caminho do projeto
$projectPath = "K:\RUFFUS_V2"

Write-Host "Iniciando Ruffus V2..." -ForegroundColor Cyan

Set-Location $projectPath

# Garante que estamos usando o Python correto
python --version

# Executa o Ruffus
python main.py

Write-Host ""
Write-Host "Execução encerrada. Pressione ENTER para fechar." -ForegroundColor Yellow
Read-Host
