#!/usr/bin/env python3
"""
Create Kibana Data View (Index Pattern) for ecommerce-logs-*
"""

import requests
import json
import time

KIBANA_URL = 'http://localhost:5601'
INDEX_PATTERN = 'ecommerce-logs-*'
TIME_FIELD = '@timestamp'

def wait_for_kibana():
    """Wait for Kibana to be ready"""
    print("🔄 Waiting for Kibana to be ready...")
    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get(f'{KIBANA_URL}/api/status')
            if response.status_code == 200:
                print("✅ Kibana is ready!")
                return True
        except Exception as e:
            pass
        time.sleep(2)
        print(f"   Retry {i+1}/{max_retries}...")
    
    print("❌ Kibana is not responding")
    return False

def create_data_view():
    """Create Data View in Kibana"""
    print(f"\n📊 Creating Data View: {INDEX_PATTERN}")
    
    headers = {
        'kbn-xsrf': 'true',
        'Content-Type': 'application/json'
    }
    
    data = {
        "data_view": {
            "title": INDEX_PATTERN,
            "name": "E-Commerce Logs",
            "timeFieldName": TIME_FIELD
        }
    }
    
    try:
        # Create data view
        response = requests.post(
            f'{KIBANA_URL}/api/data_views/data_view',
            headers=headers,
            json=data
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            data_view_id = result['data_view']['id']
            print(f"✅ Data View created successfully!")
            print(f"   ID: {data_view_id}")
            print(f"   Title: {INDEX_PATTERN}")
            print(f"   Time Field: {TIME_FIELD}")
            
            # Set as default
            set_default_data_view(data_view_id)
            
            return True
        elif response.status_code == 409:
            print(f"⚠️  Data View already exists")
            return True
        else:
            print(f"❌ Failed to create Data View: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def set_default_data_view(data_view_id):
    """Set the data view as default"""
    headers = {
        'kbn-xsrf': 'true',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(
            f'{KIBANA_URL}/api/data_views/default',
            headers=headers,
            json={"data_view_id": data_view_id, "force": True}
        )
        
        if response.status_code in [200, 201]:
            print(f"✅ Set as default Data View")
        else:
            print(f"⚠️  Could not set as default: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Could not set as default: {e}")

def main():
    print("=" * 60)
    print("🚀 Kibana Data View Setup")
    print("=" * 60)
    
    if not wait_for_kibana():
        return
    
    # Wait a bit more for Kibana to fully initialize
    time.sleep(3)
    
    if create_data_view():
        print("\n" + "=" * 60)
        print("✅ Setup completed successfully!")
        print("=" * 60)
        print(f"\n📍 Access Kibana Discover:")
        print(f"   {KIBANA_URL}/app/discover")
        print(f"\n📊 View your logs with pattern: {INDEX_PATTERN}")
    else:
        print("\n❌ Setup failed. Please create Data View manually in Kibana.")

if __name__ == '__main__':
    main()
