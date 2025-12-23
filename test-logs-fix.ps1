# Script de test pour vérifier les corrections des logs
Write-Host "=== Test de l'API après corrections ===" -ForegroundColor Cyan

# 1. Vérifier Elasticsearch
Write-Host "`n1. Vérification Elasticsearch..." -ForegroundColor Yellow
try {
    $esCount = Invoke-RestMethod -Uri "http://localhost:9200/ecommerce-logs-*/_count"
    Write-Host "✓ Elasticsearch OK - $($esCount.count) documents" -ForegroundColor Green
} catch {
    Write-Host "✗ Elasticsearch non accessible" -ForegroundColor Red
    Write-Host "  Assurez-vous que Docker Desktop est démarré et exécutez: docker-compose up -d"
    exit 1
}

# 2. Tester le Dashboard
Write-Host "`n2. Test du Dashboard..." -ForegroundColor Yellow
try {
    $dashboard = Invoke-RestMethod -Uri "http://localhost:8000/api/dashboard"
    Write-Host "✓ Total logs: $($dashboard.total_logs)" -ForegroundColor Green
    Write-Host "✓ Recent logs: $($dashboard.recent_logs.Count)" -ForegroundColor Green
    
    if ($dashboard.recent_logs.Count -gt 0) {
        Write-Host "`n  Exemple de log récent:" -ForegroundColor Cyan
        $log = $dashboard.recent_logs[0]
        Write-Host "    Timestamp: $($log.timestamp)"
        Write-Host "    Level: $($log.level)"
        Write-Host "    Service: $($log.service)"
        Write-Host "    Message: $($log.message.Substring(0, [Math]::Min(60, $log.message.Length)))..."
        
        if ($log.level -ne "" -and $log.service -ne "" -and $log.message -ne "") {
            Write-Host "`n  ✓ Tous les champs sont remplis!" -ForegroundColor Green
        } else {
            Write-Host "`n  ✗ Certains champs sont vides" -ForegroundColor Red
        }
    }
} catch {
    Write-Host "✗ Erreur Dashboard: $($_.Exception.Message)" -ForegroundColor Red
}

# 3. Tester la Recherche
Write-Host "`n3. Test de la Recherche..." -ForegroundColor Yellow
try {
    $body = @{ query = ""; size = 3 } | ConvertTo-Json
    $search = Invoke-RestMethod -Uri "http://localhost:8000/api/search" -Method POST -Body $body -ContentType "application/json"
    Write-Host "✓ Total résultats: $($search.total)" -ForegroundColor Green
    Write-Host "✓ Résultats affichés: $($search.hits.Count)" -ForegroundColor Green
    
    if ($search.hits.Count -gt 0) {
        Write-Host "`n  Exemples de résultats:" -ForegroundColor Cyan
        $search.hits | Select-Object -First 3 | ForEach-Object {
            Write-Host "`n    Timestamp: $($_.timestamp)"
            Write-Host "    Level: $($_.level)"
            Write-Host "    Service: $($_.service)"
            Write-Host "    Message: $($_.message.Substring(0, [Math]::Min(60, $_.message.Length)))..."
        }
        
        $emptyFields = $search.hits | Where-Object { $_.level -eq "" -or $_.service -eq "" -or $_.message -eq "" }
        if ($emptyFields.Count -eq 0) {
            Write-Host "`n  ✓ Tous les résultats ont des champs remplis!" -ForegroundColor Green
        } else {
            Write-Host "`n  ✗ $($emptyFields.Count) résultats ont des champs vides" -ForegroundColor Red
        }
    }
} catch {
    Write-Host "✗ Erreur Recherche: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== Test terminé ===" -ForegroundColor Cyan
