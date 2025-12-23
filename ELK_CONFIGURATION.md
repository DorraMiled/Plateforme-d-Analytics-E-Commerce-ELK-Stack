# ELK Stack Configuration - Complete Guide

## ✅ Configuration Summary

All ELK stack components have been successfully configured and tested!

### 📊 Elasticsearch Configuration

#### Index Template Created
- **Template Name**: `ecommerce-logs-template`
- **Index Pattern**: `ecommerce-logs-*`
- **Mappings Include**:
  - `@timestamp` (date) - Event timestamp
  - `customer_ip` (ip) - Customer IP address
  - `order_id` (keyword) - Unique order identifier
  - `customer_name` (text + keyword) - Customer name with full-text search
  - `product_category` (keyword) - Product category
  - `quantity` (integer) - Order quantity
  - `unit_price` (float) - Product price
  - `total_amount` (float) - Total order amount
  - `payment_method` (keyword) - Payment method
  - `order_status` (keyword) - Order status
  - `geoip` (geo_point) - Geographic location data

#### Testing
✅ Index template created successfully  
✅ Sample document inserted  
✅ Mapping verified

**Test Command**:
```powershell
.\elasticsearch\setup-elasticsearch.ps1
```

---

### 🔄 Logstash Configuration

#### Pipeline 1: CSV Orders Pipeline
**File**: [logstash/pipeline/csv-pipeline.conf](logstash/pipeline/csv-pipeline.conf)

**Features**:
- ✅ CSV parsing with header mapping
- ✅ Date parsing from `yyyy-MM-dd HH:mm:ss` format
- ✅ Type conversion (integer, float)
- ✅ GeoIP enrichment from customer IP
- ✅ Tags: `csv`, `orders`, `ecommerce`
- ✅ Event type: `order_placed`

**Filters**:
```ruby
csv { separator => "," columns => [...] }
date { match => ["timestamp", "yyyy-MM-dd HH:mm:ss"] }
mutate { convert => { "quantity" => "integer", "unit_price" => "float" } }
geoip { source => "customer_ip" }
```

#### Pipeline 2: JSON Events Pipeline
**File**: [logstash/pipeline/json-pipeline.conf](logstash/pipeline/json-pipeline.conf)

**Features**:
- ✅ JSON parsing (auto-handled by codec)
- ✅ ISO8601 timestamp parsing
- ✅ Type conversion for numeric fields
- ✅ GeoIP enrichment
- ✅ Dynamic tagging based on event_type
- ✅ Tags: `json`, `events`, `ecommerce`

**Filters**:
```ruby
date { match => ["timestamp", "ISO8601"] }
mutate { convert => { ... } add_tag => [...] }
geoip { source => "customer_ip" }
```

#### Data Sources
- **CSV**: [data/ecommerce-orders.csv](data/ecommerce-orders.csv) - 20 orders
- **JSON**: [data/ecommerce-events.json](data/ecommerce-events.json) - 10 events

#### Testing
✅ CSV pipeline processing: 20 documents  
✅ JSON pipeline processing: 10 events  
✅ Total documents ingested: 464+ (includes continuous processing)  
✅ GeoIP enrichment working  
✅ Field type conversions successful

**Test Command**:
```powershell
.\logstash\test-pipelines.ps1
```

---

### 📈 Kibana Configuration

#### Index Pattern
- **Pattern**: `ecommerce-logs-*`
- **Time Field**: `@timestamp`
- **Status**: ✅ Created and set as default

#### Visualizations Created

##### 1. Total Revenue Over Time
- **Type**: Line Chart
- **Metric**: Sum of `total_amount`
- **X-Axis**: Date histogram by hour
- **Purpose**: Track revenue trends over time

##### 2. Top 10 Products by Sales
- **Type**: Horizontal Bar Chart
- **Metric**: Sum of `total_amount`
- **Breakdown**: By `product_name.keyword`
- **Purpose**: Identify best-selling products

##### 3. Orders by Country
- **Type**: Pie Chart
- **Metric**: Count of orders
- **Breakdown**: By `customer_country`
- **Purpose**: Geographic distribution of orders

#### Dashboard
- **Name**: E-commerce Analytics Dashboard
- **Panels**: 3 visualizations
- **Layout**: 
  - Top: Revenue Over Time (full width)
  - Bottom Left: Top Products
  - Bottom Right: Orders by Country

**Access URL**: http://localhost:5601/app/dashboards#/view/ecommerce-dashboard

#### Export
✅ Dashboard exported to: [kibana/dashboard-export.json](kibana/dashboard-export.json)

**Setup Command**:
```powershell
.\kibana\setup-kibana.ps1
```

---

## 📁 Project Structure

