# Elasticsearch Configuration Scripts

Write-Host "Configuring Elasticsearch..." -ForegroundColor Cyan

# Create index template
Write-Host "`n[1/3] Creating index template for ecommerce-logs-*..." -ForegroundColor Yellow
$template = Get-Content -Path ".\elasticsearch\index-template.json" -Raw

try {
    $response = Invoke-RestMethod -Uri "http://localhost:9200/_index_template/ecommerce-logs-template" `
        -Method PUT `
        -Body $template `
        -ContentType "application/json"
    
    Write-Host "[OK] Index template created successfully" -ForegroundColor Green
    Write-Host "Response: $($response | ConvertTo-Json -Compress)" -ForegroundColor Gray
} catch {
    Write-Host "[FAIL] Error creating index template: $($_.Exception.Message)" -ForegroundColor Red
}

# Test insertion with sample document
Write-Host "`n[2/3] Testing document insertion..." -ForegroundColor Yellow
$sampleDoc = @{
    "@timestamp" = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
    order_id = "ORD-$(Get-Random -Maximum 99999)"
    customer_id = "CUST-001"
    customer_name = "John Doe"
    customer_email = "john.doe@example.com"
    customer_ip = "192.168.1.100"
    customer_country = "France"
    customer_city = "Paris"
    product_id = "PROD-001"
    product_name = "Laptop HP ProBook"
    product_category = "Electronics"
    quantity = 1
    unit_price = 899.99
    total_amount = 899.99
    payment_method = "Credit Card"
    order_status = "completed"
    shipping_method = "express"
    event_type = "order_placed"
    tags = @("ecommerce", "order", "test")
} | ConvertTo-Json

try {
    $indexName = "ecommerce-logs-$(Get-Date -Format 'yyyy.MM.dd')"
    $response = Invoke-RestMethod -Uri "http://localhost:9200/$indexName/_doc" `
        -Method POST `
        -Body $sampleDoc `
        -ContentType "application/json"
    
    Write-Host "[OK] Document inserted successfully" -ForegroundColor Green
    Write-Host "Document ID: $($response._id)" -ForegroundColor Gray
    Write-Host "Index: $($response._index)" -ForegroundColor Gray
} catch {
    Write-Host "[FAIL] Error inserting document: $($_.Exception.Message)" -ForegroundColor Red
}

# Verify index and mapping
Write-Host "`n[3/3] Verifying index and mapping..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

try {
    $indices = Invoke-RestMethod -Uri "http://localhost:9200/_cat/indices/ecommerce-logs-*?v" `
        -Method GET
    
    Write-Host "[OK] Current ecommerce indices:" -ForegroundColor Green
    Write-Host $indices -ForegroundColor Gray
} catch {
    Write-Host "[FAIL] Error retrieving indices: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Elasticsearch Configuration Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nYou can now:" -ForegroundColor White
Write-Host "  - View indices at: http://localhost:9200/_cat/indices?v" -ForegroundColor Gray
Write-Host "  - Access Kibana DevTools at: http://localhost:5601/app/dev_tools#/console" -ForegroundColor Gray
Write-Host ""
