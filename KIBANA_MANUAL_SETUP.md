# Guide de Configuration Manuelle

## 🎯 Configuration 



## Étape 1: Vérifier l'Index Pattern ✅

1. Ouvrez Kibana: http://localhost:5601
2. Allez dans **☰ Menu → Stack Management → Index Patterns**
3. Vérifiez que `ecommerce-logs-*` existe
4. Si non, cliquez sur **Create index pattern** et entrez:
   - Index pattern: `ecommerce-logs-*`
   - Time field: `@timestamp`
   - Cliquez sur **Create**

---

## Étape 2: Créer les Visualisations

### Visualisation 1: Total Revenue (Métrique)

1. Allez dans **☰ Menu → Visualize Library**
2. Cliquez sur **Create visualization**
3. Sélectionnez **Lens**
4. Configuration:
   - Index pattern: `ecommerce-logs-*`
   - Glissez le champ **total_amount** dans la zone centrale
   - Dans le panneau de droite, changez la fonction en **Sum**
   - Titre: "Total Revenue"
5. Cliquez sur **Save** → Nom: "Total Revenue"

### Visualisation 2: Orders by Country (Camembert)

1. **Create visualization** → **Lens**
2. Configuration:
   - Glissez **customer_country** dans la zone centrale
   - Glissez **Count** pour la métrique
   - En haut, cliquez sur **Bar vertical** et changez en **Pie**
   - Titre: "Orders by Country"
3. **Save** → Nom: "Orders by Country"

### Visualisation 3: Top Products (Barres)

1. **Create visualization** → **Lens**
2. Configuration:
   - Axe horizontal: Glissez **product_name.keyword**
   - Axe vertical: Glissez **total_amount** et changez en **Sum**
   - Dans les paramètres de product_name:
     - Cliquez sur le champ → **Advanced**
     - Number of values: 10
     - Ranked by: Sum of total_amount
   - En haut, sélectionnez **Bar horizontal**
   - Titre: "Top 10 Products by Revenue"
3. **Save** → Nom: "Top Products"

---

## Étape 3: Créer le Dashboard

1. Allez dans **☰ Menu → Dashboard**
2. Cliquez sur **Create dashboard**
3. Cliquez sur **Add from library**
4. Sélectionnez vos 3 visualisations:
   - Total Revenue
   - Orders by Country
   - Top Products
5. Arrangez-les comme vous voulez (glisser-déposer)
6. **Save** → Nom: "E-commerce Analytics Dashboard"

---

## Étape 4: Alternative Rapide - Discover

Si vous voulez juste explorer les données immédiatement:

1. Allez dans **☰ Menu → Discover**
2. Sélectionnez l'index pattern `ecommerce-logs-*`
3. Vous verrez toutes vos données avec:
   - Graphique temporel en haut
   - Liste des documents en bas
   - Filtres à gauche

### Requêtes utiles dans Discover:

```
# Commandes > 500 EUR
total_amount > 500

# Commandes en France
customer_country: "France"

# Produits électroniques
product_category: "Electronics"

# Combinaison
customer_country: "France" AND total_amount > 200
```

---

## 🚀 Accès Rapide

- **Discover**: http://localhost:5601/app/discover
- **Dashboard**: http://localhost:5601/app/dashboards
- **Visualizations**: http://localhost:5601/app/visualize
- **DevTools**: http://localhost:5601/app/dev_tools#/console

---

## 📊 Exemples de Requêtes DevTools

Ouvrez DevTools et testez ces requêtes:

```json
# Revenu total par pays
GET /ecommerce-logs-*/_search
{
  "size": 0,
  "aggs": {
    "by_country": {
      "terms": {
        "field": "customer_country",
        "size": 10
      },
      "aggs": {
        "total_revenue": {
          "sum": {
            "field": "total_amount"
          }
        }
      }
    }
  }
}

# Top 10 produits
GET /ecommerce-logs-*/_search
{
  "size": 0,
  "aggs": {
    "top_products": {
      "terms": {
        "field": "product_name.keyword",
        "size": 10,
        "order": {
          "total_revenue": "desc"
        }
      },
      "aggs": {
        "total_revenue": {
          "sum": {
            "field": "total_amount"
          }
        }
      }
    }
  }
}

# Statistiques de revenue
GET /ecommerce-logs-*/_search
{
  "size": 0,
  "aggs": {
    "revenue_stats": {
      "stats": {
        "field": "total_amount"
      }
    }
  }
}
```

---

## ✅ Vérification

Pour vérifier que tout fonctionne:

```powershell
# Compter les documents
curl http://localhost:9200/ecommerce-logs-*/_count

# Voir les données
curl "http://localhost:9200/ecommerce-logs-*/_search?size=5&pretty"
```

---

## 🎨 Tips pour de Belles Visualisations

1. **Couleurs**: Dans chaque viz, cliquez sur ⚙️ → Color by terms
2. **Format**: Double-cliquez sur les nombres pour formater (€, %, etc.)
3. **Filtres**: Ajoutez des filtres temporels en haut
4. **Refresh**: Configurez l'auto-refresh (en haut à droite)

---

## 📝 Données Disponibles

Vos données incluent:
- **464+ documents** d'e-commerce
- **38 commandes** uniques
- **8 pays** différents
- **Total: 7,971.44 EUR** de revenue
- Période: 21 décembre 2025

Bonne exploration! 🚀
