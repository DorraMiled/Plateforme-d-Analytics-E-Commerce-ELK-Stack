# Kibana Configuration - Fixed Version

Write-Host "Configuring Kibana (Fixed)..." -ForegroundColor Cyan
Write-Host ""

$KIBANA_URL = "http://localhost:5601"
$HEADERS = @{
    "kbn-xsrf" = "true"
    "Content-Type" = "application/json"
}

# Wait for Kibana
Write-Host "[1/4] Waiting for Kibana..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
Write-Host "[OK] Kibana ready" -ForegroundColor Green

# Get or create index pattern
Write-Host "`n[2/4] Setting up index pattern..." -ForegroundColor Yellow
$indexPatternId = "ecommerce-logs-pattern"

try {
    # Try to get existing index pattern
    $existingPattern = Invoke-RestMethod -Uri "$KIBANA_URL/api/saved_objects/index-pattern/$indexPatternId" -Method GET -Headers $HEADERS -ErrorAction SilentlyContinue
    Write-Host "[OK] Index pattern already exists" -ForegroundColor Green
} catch {
    # Create new index pattern
    $indexPatternBody = @{
        attributes = @{
            title = "ecommerce-logs-*"
            timeFieldName = "@timestamp"
        }
    } | ConvertTo-Json -Depth 10
    
    $response = Invoke-RestMethod -Uri "$KIBANA_URL/api/saved_objects/index-pattern/$indexPatternId" -Method POST -Headers $HEADERS -Body $indexPatternBody
    Write-Host "[OK] Index pattern created" -ForegroundColor Green
}

# Create simple metric visualizations using Lens API
Write-Host "`n[3/4] Creating visualizations..." -ForegroundColor Yellow

# Visualization 1: Revenue Metric
$metricViz = @{
    attributes = @{
        title = "Total Revenue"
        visualizationType = "lnsMetric"
        state = @{
            datasourceStates = @{
                formBased = @{
                    layers = @{
                        layer1 = @{
                            columns = @{
                                col1 = @{
                                    label = "Total Revenue"
                                    dataType = "number"
                                    operationType = "sum"
                                    sourceField = "total_amount"
                                    isBucketed = $false
                                }
                            }
                            columnOrder = @("col1")
                            indexPatternId = $indexPatternId
                        }
                    }
                }
            }
            visualization = @{
                layerId = "layer1"
                accessor = "col1"
            }
            query = @{
                query = ""
                language = "kuery"
            }
            filters = @()
        }
        references = @(
            @{
                type = "index-pattern"
                id = $indexPatternId
                name = "indexpattern-datasource-layer-layer1"
            }
        )
    }
} | ConvertTo-Json -Depth 20

