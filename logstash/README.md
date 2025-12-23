# 🔄 Logstash - Pipeline d'ingestion de données

Configuration Logstash pour la plateforme d'analytics e-commerce avec pipelines d'ingestion et transformation de données.

## 📋 Description

Logstash est le moteur d'ingestion de données qui collecte, transforme et envoie les logs vers Elasticsearch pour indexation et analyse.

## 🛠️ Configuration

### Version
- **Logstash**: 8.11.0
- **Ports**:
  - 5000: TCP input
  - 5044: Beats input
  - 9600: Monitoring API

### Paramètres Docker
```yaml
logstash:
  image: docker.elastic.co/logstash/logstash:8.11.0
  container_name: logstash
  environment:
    - "LS_JAVA_OPTS=-Xmx256m -Xms256m"
    - "xpack.monitoring.enabled=false"
  ports:
    - "5000:5000/tcp"
    - "5044:5044"
    - "9600:9600"
  volumes:
    - ./logstash/pipeline:/usr/share/logstash/pipeline
    - ./logstash/config:/usr/share/logstash/config
  depends_on:
    - elasticsearch
  networks:
    - elk
```

### Mémoire JVM
- **Heap min**: 256 MB
- **Heap max**: 256 MB
- **Recommandé pour production**: 1-2 GB

---

## 📁 Structure

```
logstash/
├── pipeline/
│   ├── logstash.conf         # Pipeline principal
│   ├── csv-pipeline.conf     # Pipeline CSV
│   ├── json-pipeline.conf    # Pipeline JSON
│   └── logs-pipeline.conf    # Pipeline logs texte
├── config/
│   ├── logstash.yml          # Configuration Logstash
│   └── pipelines.yml         # Définition des pipelines
└── README.md                 # Ce fichier
```

---

## 🔧 Pipelines

### Pipeline Principal (logstash.conf)

```ruby
input {
  tcp {
    port => 5000
    codec => json_lines
  }
  
  beats {
    port => 5044
  }
}

filter {
  # Parse timestamp
  date {
    match => [ "timestamp", "ISO8601", "yyyy-MM-dd'T'HH:mm:ss.SSSZ" ]
    target => "@timestamp"
  }
  
  # Add metadata
  mutate {
    add_field => {
      "[@metadata][pipeline]" => "main"
    }
  }
  
  # Grok pour logs non structurés
  if [message] =~ /^\[/ {
    grok {
      match => {
        "message" => "\[%{TIMESTAMP_ISO8601:timestamp}\] \[%{LOGLEVEL:level}\] \[%{DATA:service}\] %{GREEDYDATA:log_message}"
      }
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "ecommerce-logs-%{+YYYY.MM.dd}"
    document_type => "_doc"
  }
  
  # Debug output (optionnel)
  stdout {
    codec => rubydebug
  }
}
```

---

### Pipeline CSV (csv-pipeline.conf)

**Objectif**: Parser les fichiers CSV de logs

```ruby
input {
  file {
    path => "/usr/share/logstash/data/*.csv"
    start_position => "beginning"
    sincedb_path => "/dev/null"
    codec => plain
  }
}

filter {
  # Skip header line
  if [message] =~ /^Timestamp,/ {
    drop { }
  }
  
  # Parse CSV
  csv {
    separator => ","
    columns => ["Timestamp", "Level", "Service", "Message", "User", "IP", "Duration"]
    skip_empty_columns => true
  }
  
  # Convert types
  mutate {
    convert => {
      "Duration" => "integer"
    }
  }
  
  # Parse timestamp
  date {
    match => [ "Timestamp", "ISO8601", "yyyy-MM-dd'T'HH:mm:ss", "yyyy-MM-dd HH:mm:ss" ]
    target => "@timestamp"
  }
  
  # Remove original timestamp field
  mutate {
    remove_field => ["Timestamp", "message"]
  }
  
  # Normalize level
  mutate {
    uppercase => ["Level"]
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "ecommerce-logs-%{+YYYY.MM.dd}"
  }
}
```

---

### Pipeline JSON (json-pipeline.conf)

