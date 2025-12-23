#!/usr/bin/env python3
"""
Create Kibana Visualizations and Dashboard for ecommerce-logs
"""

import requests
import json
import time

KIBANA_URL = 'http://localhost:5601'
DATA_VIEW_PATTERN = 'ecommerce-logs-*'

headers = {
    'kbn-xsrf': 'true',
    'Content-Type': 'application/json'
}

def get_data_view_id():
    """Get the data view ID"""
    print("🔍 Finding Data View...")
    try:
        response = requests.get(f'{KIBANA_URL}/api/data_views', headers=headers)
        if response.status_code == 200:
            data_views = response.json().get('data_view', [])
            for dv in data_views:
                if dv.get('title') == DATA_VIEW_PATTERN:
                    print(f"✅ Found Data View: {dv['id']}")
                    return dv['id']
    except Exception as e:
        print(f"❌ Error finding Data View: {e}")
    return None

def create_visualization_logs_by_level(data_view_id):
    """Bar chart - Logs by Level"""
    print("\n📊 Creating: Logs by Level (Bar Chart)")
    
    vis = {
        "attributes": {
            "title": "Logs by Level",
            "visState": json.dumps({
                "title": "Logs by Level",
                "type": "histogram",
                "aggs": [
                    {
                        "id": "1",
                        "enabled": True,
                        "type": "count",
                        "schema": "metric",
                        "params": {}
                    },
                    {
                        "id": "2",
                        "enabled": True,
                        "type": "terms",
                        "schema": "segment",
                        "params": {
                            "field": "Level.keyword",
                            "size": 10,
                            "order": "desc",
                            "orderBy": "1"
                        }
                    }
                ],
                "params": {
                    "type": "histogram",
                    "grid": {"categoryLines": False},
                    "categoryAxes": [{
                        "id": "CategoryAxis-1",
                        "type": "category",
                        "position": "bottom",
                        "show": True,
                        "title": {}
                    }],
                    "valueAxes": [{
                        "id": "ValueAxis-1",
                        "name": "LeftAxis-1",
                        "type": "value",
                        "position": "left",
                        "show": True,
                        "title": {"text": "Count"}
                    }],
                    "seriesParams": [{
                        "show": True,
                        "type": "histogram",
                        "mode": "stacked",
                        "data": {"label": "Count", "id": "1"},
                        "valueAxis": "ValueAxis-1",
                        "drawLinesBetweenPoints": True,
                        "showCircles": True
                    }]
                }
            }),
            "uiStateJSON": "{}",
            "description": "",
            "version": 1,
            "kibanaSavedObjectMeta": {
                "searchSourceJSON": json.dumps({
                    "index": data_view_id,
                    "query": {"query": "", "language": "kuery"},
                    "filter": []
                })
            }
        }
    }
    
    try:
        response = requests.post(
            f'{KIBANA_URL}/api/saved_objects/visualization',
            headers=headers,
            json=vis
        )
        if response.status_code in [200, 201]:
            vis_id = response.json()['id']
            print(f"✅ Created: Logs by Level (ID: {vis_id})")
            return vis_id
    except Exception as e:
        print(f"❌ Error: {e}")
    return None

def create_visualization_logs_over_time(data_view_id):
    """Line chart - Logs over time"""
    print("\n📈 Creating: Logs Over Time (Line Chart)")
    
    vis = {
        "attributes": {
            "title": "Logs Over Time",
            "visState": json.dumps({
                "title": "Logs Over Time",
                "type": "line",
                "aggs": [
                    {
                        "id": "1",
                        "enabled": True,
                        "type": "count",
                        "schema": "metric",
                        "params": {}
                    },
                    {
                        "id": "2",
                        "enabled": True,
                        "type": "date_histogram",
                        "schema": "segment",
                        "params": {
                            "field": "@timestamp",
                            "timeRange": {"from": "now-7d", "to": "now"},
                            "useNormalizedEsInterval": True,
                            "scaleMetricValues": False,
                            "interval": "auto",
                            "drop_partials": False,
                            "min_doc_count": 1,
                            "extended_bounds": {}
                        }
                    }
                ],
                "params": {
                    "type": "line",
                    "grid": {"categoryLines": False},
                    "categoryAxes": [{
                        "id": "CategoryAxis-1",
                        "type": "category",
                        "position": "bottom",
                        "show": True,
                        "title": {}
                    }],
                    "valueAxes": [{
                        "id": "ValueAxis-1",
                        "name": "LeftAxis-1",
                        "type": "value",
                        "position": "left",
                        "show": True,
                        "title": {"text": "Count"}
                    }],
                    "seriesParams": [{
                        "show": True,
                        "type": "line",
                        "mode": "normal",
                        "data": {"label": "Count", "id": "1"},
                        "valueAxis": "ValueAxis-1",
                        "drawLinesBetweenPoints": True,
                        "lineWidth": 2,
                        "showCircles": True
                    }],
                    "addTimeMarker": False,
                    "addLegend": True,
                    "legendPosition": "right",
                    "times": [],
                    "addTooltip": True,
                    "detailedTooltip": True
                }
            }),
            "uiStateJSON": "{}",
            "description": "",
            "version": 1,
            "kibanaSavedObjectMeta": {
                "searchSourceJSON": json.dumps({
                    "index": data_view_id,
                    "query": {"query": "", "language": "kuery"},
                    "filter": []
                })
            }
        }
    }
    
    try:
        response = requests.post(
            f'{KIBANA_URL}/api/saved_objects/visualization',
            headers=headers,
            json=vis
        )
        if response.status_code in [200, 201]:
            vis_id = response.json()['id']
            print(f"✅ Created: Logs Over Time (ID: {vis_id})")
            return vis_id
    except Exception as e:
        print(f"❌ Error: {e}")
    return None

