# 🎨 Frontend - Application Angular 17

Interface utilisateur moderne pour la plateforme d'analytics e-commerce avec visualisation de logs en temps réel.

## 📋 Table des matières

- [Technologies](#technologies)
- [Architecture](#architecture)
- [Composants](#composants)
- [Installation](#installation)
- [Développement](#développement)
- [Build](#build)
- [Structure](#structure)

## 🛠️ Technologies

- **Framework**: Angular 17.x (Standalone Components)
- **UI Library**: Angular Material 17
- **Charts**: Chart.js + ng2-charts
- **HTTP**: RxJS + HttpClient
- **Styling**: SCSS + Material Theming
- **Build**: Angular CLI + Webpack

## 🏗️ Architecture

```
frontend/
├── src/
│   ├── app/
│   │   ├── components/          # Composants Angular
│   │   ├── services/            # Services (API, Auth)
│   │   ├── models/              # Interfaces TypeScript
│   │   └── app.component.ts     # Composant racine
│   ├── assets/                  # Images, fonts, etc.
│   └── styles.scss              # Styles globaux
├── angular.json                 # Configuration Angular
├── package.json                 # Dépendances NPM
└── tsconfig.json               # Configuration TypeScript
```

## 📦 Composants

### 1. **App Component** (`app.component.ts`)
**Rôle**: Shell principal de l'application

**Fonctionnalités**:
- Navigation sidebar responsive
- Toolbar avec dégradé moderne
- Footer à 3 colonnes
- Breakpoint observer pour mobile
- Routing principal

**Routes**:
- `/` → Dashboard
- `/upload` → Upload de fichiers
- `/search` → Recherche avancée
- `/results` → Résultats de recherche
- `/files` → Gestion des fichiers

---

### 2. **Dashboard Component** (`dashboard.component.ts`)
**Rôle**: Vue d'ensemble des métriques en temps réel

**Fonctionnalités**:
- ✅ 4 Cartes KPI animées (total logs, logs du jour, erreurs, fichiers)
- ✅ Bar Chart: Distribution par niveau
- ✅ Line Chart: Évolution temporelle
- ✅ Tableau des logs récents (10 derniers)
- ✅ Actions rapides (4 cards cliquables)
- ✅ Auto-refresh toutes les 30s

**Services utilisés**: `ApiService`

**Dépendances**: Chart.js, Material Cards, Material Tables

---

### 3. **Upload Component** (`upload.component.ts`)
**Rôle**: Upload et indexation de fichiers de logs

**Fonctionnalités**:
- ✅ Drag & Drop avec animations (pulse, bounce)
- ✅ Validation (CSV/JSON/TXT, max 100MB)
- ✅ Barre de progression en temps réel
- ✅ 3 cartes statistiques (fichiers, documents, taille)
- ✅ Liste des fichiers uploadés avec actions
- ✅ Card d'instructions avec formats supportés
- ✅ Indexation automatique dans Elasticsearch

**API Endpoints**:
- `POST /api/upload` - Upload fichier
- `GET /api/files` - Liste fichiers

---

### 4. **Search Component** (`search.component.ts`)
**Rôle**: Recherche avancée dans les logs

**Fonctionnalités**:
- ✅ Full-text search sur tous les champs
- ✅ Filtres: niveau, service, date début/fin
- ✅ Chips de sélection rapide
- ✅ Validation des dates
- ✅ Sauvegarde des recherches
- ✅ Design moderne avec header dégradé

**Filtres disponibles**:
- **Niveaux**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Services**: user-service, order-service, payment-service, product-service

**API Endpoint**: `POST /api/search`

---

### 5. **Results Component** (`results.component.ts`)
**Rôle**: Affichage des résultats de recherche

**Fonctionnalités**:
- ✅ Tableau Material avec pagination
- ✅ Tri multi-colonnes
- ✅ Export CSV avec filtres
- ✅ Compteur de résultats
- ✅ Badges colorés par niveau
- ✅ Hover effects

**Colonnes**:
- Timestamp (format dd/MM/yyyy HH:mm)
- Niveau (badge coloré)
- Service
- Message
- User

**API Endpoints**:
- `POST /api/search` - Recherche
- `GET /api/export/csv` - Export CSV

---

### 6. **Files Component** (`files.component.ts`)
**Rôle**: Gestion des fichiers uploadés

**Fonctionnalités**:
- ✅ 3 cartes statistiques (fichiers totaux, taille, types)
- ✅ Tableau avec métadonnées complètes
- ✅ Icônes dynamiques par type
- ✅ Badges de type MIME
- ✅ Empty state design
- ✅ Bouton actualiser

**API Endpoint**: `GET /api/files`

---

## 🎨 Design System

### Palette de couleurs
```scss
--primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
--secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
--success-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
```

### Animations
- `fadeInUp`: Entrée de pages
- `shimmer`: Effet de brillance
- `pulse`: Pulsation
- `bounce`: Rebond

### Responsive Breakpoints
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

---

## 🚀 Installation

### Prérequis
- Node.js 18.x ou supérieur
- npm 9.x ou supérieur
- Angular CLI 17.x

### Installation des dépendances
```bash
cd frontend
npm install
```

### Variables d'environnement
Créer `src/environments/environment.ts`:
```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api'
};
```

---

## 💻 Développement

### Démarrer le serveur de développement
```bash
npm start
# ou
ng serve
```

Application disponible sur: `http://localhost:4200`

### Compilation en mode watch
```bash
ng serve --watch
```

### Linter
```bash
ng lint
```

---

## 🏗️ Build

### Build de production
```bash
npm run build
# ou
ng build --configuration production
```

Sortie dans `dist/frontend/`

### Build avec optimisations
```bash
ng build --prod --aot --build-optimizer
```

### Servir le build
```bash
npx http-server dist/frontend -p 8080
```

---

## 📁 Structure détaillée

```
frontend/
├── src/
│   ├── app/
│   │   ├── components/
│   │   │   ├── dashboard/
│   │   │   │   ├── dashboard.component.ts
│   │   │   │   ├── dashboard.component.html
│   │   │   │   └── dashboard.component.scss
│   │   │   ├── upload/
│   │   │   │   ├── upload.component.ts
│   │   │   │   ├── upload.component.html
│   │   │   │   └── upload.component.scss
│   │   │   ├── search/
│   │   │   │   ├── search.component.ts
│   │   │   │   ├── search.component.html
│   │   │   │   └── search.component.scss
│   │   │   ├── results/
│   │   │   │   ├── results.component.ts
│   │   │   │   ├── results.component.html
│   │   │   │   └── results.component.scss
│   │   │   └── files/
│   │   │       ├── files.component.ts
│   │   │       ├── files.component.html
│   │   │       └── files.component.scss
│   │   ├── services/
│   │   │   └── api.service.ts         # Service HTTP principal
│   │   ├── models/
│   │   │   └── log.models.ts          # Interfaces TypeScript
│   │   ├── app.component.ts           # Composant racine
│   │   ├── app.component.html         # Template principal
│   │   └── app.routes.ts              # Configuration routes
│   ├── assets/                        # Ressources statiques
│   ├── styles.scss                    # Styles globaux
│   └── index.html                     # Point d'entrée HTML
├── angular.json                       # Config Angular CLI
├── package.json                       # Dépendances NPM
├── tsconfig.json                      # Config TypeScript
└── README.md                          # Ce fichier
```

---

## 🔧 Services

### ApiService (`api.service.ts`)
Service principal pour toutes les requêtes HTTP.

**Méthodes**:
```typescript
getDashboardStats(): Observable<DashboardStats>
searchLogs(params): Observable<SearchResults>
uploadFile(file: File): Observable<UploadResponse>
getFiles(): Observable<FileInfo[]>
exportCSV(params): Observable<Blob>
```

**Configuration**:
- Base URL: `http://localhost:8000/api`
- Timeout: 30s
- Retry: 3 tentatives

---

## 🎯 Fonctionnalités clés

### 1. Recherche en temps réel
- Debounce sur input (300ms)
- Filtres combinables
- Résultats paginés

### 2. Upload progressif
- Chunked upload pour gros fichiers
- Barre de progression
- Annulation possible

### 3. Visualisations dynamiques
- Chart.js avec animations
- Responsive charts
- Export PNG/PDF

### 4. Cache côté client
- LocalStorage pour préférences
- SessionStorage pour recherches
- IndexedDB pour données volumineuses

---

## 🐛 Debugging

### Activer le mode debug
```typescript
// src/main.ts
enableProdMode(); // Commenter cette ligne
```

### Console logs
```bash
# Logs HTTP
localStorage.setItem('debug', 'http');

# Tous les logs
localStorage.setItem('debug', '*');
```

### Angular DevTools
Installer l'extension Chrome: [Angular DevTools](https://chrome.google.com/webstore/detail/angular-devtools/)

---

## 📊 Performance

### Optimisations implémentées
- ✅ Lazy loading des modules
- ✅ OnPush change detection
- ✅ TrackBy dans ngFor
- ✅ Pipe pure pour transformations
- ✅ Debounce sur inputs
- ✅ Virtual scrolling pour longues listes

### Lighthouse Score (cible)
- Performance: > 90
- Accessibility: > 95
- Best Practices: > 90
- SEO: > 90

---

## 🔐 Sécurité

### Mesures implémentées
- ✅ CORS configuré
- ✅ Sanitization des inputs
- ✅ CSP headers
- ✅ XSS protection
- ✅ CSRF tokens

---

## 📝 Scripts NPM

```json
{
  "start": "ng serve",
  "build": "ng build",
  "watch": "ng build --watch --configuration development",
  "test": "ng test",
  "lint": "ng lint"
}
```

---

## 🤝 Contribution

### Workflow
1. Créer une branche feature
2. Développer + tests
3. Linter + build
4. Pull request
5. Code review
6. Merge

### Conventions
- **Commits**: Conventional Commits
- **Branches**: feature/*, bugfix/*, hotfix/*
- **Code style**: Angular Style Guide

---

## 📞 Support

Pour toute question ou problème:
- 📧 Email: support@ecommerce-analytics.com
- 📖 Documentation: [Wiki du projet]
- 🐛 Issues: [GitHub Issues]

---

**Version**: 1.0.0  
**Dernière mise à jour**: Décembre 2025  
**Auteur**: Équipe E-Commerce Analytics
