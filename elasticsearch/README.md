# 🔍 Elasticsearch - Moteur de recherche et analytics

Configuration et données Elasticsearch pour la plateforme d'analytics e-commerce.

## 📋 Description

Elasticsearch est utilisé comme moteur de recherche principal et pour les analyses en temps réel des logs et données e-commerce.

## 🛠️ Configuration

### Version
- **Elasticsearch**: 8.11.0
- **Port HTTP**: 9200
- **Port Transport**: 9300

### Paramètres Docker
```yaml
elasticsearch:
  image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
  container_name: elasticsearch
  environment:
    - discovery.type=single-node
    - xpack.security.enabled=false
    - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
  ports:
    - "9200:9200"
    - "9300:9300"
  volumes:
    - elasticsearch_data:/usr/share/elasticsearch/data
  networks:
    - elk
```

### Mémoire JVM
- **Heap min**: 512 MB
- **Heap max**: 512 MB
- **Recommandé pour production**: 2-4 GB

## 📊 Indices

### 1. **ecommerce-logs-\***
**Description**: Logs applicatifs et événements système

**Mapping**:
```json
{
  "mappings": {
    "properties": {
      "@timestamp": {"type": "date"},
      "Timestamp": {"type": "date"},
      "Level": {"type": "keyword"},
      "Service": {"type": "keyword"},
      "Message": {"type": "text"},
      "User": {"type": "keyword"},
      "IP": {"type": "ip"},
      "Duration": {"type": "integer"}
    }
  }
}
```

**Pattern de nommage**: `ecommerce-logs-YYYY.MM.DD`

**Documents types**:
- Logs applicatifs (Level, Service, Message)
- Events utilisateurs (event, user, page)
- Logs système (level, source, message)

---

### 2. **ecommerce-orders-\***
**Description**: Commandes e-commerce

**Mapping**:
```json
{
  "mappings": {
    "properties": {
      "@timestamp": {"type": "date"},
      "order_id": {"type": "keyword"},
      "customer_id": {"type": "keyword"},
      "customer_name": {"type": "text"},
      "customer_country": {"type": "keyword"},
      "product_id": {"type": "keyword"},
      "product_name": {"type": "text"},
      "product_category": {"type": "keyword"},
      "quantity": {"type": "integer"},
      "unit_price": {"type": "float"},
      "total_amount": {"type": "float"},
      "payment_method": {"type": "keyword"},
      "order_status": {"type": "keyword"}
    }
  }
}
```

---

### 3. **ecommerce-products-\***
**Description**: Catalogue produits

**Mapping**:
```json
{
  "mappings": {
    "properties": {
      "product_id": {"type": "keyword"},
      "name": {"type": "text"},
      "category": {"type": "keyword"},
      "price": {"type": "float"},
      "stock": {"type": "integer"},
      "description": {"type": "text"}
    }
  }
}
```

---

## 🔍 Queries utiles

### Compter tous les documents
```bash
curl -X GET "http://localhost:9200/ecommerce-logs-*/_count"
```

### Recherche simple
```bash
curl -X GET "http://localhost:9200/ecommerce-logs-*/_search" \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {
      "match": {
        "Level": "ERROR"
      }
    }
  }'
```

### Recherche avec filtres
```bash
curl -X POST "http://localhost:9200/ecommerce-logs-*/_search" \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {
      "bool": {
        "must": [
          {"match": {"Level": "ERROR"}},
          {"match": {"Service": "payment-service"}}
        ],
        "filter": [
          {"range": {"@timestamp": {"gte": "2025-12-01", "lte": "2025-12-31"}}}
        ]
      }
    },
    "size": 100,
    "sort": [{"@timestamp": {"order": "desc"}}]
  }'
```

### Agrégation par niveau
```bash
curl -X POST "http://localhost:9200/ecommerce-logs-*/_search" \
  -H 'Content-Type: application/json' \
  -d '{
    "size": 0,
    "aggs": {
      "by_level": {
        "terms": {
          "field": "Level",
          "size": 10
        }
      }
    }
  }'
```

### Time series (logs par jour)
```bash
curl -X POST "http://localhost:9200/ecommerce-logs-*/_search" \
  -H 'Content-Type: application/json' \
  -d '{
    "size": 0,
    "aggs": {
      "logs_over_time": {
        "date_histogram": {
          "field": "@timestamp",
          "calendar_interval": "day"
        }
      }
    }
  }'
```

---

## 📈 Analytics

### Top services par volume
```json
{
  "size": 0,
  "aggs": {
    "top_services": {
      "terms": {
        "field": "Service",
        "size": 10,
        "order": {"_count": "desc"}
      }
    }
  }
}
```

### Distribution des erreurs
```json
{
  "query": {
    "terms": {"Level": ["ERROR", "CRITICAL"]}
  },
  "size": 0,
  "aggs": {
    "error_by_service": {
      "terms": {"field": "Service"}
    }
  }
}
```

### Statistiques de performance
```json
{
  "size": 0,
  "aggs": {
    "avg_duration": {"avg": {"field": "Duration"}},
    "max_duration": {"max": {"field": "Duration"}},
    "min_duration": {"min": {"field": "Duration"}}
  }
}
```

---

## 🔧 Maintenance

### Voir tous les indices
```bash
curl -X GET "http://localhost:9200/_cat/indices?v"
```

### Voir le mapping
```bash
curl -X GET "http://localhost:9200/ecommerce-logs-*/_mapping"
```

### Voir les settings
```bash
curl -X GET "http://localhost:9200/ecommerce-logs-*/_settings"
```