def create_visualization_logs_by_service(data_view_id):
    """Pie chart - Logs by Service"""
    print("\n🥧 Creating: Logs by Service (Pie Chart)")
    
    vis = {
        "attributes": {
            "title": "Logs by Service",
            "visState": json.dumps({
                "title": "Logs by Service",
                "type": "pie",
                "aggs": [
                    {
                        "id": "1",
                        "enabled": True,
                        "type": "count",
                        "schema": "metric",
                        "params": {}
                    },
                    {
                        "id": "2",
                        "enabled": True,
                        "type": "terms",
                        "schema": "segment",
                        "params": {
                            "field": "Service.keyword",
                            "size": 10,
                            "order": "desc",
                            "orderBy": "1"
                        }
                    }
                ],
                "params": {
                    "type": "pie",
                    "addTooltip": True,
                    "addLegend": True,
                    "legendPosition": "right",
                    "isDonut": True,
                    "labels": {
                        "show": True,
                        "values": True,
                        "last_level": True,
                        "truncate": 100
                    }
                }
            }),
            "uiStateJSON": "{}",
            "description": "",
            "version": 1,
            "kibanaSavedObjectMeta": {
                "searchSourceJSON": json.dumps({
                    "index": data_view_id,
                    "query": {"query": "", "language": "kuery"},
                    "filter": []
                })
            }
        }
    }
    
    try:
        response = requests.post(
            f'{KIBANA_URL}/api/saved_objects/visualization',
            headers=headers,
            json=vis
        )
        if response.status_code in [200, 201]:
            vis_id = response.json()['id']
            print(f"✅ Created: Logs by Service (ID: {vis_id})")
            return vis_id
    except Exception as e:
        print(f"❌ Error: {e}")
    return None

def create_visualization_total_logs(data_view_id):
    """Metric - Total Logs Count"""
    print("\n🔢 Creating: Total Logs (Metric)")
    
    vis = {
        "attributes": {
            "title": "Total Logs",
            "visState": json.dumps({
                "title": "Total Logs",
                "type": "metric",
                "aggs": [
                    {
                        "id": "1",
                        "enabled": True,
                        "type": "count",
                        "schema": "metric",
                        "params": {}
                    }
                ],
                "params": {
                    "addTooltip": True,
                    "addLegend": False,
                    "type": "metric",
                    "metric": {
                        "percentageMode": False,
                        "useRanges": False,
                        "colorSchema": "Green to Red",
                        "metricColorMode": "None",
                        "colorsRange": [{"from": 0, "to": 10000}],
                        "labels": {"show": True},
                        "invertColors": False,
                        "style": {
                            "bgFill": "#000",
                            "bgColor": False,
                            "labelColor": False,
                            "subText": "",
                            "fontSize": 60
                        }
                    }
                }
            }),
            "uiStateJSON": "{}",
            "description": "",
            "version": 1,
            "kibanaSavedObjectMeta": {
                "searchSourceJSON": json.dumps({
                    "index": data_view_id,
                    "query": {"query": "", "language": "kuery"},
                    "filter": []
                })
            }
        }
    }
    
    try:
        response = requests.post(
            f'{KIBANA_URL}/api/saved_objects/visualization',
            headers=headers,
            json=vis
        )
        if response.status_code in [200, 201]:
            vis_id = response.json()['id']
            print(f"✅ Created: Total Logs (ID: {vis_id})")
            return vis_id
    except Exception as e:
        print(f"❌ Error: {e}")
    return None

