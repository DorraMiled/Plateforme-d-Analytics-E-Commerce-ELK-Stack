# Kibana Configuration Script - Create Index Pattern, Visualizations, and Dashboard

Write-Host "Configuring Kibana..." -ForegroundColor Cyan
Write-Host ""

$KIBANA_URL = "http://localhost:5601"
$HEADERS = @{
    "kbn-xsrf" = "true"
    "Content-Type" = "application/json"
}

# Wait for Kibana to be ready
Write-Host "[1/5] Waiting for Kibana to be ready..." -ForegroundColor Yellow
$maxRetries = 10
$retry = 0
while ($retry -lt $maxRetries) {
    try {
        $status = Invoke-RestMethod -Uri "$KIBANA_URL/api/status" -Method GET -TimeoutSec 5
        if ($status.status.overall.level -eq "available") {
            Write-Host "[OK] Kibana is ready" -ForegroundColor Green
            break
        }
    } catch {
        $retry++
        Write-Host "Waiting... (attempt $retry/$maxRetries)" -ForegroundColor Gray
        Start-Sleep -Seconds 10
    }
}

# Create Index Pattern
Write-Host "`n[2/5] Creating index pattern for ecommerce-logs-*..." -ForegroundColor Yellow
$indexPatternBody = @{
    attributes = @{
        title = "ecommerce-logs-*"
        timeFieldName = "@timestamp"
    }
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$KIBANA_URL/api/saved_objects/index-pattern/ecommerce-logs-pattern" `
        -Method POST `
        -Headers $HEADERS `
        -Body $indexPatternBody `
        -TimeoutSec 10
    
    Write-Host "[OK] Index pattern created: ecommerce-logs-*" -ForegroundColor Green
    $indexPatternId = $response.id
} catch {
    Write-Host "[WARN] Index pattern may already exist or error occurred: $($_.Exception.Message)" -ForegroundColor Yellow
    $indexPatternId = "ecommerce-logs-pattern"
}

# Set as default index pattern
try {
    Invoke-RestMethod -Uri "$KIBANA_URL/api/kibana/settings/defaultIndex" `
        -Method POST `
        -Headers $HEADERS `
        -Body "{`"value`":`"$indexPatternId`"}" `
        -TimeoutSec 10
    Write-Host "[OK] Set as default index pattern" -ForegroundColor Green
} catch {
    Write-Host "[INFO] Could not set default index pattern" -ForegroundColor Gray
}

Start-Sleep -Seconds 3

# Create Visualizations
Write-Host "`n[3/5] Creating visualizations..." -ForegroundColor Yellow

# Visualization 1: Total Revenue Over Time
$viz1 = @{
    attributes = @{
        title = "Total Revenue Over Time"
        visState = @{
            title = "Total Revenue Over Time"
            type = "line"
            aggs = @(
                @{
                    id = "1"
                    enabled = $true
                    type = "sum"
                    schema = "metric"
                    params = @{
                        field = "total_amount"
                    }
                },
                @{
                    id = "2"
                    enabled = $true
                    type = "date_histogram"
                    schema = "segment"
                    params = @{
                        field = "@timestamp"
                        interval = "h"
                        min_doc_count = 1
                    }
                }
            )
            params = @{
                type = "line"
                grid = @{
                    categoryLines = $false
                }
                categoryAxes = @(
                    @{
                        id = "CategoryAxis-1"
                        type = "category"
                        position = "bottom"
                        show = $true
                        title = @{}
                    }
                )
                valueAxes = @(
                    @{
                        id = "ValueAxis-1"
                        name = "LeftAxis-1"
                        type = "value"
                        position = "left"
                        show = $true
                        title = @{
                            text = "Revenue"
                        }
                    }
                )
            }
        } | ConvertTo-Json -Depth 10 -Compress
        kibanaSavedObjectMeta = @{
            searchSourceJSON = @{
                index = $indexPatternId
                query = @{
                    query = ""
                    language = "kuery"
                }
                filter = @()
            } | ConvertTo-Json -Compress
        }
    }
} | ConvertTo-Json -Depth 10

try {
    $response = Invoke-RestMethod -Uri "$KIBANA_URL/api/saved_objects/visualization/viz-revenue-over-time" `
        -Method POST `
        -Headers $HEADERS `
        -Body $viz1 `
        -TimeoutSec 10
    Write-Host "[OK] Created visualization: Total Revenue Over Time" -ForegroundColor Green
    $viz1Id = $response.id
} catch {
    Write-Host "[WARN] Visualization 1 may already exist: $($_.Exception.Message)" -ForegroundColor Yellow
    $viz1Id = "viz-revenue-over-time"
}

# Visualization 2: Top Products by Sales
$viz2 = @{
    attributes = @{
        title = "Top 10 Products by Sales"
        visState = @{
            title = "Top 10 Products by Sales"
            type = "horizontal_bar"
            aggs = @(
                @{
                    id = "1"
                    enabled = $true
                    type = "sum"
                    schema = "metric"
                    params = @{
                        field = "total_amount"
                    }
                },
                @{
                    id = "2"
                    enabled = $true
                    type = "terms"
                    schema = "segment"
                    params = @{
                        field = "product_name.keyword"
                        size = 10
                        order = "desc"
                        orderBy = "1"
                    }
                }
            )
            params = @{
                type = "horizontal_bar"
                addLegend = $true
                addTooltip = $true
            }
        } | ConvertTo-Json -Depth 10 -Compress
        kibanaSavedObjectMeta = @{
            searchSourceJSON = @{
                index = $indexPatternId
                query = @{
                    query = ""
                    language = "kuery"
                }
                filter = @()
            } | ConvertTo-Json -Compress
        }
    }
} | ConvertTo-Json -Depth 10