### Supprimer un index
```bash
curl -X DELETE "http://localhost:9200/ecommerce-logs-2025.12.23"
```

### Supprimer tous les indices ecommerce
```bash
curl -X DELETE "http://localhost:9200/ecommerce-*"
```

### Créer un index avec mapping
```bash
curl -X PUT "http://localhost:9200/ecommerce-logs-2025.12.23" \
  -H 'Content-Type: application/json' \
  -d '{
    "mappings": {
      "properties": {
        "@timestamp": {"type": "date"},
        "Level": {"type": "keyword"},
        "Service": {"type": "keyword"},
        "Message": {"type": "text"}
      }
    }
  }'
```

---

## 🔄 Réindexation

### Réindexer d'un index à un autre
```bash
curl -X POST "http://localhost:9200/_reindex" \
  -H 'Content-Type: application/json' \
  -d '{
    "source": {"index": "ecommerce-logs-old"},
    "dest": {"index": "ecommerce-logs-new"}
  }'
```

### Réindexer avec transformation
```bash
curl -X POST "http://localhost:9200/_reindex" \
  -H 'Content-Type: application/json' \
  -d '{
    "source": {
      "index": "ecommerce-logs-*"
    },
    "dest": {
      "index": "ecommerce-logs-merged"
    },
    "script": {
      "source": "ctx._source.new_field = ctx._source.old_field"
    }
  }'
```

---

## 📊 Monitoring

### Health du cluster
```bash
curl -X GET "http://localhost:9200/_cluster/health?pretty"
```

**Statuts**:
- 🟢 **green**: Tous les shards sont alloués
- 🟡 **yellow**: Tous les primary shards alloués, réplicas manquants
- 🔴 **red**: Certains primary shards non alloués

### Statistiques du cluster
```bash
curl -X GET "http://localhost:9200/_cluster/stats?pretty"
```

### Stats par node
```bash
curl -X GET "http://localhost:9200/_nodes/stats?pretty"
```

### Stats d'indexation
```bash
curl -X GET "http://localhost:9200/_stats/indexing?pretty"
```

---

## 🎯 Optimisations

### Augmenter le refresh interval
```bash
curl -X PUT "http://localhost:9200/ecommerce-logs-*/_settings" \
  -H 'Content-Type: application/json' \
  -d '{
    "index": {
      "refresh_interval": "30s"
    }
  }'
```

### Désactiver les réplicas (single node)
```bash
curl -X PUT "http://localhost:9200/ecommerce-logs-*/_settings" \
  -H 'Content-Type: application/json' \
  -d '{
    "index": {
      "number_of_replicas": 0
    }
  }'
```

### Force merge (compaction)
```bash
curl -X POST "http://localhost:9200/ecommerce-logs-*/_forcemerge?max_num_segments=1"
```

---

## 🗑️ Gestion du lifecycle

### Index Lifecycle Management (ILM)
```json
{
  "policy": {
    "phases": {
      "hot": {
        "actions": {
          "rollover": {
            "max_size": "50GB",
            "max_age": "7d"
          }
        }
      },
      "delete": {
        "min_age": "30d",
        "actions": {
          "delete": {}
        }
      }
    }
  }
}
```

### Créer une policy ILM
```bash
curl -X PUT "http://localhost:9200/_ilm/policy/ecommerce-policy" \
  -H 'Content-Type: application/json' \
  -d @ilm-policy.json
```

---

## 🐛 Troubleshooting

### Logs Elasticsearch
```bash
# Dans le conteneur
docker logs elasticsearch

# Suivre les logs
docker logs -f elasticsearch
```

### Erreurs communes

#### "Unable to create mapping"
**Solution**: Vérifier le mapping et les types de données

#### "Circuit breaker tripped"
**Solution**: Augmenter la mémoire JVM ou réduire la taille des requêtes

#### "Too many open files"
**Solution**: Augmenter les file descriptors
```bash
ulimit -n 65535
```

#### "Disk watermark exceeded"
**Solution**: Libérer de l'espace disque ou supprimer les vieux indices

---

## 📚 Ressources

### Documentation officielle
- [Elasticsearch Guide](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
- [Query DSL](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html)
- [Aggregations](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations.html)

### Outils utiles
- **Cerebro**: Interface web pour gérer Elasticsearch
- **ElasticHQ**: Monitoring et management
- **Elasticvue**: Extension Chrome/Firefox

---

## 🔐 Sécurité

### Désactiver la sécurité (dev only)
```yaml
xpack.security.enabled: false
```

### Activer la sécurité (production)
```yaml
xpack.security.enabled: true
xpack.security.transport.ssl.enabled: true
```

### Créer un utilisateur
```bash
curl -X POST "http://localhost:9200/_security/user/admin" \
  -H 'Content-Type: application/json' \
  -d '{
    "password": "strong_password",
    "roles": ["superuser"]
  }'
```

---

## 🚀 Performance Tips

1. **Bulk indexing**: Utiliser `_bulk` API pour gros volumes
2. **Mapping explicite**: Définir le mapping avant d'indexer
3. **Disable _source**: Si pas besoin du document original
4. **Use filters**: Plus rapides que queries (cachées)
5. **Limit size**: Ne pas récupérer plus que nécessaire
6. **Use scroll**: Pour parcourir de gros résultats

---

**Version**: 8.11.0  
**Dernière mise à jour**: Décembre 2025  
**Documentation**: [ELK_CONFIGURATION.md](../ELK_CONFIGURATION.md)
