# Test script for E-commerce API

Write-Host "Testing E-commerce Docker Stack..." -ForegroundColor Cyan
Write-Host ""

# Test Elasticsearch
Write-Host "Testing Elasticsearch (port 9200)..." -ForegroundColor Yellow
try {
    $esResponse = Invoke-WebRequest -Uri http://localhost:9200 -UseBasicParsing -TimeoutSec 5
    $esData = $esResponse.Content | ConvertFrom-Json
    Write-Host "[OK] Elasticsearch: Version $($esData.version.number)" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Elasticsearch: Not accessible" -ForegroundColor Red
}
Write-Host ""

# Test Flask Web App
Write-Host "Testing Flask Web App (port 8000)..." -ForegroundColor Yellow
try {
    $appResponse = Invoke-WebRequest -Uri http://localhost:8000 -UseBasicParsing -TimeoutSec 5
    $appData = $appResponse.Content | ConvertFrom-Json
    Write-Host "[OK] Flask App: $($appData.message)" -ForegroundColor Green
    Write-Host "   Status: $($appData.status)" -ForegroundColor Gray
    Write-Host "   MongoDB: $($appData.services.mongodb)" -ForegroundColor Gray
    Write-Host "   Redis: $($appData.services.redis)" -ForegroundColor Gray
    Write-Host "   Elasticsearch: $($appData.services.elasticsearch)" -ForegroundColor Gray
} catch {
    Write-Host "[FAIL] Flask App: Not accessible" -ForegroundColor Red
}
Write-Host ""

# Test Kibana
Write-Host "Testing Kibana (port 5601)..." -ForegroundColor Yellow
try {
    $kibanaResponse = Invoke-WebRequest -Uri http://localhost:5601/api/status -UseBasicParsing -TimeoutSec 10
    Write-Host "[OK] Kibana: Accessible (Status Code: $($kibanaResponse.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "[WAIT] Kibana: Still starting up (this can take 1-2 minutes)..." -ForegroundColor Yellow
}
Write-Host ""

# Test creating a product
Write-Host "Testing Product Creation..." -ForegroundColor Yellow
try {
    $product = @{
        name = "Test Laptop HP"
        price = 899.99
        category = "Electronics"
        description = "High-performance laptop for testing"
        stock = 50
    } | ConvertTo-Json

    $headers = @{
        "Content-Type" = "application/json"
    }

    $createResponse = Invoke-WebRequest -Uri http://localhost:8000/api/products -Method POST -Body $product -Headers $headers -UseBasicParsing
    $createData = $createResponse.Content | ConvertFrom-Json
    Write-Host "[OK] Product created: ID = $($createData.id)" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Product creation failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test getting products
Write-Host "Testing Get Products..." -ForegroundColor Yellow
try {
    $productsResponse = Invoke-WebRequest -Uri http://localhost:8000/api/products -UseBasicParsing
    $productsData = $productsResponse.Content | ConvertFrom-Json
    Write-Host "[OK] Products retrieved: $($productsData.count) product(s)" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Get products failed" -ForegroundColor Red
}
Write-Host ""

# Test Redis cache
Write-Host "Testing Redis Cache..." -ForegroundColor Yellow
try {
    $cacheData = @{
        value = "Test User - John Doe"
    } | ConvertTo-Json

    $headers = @{
        "Content-Type" = "application/json"
    }

    $cacheSetResponse = Invoke-WebRequest -Uri http://localhost:8000/api/cache/test_user -Method POST -Body $cacheData -Headers $headers -UseBasicParsing
    Write-Host "[OK] Cache set successfully" -ForegroundColor Green

    $cacheGetResponse = Invoke-WebRequest -Uri http://localhost:8000/api/cache/test_user -UseBasicParsing
    $cacheGetData = $cacheGetResponse.Content | ConvertFrom-Json
    Write-Host "[OK] Cache retrieved: $($cacheGetData.value)" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Cache test failed" -ForegroundColor Red
}
Write-Host ""

Write-Host "Testing Complete!" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access URLs:" -ForegroundColor White
Write-Host "   Kibana:        http://localhost:5601" -ForegroundColor Gray
Write-Host "   Elasticsearch: http://localhost:9200" -ForegroundColor Gray
Write-Host "   Web App:       http://localhost:8000" -ForegroundColor Gray
Write-Host ""
