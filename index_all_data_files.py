#!/usr/bin/env python3
"""
Index all files from data folder into Elasticsearch
"""

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import csv
import json
import os
from datetime import datetime
from dateutil import parser as date_parser
from pathlib import Path

ES_HOST = 'http://localhost:9200'
DATA_FOLDER = 'data'
INDEX_NAME = 'ecommerce-logs-{}'.format(datetime.now().strftime('%Y.%m.%d'))

def index_csv_file(es_client, file_path):
    """Index CSV file into Elasticsearch"""
    print(f"📄 Processing CSV: {file_path}")
    
    actions = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Find timestamp field (case-insensitive)
                timestamp = None
                timestamp_key = None
                for key in row.keys():
                    if key.lower() in ['timestamp', '@timestamp', 'time', 'date']:
                        timestamp_str = row[key]
                        timestamp_key = key
                        # Parse and convert to ISO 8601 format
                        try:
                            # Try to parse the timestamp
                            dt = date_parser.parse(timestamp_str)
                            timestamp = dt.isoformat()
                        except Exception as e:
                            print(f"   ⚠️  Could not parse timestamp '{timestamp_str}': {e}")
                            timestamp = datetime.now().isoformat()
                        break
                
                if not timestamp:
                    timestamp = datetime.now().isoformat()
                
                # Remove original timestamp key and use only @timestamp
                source_data = {k: v for k, v in row.items() if k != timestamp_key}
                
                action = {
                    '_index': INDEX_NAME,
                    '_source': {
                        '@timestamp': timestamp,
                        **source_data,
                        'source_file': os.path.basename(file_path),
                        'file_type': 'csv'
                    }
                }
                actions.append(action)
        
        if actions:
            success, failed = bulk(es_client, actions, raise_on_error=False, stats_only=False)
            print(f"   ✅ Indexed {success} documents from {os.path.basename(file_path)}")
            if failed:
                print(f"   ⚠️  {failed} documents failed")
                # Print first few errors for debugging
                for err in failed[:3]:
                    print(f"   🔍 Error: {err}")
            return success
    except Exception as e:
        print(f"   ❌ Error: {e}")
    return 0

def index_json_file(es_client, file_path):
    """Index JSON file into Elasticsearch"""
    print(f"📄 Processing JSON: {file_path}")
    
    actions = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Handle both array and single object
            if isinstance(data, list):
                items = data
            else:
                items = [data]
            
            for item in items:
                # Find timestamp field (case-insensitive)
                timestamp = None
                timestamp_key = None
                for key in list(item.keys()):
                    if key.lower() in ['timestamp', '@timestamp', 'time', 'date']:
                        timestamp_str = item[key]
                        timestamp_key = key
                        # Parse and convert to ISO 8601 format
                        try:
                            dt = date_parser.parse(timestamp_str)
                            timestamp = dt.isoformat()
                        except Exception as e:
                            print(f"   ⚠️  Could not parse timestamp '{timestamp_str}': {e}")
                            timestamp = datetime.now().isoformat()
                        break
                
                if not timestamp:
                    timestamp = datetime.now().isoformat()
                
                # Remove original timestamp key and use only @timestamp
                source_data = {k: v for k, v in item.items() if k != timestamp_key}
                
                action = {
                    '_index': INDEX_NAME,
                    '_source': {
                        '@timestamp': timestamp,
                        **source_data,
                        'source_file': os.path.basename(file_path),
                        'file_type': 'json'
                    }
                }
                actions.append(action)
        
        if actions:
            success, failed = bulk(es_client, actions, raise_on_error=False, stats_only=False)
            print(f"   ✅ Indexed {success} documents from {os.path.basename(file_path)}")
            if failed:
                print(f"   ⚠️  {failed} documents failed")
                # Print first few errors for debugging
                for err in failed[:3]:
                    print(f"   🔍 Error: {err}")
            return success
    except Exception as e:
        print(f"   ❌ Error: {e}")
    return 0

def index_all_files():
    """Index all CSV and JSON files from data folder"""
    print("=" * 70)
    print("🚀 Indexing all files from data folder into Elasticsearch")
    print("=" * 70)
    print(f"📁 Data folder: {DATA_FOLDER}")
    print(f"🔗 Elasticsearch: {ES_HOST}")
    print(f"📊 Target index: {INDEX_NAME}")
    print("-" * 70)
    
    # Connect to Elasticsearch
    try:
        es = Elasticsearch([ES_HOST])
        info = es.info()
        print(f"✅ Connected to Elasticsearch {info['version']['number']}\n")
    except Exception as e:
        print(f"❌ Failed to connect to Elasticsearch: {e}")
        return
    
    # Find all CSV and JSON files
    csv_files = list(Path(DATA_FOLDER).glob('*.csv'))
    json_files = list(Path(DATA_FOLDER).glob('*.json'))
    
    total_docs = 0
    
    # Index CSV files
    if csv_files:
        print(f"📋 Found {len(csv_files)} CSV file(s)")
        for csv_file in csv_files:
            count = index_csv_file(es, str(csv_file))
            total_docs += count
        print()
    
    # Index JSON files
    if json_files:
        print(f"📋 Found {len(json_files)} JSON file(s)")
        for json_file in json_files:
            count = index_json_file(es, str(json_file))
            total_docs += count
        print()
    
    # Refresh index
    es.indices.refresh(index=INDEX_NAME)
    
    # Get total count
    try:
        total_in_index = es.count(index='ecommerce-logs-*')['count']
        print("=" * 70)
        print(f"✅ Indexing completed!")
        print(f"📊 Documents indexed in this run: {total_docs}")
        print(f"📊 Total documents in ecommerce-logs-*: {total_in_index}")
        print("=" * 70)
        print(f"\n📍 View in Kibana: http://localhost:5601/app/discover")
        print(f"📍 Dashboard: http://localhost:5601/app/dashboards")
        print(f"🌐 Angular App: http://localhost:4200")
    except Exception as e:
        print(f"⚠️  Could not get count: {e}")

if __name__ == '__main__':
    index_all_files()
