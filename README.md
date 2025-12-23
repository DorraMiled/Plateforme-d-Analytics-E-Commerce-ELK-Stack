# Mini-Projet E-Commerce - Gestion des Logs

Application de gestion et analyse de logs avec Angular Material UI + Flask + ELK Stack.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          UTILISATEUR                            │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                    ┌───────────▼──────────┐
                    │   ANGULAR FRONTEND   │
                    │  (Material UI 17.0)  │
                    │   Port 4200/80       │
                    └───────────┬──────────┘
                                │ HTTP/REST
                    ┌───────────▼──────────┐
                    │    FLASK API         │
                    │   (Python 3.9)       │
                    │   Port 8000          │
                    └─────┬─────┬─────┬────┘
                          │     │     │
         ┌────────────────┘     │     └────────────────┐
         │                      │                      │
    ┌────▼─────┐         ┌─────▼──────┐        ┌──────▼──────┐
    │ ELASTIC  │         │  MONGODB   │        │    REDIS    │
    │  SEARCH  │         │ (Métadon.) │        │   (Cache)   │
    │  (Logs)  │         │ (Fichiers) │        │             │
    └──────────┘         └────────────┘        └─────────────┘
```

### Stack Technique

- **Elasticsearch** : Moteur de recherche et analyse de logs
- **Logstash** : Pipeline d'ingestion de données
- **Kibana** : Visualisation avancée des données
- **MongoDB** : Base NoSQL pour métadonnées fichiers
- **Redis** : Cache en mémoire
- **Flask** : API REST Python
- **Angular 17** : Frontend avec Material UI

## 🚀 Démarrage rapide

### Prérequis
- Docker Desktop installé
- Docker Compose

### Lancement des services

```bash
docker-compose up -d
```

### Arrêt des services

```bash
docker-compose down
```

### Arrêt et suppression des volumes

```bash
docker-compose down -v
```

## 🌐 Accès aux services

| Service | URL | Description |
|---------|-----|-------------|
| **Angular Frontend** | http://localhost:4200 | Interface utilisateur Material UI |
| **Kibana** | http://localhost:5601 | Visualisation Elasticsearch |
| **Elasticsearch** | http://localhost:9200 | API Elasticsearch |
| **Flask API** | http://localhost:8000 | API REST Backend |
| **MongoDB** | mongodb://localhost:27017 | Base de données |
| **Redis** | redis://localhost:6379 | Cache |
| **Logstash** | TCP: 5000, HTTP: 9600 | Pipeline de données |

## 🎨 Composants Angular Material UI

### Dashboard
- **KPI Cards** : MatCard avec MatIcon (total logs, logs today, errors, files)
- **Chart.js** : Bar chart (logs by level), Line chart (temporal evolution)
- **Recent Logs** : MatTable avec 4 colonnes

### Upload
- **Drag & Drop Zone** : Custom directive avec CSS animations
- **File Input** : Hidden input avec Material styling
- **Progress Bar** : MatProgressBar linéaire
- **Validation** : MatSnackBar pour erreurs/succès
- **Recent Uploads** : MatTable avec file icons

### Search
- **Search Bar** : MatFormField avec mat-input
- **Filters** : MatSelect (log level, service)
- **Date Pickers** : MatDatepicker avec MatNativeDateModule
- **Recent Searches** : MatChip clickable
- **Buttons** : MatButton raised/stroked

### Results
- **Results Table** : MatTable avec MatPaginator et MatSort
- **Status Badges** : Spans color-coded (DEBUG/INFO/WARNING/ERROR/CRITICAL)
- **Export CSV** : MatButton téléchargeant Blob
- **View Details** : MatIconButton ouvrant MatSnackBar
- **Pagination** : 50/page, options [10, 25, 50, 100]

### Files
- **Files List** : MatTable avec file metadata
- **File Icons** : MatIcon (table_chart, code, description)
- **No Files State** : MatCard centré avec bouton CTA

## 🛠️ Développement Frontend

### Installation
```bash
cd frontend
npm install
```

### Démarrage
```bash
npm start
# → http://localhost:4200
```

### Build Production
```bash
npm run build
# → dist/frontend/browser/
```

### Technologies Frontend
- **Angular 17** : Standalone components, Signals
- **Material UI** : Composants Material Design
- **Chart.js 4** : Visualisations de données
- **RxJS 7** : Programmation réactive
- **TypeScript 5** : Type safety

## 📱 Design Responsive

- **Desktop** : 1920x1080+ (4-column grid, sidenav side mode)
- **Tablet** : 768-1024px (2-column grid, sidenav over mode)
- **Mobile** : < 768px (1-column grid, hamburger menu)

Breakpoints :
```scss
@media (max-width: 768px) { /* Mobile */ }
@media (min-width: 769px) and (max-width: 1024px) { /* Tablet */ }
@media (min-width: 1025px) { /* Desktop */ }
```

## � Flux de Données

### 1. Upload de Fichiers
```
User → [Drag & Drop] → Angular Upload Component
   ↓ FormData (multipart/form-data)