```
miniprojetEcommerce/
├── elasticsearch/
│   ├── index-template.json         # Index template definition
│   └── setup-elasticsearch.ps1     # Setup script
├── logstash/
│   ├── config/
│   │   └── logstash.yml           # Logstash config
│   ├── pipeline/
│   │   ├── csv-pipeline.conf      # CSV processing pipeline
│   │   ├── json-pipeline.conf     # JSON processing pipeline
│   │   └── logstash.conf          # Original pipeline
│   └── test-pipelines.ps1         # Pipeline test script
├── kibana/
│   ├── setup-kibana.ps1           # Kibana setup script
│   └── dashboard-export.json      # Exported dashboard
├── data/
│   ├── ecommerce-orders.csv       # Sample CSV data (20 orders)
│   └── ecommerce-events.json      # Sample JSON data (10 events)
└── docker-compose.yml             # Updated with data volume mount
```

---

## 🧪 Testing & Validation

### Complete Test Suite

#### 1. Elasticsearch
```powershell
# Create index template
.\elasticsearch\setup-elasticsearch.ps1

# View indices
curl http://localhost:9200/_cat/indices/ecommerce-logs-*?v

# Query data
curl http://localhost:9200/ecommerce-logs-2025.12.21/_search?pretty
```

#### 2. Logstash
```powershell
# Test pipelines
.\logstash\test-pipelines.ps1

# View logs
docker-compose logs logstash

# Check document count
curl http://localhost:9200/ecommerce-logs-*/_count
```

#### 3. Kibana
```powershell
# Setup Kibana
.\kibana\setup-kibana.ps1

# Access dashboard
Start-Process "http://localhost:5601/app/dashboards#/view/ecommerce-dashboard"
```

### Verification Queries

#### Aggregations Example
```json
POST /ecommerce-logs-*/_search
{
  "size": 0,
  "aggs": {
    "total_revenue": {
      "sum": { "field": "total_amount" }
    },
    "orders_by_country": {
      "terms": { "field": "customer_country" }
    },
    "top_products": {
      "terms": { 
        "field": "product_name.keyword",
        "size": 10
      },
      "aggs": {
        "revenue": {
          "sum": { "field": "total_amount" }
        }
      }
    }
  }
}
```

---

## 📊 Key Metrics

### Data Processed
- **Total Documents**: 464+
- **CSV Orders**: 20
- **JSON Events**: 10
- **Index**: ecommerce-logs-2025.12.21

### Field Types
- **Keywords**: 12 (order_id, customer_id, payment_method, etc.)
- **Text Fields**: 3 (customer_name, product_name, message)
- **Numeric**: 3 (quantity, unit_price, total_amount)
- **Date**: 2 (@timestamp, timestamp)
- **IP**: 1 (customer_ip)
- **GeoIP**: 1 (geoip with location)

---

## 🎯 Features Implemented

### ✅ Elasticsearch
- [x] Index template for `ecommerce-logs-*`
- [x] Proper field mappings (date, ip, keyword, number)
- [x] Test document insertion
- [x] Index verification

### ✅ Logstash
- [x] CSV pipeline with `csv{}` filter
- [x] JSON pipeline with `json` codec
- [x] Date parsing
- [x] Mutate filters (convert, add_field, add_tag)
- [x] GeoIP enrichment
- [x] Output to Elasticsearch

### ✅ Kibana
- [x] Index pattern configuration
- [x] 3 visualizations (Revenue, Products, Countries)
- [x] Complete dashboard
- [x] Dashboard export

---

## 🚀 Quick Start Commands

```powershell
# Setup everything at once
.\elasticsearch\setup-elasticsearch.ps1
Start-Sleep -Seconds 10
.\logstash\test-pipelines.ps1
Start-Sleep -Seconds 10
.\kibana\setup-kibana.ps1

# Or use individual scripts as needed
```

---

## 🔗 Access URLs

| Service | URL |
|---------|-----|
| **Kibana Dashboard** | http://localhost:5601/app/dashboards#/view/ecommerce-dashboard |
| **Kibana Discover** | http://localhost:5601/app/discover |
| **Kibana DevTools** | http://localhost:5601/app/dev_tools#/console |
| **Elasticsearch** | http://localhost:9200 |
| **Logstash Monitoring** | http://localhost:9600 |
| **Flask Web App** | http://localhost:8000 |

---

## 📝 DevTools Examples

Use these in Kibana DevTools (http://localhost:5601/app/dev_tools#/console):

```json
# Get all indices
GET /_cat/indices/ecommerce-*?v

# View index mapping
GET /ecommerce-logs-2025.12.21/_mapping

# Search for high-value orders
GET /ecommerce-logs-*/_search
{
  "query": {
    "range": {
      "total_amount": {
        "gte": 500
      }
    }
  }
}

# Get orders by country
GET /ecommerce-logs-*/_search
{
  "size": 0,
  "aggs": {
    "by_country": {
      "terms": {
        "field": "customer_country",
        "size": 10
      }
    }
  }
}
```

---

## 🎉 Configuration Complete!

All ELK stack components are configured and ready to use. You can now:

1. ✅ View the dashboard at http://localhost:5601/app/dashboards
2. ✅ Explore data in Discover
3. ✅ Query data via DevTools
4. ✅ Add more visualizations
5. ✅ Ingest new data through Logstash pipelines

**Status**: All systems operational! 🚀
