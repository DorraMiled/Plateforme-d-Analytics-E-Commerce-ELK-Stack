# Test Backend API Routes

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   TESTING BACKEND API ROUTES" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$API_URL = "http://localhost:8000/api"

# Test 1: Health Check
Write-Host "[1/6] Testing health endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET
    Write-Host "[OK] Health: $($response.status)" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Health check failed" -ForegroundColor Red
}

# Test 2: GET /stats
Write-Host "`n[2/6] Testing GET /api/stats..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$API_URL/stats" -Method GET
    Write-Host "[OK] Stats retrieved" -ForegroundColor Green
    Write-Host "  - Services: ES=$($response.services.elasticsearch), MongoDB=$($response.services.mongodb), Redis=$($response.services.redis)" -ForegroundColor Gray
    if ($response.data.elasticsearch) {
        Write-Host "  - Total Documents: $($response.data.elasticsearch.total_documents)" -ForegroundColor Gray
    }
} catch {
    Write-Host "[FAIL] Stats failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: GET /files
Write-Host "`n[3/6] Testing GET /api/files..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$API_URL/files" -Method GET
    Write-Host "[OK] Files listed: $($response.count) file(s)" -ForegroundColor Green
    if ($response.count -gt 0) {
        Write-Host "  First file: $($response.files[0].filename)" -ForegroundColor Gray
    }
} catch {
    Write-Host "[FAIL] Files listing failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: POST /upload
Write-Host "`n[4/6] Testing POST /api/upload..." -ForegroundColor Yellow
try {
    # Create a test CSV file
    $testCsvPath = ".\test_upload.csv"
    $csvContent = @"
timestamp,order_id,customer_id,customer_name,customer_email,customer_ip,customer_country,customer_city,product_id,product_name,product_category,quantity,unit_price,total_amount,payment_method,order_status,shipping_method
2025-12-21 15:00:00,ORD-TEST-001,CUST-TEST-001,Test User,test@example.com,192.168.1.50,France,Paris,PROD-TEST-001,Test Product,Electronics,1,99.99,99.99,Credit Card,completed,express
"@
    $csvContent | Out-File -FilePath $testCsvPath -Encoding UTF8
    
    # Upload the file
    $boundary = [System.Guid]::NewGuid().ToString()
    $fileBytes = [System.IO.File]::ReadAllBytes($testCsvPath)
    $fileEnc = [System.Text.Encoding]::GetEncoding('iso-8859-1').GetString($fileBytes)
    
    $bodyLines = @(
        "--$boundary",
        "Content-Disposition: form-data; name=`"file`"; filename=`"test_upload.csv`"",
        "Content-Type: text/csv",
        "",
        $fileEnc,
        "--$boundary--"
    ) -join "`r`n"
    
    $response = Invoke-RestMethod -Uri "$API_URL/upload" `
        -Method POST `
        -ContentType "multipart/form-data; boundary=$boundary" `
        -Body $bodyLines
    
    Write-Host "[OK] File uploaded: $($response.filename)" -ForegroundColor Green
    Write-Host "  - Documents indexed: $($response.documents_indexed)" -ForegroundColor Gray
    Write-Host "  - File type: $($response.file_type)" -ForegroundColor Gray
    
    # Clean up test file
    Remove-Item $testCsvPath -ErrorAction SilentlyContinue
    
} catch {
    Write-Host "[FAIL] Upload failed: $($_.Exception.Message)" -ForegroundColor Red
    Remove-Item $testCsvPath -ErrorAction SilentlyContinue
}

# Test 5: GET /search
Write-Host "`n[5/6] Testing GET /api/search..." -ForegroundColor Yellow
try {
    # Search without query (get all)
    $response = Invoke-RestMethod -Uri "$API_URL/search?size=5" -Method GET
    Write-Host "[OK] Search returned $($response.count) results (Total: $($response.total))" -ForegroundColor Green
    
    # Search with query
    $response = Invoke-RestMethod -Uri "$API_URL/search?q=laptop&size=3" -Method GET
    Write-Host "[OK] Search for 'laptop' returned $($response.count) results" -ForegroundColor Green
    
    # Search by field
    $response = Invoke-RestMethod -Uri "$API_URL/search?q=France&field=customer_country&size=3" -Method GET
    Write-Host "[OK] Search in 'customer_country' returned $($response.count) results" -ForegroundColor Green
    
} catch {
    Write-Host "[FAIL] Search failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 6: GET /results
Write-Host "`n[6/6] Testing GET /api/results..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$API_URL/results" -Method GET
    Write-Host "[OK] Results analytics retrieved" -ForegroundColor Green
    Write-Host "`n  Summary:" -ForegroundColor Cyan
    Write-Host "    Total Revenue: $($response.summary.total_revenue) EUR" -ForegroundColor Gray
    Write-Host "    Total Orders: $($response.summary.total_orders)" -ForegroundColor Gray
    Write-Host "    Avg Order Value: $($response.summary.avg_order_value) EUR" -ForegroundColor Gray
    Write-Host "    Unique Customers: $($response.summary.unique_customers)" -ForegroundColor Gray
    
    Write-Host "`n  Top 3 Products:" -ForegroundColor Cyan
    foreach ($product in $response.top_products | Select-Object -First 3) {
        Write-Host "    - $($product.product): $($product.revenue) EUR ($($product.orders) orders)" -ForegroundColor Gray
    }
    
    Write-Host "`n  Top 3 Countries:" -ForegroundColor Cyan
    foreach ($country in $response.by_country | Select-Object -First 3) {
        Write-Host "    - $($country.country): $($country.revenue) EUR ($($country.orders) orders)" -ForegroundColor Gray
    }
    
} catch {
    Write-Host "[FAIL] Results failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   API TESTING COMPLETE!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`nAPI Documentation:" -ForegroundColor White
Write-Host "  POST /api/upload     - Upload CSV/JSON files" -ForegroundColor Gray
Write-Host "  GET  /api/search     - Search in Elasticsearch" -ForegroundColor Gray
Write-Host "  GET  /api/results    - Get analytics results" -ForegroundColor Gray
Write-Host "  GET  /api/files      - List uploaded files" -ForegroundColor Gray
Write-Host "  GET  /api/stats      - System statistics" -ForegroundColor Gray
Write-Host "`nTest with curl or Postman:" -ForegroundColor White
Write-Host "  curl http://localhost:8000/api/stats" -ForegroundColor Gray
Write-Host ""
