# 📊 Kibana - Interface de visualisation

Configuration Kibana pour la plateforme d'analytics e-commerce avec dashboards et visualisations automatisés.

## 📋 Description

Kibana est l'interface de visualisation qui permet d'explorer, analyser et créer des dashboards à partir des données Elasticsearch.

## 🛠️ Configuration

### Version
- **Kibana**: 8.11.0
- **Port**: 5601
- **Elasticsearch URL**: http://elasticsearch:9200

### Paramètres Docker
```yaml
kibana:
  image: docker.elastic.co/kibana/kibana:8.11.0
  container_name: kibana
  environment:
    - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    - SERVER_NAME=kibana
    - XPACK_SECURITY_ENABLED=false
  ports:
    - "5601:5601"
  depends_on:
    - elasticsearch
  networks:
    - elk
```

### Accès
- **URL**: http://localhost:5601
- **Authentication**: Désactivée (dev)
- **Langue**: Anglais (par défaut)

---

## 🎨 Data Views

### ecommerce-logs-*
**Description**: Vue principale pour tous les logs et événements

**Configuration**:
```json
{
  "title": "ecommerce-logs-*",
  "timeFieldName": "@timestamp",
  "sourceFilters": [],
  "fieldFormatMap": {
    "Level": {
      "id": "color",
      "params": {
        "colors": [
          {"range": "DEBUG", "text": "#3f51b5"},
          {"range": "INFO", "text": "#4caf50"},
          {"range": "WARNING", "text": "#ff9800"},
          {"range": "ERROR", "text": "#f44336"},
          {"range": "CRITICAL", "text": "#9c27b0"}
        ]
      }
    }
  }
}
```

**Champs indexés**:
- @timestamp (date)
- Level (keyword)
- Service (keyword)
- Message (text)
- User (keyword)
- IP (ip)
- Duration (integer)

**Création**:
1. Aller dans **Stack Management** > **Data Views**
2. Créer Data View
3. Pattern: `ecommerce-logs-*`
4. Time field: `@timestamp`
5. Sauvegarder

---

## 📈 Visualisations

### 1. **Logs Distribution by Level** (Pie Chart)
**Type**: Pie Chart  
**Objectif**: Répartition des logs par niveau de sévérité

**Configuration**:
```json
{
  "type": "pie",
  "aggs": {
    "buckets": {
      "terms": {
        "field": "Level",
        "size": 10,
        "order": {"_count": "desc"}
      }
    }
  },
  "params": {
    "type": "pie",
    "addTooltip": true,
    "addLegend": true,
    "legendPosition": "right",
    "isDonut": false
  }
}
```

**Metrics**:
- Count (nombre de logs par niveau)

**Buckets**:
- Terms: Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

---

### 2. **Logs Over Time** (Line Chart)
**Type**: Line Chart / Time Series  
**Objectif**: Évolution temporelle des logs

**Configuration**:
```json
{
  "type": "line",
  "aggs": {
    "x-axis": {
      "date_histogram": {
        "field": "@timestamp",
        "calendar_interval": "hour",
        "min_doc_count": 1
      }
    },
    "y-axis": {
      "count": {}
    }
  },
  "params": {
    "type": "line",
    "addTimeMarker": true,
    "addTooltip": true,
    "smoothLines": true
  }
}
```

**Metrics**:
- Count (nombre de logs)

**Buckets**:
- X-Axis: Date Histogram (@timestamp, hourly)

---

### 3. **Top Services** (Bar Chart Horizontal)
**Type**: Horizontal Bar Chart  
**Objectif**: Services les plus actifs

**Configuration**:
```json
{
  "type": "horizontal_bar",
  "aggs": {
    "buckets": {
      "terms": {
        "field": "Service",
        "size": 10,
        "order": {"_count": "desc"}
      }
    }
  },
  "params": {
    "type": "histogram",
    "addTooltip": true,
    "addLegend": false,
    "mode": "stacked"
  }
}
```

**Metrics**:
- Count

**Buckets**:
- Y-Axis: Terms Service (top 10)

---

### 4. **Error Logs Timeline** (Area Chart)
**Type**: Area Chart  
**Objectif**: Tendance des erreurs au fil du temps

**Configuration**:
```json
{
  "type": "area",
  "query": {
    "bool": {
      "filter": [
        {
          "terms": {
            "Level": ["ERROR", "CRITICAL"]
          }
        }
      ]
    }
  },
  "aggs": {
    "x-axis": {
      "date_histogram": {
        "field": "@timestamp",
        "calendar_interval": "hour"
      }
    }
  },
  "params": {
    "type": "area",
    "addTimeMarker": true,
    "smoothLines": true,
    "interpolate": "linear"
  }
}
```

**Filters**:
- Level: ERROR or CRITICAL

