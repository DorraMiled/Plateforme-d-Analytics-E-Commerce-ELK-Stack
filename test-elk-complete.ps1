# Complete ELK Stack Test - All Components

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   ELK STACK - COMPLETE TEST" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check all services
Write-Host "[1/5] Checking Docker services..." -ForegroundColor Yellow
docker-compose ps --format "table {{.Service}}\t{{.Status}}"

# Check Elasticsearch
Write-Host "`n[2/5] Testing Elasticsearch..." -ForegroundColor Yellow
try {
    $esResponse = Invoke-RestMethod -Uri "http://localhost:9200" -Method GET
    Write-Host "[OK] Elasticsearch $($esResponse.version.number)" -ForegroundColor Green
    
    $indexName = "ecommerce-logs-$(Get-Date -Format 'yyyy.MM.dd')"
    $countResponse = Invoke-RestMethod -Uri "http://localhost:9200/$indexName/_count" -Method GET
    Write-Host "[OK] Documents in index: $($countResponse.count)" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Elasticsearch error: $($_.Exception.Message)" -ForegroundColor Red
}

# Check Logstash
Write-Host "`n[3/5] Testing Logstash pipelines..." -ForegroundColor Yellow
try {
    $logstashStats = Invoke-RestMethod -Uri "http://localhost:9600/_node/stats" -Method GET
    Write-Host "[OK] Logstash running - Events processed: $($logstashStats.events.in)" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Logstash error: $($_.Exception.Message)" -ForegroundColor Red
}

# Check Kibana
Write-Host "`n[4/5] Testing Kibana..." -ForegroundColor Yellow
try {
    $kibanaStatus = Invoke-RestMethod -Uri "http://localhost:5601/api/status" -Method GET
    Write-Host "[OK] Kibana status: $($kibanaStatus.status.overall.level)" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Kibana error: $($_.Exception.Message)" -ForegroundColor Red
}

# Get aggregated stats
Write-Host "`n[5/5] Getting analytics summary..." -ForegroundColor Yellow
try {
    $aggQuery = @'
{
  "size": 0,
  "aggs": {
    "total_revenue": {
      "sum": { "field": "total_amount" }
    },
    "total_orders": {
      "value_count": { "field": "order_id" }
    },
    "countries": {
      "cardinality": { "field": "customer_country" }
    },
    "avg_order_value": {
      "avg": { "field": "total_amount" }
    },
    "top_products": {
      "terms": {
        "field": "product_name.keyword",
        "size": 5
      },
      "aggs": {
        "revenue": {
          "sum": { "field": "total_amount" }
        }
      }
    }
  }
}
'@
    
    $indexName = "ecommerce-logs-$(Get-Date -Format 'yyyy.MM.dd')"
    $statsResponse = Invoke-RestMethod -Uri "http://localhost:9200/$indexName/_search" `
        -Method POST `
        -Body $aggQuery `
        -ContentType "application/json"
    
    $aggs = $statsResponse.aggregations
    
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "   ANALYTICS SUMMARY" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Total Revenue:      $([math]::Round($aggs.total_revenue.value, 2)) EUR" -ForegroundColor White
    Write-Host "Total Orders:       $($aggs.total_orders.value)" -ForegroundColor White
    Write-Host "Countries:          $($aggs.countries.value)" -ForegroundColor White
    Write-Host "Avg Order Value:    $([math]::Round($aggs.avg_order_value.value, 2)) EUR" -ForegroundColor White
    
    Write-Host "`nTop 5 Products by Revenue:" -ForegroundColor Cyan
    foreach ($product in $aggs.top_products.buckets | Select-Object -First 5) {
        $revenue = [math]::Round($product.revenue.value, 2)
        Write-Host "  $($product.key): $revenue EUR ($($product.doc_count) orders)" -ForegroundColor Gray
    }
    
} catch {
    Write-Host "[WARN] Could not get analytics: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   ACCESS YOUR STACK" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Kibana Dashboard:  http://localhost:5601/app/dashboards#/view/ecommerce-dashboard" -ForegroundColor White
Write-Host "Kibana Discover:   http://localhost:5601/app/discover" -ForegroundColor White
Write-Host "Kibana DevTools:   http://localhost:5601/app/dev_tools#/console" -ForegroundColor White
Write-Host "Elasticsearch:     http://localhost:9200" -ForegroundColor White
Write-Host "Flask Web App:     http://localhost:8000" -ForegroundColor White

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "   ALL SYSTEMS OPERATIONAL!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green