**Objectif**: Parser les fichiers JSON et JSON Lines

```ruby
input {
  file {
    path => "/usr/share/logstash/data/*.json"
    start_position => "beginning"
    sincedb_path => "/dev/null"
    codec => json_lines
  }
}

filter {
  # Parse timestamp
  if [timestamp] {
    date {
      match => [ "timestamp", "ISO8601" ]
      target => "@timestamp"
    }
    mutate {
      remove_field => ["timestamp"]
    }
  }
  
  # Parse nested event data
  if [event] {
    mutate {
      add_field => {
        "event_type" => "%{event}"
      }
    }
  }
  
  # Add metadata
  mutate {
    add_field => {
      "source_type" => "json"
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "ecommerce-logs-%{+YYYY.MM.dd}"
  }
}
```

---

### Pipeline Logs Texte (logs-pipeline.conf)

**Objectif**: Parser les logs texte avec Grok

```ruby
input {
  file {
    path => "/usr/share/logstash/data/*.log"
    start_position => "beginning"
    sincedb_path => "/dev/null"
    codec => plain
  }
}

filter {
  # Grok pattern pour logs standards
  grok {
    match => {
      "message" => "\[%{TIMESTAMP_ISO8601:timestamp}\] \[%{LOGLEVEL:Level}\] \[%{DATA:Service}\] %{GREEDYDATA:Message}"
    }
  }
  
  # Fallback si grok échoue
  if "_grokparsefailure" in [tags] {
    mutate {
      add_field => {
        "Level" => "INFO"
        "Service" => "unknown"
        "Message" => "%{message}"
      }
    }
    mutate {
      remove_tag => ["_grokparsefailure"]
    }
  }
  
  # Parse timestamp
  date {
    match => [ "timestamp", "yyyy-MM-dd HH:mm:ss", "ISO8601" ]
    target => "@timestamp"
  }
  
  # Cleanup
  mutate {
    remove_field => ["message", "timestamp"]
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "ecommerce-logs-%{+YYYY.MM.dd}"
  }
}
```

---

## 🎯 Filtres Logstash

### 1. **grok** - Pattern matching
**Usage**: Parser logs non structurés

**Patterns courants**:
```ruby
# Timestamp ISO
%{TIMESTAMP_ISO8601:timestamp}

# Log level
%{LOGLEVEL:level}

# IP address
%{IP:client_ip}

# Number
%{NUMBER:response_time:float}

# Custom pattern
(?<custom_field>[a-zA-Z0-9]+)
```

**Exemple**:
```ruby
grok {
  match => {
    "message" => "%{IP:client} - \[%{HTTPDATE:timestamp}\] \"%{WORD:method} %{URIPATHPARAM:request}\" %{NUMBER:status} %{NUMBER:bytes}"
  }
}
```

---

### 2. **date** - Parse dates
**Usage**: Convertir string en timestamp

```ruby
date {
  match => [ "timestamp", "ISO8601", "yyyy-MM-dd HH:mm:ss" ]
  target => "@timestamp"
  timezone => "Europe/Paris"
}
```

---

### 3. **mutate** - Transformations
**Usage**: Modifier, ajouter, supprimer champs

```ruby
mutate {
  # Ajouter champ
  add_field => { "environment" => "production" }
  
  # Renommer champ
  rename => { "old_name" => "new_name" }
  
  # Supprimer champs
  remove_field => ["temp_field", "useless_data"]
  
  # Convertir type
  convert => {
    "duration" => "integer"
    "amount" => "float"
  }
  
  # Uppercase/Lowercase
  uppercase => ["level"]
  lowercase => ["service"]
  
  # Split string
  split => { "tags" => "," }
  
  # Join array
  join => { "tags" => ", " }
}
```

---

### 4. **csv** - Parse CSV
**Usage**: Parser lignes CSV

```ruby
csv {
  separator => ","
  columns => ["timestamp", "level", "service", "message"]
  skip_empty_columns => true
  skip_empty_rows => true
}
```

---

### 5. **json** - Parse JSON
**Usage**: Parser string JSON