try {
    $response = Invoke-RestMethod -Uri "$KIBANA_URL/api/saved_objects/visualization/viz-top-products" `
        -Method POST `
        -Headers $HEADERS `
        -Body $viz2 `
        -TimeoutSec 10
    Write-Host "[OK] Created visualization: Top 10 Products by Sales" -ForegroundColor Green
    $viz2Id = $response.id
} catch {
    Write-Host "[WARN] Visualization 2 may already exist: $($_.Exception.Message)" -ForegroundColor Yellow
    $viz2Id = "viz-top-products"
}

# Visualization 3: Orders by Country
$viz3 = @{
    attributes = @{
        title = "Orders by Country"
        visState = @{
            title = "Orders by Country"
            type = "pie"
            aggs = @(
                @{
                    id = "1"
                    enabled = $true
                    type = "count"
                    schema = "metric"
                    params = @{}
                },
                @{
                    id = "2"
                    enabled = $true
                    type = "terms"
                    schema = "segment"
                    params = @{
                        field = "customer_country"
                        size = 10
                        order = "desc"
                        orderBy = "1"
                    }
                }
            )
            params = @{
                type = "pie"
                addLegend = $true
                addTooltip = $true
                isDonut = $false
            }
        } | ConvertTo-Json -Depth 10 -Compress
        kibanaSavedObjectMeta = @{
            searchSourceJSON = @{
                index = $indexPatternId
                query = @{
                    query = ""
                    language = "kuery"
                }
                filter = @()
            } | ConvertTo-Json -Compress
        }
    }
} | ConvertTo-Json -Depth 10

try {
    $response = Invoke-RestMethod -Uri "$KIBANA_URL/api/saved_objects/visualization/viz-orders-by-country" `
        -Method POST `
        -Headers $HEADERS `
        -Body $viz3 `
        -TimeoutSec 10
    Write-Host "[OK] Created visualization: Orders by Country" -ForegroundColor Green
    $viz3Id = $response.id
} catch {
    Write-Host "[WARN] Visualization 3 may already exist: $($_.Exception.Message)" -ForegroundColor Yellow
    $viz3Id = "viz-orders-by-country"
}

Write-Host "`n[4/5] Creating dashboard..." -ForegroundColor Yellow

# Create Dashboard
$dashboard = @{
    attributes = @{
        title = "E-commerce Analytics Dashboard"
        description = "Complete e-commerce analytics dashboard with revenue, products, and geographic distribution"
        panelsJSON = @(
            @{
                version = "8.11.0"
                gridData = @{
                    x = 0
                    y = 0
                    w = 24
                    h = 15
                    i = "1"
                }
                panelIndex = "1"
                embeddableConfig = @{}
                panelRefName = "panel_1"
            },
            @{
                version = "8.11.0"
                gridData = @{
                    x = 0
                    y = 15
                    w = 12
                    h = 15
                    i = "2"
                }
                panelIndex = "2"
                embeddableConfig = @{}
                panelRefName = "panel_2"
            },
            @{
                version = "8.11.0"
                gridData = @{
                    x = 12
                    y = 15
                    w = 12
                    h = 15
                    i = "3"
                }
                panelIndex = "3"
                embeddableConfig = @{}
                panelRefName = "panel_3"
            }
        ) | ConvertTo-Json -Compress
        optionsJSON = @{
            hidePanelTitles = $false
            useMargins = $true
        } | ConvertTo-Json -Compress
        timeRestore = $false
    }
    references = @(
        @{
            name = "panel_1"
            type = "visualization"
            id = $viz1Id
        },
        @{
            name = "panel_2"
            type = "visualization"
            id = $viz2Id
        },
        @{
            name = "panel_3"
            type = "visualization"
            id = $viz3Id
        }
    )
} | ConvertTo-Json -Depth 10

try {
    $response = Invoke-RestMethod -Uri "$KIBANA_URL/api/saved_objects/dashboard/ecommerce-dashboard" `
        -Method POST `
        -Headers $HEADERS `
        -Body $dashboard `
        -TimeoutSec 10
    Write-Host "[OK] Dashboard created: E-commerce Analytics Dashboard" -ForegroundColor Green
    $dashboardId = $response.id
} catch {
    Write-Host "[WARN] Dashboard may already exist: $($_.Exception.Message)" -ForegroundColor Yellow
    $dashboardId = "ecommerce-dashboard"
}

# Export Dashboard
Write-Host "`n[5/5] Exporting dashboard..." -ForegroundColor Yellow
try {
    $exportUrl = "$KIBANA_URL/api/kibana/dashboards/export?dashboard=$dashboardId"
    $exportedDashboard = Invoke-RestMethod -Uri $exportUrl -Method GET -Headers $HEADERS -TimeoutSec 10
    
    $exportedDashboard | ConvertTo-Json -Depth 20 | Out-File -FilePath ".\kibana\dashboard-export.json" -Encoding UTF8
    Write-Host "[OK] Dashboard exported to: kibana\dashboard-export.json" -ForegroundColor Green
} catch {
    Write-Host "[WARN] Could not export dashboard: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Kibana Configuration Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access your dashboard at:" -ForegroundColor White
Write-Host "  $KIBANA_URL/app/dashboards#/view/$dashboardId" -ForegroundColor Green
Write-Host ""
Write-Host "Or browse all dashboards:" -ForegroundColor White
Write-Host "  $KIBANA_URL/app/dashboards" -ForegroundColor Gray
Write-Host ""
