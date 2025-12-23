# 🚀 Backend API Documentation

## Vue d'ensemble

Backend Flask avec API REST complète pour l'application e-commerce. Intégration avec Elasticsearch, MongoDB et Redis.

**Base URL**: `http://localhost:8000`

---

## ✅ Routes API Implémentées

### 1. POST `/api/upload`

Upload de fichiers CSV ou JSON et indexation automatique dans Elasticsearch.

**Méthode**: `POST`  
**Content-Type**: `multipart/form-data`  
**Formats acceptés**: `.csv`, `.json`  
**Taille max**: 16MB

**Paramètres**:
- `file` (FormData) - Fichier CSV ou JSON

**Exemple avec cURL**:
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@data/ecommerce-orders.csv"
```

**Exemple avec PowerShell**:
```powershell
$file = Get-Item ".\data\ecommerce-orders.csv"
$boundary = [System.Guid]::NewGuid().ToString()
$fileBytes = [System.IO.File]::ReadAllBytes($file.FullName)
$fileEnc = [System.Text.Encoding]::GetEncoding('iso-8859-1').GetString($fileBytes)

$bodyLines = @(
    "--$boundary",
    "Content-Disposition: form-data; name=`"file`"; filename=`"$($file.Name)`"",
    "Content-Type: text/csv",
    "",
    $fileEnc,
    "--$boundary--"
) -join "`r`n"

Invoke-RestMethod -Uri "http://localhost:8000/api/upload" `
    -Method POST `
    -ContentType "multipart/form-data; boundary=$boundary" `
    -Body $bodyLines
```

**Réponse (201)**:
```json
{
  "message": "File uploaded and indexed successfully",
  "filename": "20251221_141630_orders.csv",
  "documents_indexed": 20,
  "file_type": "csv"
}
```

**Fonctionnalités**:
- ✅ Validation du format de fichier
- ✅ Nom de fichier unique avec timestamp
- ✅ Indexation automatique dans Elasticsearch
- ✅ Sauvegarde dans MongoDB
- ✅ Métadonnées dans Redis (cache 24h)
- ✅ Ajout automatique de @timestamp

---

### 2. GET `/api/search`

Recherche dans Elasticsearch avec filtres et pagination.

**Méthode**: `GET`

**Paramètres (Query)**:
- `q` (string) - Texte de recherche
- `field` (string, optional) - Champ spécifique pour la recherche
- `index` (string, optional) - Index cible (défaut: `ecommerce-logs-*`)
- `size` (int, optional) - Nombre de résultats (défaut: 10)
- `from` (int, optional) - Offset pour pagination (défaut: 0)

**Exemples**:

```bash
# Recherche générale
curl "http://localhost:8000/api/search?q=laptop&size=5"

# Recherche dans un champ spécifique
curl "http://localhost:8000/api/search?q=France&field=customer_country"

# Récupérer tous les documents (sans query)
curl "http://localhost:8000/api/search?size=10"

# Pagination
curl "http://localhost:8000/api/search?q=electronics&size=10&from=10"
```

**Réponse (200)**:
```json
{
  "total": 464,
  "count": 5,
  "query": "laptop",
  "results": [
    {
      "order_id": "ORD-10001",
      "customer_name": "John Doe",
      "product_name": "Laptop HP ProBook",
      "total_amount": 899.99,
      "@timestamp": "2025-12-21T10:15:30Z",
      ...
    }
  ]
}
```

**Champs recherchés (multi-match)**:
- `product_name`
- `product_category`
- `customer_name`
- `customer_country`
- `customer_city`
- `order_id`
- `event_type`

---

### 3. GET `/api/results`

Analyse et agrégations complètes des données e-commerce.

**Méthode**: `GET`

**Paramètres (Query)**:
- `index` (string, optional) - Index cible (défaut: `ecommerce-logs-*`)

**Exemple**:
```bash
curl "http://localhost:8000/api/results"
```