**Metrics**:
- Count

**Buckets**:
- X-Axis: Date Histogram (hourly)

---

### 5. **Log Messages Table** (Data Table)
**Type**: Data Table  
**Objectif**: Tableau détaillé des logs récents

**Configuration**:
```json
{
  "type": "table",
  "columns": [
    "@timestamp",
    "Level",
    "Service",
    "Message",
    "User"
  ],
  "sort": [
    ["@timestamp", "desc"]
  ],
  "size": 100
}
```

**Colonnes**:
- @timestamp (formaté)
- Level (badge coloré)
- Service
- Message (tronqué)
- User

**Tri**: Date descendant (plus récents en premier)

---

## 📊 Dashboard Principal

### "ELK E-Commerce Analytics"
**Description**: Dashboard unifié avec toutes les visualisations

**Layout**:
```
┌──────────────────────────────────────────────────────┐
│  Logs Distribution by Level  │  Error Logs Timeline  │
│         (Pie Chart)          │     (Area Chart)      │
├──────────────────────────────────────────────────────┤
│             Logs Over Time (Line Chart)              │
├──────────────────────────────────────────────────────┤
│  Top Services              │  Log Messages Table     │
│  (Bar Chart)               │  (Recent logs)          │
└──────────────────────────────────────────────────────┘
```

**Filtres disponibles**:
- Time range (last 15 minutes, 1 hour, 24 hours, 7 days, 30 days)
- Level (multi-select)
- Service (multi-select)
- User (search)

**Refresh**:
- Auto-refresh: 30 secondes
- Manuel: Bouton refresh

**Création du dashboard**:
```bash
# Via script Python
python create_kibana_visualizations.py

# Ou manuellement dans Kibana
# Dashboard > Create dashboard > Add visualizations
```

---

## 🚀 Utilisation

### Accéder à Kibana
1. Ouvrir navigateur: http://localhost:5601
2. Patienter chargement initial (~30s première fois)
3. Aller dans **Analytics** > **Discover**

### Discover (Exploration)
**Fonctionnalités**:
- Recherche full-text dans tous les champs
- Filtres par champ (Level, Service, etc.)
- Time picker pour sélection période
- Export CSV des résultats
- Sauvegarde des recherches

**Exemples de recherches**:
```
# Recherche simple
Level: ERROR

# Recherche combinée
Level: ERROR AND Service: payment-service

# Recherche par wildcard
Message: *timeout*

# Recherche par range
Duration > 1000
```

### Visualize (Visualisations)
1. Aller dans **Analytics** > **Visualize Library**
2. Voir toutes les visualisations créées
3. Cliquer pour ouvrir/éditer
4. Ajouter au dashboard

### Dashboard
1. Aller dans **Analytics** > **Dashboard**
2. Ouvrir "ELK E-Commerce Analytics"
3. Utiliser les filtres en haut
4. Zoomer sur les graphiques
5. Export PNG/PDF

---

## 🔧 Configuration avancée

### Custom Index Pattern
```json
{
  "title": "ecommerce-*",
  "timeFieldName": "@timestamp",
  "fields": {
    "Level": {
      "count": 0,
      "scripted": false,
      "searchable": true,
      "aggregatable": true,
      "type": "string"
    }
  }
}
```

### Scripted Field
Créer un champ calculé:
```painless
if (doc['Level'].value == 'ERROR' || doc['Level'].value == 'CRITICAL') {
  return 'High Priority';
} else {
  return 'Normal';
}
```

### Advanced Settings
```
# Découvrir plus de hits
discover:sampleSize: 1000

# Format de date
dateFormat: DD/MM/YYYY HH:mm:ss

# Timezone
dateFormat:tz: Europe/Paris
```

---

## 📊 Métriques disponibles

### Aggregations numériques
- **Count**: Nombre de documents
- **Average**: Moyenne d'un champ
- **Sum**: Somme d'un champ
- **Min/Max**: Valeurs min/max
- **Median**: Médiane
- **Percentiles**: 50th, 95th, 99th

### Buckets
- **Terms**: Grouper par valeur
- **Date Histogram**: Grouper par intervalle temps
- **Range**: Grouper par range de valeurs
- **Filters**: Buckets personnalisés avec queries

---

## 🎨 Customisation

### Couleurs par niveau
```javascript
{
  "DEBUG": "#3f51b5",   // Bleu
  "INFO": "#4caf50",    // Vert
  "WARNING": "#ff9800", // Orange
  "ERROR": "#f44336",   // Rouge
  "CRITICAL": "#9c27b0" // Violet
}
```

### Thème sombre
1. Stack Management > Advanced Settings
2. Chercher "theme"
3. Sélectionner "dark"

### Logo personnalisé
```bash
# Remplacer le logo Kibana
docker cp custom-logo.svg kibana:/usr/share/kibana/src/core/server/core_app/assets/
```