def create_visualization_top_messages(data_view_id):
    """Data Table - Top Messages"""
    print("\n📋 Creating: Top Messages (Data Table)")
    
    vis = {
        "attributes": {
            "title": "Top Log Messages",
            "visState": json.dumps({
                "title": "Top Log Messages",
                "type": "table",
                "aggs": [
                    {
                        "id": "1",
                        "enabled": True,
                        "type": "count",
                        "schema": "metric",
                        "params": {}
                    },
                    {
                        "id": "2",
                        "enabled": True,
                        "type": "terms",
                        "schema": "bucket",
                        "params": {
                            "field": "Message.keyword",
                            "size": 10,
                            "order": "desc",
                            "orderBy": "1"
                        }
                    }
                ],
                "params": {
                    "perPage": 10,
                    "showPartialRows": False,
                    "showMetricsAtAllLevels": False,
                    "showTotal": False,
                    "totalFunc": "sum",
                    "percentageCol": ""
                }
            }),
            "uiStateJSON": json.dumps({
                "vis": {"params": {"sort": {"columnIndex": None, "direction": None}}}
            }),
            "description": "",
            "version": 1,
            "kibanaSavedObjectMeta": {
                "searchSourceJSON": json.dumps({
                    "index": data_view_id,
                    "query": {"query": "", "language": "kuery"},
                    "filter": []
                })
            }
        }
    }
    
    try:
        response = requests.post(
            f'{KIBANA_URL}/api/saved_objects/visualization',
            headers=headers,
            json=vis
        )
        if response.status_code in [200, 201]:
            vis_id = response.json()['id']
            print(f"✅ Created: Top Messages (ID: {vis_id})")
            return vis_id
    except Exception as e:
        print(f"❌ Error: {e}")
    return None

def create_dashboard(vis_ids):
    """Create Dashboard with all visualizations"""
    print("\n📊 Creating Dashboard...")
    
    panels = []
    positions = [
        {"x": 0, "y": 0, "w": 12, "h": 8},   # Total Logs
        {"x": 12, "y": 0, "w": 36, "h": 8},  # Logs Over Time
        {"x": 0, "y": 8, "w": 24, "h": 12},  # Logs by Level
        {"x": 24, "y": 8, "w": 24, "h": 12}, # Logs by Service
        {"x": 0, "y": 20, "w": 48, "h": 12}  # Top Messages
    ]
    
    for i, vis_id in enumerate(vis_ids):
        if vis_id and i < len(positions):
            panels.append({
                "version": "8.11.0",
                "type": "visualization",
                "gridData": {
                    "x": positions[i]["x"],
                    "y": positions[i]["y"],
                    "w": positions[i]["w"],
                    "h": positions[i]["h"],
                    "i": str(i)
                },
                "panelIndex": str(i),
                "embeddableConfig": {"enhancements": {}},
                "panelRefName": f"panel_{i}"
            })
    
    dashboard = {
        "attributes": {
            "title": "E-Commerce Logs Dashboard",
            "hits": 0,
            "description": "Overview of e-commerce application logs",
            "panelsJSON": json.dumps(panels),
            "optionsJSON": json.dumps({
                "useMargins": True,
                "syncColors": False,
                "hidePanelTitles": False
            }),
            "version": 1,
            "timeRestore": False,
            "kibanaSavedObjectMeta": {
                "searchSourceJSON": json.dumps({
                    "query": {"query": "", "language": "kuery"},
                    "filter": []
                })
            }
        },
        "references": [
            {
                "name": f"panel_{i}",
                "type": "visualization",
                "id": vis_id
            }
            for i, vis_id in enumerate(vis_ids) if vis_id
        ]
    }
    
    try:
        response = requests.post(
            f'{KIBANA_URL}/api/saved_objects/dashboard',
            headers=headers,
            json=dashboard
        )
        if response.status_code in [200, 201]:
            dash_id = response.json()['id']
            print(f"✅ Dashboard created (ID: {dash_id})")
            return dash_id
    except Exception as e:
        print(f"❌ Error: {e}")
    return None

def main():
    print("=" * 70)
    print("🎨 Kibana Visualizations & Dashboard Setup")
    print("=" * 70)
    
    # Get Data View ID
    data_view_id = get_data_view_id()
    if not data_view_id:
        print("\n❌ Could not find Data View. Run setup_kibana_dataview.py first.")
        return
    
    # Create visualizations
    vis_ids = []
    vis_ids.append(create_visualization_total_logs(data_view_id))
    vis_ids.append(create_visualization_logs_over_time(data_view_id))
    vis_ids.append(create_visualization_logs_by_level(data_view_id))
    vis_ids.append(create_visualization_logs_by_service(data_view_id))
    vis_ids.append(create_visualization_top_messages(data_view_id))
    
    # Create dashboard
    dashboard_id = create_dashboard(vis_ids)
    
    print("\n" + "=" * 70)
    print("✅ Setup Complete!")
    print("=" * 70)
    
    if dashboard_id:
        print(f"\n📊 Dashboard URL:")
        print(f"   {KIBANA_URL}/app/dashboards#/view/{dashboard_id}")
    
    print(f"\n📍 Access Kibana:")
    print(f"   Dashboards: {KIBANA_URL}/app/dashboards")
    print(f"   Visualizations: {KIBANA_URL}/app/visualize")
    print(f"   Discover: {KIBANA_URL}/app/discover")

if __name__ == '__main__':
    main()