try {
    Invoke-RestMethod -Uri "$KIBANA_URL/api/saved_objects/lens/lens-revenue-metric" -Method POST -Headers $HEADERS -Body $metricViz | Out-Null
    Write-Host "[OK] Revenue metric created" -ForegroundColor Green
} catch {
    Write-Host "[WARN] Could not create revenue metric: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Visualization 2: Orders by Country (Pie)
$pieViz = @{
    attributes = @{
        title = "Orders by Country"
        visualizationType = "lnsPie"
        state = @{
            datasourceStates = @{
                formBased = @{
                    layers = @{
                        layer1 = @{
                            columns = @{
                                col1 = @{
                                    label = "Country"
                                    dataType = "string"
                                    operationType = "terms"
                                    sourceField = "customer_country"
                                    isBucketed = $true
                                    params = @{
                                        size = 10
                                        orderBy = @{
                                            type = "column"
                                            columnId = "col2"
                                        }
                                        orderDirection = "desc"
                                    }
                                }
                                col2 = @{
                                    label = "Count"
                                    dataType = "number"
                                    operationType = "count"
                                    isBucketed = $false
                                }
                            }
                            columnOrder = @("col1", "col2")
                            indexPatternId = $indexPatternId
                        }
                    }
                }
            }
            visualization = @{
                shape = "pie"
                layers = @(
                    @{
                        layerId = "layer1"
                        groups = @("col1")
                        metric = "col2"
                        numberDisplay = "percent"
                        categoryDisplay = "default"
                        legendDisplay = "default"
                        nestedLegend = $false
                    }
                )
            }
            query = @{
                query = ""
                language = "kuery"
            }
            filters = @()
        }
        references = @(
            @{
                type = "index-pattern"
                id = $indexPatternId
                name = "indexpattern-datasource-layer-layer1"
            }
        )
    }
} | ConvertTo-Json -Depth 20

try {
    Invoke-RestMethod -Uri "$KIBANA_URL/api/saved_objects/lens/lens-orders-by-country" -Method POST -Headers $HEADERS -Body $pieViz | Out-Null
    Write-Host "[OK] Orders by country pie chart created" -ForegroundColor Green
} catch {
    Write-Host "[WARN] Could not create pie chart: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Visualization 3: Top Products (Bar)
$barViz = @{
    attributes = @{
        title = "Top Products by Revenue"
        visualizationType = "lnsXY"
        state = @{
            datasourceStates = @{
                formBased = @{
                    layers = @{
                        layer1 = @{
                            columns = @{
                                col1 = @{
                                    label = "Product"
                                    dataType = "string"
                                    operationType = "terms"
                                    sourceField = "product_name.keyword"
                                    isBucketed = $true
                                    params = @{
                                        size = 10
                                        orderBy = @{
                                            type = "column"
                                            columnId = "col2"
                                        }
                                        orderDirection = "desc"
                                    }
                                }
                                col2 = @{
                                    label = "Revenue"
                                    dataType = "number"
                                    operationType = "sum"
                                    sourceField = "total_amount"
                                    isBucketed = $false
                                }
                            }
                            columnOrder = @("col1", "col2")
                            indexPatternId = $indexPatternId
                        }
                    }
                }
            }
            visualization = @{
                legend = @{
                    isVisible = $true
                    position = "right"
                }
                valueLabels = "hide"
                fittingFunction = "None"
                axisTitlesVisibilitySettings = @{
                    x = $true
                    yLeft = $true
                    yRight = $true
                }
                tickLabelsVisibilitySettings = @{
                    x = $true
                    yLeft = $true
                    yRight = $true
                }
                layers = @(
                    @{
                        layerId = "layer1"
                        accessors = @("col2")
                        position = "top"
                        seriesType = "bar_horizontal"
                        showGridlines = $false
                        xAccessor = "col1"
                    }
                )
            }
            query = @{
                query = ""
                language = "kuery"
            }
            filters = @()
        }
        references = @(
            @{
                type = "index-pattern"
                id = $indexPatternId
                name = "indexpattern-datasource-layer-layer1"
            }
        )
    }
} | ConvertTo-Json -Depth 20

try {
    Invoke-RestMethod -Uri "$KIBANA_URL/api/saved_objects/lens/lens-top-products" -Method POST -Headers $HEADERS -Body $barViz | Out-Null
    Write-Host "[OK] Top products bar chart created" -ForegroundColor Green
} catch {
    Write-Host "[WARN] Could not create bar chart: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Create Dashboard
Write-Host "`n[4/4] Creating dashboard..." -ForegroundColor Yellow

$dashboard = @{
    attributes = @{
        title = "E-commerce Analytics Dashboard"
        description = "Analytics dashboard with revenue, products, and geographic distribution"
        panelsJSON = '[{"version":"8.11.0","type":"lens","gridData":{"x":0,"y":0,"w":12,"h":15,"i":"1"},"panelIndex":"1","embeddableConfig":{"enhancements":{}},"panelRefName":"panel_1"},{"version":"8.11.0","type":"lens","gridData":{"x":12,"y":0,"w":12,"h":15,"i":"2"},"panelIndex":"2","embeddableConfig":{"enhancements":{}},"panelRefName":"panel_2"},{"version":"8.11.0","type":"lens","gridData":{"x":0,"y":15,"w":24,"h":15,"i":"3"},"panelIndex":"3","embeddableConfig":{"enhancements":{}},"panelRefName":"panel_3"}]'
        optionsJSON = '{"useMargins":true,"syncColors":false,"hidePanelTitles":false}'
        version = 1
        timeRestore = $false
        kibanaSavedObjectMeta = @{
            searchSourceJSON = '{"query":{"query":"","language":"kuery"},"filter":[]}'
        }
    }
    references = @(
        @{
            name = "panel_1"
            type = "lens"
            id = "lens-revenue-metric"
        }
        @{
            name = "panel_2"
            type = "lens"
            id = "lens-orders-by-country"
        }
        @{
            name = "panel_3"
            type = "lens"
            id = "lens-top-products"
        }
    )
} | ConvertTo-Json -Depth 10

try {
    $dashResponse = Invoke-RestMethod -Uri "$KIBANA_URL/api/saved_objects/dashboard/ecommerce-dashboard" -Method POST -Headers $HEADERS -Body $dashboard
    Write-Host "[OK] Dashboard created successfully!" -ForegroundColor Green
    $dashboardId = $dashResponse.id
} catch {
    Write-Host "[FAIL] Could not create dashboard: $($_.Exception.Message)" -ForegroundColor Red
    $dashboardId = "ecommerce-dashboard"
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Kibana Configuration Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access your dashboard at:" -ForegroundColor White
Write-Host "  $KIBANA_URL/app/dashboards#/view/$dashboardId" -ForegroundColor Green
Write-Host ""
Write-Host "Or go to Discover to explore data:" -ForegroundColor White
Write-Host "  $KIBANA_URL/app/discover" -ForegroundColor Gray
Write-Host ""