```ruby
json {
  source => "message"
  target => "parsed_json"
}
```

---

### 6. **drop** - Ignorer événement
**Usage**: Filtrer événements non désirés

```ruby
if [level] == "DEBUG" {
  drop { }
}
```

---

### 7. **geoip** - Géolocalisation
**Usage**: Enrichir avec géolocalisation IP

```ruby
geoip {
  source => "client_ip"
  target => "geoip"
}
```

---

### 8. **useragent** - Parse User-Agent
**Usage**: Extraire browser, OS, device

```ruby
useragent {
  source => "user_agent"
  target => "ua"
}
```

---

## 📊 Patterns Grok personnalisés

### Créer patterns customisés
```ruby
# patterns/custom
LOGLEVEL (DEBUG|INFO|WARNING|ERROR|CRITICAL|WARN|FATAL)
SERVICE [a-z-]+
ORDER_ID ORD[0-9]{6}
PRODUCT_ID PROD[0-9]{4}
```

### Utiliser patterns custom
```ruby
grok {
  patterns_dir => ["/usr/share/logstash/patterns"]
  match => {
    "message" => "%{LOGLEVEL:level} %{SERVICE:service} Order %{ORDER_ID:order_id}"
  }
}
```

---

## 🔍 Inputs

### TCP Input
```ruby
input {
  tcp {
    port => 5000
    codec => json_lines
  }
}
```

### File Input
```ruby
input {
  file {
    path => "/var/log/*.log"
    start_position => "beginning"
    sincedb_path => "/var/lib/logstash/sincedb"
  }
}
```

### Beats Input (Filebeat, Metricbeat)
```ruby
input {
  beats {
    port => 5044
  }
}
```

### HTTP Input
```ruby
input {
  http {
    port => 8080
    codec => json
  }
}
```

### Kafka Input
```ruby
input {
  kafka {
    bootstrap_servers => "kafka:9092"
    topics => ["logs"]
    group_id => "logstash"
  }
}
```

---

## 📤 Outputs

### Elasticsearch Output
```ruby
output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "logs-%{+YYYY.MM.dd}"
    document_type => "_doc"
    user => "elastic"
    password => "changeme"
  }
}
```

### File Output
```ruby
output {
  file {
    path => "/var/log/logstash/output.log"
    codec => line { format => "%{message}" }
  }
}
```

### Stdout Output (debug)
```ruby
output {
  stdout {
    codec => rubydebug
  }
}
```

### Multiple Outputs
```ruby
output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "logs-%{+YYYY.MM.dd}"
  }
  
  if [level] == "ERROR" {
    file {
      path => "/var/log/errors.log"
    }
  }
}
```

---

## 🎛️ Configuration

### logstash.yml
```yaml
# Node name
node.name: logstash

# Pipeline settings
pipeline.workers: 2
pipeline.batch.size: 125
pipeline.batch.delay: 50

# Monitoring
xpack.monitoring.enabled: false

# Queue type (memory or persisted)
queue.type: memory

# Log level
log.level: info

# Elasticsearch output
elasticsearch.hosts: ["http://elasticsearch:9200"]
```

### pipelines.yml
```yaml
- pipeline.id: main
  path.config: "/usr/share/logstash/pipeline/logstash.conf"
  
- pipeline.id: csv
  path.config: "/usr/share/logstash/pipeline/csv-pipeline.conf"
  
- pipeline.id: json
  path.config: "/usr/share/logstash/pipeline/json-pipeline.conf"
```

---

## 🚀 Utilisation

### Démarrer Logstash
```bash
# Via Docker
docker-compose up -d logstash

# Suivre les logs
docker logs -f logstash
```

### Tester un pipeline
```bash
# Syntax check
docker exec logstash bin/logstash --config.test_and_exit -f /usr/share/logstash/pipeline/logstash.conf

# Test avec stdin/stdout
docker exec -it logstash bin/logstash -e 'input { stdin { } } output { stdout { codec => rubydebug } }'
```

### Envoyer données via TCP
```bash
# Envoyer JSON
echo '{"level":"INFO","service":"test","message":"Hello"}' | nc localhost 5000

# Envoyer fichier
cat data/logs.json | nc localhost 5000
```