**Réponse (200)**:
```json
{
  "summary": {
    "total_revenue": 7971.44,
    "total_orders": 38,
    "avg_order_value": 209.77,
    "unique_customers": 18
  },
  "by_country": [
    {
      "country": "France",
      "orders": 10,
      "revenue": 3959.88
    }
  ],
  "top_products": [
    {
      "product": "Laptop HP ProBook",
      "orders": 4,
      "revenue": 3599.96,
      "quantity": 4
    }
  ],
  "by_category": [
    {
      "category": "Electronics",
      "count": 15
    }
  ],
  "over_time": [
    {
      "timestamp": "2025-12-21T10:00:00.000Z",
      "orders": 5,
      "revenue": 1234.56
    }
  ],
  "payment_methods": [
    {
      "method": "Credit Card",
      "count": 20
    }
  ],
  "order_status": [
    {
      "status": "completed",
      "count": 30
    }
  ]
}
```

**Agrégations fournies**:
- ✅ Résumé (revenue, commandes, clients)
- ✅ Ventes par pays avec revenue
- ✅ Top 10 produits par revenue
- ✅ Distribution par catégorie
- ✅ Évolution temporelle (par heure)
- ✅ Méthodes de paiement
- ✅ Statuts des commandes

---

### 4. GET `/api/files`

Liste tous les fichiers uploadés avec métadonnées.

**Méthode**: `GET`

**Exemple**:
```bash
curl "http://localhost:8000/api/files"
```

**Réponse (200)**:
```json
{
  "count": 3,
  "files": [
    {
      "filename": "20251221_141630_orders.csv",
      "original_name": "orders.csv",
      "uploaded_at": "2025-12-21T14:16:30Z",
      "size": 3754,
      "type": "csv",
      "documents_count": 20
    },
    {
      "filename": "20251221_140000_events.json",
      "size": 6947,
      "type": "json",
      "modified": "2025-12-21T14:00:00Z"
    }
  ]
}
```

**Informations fournies**:
- Nom du fichier (unique avec timestamp)
- Nom original
- Date d'upload
- Taille (bytes)
- Type (csv/json)
- Nombre de documents indexés

**Source des données**:
- Métadonnées complètes depuis Redis (si disponible)
- Informations du système de fichiers (fallback)

---

### 5. GET `/api/stats`

Statistiques système et métriques de santé.

**Méthode**: `GET`

**Exemple**:
```bash
curl "http://localhost:8000/api/stats"
```

**Réponse (200)**:
```json
{
  "timestamp": "2025-12-21T14:16:30Z",
  "services": {
    "elasticsearch": "connected",
    "mongodb": "connected",
    "redis": "connected"
  },
  "data": {
    "elasticsearch": {
      "total_documents": 464,
      "total_indices": 1,
      "indices": [
        {
          "name": "ecommerce-logs-2025.12.21",
          "documents": 464,
          "size": "145kb"
        }
      ]
    },
    "mongodb": {
      "products_count": 5,
      "uploads_count": 21,
      "collections": ["products", "uploads"]
    },
    "redis": {
      "connected_clients": 2,
      "used_memory": "1.2M",
      "total_keys": 15
    },
    "filesystem": {
      "upload_folder": "/app/uploads",
      "total_files": 3,
      "total_size_bytes": 15234,
      "total_size_mb": 0.01
    }
  }
}
```

**Métriques surveillées**:
- ✅ État des services (Elasticsearch, MongoDB, Redis)
- ✅ Statistiques Elasticsearch (docs, indices, taille)
- ✅ Collections MongoDB avec comptages
- ✅ Métriques Redis (mémoire, connexions, clés)
- ✅ Espace disque (fichiers uploadés)

---

## 🔧 Routes Existantes (Conservées)

### GET `/`
Page d'accueil avec statut système.

**Réponse**:
```json
{
  "message": "E-commerce Flask Application",
  "status": "running",
  "timestamp": "2025-12-21T14:16:30Z",
  "services": {
    "mongodb": "connected",
    "redis": "connected",
    "elasticsearch": "connected"
  }
}
```

