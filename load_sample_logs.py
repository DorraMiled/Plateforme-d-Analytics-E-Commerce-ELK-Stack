#!/usr/bin/env python3
"""
Script to load sample logs into Elasticsearch
"""

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import csv
from datetime import datetime
import sys

# Configuration
ES_HOST = 'http://localhost:9200'
INDEX_NAME = 'ecommerce-logs-2025.12.21'
CSV_FILE = 'data/sample_logs.csv'

def create_index_template(es_client):
    """Create index template for logs"""
    template = {
        "index_patterns": ["ecommerce-logs-*"],
        "template": {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            },
            "mappings": {
                "properties": {
                    "@timestamp": {"type": "date"},
                    "Timestamp": {"type": "date"},
                    "Level": {
                        "type": "text",
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    },
                    "Service": {
                        "type": "text",
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    },
                    "Message": {"type": "text"},
                    "User": {
                        "type": "text",
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    }
                }
            }
        }
    }
    
    try:
        es_client.indices.put_index_template(name='ecommerce-logs-template', body=template)
        print("✅ Index template created")
    except Exception as e:
        print(f"⚠️  Template creation warning: {e}")

def load_logs_from_csv(csv_file):
    """Load logs from CSV file"""
    logs = []
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            log = {
                '_index': INDEX_NAME,
                '_source': {
                    '@timestamp': row['Timestamp'],
                    'Timestamp': row['Timestamp'],
                    'Level': row['Level'],
                    'Service': row['Service'],
                    'Message': row['Message'],
                    'User': row['User']
                }
            }
            logs.append(log)
    
    return logs

def main():
    """Main function"""
    print(f"🚀 Starting log indexing...")
    print(f"📁 CSV file: {CSV_FILE}")
    print(f"🔗 Elasticsearch: {ES_HOST}")
    print(f"📊 Target index: {INDEX_NAME}")
    print("-" * 50)
    
    # Connect to Elasticsearch
    try:
        es = Elasticsearch([ES_HOST])
        info = es.info()
        print(f"✅ Connected to Elasticsearch {info['version']['number']}")
    except Exception as e:
        print(f"❌ Failed to connect to Elasticsearch: {e}")
        sys.exit(1)
    
    # Create index template
    create_index_template(es)
    
    # Load logs from CSV
    try:
        logs = load_logs_from_csv(CSV_FILE)
        print(f"📄 Loaded {len(logs)} logs from CSV")
    except Exception as e:
        print(f"❌ Failed to read CSV file: {e}")
        sys.exit(1)
    
    # Bulk index logs
    try:
        success, failed = bulk(es, logs, raise_on_error=False, stats_only=False)
        print(f"✅ Indexed {success} documents successfully")
        if failed:
            print(f"⚠️  {len(failed)} documents failed to index")
    except Exception as e:
        print(f"❌ Bulk indexing failed: {e}")
        sys.exit(1)
    
    # Refresh index
    es.indices.refresh(index=INDEX_NAME)
    
    # Verify indexing
    count = es.count(index=INDEX_NAME)['count']
    print(f"✅ Total documents in {INDEX_NAME}: {count}")
    
    # Show sample document
    sample = es.search(index=INDEX_NAME, body={"query": {"match_all": {}}, "size": 1})
    if sample['hits']['hits']:
        print("\n📝 Sample document:")
        doc = sample['hits']['hits'][0]['_source']
        for key, value in doc.items():
            print(f"   {key}: {value}")
    
    print("\n✅ Indexing completed successfully!")
    print(f"🔍 View logs in Kibana: http://localhost:5601")
    print(f"🌐 Or in Angular app: http://localhost:4200")

if __name__ == '__main__':
    main()