---

## 📊 Monitoring

### API Monitoring
```bash
# Node info
curl http://localhost:9600/_node?pretty

# Node stats
curl http://localhost:9600/_node/stats?pretty

# Pipeline stats
curl http://localhost:9600/_node/stats/pipelines?pretty

# Hot threads
curl http://localhost:9600/_node/hot_threads?pretty
```

### Métriques clés
- **Events in**: Nombre d'événements reçus
- **Events out**: Nombre d'événements envoyés
- **Events filtered**: Événements filtrés/droppés
- **Duration**: Temps de traitement
- **Queue**: Taille de la queue

---

## 🐛 Troubleshooting

### Logs Logstash
```bash
# Voir les logs
docker logs logstash

# Suivre en temps réel
docker logs -f logstash

# Dernières 100 lignes
docker logs --tail 100 logstash
```

### Erreurs communes

#### "Pipeline aborted due to error"
**Causes**:
- Syntax error dans pipeline
- Plugin manquant
- Connexion Elasticsearch échouée

**Solutions**:
```bash
# Vérifier syntax
bin/logstash --config.test_and_exit -f pipeline.conf

# Installer plugin manquant
bin/logstash-plugin install logstash-filter-geoip

# Vérifier Elasticsearch
curl http://elasticsearch:9200
```

#### "Grok parse failure"
**Causes**:
- Pattern grok incorrect
- Format de log différent

**Solutions**:
```ruby
# Ajouter fallback
if "_grokparsefailure" in [tags] {
  mutate {
    add_field => { "raw_message" => "%{message}" }
  }
}

# Tester pattern sur grokdebug.com
```

#### "Out of memory"
**Causes**:
- Heap trop petit
- Queue trop grande
- Batch size trop élevé

**Solutions**:
```yaml
# Augmenter heap
LS_JAVA_OPTS: "-Xmx1g -Xms1g"

# Réduire batch
pipeline.batch.size: 50
```

---

## 🔧 Optimisations

### Performance
```yaml
# Workers (nombre de CPU cores)
pipeline.workers: 4

# Batch size (augmenter pour throughput)
pipeline.batch.size: 500

# Batch delay (réduire pour faible latence)
pipeline.batch.delay: 5

# Queue persisted (pour durabilité)
queue.type: persisted
queue.max_bytes: 1gb
```

### Output Elasticsearch optimisé
```ruby
output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "logs-%{+YYYY.MM.dd}"
    
    # Bulk settings
    flush_size => 500
    idle_flush_time => 1
    
    # Connection pool
    pool_max => 500
    pool_max_per_route => 100
  }
}
```

---

## 📚 Ressources

### Documentation officielle
- [Logstash Reference](https://www.elastic.co/guide/en/logstash/current/index.html)
- [Configuration](https://www.elastic.co/guide/en/logstash/current/configuration.html)
- [Plugins](https://www.elastic.co/guide/en/logstash/current/input-plugins.html)

### Outils
- [Grok Debugger](https://grokdebug.herokuapp.com/)
- [Grok Constructor](http://grokconstructor.appspot.com/)

---

## 📝 Exemples complets

### E-Commerce Order Pipeline
```ruby
input {
  kafka {
    bootstrap_servers => "kafka:9092"
    topics => ["orders"]
    codec => json
  }
}

filter {
  # Parse order data
  json {
    source => "message"
  }
  
  # Calculate total with tax
  ruby {
    code => "event.set('total_with_tax', event.get('total') * 1.20)"
  }
  
  # Geo-locate customer IP
  geoip {
    source => "customer_ip"
    target => "customer_location"
  }
  
  # Add timestamp
  date {
    match => [ "order_date", "ISO8601" ]
    target => "@timestamp"
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "ecommerce-orders-%{+YYYY.MM.dd}"
  }
}
```

---

**Version**: 8.11.0  
**Dernière mise à jour**: Décembre 2025  
**Documentation complète**: [ELK_CONFIGURATION.md](../ELK_CONFIGURATION.md)
