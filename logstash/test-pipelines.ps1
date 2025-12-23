# Test Logstash Pipelines

Write-Host "Testing Logstash Pipelines..." -ForegroundColor Cyan
Write-Host ""

# Restart Logstash to pick up new pipelines
Write-Host "[1/4] Restarting Logstash with updated pipelines..." -ForegroundColor Yellow
docker-compose restart logstash
Write-Host "[OK] Logstash restarted" -ForegroundColor Green

# Wait for Logstash to start
Write-Host "`n[2/4] Waiting for Logstash to process files (30 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Check Logstash logs
Write-Host "`n[3/4] Checking Logstash logs..." -ForegroundColor Yellow
docker-compose logs logstash | Select-Object -Last 20

# Verify data in Elasticsearch
Write-Host "`n[4/4] Verifying data in Elasticsearch..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

try {
    # Get document count
    $indexName = "ecommerce-logs-$(Get-Date -Format 'yyyy.MM.dd')"
    $countResponse = Invoke-RestMethod -Uri "http://localhost:9200/$indexName/_count" -Method GET
    
    Write-Host "[OK] Documents in index: $($countResponse.count)" -ForegroundColor Green
    
    # Get sample documents
    $searchResponse = Invoke-RestMethod -Uri "http://localhost:9200/$indexName/_search?size=2&pretty" -Method GET
    
    Write-Host "`nSample documents:" -ForegroundColor White
    foreach ($hit in $searchResponse.hits.hits) {
        Write-Host "  - Order ID: $($hit._source.order_id), Customer: $($hit._source.customer_name), Amount: $($hit._source.total_amount)" -ForegroundColor Gray
    }
    
    # Check for different event types
    Write-Host "`n[OK] Checking event types..." -ForegroundColor Yellow
    $aggResponse = Invoke-RestMethod -Uri "http://localhost:9200/$indexName/_search" -Method POST -Body @'
{
  "size": 0,
  "aggs": {
    "event_types": {
      "terms": {
        "field": "event_type"
      }
    },
    "categories": {
      "terms": {
        "field": "product_category"
      }
    },
    "total_revenue": {
      "sum": {
        "field": "total_amount"
      }
    }
  }
}
'@ -ContentType "application/json"
    
    Write-Host "`nEvent Types Distribution:" -ForegroundColor White
    foreach ($bucket in $aggResponse.aggregations.event_types.buckets) {
        Write-Host "  - $($bucket.key): $($bucket.doc_count) events" -ForegroundColor Gray
    }
    
    Write-Host "`nProduct Categories:" -ForegroundColor White
    foreach ($bucket in $aggResponse.aggregations.categories.buckets) {
        Write-Host "  - $($bucket.key): $($bucket.doc_count) orders" -ForegroundColor Gray
    }
    
    Write-Host "`nTotal Revenue: $([math]::Round($aggResponse.aggregations.total_revenue.value, 2)) EUR" -ForegroundColor Cyan
    
} catch {
    Write-Host "[FAIL] Error querying Elasticsearch: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Pipeline Testing Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "  1. Open Kibana: http://localhost:5601" -ForegroundColor Gray
Write-Host "  2. Create index pattern: ecommerce-logs-*" -ForegroundColor Gray
Write-Host "  3. Explore data in Discover" -ForegroundColor Gray
Write-Host ""
