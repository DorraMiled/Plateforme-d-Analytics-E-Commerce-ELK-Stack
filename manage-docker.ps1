# Script de gestion Docker pour le projet E-Commerce
param(
    [Parameter(Position=0)]
    [ValidateSet("start", "stop", "restart", "status", "logs", "clean")]
    [string]$Action = "status"
)

$ProjectPath = "C:\Users\DELL\Desktop\3eme\Big Data\miniprojetEcommerce"

function Show-Header {
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "   Gestion Docker - Projet E-Commerce" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
}

function Test-DockerRunning {
    try {
        docker ps > $null 2>&1
        return $true
    } catch {
        return $false
    }
}

function Show-Status {
    Write-Host "État des conteneurs:" -ForegroundColor Yellow
    Write-Host ""
    
    if (-not (Test-DockerRunning)) {
        Write-Host "✗ Docker Desktop n'est pas démarré!" -ForegroundColor Red
        Write-Host "  Veuillez démarrer Docker Desktop et réessayer." -ForegroundColor Yellow
        return
    }
    
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | Write-Host
    
    Write-Host "`nVérification des services:" -ForegroundColor Yellow
    
    # Elasticsearch
    try {
        $es = Invoke-RestMethod -Uri "http://localhost:9200" -TimeoutSec 2 -ErrorAction Stop
        Write-Host "✓ Elasticsearch: " -NoNewline -ForegroundColor Green
        Write-Host "Version $($es.version.number)" -ForegroundColor White
    } catch {
        Write-Host "✗ Elasticsearch: Non accessible" -ForegroundColor Red
    }
    
    # Kibana
    try {
        $null = Invoke-WebRequest -Uri "http://localhost:5601/api/status" -TimeoutSec 2 -ErrorAction Stop
        Write-Host "✓ Kibana: Accessible sur http://localhost:5601" -ForegroundColor Green
    } catch {
        Write-Host "✗ Kibana: Non accessible" -ForegroundColor Red
    }
    
    # MongoDB
    try {
        $mongoTest = docker exec mongodb mongosh --quiet --eval "db.adminCommand('ping').ok" 2>$null
        if ($mongoTest -eq "1") {
            Write-Host "✓ MongoDB: Accessible sur port 27017" -ForegroundColor Green
        } else {
            Write-Host "✗ MongoDB: Erreur de connexion" -ForegroundColor Red
        }
    } catch {
        Write-Host "✗ MongoDB: Non accessible" -ForegroundColor Red
    }
    
    # Redis
    try {
        $redisTest = docker exec redis redis-cli ping 2>$null
        if ($redisTest -eq "PONG") {
            Write-Host "✓ Redis: Accessible sur port 6379" -ForegroundColor Green
        } else {
            Write-Host "✗ Redis: Erreur de connexion" -ForegroundColor Red
        }
    } catch {
        Write-Host "✗ Redis: Non accessible" -ForegroundColor Red
    }
}

function Start-Services {
    Write-Host "Démarrage des services..." -ForegroundColor Yellow
    
    if (-not (Test-DockerRunning)) {
        Write-Host "✗ Docker Desktop n'est pas démarré!" -ForegroundColor Red
        Write-Host "  Veuillez démarrer Docker Desktop et réessayer." -ForegroundColor Yellow
        return
    }
    
    Push-Location $ProjectPath
    docker-compose up -d
    Pop-Location
    
    Write-Host "`nAttente du démarrage complet..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    
    Write-Host "`nVérification de la santé des conteneurs..." -ForegroundColor Yellow
    docker ps --format "table {{.Names}}\t{{.Status}}" | Write-Host
    
    Write-Host "`n✓ Services démarrés!" -ForegroundColor Green
    Write-Host "  Elasticsearch: http://localhost:9200" -ForegroundColor Cyan
    Write-Host "  Kibana: http://localhost:5601" -ForegroundColor Cyan
    Write-Host "  Backend API: http://localhost:8000" -ForegroundColor Cyan
}

function Stop-Services {
    Write-Host "Arrêt des services..." -ForegroundColor Yellow
    
    if (-not (Test-DockerRunning)) {
        Write-Host "✗ Docker Desktop n'est pas démarré!" -ForegroundColor Red
        return
    }
    
    Push-Location $ProjectPath
    docker-compose down
    Pop-Location
    
    Write-Host "✓ Services arrêtés!" -ForegroundColor Green
}

function Restart-Services {
    Write-Host "Redémarrage des services..." -ForegroundColor Yellow
    Stop-Services
    Start-Sleep -Seconds 3
    Start-Services
}

function Show-Logs {
    param([string]$Service = "")
    
    if (-not (Test-DockerRunning)) {
        Write-Host "✗ Docker Desktop n'est pas démarré!" -ForegroundColor Red
        return
    }
    
    Push-Location $ProjectPath
    
    if ($Service) {
        Write-Host "Logs de $Service (Ctrl+C pour quitter):" -ForegroundColor Yellow
        docker-compose logs -f $Service
    } else {
        Write-Host "Services disponibles:" -ForegroundColor Yellow
        Write-Host "  - elasticsearch"
        Write-Host "  - kibana"
        Write-Host "  - logstash"
        Write-Host "  - mongodb"
        Write-Host "  - redis"
        Write-Host "`nUtilisez: .\manage-docker.ps1 logs <service>" -ForegroundColor Cyan
        Write-Host "Exemple: .\manage-docker.ps1 logs elasticsearch" -ForegroundColor Cyan
    }
    
    Pop-Location
}

function Clean-All {
    Write-Host "⚠️  ATTENTION: Cette action va supprimer tous les volumes!" -ForegroundColor Yellow
    $confirm = Read-Host "Êtes-vous sûr? (oui/non)"
    
    if ($confirm -eq "oui") {
        Write-Host "Nettoyage complet..." -ForegroundColor Yellow
        
        Push-Location $ProjectPath
        docker-compose down -v
        docker volume prune -f
        Pop-Location
        
        Write-Host "✓ Nettoyage terminé!" -ForegroundColor Green
    } else {
        Write-Host "Nettoyage annulé." -ForegroundColor Yellow
    }
}

# Main
Show-Header

switch ($Action) {
    "start" { Start-Services }
    "stop" { Stop-Services }
    "restart" { Restart-Services }
    "status" { Show-Status }
    "logs" { Show-Logs -Service $args[0] }
    "clean" { Clean-All }
}

Write-Host ""
