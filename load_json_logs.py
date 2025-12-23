#!/usr/bin/env python3
"""
Load JSON logs into Elasticsearch
"""

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import json

ES_HOST = 'http://localhost:9200'
INDEX_NAME = 'ecommerce-logs-2025.12.21'
JSON_FILE = 'data/sample_logs.json'

def main():
    print(f"🚀 Loading JSON logs into Elasticsearch...")
    
    # Connect
    es = Elasticsearch([ES_HOST])
    print(f"✅ Connected to Elasticsearch")
    
    # Load JSON
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        logs_data = json.load(f)
    
    # Prepare for bulk indexing
    actions = [
        {
            '_index': INDEX_NAME,
            '_source': {
                '@timestamp': log['Timestamp'],
                **log
            }
        }
        for log in logs_data
    ]
    
    # Bulk index
    success, failed = bulk(es, actions, raise_on_error=False)
    print(f"✅ Indexed {success} documents from JSON")
    
    # Refresh
    es.indices.refresh(index=INDEX_NAME)
    
    # Total count
    total = es.count(index=INDEX_NAME)['count']
    print(f"📊 Total documents in {INDEX_NAME}: {total}")
    print(f"🌐 View in Angular: http://localhost:4200")

if __name__ == '__main__':
    main()