---

## 🔍 Queries KQL (Kibana Query Language)

### Syntaxe de base
```kql
# Égalité
Level: ERROR

# OU
Level: ERROR or Level: CRITICAL

# ET
Level: ERROR and Service: payment-service

# NOT
NOT Level: DEBUG

# Wildcard
Message: *timeout*

# Range
Duration > 1000 and Duration < 5000

# Existe
User: *

# N'existe pas
NOT User: *
```

### Exemples avancés
```kql
# Erreurs paiement dernières 24h
Level: ERROR AND Service: payment-service

# Logs lents (> 2s)
Duration > 2000

# Tous sauf DEBUG et INFO
NOT (Level: DEBUG or Level: INFO)

# Messages contenant "failed" ou "error"
Message: (*failed* or *error*)

# Users spécifiques
User: (user123 or user456)
```

---

## 📤 Export

### Export CSV (Discover)
1. Effectuer recherche
2. Cliquer "Share" > "CSV Reports"
3. Générer rapport
4. Télécharger

### Export Dashboard PNG
1. Ouvrir dashboard
2. Cliquer "Share" > "PNG Reports"
3. Générer image
4. Télécharder

### Export Dashboard PDF
1. Ouvrir dashboard
2. Cliquer "Share" > "PDF Reports"
3. Générer PDF
4. Télécharger

---

## 🔔 Alertes (Watcher)

### Créer une alerte
```json
{
  "trigger": {
    "schedule": {
      "interval": "5m"
    }
  },
  "input": {
    "search": {
      "request": {
        "indices": ["ecommerce-logs-*"],
        "body": {
          "query": {
            "bool": {
              "must": [
                {"match": {"Level": "ERROR"}},
                {"range": {"@timestamp": {"gte": "now-5m"}}}
              ]
            }
          }
        }
      }
    }
  },
  "condition": {
    "compare": {
      "ctx.payload.hits.total": {
        "gt": 10
      }
    }
  },
  "actions": {
    "email_admin": {
      "email": {
        "to": "admin@example.com",
        "subject": "High error rate detected",
        "body": "More than 10 errors in last 5 minutes"
      }
    }
  }
}
```

---

## 🐛 Troubleshooting

### Kibana ne démarre pas
```bash
# Vérifier les logs
docker logs kibana

# Vérifier Elasticsearch est up
curl http://localhost:9200

# Redémarrer Kibana
docker restart kibana
```

### Data View non trouvé
```bash
# Vérifier les indices Elasticsearch
curl http://localhost:9200/_cat/indices

# Recréer data view
# Stack Management > Data Views > Create
```

### Visualisation vide
- Vérifier le time range
- Vérifier les filtres appliqués
- Vérifier les données existent dans Elasticsearch
- Rafraîchir les field mappings

---

## 📚 Ressources

### Documentation officielle
- [Kibana Guide](https://www.elastic.co/guide/en/kibana/current/index.html)
- [Visualizations](https://www.elastic.co/guide/en/kibana/current/visualize.html)
- [Dashboards](https://www.elastic.co/guide/en/kibana/current/dashboard.html)
- [KQL](https://www.elastic.co/guide/en/kibana/current/kuery-query.html)

### Tutoriels
- [Getting Started](https://www.elastic.co/guide/en/kibana/current/get-started.html)
- [Creating Visualizations](https://www.elastic.co/guide/en/kibana/current/createvis.html)

---

## 🔐 Sécurité

### Authentification (production)
```yaml
xpack.security.enabled: true
elasticsearch.username: kibana_system
elasticsearch.password: ${KIBANA_PASSWORD}
```

### HTTPS
```yaml
server.ssl.enabled: true
server.ssl.certificate: /path/to/cert.crt
server.ssl.key: /path/to/cert.key
```

---

## 📝 Scripts utiles

### Créer visualisations automatiquement
```bash
python create_kibana_visualizations.py
```

### Setup data view
```bash
python setup_kibana_dataview.py
```

### Backup dashboard
```bash
# Export dashboard
curl -X GET "http://localhost:5601/api/saved_objects/_export" \
  -H 'kbn-xsrf: true' \
  -H 'Content-Type: application/json' \
  -d '{"type": "dashboard"}' \
  > dashboard_backup.ndjson
```

### Restore dashboard
```bash
# Import dashboard
curl -X POST "http://localhost:5601/api/saved_objects/_import" \
  -H 'kbn-xsrf: true' \
  --form file=@dashboard_backup.ndjson
```

---

**Version**: 8.11.0  
**Dernière mise à jour**: Décembre 2025  
**Documentation complète**: [KIBANA_MANUAL_SETUP.md](../KIBANA_MANUAL_SETUP.md)
