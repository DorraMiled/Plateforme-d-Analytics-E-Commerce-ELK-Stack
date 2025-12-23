# 🔧 Guide de Dépannage Docker

## Problème: Elasticsearch démarre puis devient inaccessible

### Causes Fréquentes

1. **Manque de mémoire**
   - Elasticsearch nécessite au moins 1GB de RAM
   - Docker Desktop peut manquer de ressources

2. **Problème de volumes Docker**
   - Les données corrompues dans les volumes peuvent causer des crashs

3. **Conflits de ports**
   - Un autre service utilise déjà les ports 9200, 5601, etc.

### Solutions

#### Solution 1: Augmenter la mémoire Docker Desktop

1. Ouvrir Docker Desktop
2. Aller dans **Settings** → **Resources** → **Advanced**
3. Augmenter la **Memory** à au moins **4 GB** (recommandé: 6 GB)
4. Cliquer sur **Apply & Restart**

#### Solution 2: Nettoyer et redémarrer

```powershell
# Arrêter tous les conteneurs
.\manage-docker.ps1 stop

# Nettoyer les volumes (ATTENTION: supprime les données)
.\manage-docker.ps1 clean

# Redémarrer proprement
.\manage-docker.ps1 start
```

#### Solution 3: Vérifier les logs

```powershell
# Voir les logs d'Elasticsearch
.\manage-docker.ps1 logs elasticsearch

# Chercher les erreurs "OutOfMemoryError" ou "killed"
```

#### Solution 4: Redémarrer uniquement Elasticsearch

```powershell
# Redémarrer le conteneur Elasticsearch
docker restart elasticsearch

# Attendre 30 secondes
Start-Sleep -Seconds 30

# Vérifier qu'il fonctionne
Invoke-RestMethod http://localhost:9200
```

#### Solution 5: Désactiver WSL 2 (si applicable)

Si Docker utilise WSL 2 et a des problèmes:

1. Docker Desktop → Settings → General
2. Décocher **Use the WSL 2 based engine**
3. Apply & Restart

## Commandes de Diagnostic

### Vérifier l'état général
```powershell
.\manage-docker.ps1 status
```

### Vérifier la santé d'Elasticsearch
```powershell
# Santé du cluster
Invoke-RestMethod http://localhost:9200/_cluster/health | ConvertTo-Json

# Statistiques des nœuds
Invoke-RestMethod http://localhost:9200/_nodes/stats | ConvertTo-Json -Depth 3
```

### Vérifier l'utilisation mémoire
```powershell
docker stats --no-stream elasticsearch
```

### Voir les conteneurs en erreur
```powershell
docker ps -a --filter "status=exited"
```

## Prévention des Problèmes

### 1. Configuration Docker Desktop Recommandée

- **Memory**: 6 GB minimum
- **CPUs**: 4 minimum
- **Disk size**: 60 GB minimum

### 2. Redémarrage Périodique

Si vous travaillez longtemps:
```powershell
# Tous les jours ou quand les performances baissent
.\manage-docker.ps1 restart
```

### 3. Surveillance

Vérifier régulièrement:
```powershell
# Tous les 30 minutes
while ($true) {
    Clear-Host
    .\manage-docker.ps1 status
    Start-Sleep -Seconds 1800
}
```

## Erreurs Courantes

### Erreur: "Connection refused"

**Cause**: Le service n'est pas encore démarré

**Solution**:
```powershell
# Attendre que le healthcheck passe
docker ps --format "{{.Names}}: {{.Status}}"

# Vérifier les logs
docker logs elasticsearch --tail 50
```

### Erreur: "max virtual memory areas"

**Cause**: Limite système (Linux/WSL)

**Solution** (WSL 2):
```powershell
# Dans WSL
wsl -d docker-desktop
sysctl -w vm.max_map_count=262144
```

### Erreur: "Port already in use"

**Cause**: Un autre service utilise le port

**Solution**:
```powershell
# Trouver le processus sur le port 9200
Get-NetTCPConnection -LocalPort 9200 | Select-Object OwningProcess

# Arrêter le processus
Stop-Process -Id <PID> -Force
```

## Script de Test Automatique

Créez `test-services.ps1`:

```powershell
$services = @{
    "Elasticsearch" = "http://localhost:9200"
    "Kibana" = "http://localhost:5601/api/status"
}

foreach ($service in $services.GetEnumerator()) {
    try {
        $response = Invoke-RestMethod -Uri $service.Value -TimeoutSec 5
        Write-Host "✓ $($service.Key): OK" -ForegroundColor Green
    } catch {
        Write-Host "✗ $($service.Key): ERREUR" -ForegroundColor Red
        
        # Redémarrer automatiquement
        $containerName = $service.Key.ToLower()
        Write-Host "  Redémarrage de $containerName..." -ForegroundColor Yellow
        docker restart $containerName
    }
}
```

## Support

Si le problème persiste:

1. Vérifier les logs: `.\manage-docker.ps1 logs elasticsearch`
2. Capturer l'erreur exacte
3. Vérifier la mémoire disponible: `docker stats`
4. Essayer un nettoyage complet: `.\manage-docker.ps1 clean`

## Fichiers de Configuration Modifiés

Les améliorations apportées:

1. **docker-compose.yml**:
   - Augmentation mémoire Elasticsearch: 512m → 1GB
   - Ajout `restart: unless-stopped` à tous les services
   - Health checks améliorés avec plus de retries
   - Ajout `start_period` pour laisser le temps au démarrage
   - Configuration CORS pour Elasticsearch
   - Désactivation du seuil d'espace disque

2. **Health Checks**:
   - Elasticsearch: Vérifie le statut du cluster (green/yellow)
   - Kibana: Vérifie l'API status
   - MongoDB: Utilise mongosh pour ping
   - Redis: Utilise redis-cli ping
   - Logstash: Vérifie l'API de stats

Ces modifications devraient rendre les services beaucoup plus stables!
