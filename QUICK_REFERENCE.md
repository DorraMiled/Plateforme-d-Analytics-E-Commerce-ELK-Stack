# Quick Reference - E-commerce Docker Stack

## Service Status
All services are running and healthy!

## URLs
- **Kibana**: http://localhost:5601
- **Elasticsearch**: http://localhost:9200
- **Flask Web App**: http://localhost:8000
- **MongoDB**: mongodb://admin:admin123@localhost:27017
- **Redis**: redis://localhost:6379

## Docker Commands

### Start all services
```bash
docker-compose up -d
```

### Stop all services
```bash
docker-compose down
```

### View logs
```bash
docker-compose logs -f
docker-compose logs -f webapp
```

### Check status
```bash
docker-compose ps
```

### Restart a specific service
```bash
docker-compose restart webapp
```

## API Examples

### Check Flask app status
```bash
curl http://localhost:8000
```

### Create a product
```powershell
$product = @{
    name = "Laptop"
    price = 899.99
    category = "Electronics"
    description = "High-performance laptop"
    stock = 50
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:8000/api/products `
    -Method POST `
    -Body $product `
    -ContentType "application/json"
```

### Get all products
```bash
curl http://localhost:8000/api/products
```

### Search products
```bash
curl "http://localhost:8000/api/search?q=laptop"
```

### Cache operations
```powershell
# Set cache
$data = @{ value = "John Doe" } | ConvertTo-Json
Invoke-WebRequest -Uri http://localhost:8000/api/cache/user_123 `
    -Method POST `
    -Body $data `
    -ContentType "application/json"

# Get cache
curl http://localhost:8000/api/cache/user_123
```

## Test Script
Run the comprehensive test:
```bash
.\test-api.ps1
```

## Database Access

### MongoDB
```bash
docker exec -it mongodb mongosh -u admin -p admin123
use ecommerce
db.products.find()
```

### Redis
```bash
docker exec -it redis redis-cli
KEYS *
GET user_123
```

### Elasticsearch
```bash
curl http://localhost:9200/_cat/indices?v
curl http://localhost:9200/products/_search
```

## Troubleshooting

### View container logs
```bash
docker-compose logs webapp
```

### Rebuild a service
```bash
docker-compose up -d --build webapp
```

### Reset everything
```bash
docker-compose down -v
docker-compose up -d --build
```

## Project Structure
```
miniprojetEcommerce/
├── docker-compose.yml       # Main orchestration
├── webapp/                  # Flask application
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── logstash/               # Log processing
│   ├── config/
│   │   └── logstash.yml
│   └── pipeline/
│       └── logstash.conf
├── test-api.ps1           # Test script
└── README.md              # Full documentation
```