Flask API → Validation (100MB max, CSV/JSON/TXT)
   ↓ Parse & Transform
Logstash → Bulk Index
   ↓ Index logs-*
Elasticsearch ← Store logs
MongoDB ← Save file metadata
```

### 2. Recherche de Logs
```
User → [Filters: text, level, service, dates] → Angular Search Component
   ↓ HTTP POST /api/search
Flask API → Build Elasticsearch Query DSL
   ↓ {query: {bool: {must: [...]}}}
Elasticsearch → Execute search
   ↓ {hits: [...], total: 1234}
Angular Results Component ← Display Material Table
   ↓ Pagination (50/page), Sort, Export CSV
```

### 3. Dashboard en Temps Réel
```
Angular Dashboard Component → HTTP GET /api/dashboard
   ↓
Flask API → Elasticsearch Aggregations
   ↓ Sum, Cardinality, Date Histogram
Chart.js ← Render graphs (Bar, Line)
Material Cards ← Display KPIs
Auto-refresh every 30s
```

## 📡 API Endpoints

### Statistiques
- `GET /api/stats` - Statut Elasticsearch/MongoDB/Redis
- `GET /api/dashboard` - KPIs et données pour graphiques

### Upload
- `POST /api/upload` - Upload fichier (FormData)
  - Validation : 100MB max, CSV/JSON/TXT
  - Response : `{filename, documents_indexed, file_size}`

### Recherche
- `POST /api/search` - Recherche avec filtres
  - Body : `{query, level, service, start_date, end_date, size, from}`
  - Response : `{total, hits: [...], took}`
- `GET /api/export/csv` - Export résultats CSV
- `POST /api/searches` - Sauvegarder recherche MongoDB
- `GET /api/searches/recent?limit=10` - Récupérer recherches récentes

### Fichiers
- `GET /api/files` - Liste fichiers uploadés
- `GET /api/logs/:id` - Détails d'un log

### Monitoring
- `GET /health` - Health check

## 🔍 Vérification des services

### Backend (déjà configuré)
```bash
cd miniprojetEcommerce
docker-compose up -d
```

### Frontend Angular
```bash
# Option 1: Développement
cd frontend
npm install
npm start  # → http://localhost:4200

# Option 2: Docker
cd frontend
docker build -t angular-frontend .
docker run -p 4200:80 angular-frontend
```

### Vérifier Elasticsearch
```bash
curl http://localhost:9200
```

### Vérifier MongoDB
```bash
docker exec -it mongodb mongosh -u admin -p admin123
```

### Vérifier Redis
```bash
docker exec -it redis redis-cli ping
```

### Voir les logs
```bash
# Tous les services
docker-compose logs -f

# Un service spécifique
docker-compose logs -f webapp
docker-compose logs -f elasticsearch
```

## 📊 Configuration Kibana

1. Accéder à Kibana : http://localhost:5601
2. Aller dans "Management" → "Stack Management"
3. Créer un index pattern pour `logs-*`
4. Explorer les données dans "Discover"

## 🎓 Contexte Académique

**Projet** : Mini-Projet Big Data  
**Matière** : Traitement et Analyse de Données Massives  
**Niveau** : 3ème année  
**Technologies** : Angular 17, Flask, Elasticsearch, MongoDB, Redis, Chart.js

## 📝 Licence

Projet académique - Usage éducatif uniquement

```
miniprojetEcommerce/
├── docker-compose.yml          # Configuration Docker
├── webapp/                     # Application Flask
│   ├── app.py                 # Code principal
│   ├── requirements.txt       # Dépendances Python
│   └── Dockerfile            # Image Docker Flask
├── logstash/
│   ├── config/
│   │   └── logstash.yml      # Config Logstash
│   └── pipeline/
│       └── logstash.conf     # Pipeline de traitement
└── README.md                  # Ce fichier
```

## 📝 Identifiants par défaut

- **MongoDB** : admin / admin123
- **Elasticsearch** : Pas d'authentification (mode dev)
- **Kibana** : Pas d'authentification (mode dev)

## ⚠️ Note

Cette configuration est pour le développement. En production, il faut :
- Activer l'authentification sur tous les services
- Utiliser des secrets sécurisés
- Configurer les limites de ressources
- Mettre en place des sauvegardes