### GET `/health`
Health check endpoint.

### GET `/api/products`
Liste des produits MongoDB.

### POST `/api/products`
Créer un produit.

### GET `/api/cache/<key>`
Récupérer du cache Redis.

### POST `/api/cache/<key>`
Sauvegarder dans le cache.

---

## 📦 Configuration Docker

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "app.py"]
```

### docker-compose.yml (extrait)

```yaml
webapp:
  build:
    context: ./webapp
    dockerfile: Dockerfile
  container_name: flask_webapp
  ports:
    - "8000:8000"
  environment:
    - FLASK_APP=app.py
    - MONGODB_URI=mongodb://admin:admin123@mongodb:27017/ecommerce?authSource=admin
    - REDIS_HOST=redis
    - ELASTICSEARCH_HOST=http://elasticsearch:9200
    - UPLOAD_FOLDER=/app/uploads
  volumes:
    - ./webapp:/app
    - webapp_uploads:/app/uploads
  depends_on:
    - mongodb
    - redis
    - elasticsearch
```

---

## 🧪 Tests

### Script de test automatique

```powershell
.\test-backend-api.ps1
```

Tests tous les endpoints et affiche les résultats.

### Tests manuels

```bash
# Test upload
curl -X POST http://localhost:8000/api/upload \
  -F "file=@data/ecommerce-orders.csv"

# Test search
curl "http://localhost:8000/api/search?q=laptop&size=3"

# Test results
curl "http://localhost:8000/api/results"

# Test files list
curl "http://localhost:8000/api/files"

# Test stats
curl "http://localhost:8000/api/stats"
```

---

## 📊 Formats de données acceptés

### CSV
```csv
timestamp,order_id,customer_name,product_name,quantity,unit_price,total_amount
2025-12-21 10:00:00,ORD-001,John Doe,Laptop,1,899.99,899.99
```

### JSON (objet unique)
```json
{
  "timestamp": "2025-12-21T10:00:00Z",
  "order_id": "ORD-001",
  "customer_name": "John Doe",
  "product_name": "Laptop",
  "quantity": 1,
  "unit_price": 899.99,
  "total_amount": 899.99
}
```

### JSON (array)
```json
[
  {
    "timestamp": "2025-12-21T10:00:00Z",
    "order_id": "ORD-001",
    ...
  },
  {
    "timestamp": "2025-12-21T11:00:00Z",
    "order_id": "ORD-002",
    ...
  }
]
```

---

## 🔒 Sécurité & Limites

- **Taille max fichier**: 16MB
- **Types autorisés**: CSV, JSON uniquement
- **CORS**: Activé pour tous les domaines (à restreindre en production)
- **Validation**: Noms de fichiers sécurisés (secure_filename)
- **Cache Redis**: Expiration automatique après 24h

---

## 🐛 Gestion des erreurs

Toutes les routes renvoient des codes HTTP appropriés:

- **200**: Succès
- **201**: Créé (upload réussi)
- **400**: Requête invalide
- **404**: Ressource non trouvée
- **500**: Erreur serveur

Format des erreurs:
```json
{
  "error": "Description de l'erreur"
}
```

---

## ✅ Checklist Backend

- [x] Projet Flask créé
- [x] Dockerfile configuré
- [x] Intégration dans docker-compose
- [x] Route POST `/api/upload`
- [x] Route GET `/api/search`
- [x] Route GET `/api/results`
- [x] Route GET `/api/files`
- [x] Route GET `/api/stats`
- [x] Tests automatisés
- [x] Documentation complète

---

## 🚀 Démarrage

```bash
# Rebuild et démarrer
docker-compose up -d --build webapp

# Voir les logs
docker-compose logs -f webapp

# Tester l'API
.\test-backend-api.ps1
```

---

## 📞 Support

**URL API**: http://localhost:8000  
**Health Check**: http://localhost:8000/health  
**API Docs**: Ce fichier

Tous les endpoints sont testés et fonctionnels! 🎉
