from flask import Flask, jsonify, request, send_from_directory, make_response
from pymongo import MongoClient
import redis
from elasticsearch import Elasticsearch
import os
import json
import csv
import io
from datetime import datetime
from werkzeug.utils import secure_filename
import pandas as pd

# Import du blueprint d'authentification
from auth.routes import auth_bp
from auth.models import create_user_indexes

# Import du cache Redis
from cache.redis_cache import cache_manager, cache_response, invalidate_pattern, get_cache_stats, invalidate_cache_type
from cache.config import CacheType, CacheConfig

app = Flask(__name__)

# Configuration
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://admin:admin123@localhost:27017/ecommerce?authSource=admin')
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
ELASTICSEARCH_HOST = os.getenv('ELASTICSEARCH_HOST', 'http://localhost:9200')

# Configuration JWT
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-super-secret-key-change-in-production-2024!')

# Upload folder - use local path by default, Docker will override via env var
default_upload_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', default_upload_folder)
ALLOWED_EXTENSIONS = {'csv', 'json'}

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Initialize connections
try:
    mongo_client = MongoClient(MONGODB_URI)
    db = mongo_client.ecommerce
    print("[OK] Connected to MongoDB")
    
    # Stocker la DB dans la config Flask pour les blueprints
    app.config['DB'] = db
    
    # Créer les index pour la collection users
    create_user_indexes(db)
except Exception as e:
    print(f"[ERROR] MongoDB connection error: {e}")
    db = None
    app.config['DB'] = None

try:
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    redis_client.ping()
    print("[OK] Connected to Redis")
    
    # Initialiser le cache manager avec le client Redis
    cache_manager.set_client(redis_client)
    print("[OK] Cache Manager initialized")
except Exception as e:
    print(f"[ERROR] Redis connection error: {e}")
    redis_client = None

try:
    es_client = Elasticsearch([ELASTICSEARCH_HOST])
    print("[OK] Connected to Elasticsearch")
except Exception as e:
    print(f"[ERROR] Elasticsearch connection error: {e}")
    es_client = None


@app.route('/')
def index():
    """Home page with system status"""
    services_status = {
        'mongodb': 'connected' if db is not None else 'disconnected',
        'redis': 'connected' if redis_client is not None else 'disconnected',
        'elasticsearch': 'connected' if es_client is not None else 'disconnected'
    }
    
    return jsonify({
        'message': 'E-commerce Flask Application',
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'services': services_status
    })


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all products from MongoDB"""
    if db is None:
        return jsonify({'error': 'Database not connected'}), 500
    
    try:
        products = list(db.products.find({}, {'_id': 0}))
        return jsonify({
            'count': len(products),
            'products': products
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/products', methods=['POST'])
def create_product():
    """Create a new product"""
    if db is None:
        return jsonify({'error': 'Database not connected'}), 500
    
    try:
        data = request.get_json()
        data['created_at'] = datetime.now().isoformat()
        
        result = db.products.insert_one(data)
        
        # Index in Elasticsearch
        if es_client:
            try:
                es_client.index(index='products', id=str(result.inserted_id), document=data)
            except Exception as e:
                print(f"Elasticsearch indexing error: {e}")
        
        return jsonify({
            'message': 'Product created successfully',
            'id': str(result.inserted_id)
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/cache/<key>', methods=['GET'])
def get_cache(key):
    """Get value from Redis cache"""
    if redis_client is None:
        return jsonify({'error': 'Redis not connected'}), 500
    
    try:
        value = redis_client.get(key)
        if value:
            return jsonify({'key': key, 'value': value})
        else:
            return jsonify({'error': 'Key not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/cache/<key>', methods=['POST'])
def set_cache(key):
    """Set value in Redis cache"""
    if redis_client is None:
        return jsonify({'error': 'Redis not connected'}), 500
    
    try:
        data = request.get_json()
        value = data.get('value')
        redis_client.set(key, value)
        return jsonify({'message': 'Cache set successfully', 'key': key, 'value': value})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload CSV or JSON file and index to Elasticsearch"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only CSV and JSON are allowed'}), 400
    
    try:
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Save file
        file.save(filepath)
        
        # Process and index the file
        documents_indexed = 0
        file_type = filename.rsplit('.', 1)[1].lower()
        
        if file_type == 'csv':
            # Process CSV file
            df = pd.read_csv(filepath)
            documents = df.to_dict('records')
            
            # Index to Elasticsearch
            for doc in documents:
                # Add timestamp if not present
                if '@timestamp' not in doc:
                    doc['@timestamp'] = datetime.now().isoformat()
                
                # Index to Elasticsearch
                if es_client:
                    index_name = f"ecommerce-logs-{datetime.now().strftime('%Y.%m.%d')}"
                    es_client.index(index=index_name, document=doc)
                    documents_indexed += 1
                
                # Also save to MongoDB
                if db is not None:
                    db.uploads.insert_one({
                        **doc,
                        'source_file': unique_filename,
                        'uploaded_at': datetime.now().isoformat()
                    })
        
        elif file_type == 'json':
            # Process JSON file
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Handle both single object and array of objects
            documents = data if isinstance(data, list) else [data]
            
            # Index to Elasticsearch
            for doc in documents:
                # Add timestamp if not present
                if '@timestamp' not in doc:
                    doc['@timestamp'] = datetime.now().isoformat()
                
                if es_client:
                    index_name = f"ecommerce-logs-{datetime.now().strftime('%Y.%m.%d')}"
                    es_client.index(index=index_name, document=doc)
                    documents_indexed += 1
                
                # Also save to MongoDB
                if db is not None:
                    db.uploads.insert_one({
                        **doc,
                        'source_file': unique_filename,
                        'uploaded_at': datetime.now().isoformat()
                    })
        
        # Store file metadata in Redis
        if redis_client:
            file_info = {
                'filename': unique_filename,
                'original_name': filename,
                'uploaded_at': datetime.now().isoformat(),
                'size': os.path.getsize(filepath),
                'type': file_type,
                'documents_count': documents_indexed
            }
            redis_client.setex(
                f"file:{unique_filename}",
                86400,  # Expire after 24 hours
                json.dumps(file_info)
            )
        
        return jsonify({
            'message': 'File uploaded and indexed successfully',
            'filename': unique_filename,
            'documents_indexed': documents_indexed,
            'file_type': file_type
        }), 201
    
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500


@app.route('/api/search', methods=['GET', 'POST'])
def search():
    """Search in Elasticsearch with advanced queries"""
    if es_client is None:
        return jsonify({'error': 'Elasticsearch not connected'}), 500
    
    try:
        # Handle both GET and POST requests
        if request.method == 'POST':
            data = request.get_json()
            query_text = data.get('query', '')
            level = data.get('level', '')
            service = data.get('service', '')
            start_date = data.get('start_date', '')
            end_date = data.get('end_date', '')
            size = int(data.get('size', 50))
            from_param = int(data.get('from', 0))
        else:
            query_text = request.args.get('q', '')
            level = request.args.get('level', '')
            service = request.args.get('service', '')
            start_date = request.args.get('start_date', '')
            end_date = request.args.get('end_date', '')
            size = int(request.args.get('size', 50))
            from_param = int(request.args.get('from', 0))
        
        # Build query
        must_clauses = []
        
        if query_text:
            must_clauses.append({
                "multi_match": {
                    "query": query_text,
                    "fields": ["Message", "Service", "User", "Level"]
                }
            })
        
        if level:
            must_clauses.append({"term": {"Level": level}})
        
        if service:
            must_clauses.append({"term": {"Service": service}})
        
        if start_date or end_date:
            date_range = {"@timestamp": {}}
            if start_date:
                date_range["@timestamp"]["gte"] = start_date
            if end_date:
                date_range["@timestamp"]["lte"] = end_date
            must_clauses.append({"range": date_range})
        
        if must_clauses:
            search_body = {
                "query": {
                    "bool": {
                        "must": must_clauses
                    }
                },
                "size": size,
                "from": from_param,
                "sort": [{"@timestamp": {"order": "desc"}}]
            }
        else:
            search_body = {
                "query": {"match_all": {}},
                "size": size,
                "from": from_param,
                "sort": [{"@timestamp": {"order": "desc"}}]
            }
        
        result = es_client.search(index='ecommerce-logs-*', body=search_body)
        
        hits = []
        for hit in result['hits']['hits']:
            source = hit['_source']
            
            # Helper function to get service from multiple possible fields
            def get_service_name(src):
                # Try different field name variations
                service_fields = ['Service', 'service', 'source', 'Source', 'event', 'Event', 
                                'application', 'Application', 'app', 'App', 'component', 'Component']
                for field in service_fields:
                    if field in src and src[field]:
                        return src[field]
                # If no service field found, try to infer from other fields
                if 'product_name' in src or 'customer_name' in src:
                    return 'E-commerce'
                return 'Application'
            
            # Handle different document types
            if 'Level' in source:
                # Standard log format
                hits.append({
                    "_id": hit['_id'],
                    "timestamp": source.get('@timestamp', ''),
                    "level": source.get('Level', ''),
                    "service": get_service_name(source),
                    "message": source.get('Message', ''),
                    "user": source.get('User', '')
                })
            elif 'event' in source:
                # E-commerce event format
                hits.append({
                    "_id": hit['_id'],
                    "timestamp": source.get('@timestamp', ''),
                    "level": "INFO",
                    "service": source.get('event', 'E-commerce'),
                    "message": f"{source.get('event', '')} - User: {source.get('user', '')} - Page: {source.get('page', '')}",
                    "user": source.get('user', '')
                })
            else:
                # Generic format
                hits.append({
                    "_id": hit['_id'],
                    "timestamp": source.get('@timestamp', ''),
                    "level": source.get('level', source.get('severity', 'INFO')),
                    "service": get_service_name(source),
                    "message": source.get('message', source.get('msg', str(source))),
                    "user": source.get('user', source.get('User', ''))
                })
        
        return jsonify({
            'total': result['hits']['total']['value'],
            'hits': hits,
            'took': result['took']
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/export/csv', methods=['GET'])
def export_to_csv():
    """Export search results to CSV file"""
    if es_client is None:
        return jsonify({'error': 'Elasticsearch not connected'}), 500
    
    try:
        # Get filters from query parameters
        query = request.args.get('q', '')
        level = request.args.get('level', '')
        service = request.args.get('service', '')
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        
        # Build Elasticsearch query (same as search endpoint)
        must = []
        if query:
            must.append({"query_string": {"query": f"*{query}*", "fields": ["*"]}})
        if level:
            must.append({"match": {"Level": level}})
        if service:
            must.append({"match": {"Service": service}})
        if start_date or end_date:
            date_range = {}
            if start_date:
                date_range["gte"] = start_date
            if end_date:
                date_range["lte"] = end_date
            must.append({"range": {"@timestamp": date_range}})
        
        search_body = {
            "query": {"bool": {"must": must}} if must else {"match_all": {}},
            "size": 10000,  # Export up to 10000 records
            "sort": [{"@timestamp": {"order": "desc"}}]
        }
        
        result = es_client.search(index='ecommerce-logs-*', body=search_body)
        
        # Create CSV in memory
        output = io.StringIO()
        csv_writer = csv.writer(output)
        
        # Write header
        csv_writer.writerow(['Timestamp', 'Level', 'Service', 'Message', 'User'])
        
        # Helper function to get service from multiple possible fields
        def get_service_name(src):
            service_fields = ['Service', 'service', 'source', 'Source', 'event', 'Event', 
                            'application', 'Application', 'app', 'App', 'component', 'Component']
            for field in service_fields:
                if field in src and src[field]:
                    return src[field]
            if 'product_name' in src or 'customer_name' in src:
                return 'E-commerce'
            return 'Application'
        
        # Write data rows
        for hit in result['hits']['hits']:
            source = hit['_source']
            
            # Handle different document types (same logic as search)
            if 'Level' in source:
                row = [
                    source.get('@timestamp', ''),
                    source.get('Level', ''),
                    get_service_name(source),
                    source.get('Message', ''),
                    source.get('User', '')
                ]
            elif 'event' in source:
                row = [
                    source.get('@timestamp', ''),
                    'INFO',
                    source.get('event', 'E-commerce'),
                    f"{source.get('event', '')} - User: {source.get('user', '')} - Page: {source.get('page', '')}",
                    source.get('user', '')
                ]
            else:
                row = [
                    source.get('@timestamp', ''),
                    source.get('level', source.get('severity', 'INFO')),
                    get_service_name(source),
                    source.get('message', source.get('msg', str(source))),
                    source.get('user', source.get('User', ''))
                ]
            
            csv_writer.writerow(row)
        
        # Prepare response
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=logs_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return response
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/results', methods=['GET'])
def get_results():
    """Get aggregated results and analytics from Elasticsearch"""
    if es_client is None:
        return jsonify({'error': 'Elasticsearch not connected'}), 500
    
    try:
        index = request.args.get('index', 'ecommerce-logs-*')
        
        # Complex aggregation query
        agg_body = {
            "size": 0,
            "aggs": {
                "total_revenue": {
                    "sum": {"field": "total_amount"}
                },
                "total_orders": {
                    "value_count": {"field": "order_id"}
                },
                "avg_order_value": {
                    "avg": {"field": "total_amount"}
                },
                "unique_customers": {
                    "cardinality": {"field": "customer_id"}
                },
                "orders_by_country": {
                    "terms": {
                        "field": "customer_country",
                        "size": 10
                    },
                    "aggs": {
                        "country_revenue": {
                            "sum": {"field": "total_amount"}
                        }
                    }
                },
                "top_products": {
                    "terms": {
                        "field": "product_name.keyword",
                        "size": 10,
                        "order": {"product_revenue": "desc"}
                    },
                    "aggs": {
                        "product_revenue": {
                            "sum": {"field": "total_amount"}
                        },
                        "quantity_sold": {
                            "sum": {"field": "quantity"}
                        }
                    }
                },
                "orders_by_category": {
                    "terms": {
                        "field": "product_category",
                        "size": 10
                    }
                },
                "orders_over_time": {
                    "date_histogram": {
                        "field": "@timestamp",
                        "calendar_interval": "hour"
                    },
                    "aggs": {
                        "hourly_revenue": {
                            "sum": {"field": "total_amount"}
                        }
                    }
                },
                "payment_methods": {
                    "terms": {
                        "field": "payment_method",
                        "size": 10
                    }
                },
                "order_status": {
                    "terms": {
                        "field": "order_status",
                        "size": 10
                    }
                }
            }
        }
        
        result = es_client.search(index=index, body=agg_body)
        aggs = result['aggregations']
        
        # Format response
        response = {
            'summary': {
                'total_revenue': round(aggs['total_revenue']['value'], 2),
                'total_orders': aggs['total_orders']['value'],
                'avg_order_value': round(aggs['avg_order_value']['value'], 2),
                'unique_customers': aggs['unique_customers']['value']
            },
            'by_country': [
                {
                    'country': bucket['key'],
                    'orders': bucket['doc_count'],
                    'revenue': round(bucket['country_revenue']['value'], 2)
                }
                for bucket in aggs['orders_by_country']['buckets']
            ],
            'top_products': [
                {
                    'product': bucket['key'],
                    'orders': bucket['doc_count'],
                    'revenue': round(bucket['product_revenue']['value'], 2),
                    'quantity': bucket['quantity_sold']['value']
                }
                for bucket in aggs['top_products']['buckets']
            ],
            'by_category': [
                {
                    'category': bucket['key'],
                    'count': bucket['doc_count']
                }
                for bucket in aggs['orders_by_category']['buckets']
            ],
            'over_time': [
                {
                    'timestamp': bucket['key_as_string'],
                    'orders': bucket['doc_count'],
                    'revenue': round(bucket['hourly_revenue']['value'], 2)
                }
                for bucket in aggs['orders_over_time']['buckets']
            ],
            'payment_methods': [
                {
                    'method': bucket['key'],
                    'count': bucket['doc_count']
                }
                for bucket in aggs['payment_methods']['buckets']
            ],
            'order_status': [
                {
                    'status': bucket['key'],
                    'count': bucket['doc_count']
                }
                for bucket in aggs['order_status']['buckets']
            ]
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/files', methods=['GET'])
def list_files():
    """List all uploaded files"""
    try:
        files = []
        upload_folder = app.config['UPLOAD_FOLDER']
        print(f"[DEBUG] Checking upload folder: {upload_folder}")
        print(f"[DEBUG] Folder exists: {os.path.exists(upload_folder)}")
        
        # Get files from upload folder
        if os.path.exists(upload_folder):
            file_list = os.listdir(upload_folder)
            print(f"[DEBUG] Found {len(file_list)} files: {file_list[:3]}")
            
            for filename in file_list:
                filepath = os.path.join(upload_folder, filename)
                
                # Try to get metadata from Redis
                file_info = None
                if redis_client:
                    cached_info = redis_client.get(f"file:{filename}")
                    if cached_info:
                        file_info = json.loads(cached_info)
                
                # If not in Redis, create basic info
                if not file_info:
                    file_info = {
                        'filename': filename,
                        'size': os.path.getsize(filepath),
                        'upload_time': datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat(),
                        'type': filename.rsplit('.', 1)[1].lower() if '.' in filename else 'unknown'
                    }
                else:
                    # Ensure upload_time field exists for Redis cached files
                    if 'uploaded_at' in file_info and 'upload_time' not in file_info:
                        file_info['upload_time'] = file_info['uploaded_at']
                
                files.append(file_info)
        
        # Sort by upload time (most recent first)
        files.sort(key=lambda x: x.get('upload_time', x.get('uploaded_at', x.get('modified', ''))), reverse=True)
        
        return jsonify({
            'count': len(files),
            'files': files
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get system statistics and health metrics"""
    try:
        stats = {
            'timestamp': datetime.now().isoformat(),
            'services': {
                'elasticsearch': 'connected' if es_client else 'disconnected',
                'mongodb': 'connected' if db is not None else 'disconnected',
                'redis': 'connected' if redis_client else 'disconnected'
            },
            'data': {}
        }
        
        # Elasticsearch stats
        if es_client:
            try:
                # Get index stats
                indices_info = es_client.cat.indices(index='ecommerce-logs-*', format='json')
                total_docs = sum(int(idx.get('docs.count', 0)) for idx in indices_info)
                total_size = sum(float(idx.get('store.size', '0b').replace('kb', '').replace('mb', '').replace('gb', '')) for idx in indices_info)
                
                stats['data']['elasticsearch'] = {
                    'total_documents': total_docs,
                    'total_indices': len(indices_info),
                    'indices': [
                        {
                            'name': idx['index'],
                            'documents': int(idx.get('docs.count', 0)),
                            'size': idx.get('store.size', 'N/A')
                        }
                        for idx in indices_info
                    ]
                }
            except Exception as e:
                stats['data']['elasticsearch'] = {'error': str(e)}
        
        # MongoDB stats
        if db is not None:
            try:
                stats['data']['mongodb'] = {
                    'products_count': db.products.count_documents({}),
                    'uploads_count': db.uploads.count_documents({}),
                    'collections': db.list_collection_names()
                }
            except Exception as e:
                stats['data']['mongodb'] = {'error': str(e)}
        
        # Redis stats
        if redis_client:
            try:
                info = redis_client.info()
                stats['data']['redis'] = {
                    'connected_clients': info.get('connected_clients', 0),
                    'used_memory': info.get('used_memory_human', 'N/A'),
                    'total_keys': redis_client.dbsize()
                }
            except Exception as e:
                stats['data']['redis'] = {'error': str(e)}
        
        # File system stats
        try:
            if os.path.exists(app.config['UPLOAD_FOLDER']):
                files = os.listdir(app.config['UPLOAD_FOLDER'])
                total_size = sum(
                    os.path.getsize(os.path.join(app.config['UPLOAD_FOLDER'], f))
                    for f in files
                )
                stats['data']['filesystem'] = {
                    'upload_folder': app.config['UPLOAD_FOLDER'],
                    'total_files': len(files),
                    'total_size_bytes': total_size,
                    'total_size_mb': round(total_size / (1024 * 1024), 2)
                }
        except Exception as e:
            stats['data']['filesystem'] = {'error': str(e)}
        
        return jsonify(stats)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/dashboard', methods=['GET'])
@cache_response(CacheType.DASHBOARD, ttl=300)  # Cache 5 minutes
def get_dashboard():
    """Get dashboard statistics - Cached for better performance"""
    if es_client is None:
        return jsonify({'error': 'Elasticsearch not connected'}), 500
    
    try:
        # Get total logs count
        total_logs = es_client.count(index='ecommerce-logs-*')['count']
        
        # Get logs from today
        today_query = {
            "query": {
                "range": {
                    "@timestamp": {
                        "gte": "now/d",
                        "lte": "now"
                    }
                }
            }
        }
        logs_today = es_client.count(index='ecommerce-logs-*', body=today_query)['count']
        
        # Get error logs count
        error_query = {
            "query": {
                "term": {"Level": "ERROR"}
            }
        }
        error_logs = es_client.count(index='ecommerce-logs-*', body=error_query)['count']
        
        # Get files count from uploads folder
        files_uploaded = 0
        if os.path.exists(app.config['UPLOAD_FOLDER']):
            files_uploaded = len(os.listdir(app.config['UPLOAD_FOLDER']))
        
        # Get logs by level aggregation
        agg_query = {
            "size": 0,
            "aggs": {
                "by_level": {
                    "terms": {"field": "Level", "size": 10}
                }
            }
        }
        agg_result = es_client.search(index='ecommerce-logs-*', body=agg_query)
        logs_by_level = [
            {"level": bucket['key'], "count": bucket['doc_count']}
            for bucket in agg_result['aggregations']['by_level']['buckets']
        ]
        
        # Get recent logs
        recent_query = {
            "query": {"match_all": {}},
            "size": 10,
            "sort": [{"@timestamp": {"order": "desc"}}]
        }
        recent_result = es_client.search(index='ecommerce-logs-*', body=recent_query)
        recent_logs = []
        
        # Helper function to get service from multiple possible fields
        def get_service_name(src):
            service_fields = ['Service', 'service', 'source', 'Source', 'event', 'Event', 
                            'application', 'Application', 'app', 'App', 'component', 'Component']
            for field in service_fields:
                if field in src and src[field]:
                    return src[field]
            if 'product_name' in src or 'customer_name' in src:
                return 'E-commerce'
            return 'Application'
        
        for hit in recent_result['hits']['hits']:
            source = hit['_source']
            # Handle different document types
            if 'Level' in source:
                # Standard log format
                recent_logs.append({
                    "_id": hit['_id'],
                    "timestamp": source.get('@timestamp', ''),
                    "level": source.get('Level', ''),
                    "service": get_service_name(source),
                    "message": source.get('Message', '')
                })
            elif 'event' in source:
                # E-commerce event format
                recent_logs.append({
                    "_id": hit['_id'],
                    "timestamp": source.get('@timestamp', ''),
                    "level": "INFO",
                    "service": source.get('event', 'E-commerce'),
                    "message": f"{source.get('event', '')} - User: {source.get('user', '')} - Page: {source.get('page', '')}"
                })
            else:
                # Generic format
                recent_logs.append({
                    "_id": hit['_id'],
                    "timestamp": source.get('@timestamp', ''),
                    "level": source.get('level', source.get('severity', 'INFO')),
                    "service": get_service_name(source),
                    "message": source.get('message', source.get('msg', str(source)))
                })

        
        # Get logs over time (last 7 days)
        time_agg_query = {
            "size": 0,
            "query": {
                "range": {
                    "@timestamp": {
                        "gte": "now-7d/d"
                    }
                }
            },
            "aggs": {
                "by_date": {
                    "date_histogram": {
                        "field": "@timestamp",
                        "calendar_interval": "day"
                    }
                }
            }
        }
        time_result = es_client.search(index='ecommerce-logs-*', body=time_agg_query)
        logs_over_time = [
            {"date": bucket['key_as_string'][:10], "count": bucket['doc_count']}
            for bucket in time_result['aggregations']['by_date']['buckets']
        ]
        
        return jsonify({
            "total_logs": total_logs,
            "logs_today": logs_today,
            "error_logs": error_logs,
            "files_uploaded": files_uploaded,
            "logs_by_level": logs_by_level,
            "logs_over_time": logs_over_time,
            "recent_logs": recent_logs
        })
    
    except Exception as e:
        print(f"Dashboard error: {e}")
        return jsonify({
            "total_logs": 0,
            "logs_today": 0,
            "error_logs": 0,
            "files_uploaded": 0,
            "logs_by_level": [],
            "logs_over_time": [],
            "recent_logs": []
        })


@app.route('/api/search/products', methods=['GET'])
def search_products():
    """Search products in Elasticsearch"""
    if es_client is None:
        return jsonify({'error': 'Elasticsearch not connected'}), 500
    
    try:
        query = request.args.get('q', '')
        
        search_body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["name", "description", "category"]
                }
            }
        }
        
        result = es_client.search(index='products', body=search_body)
        hits = result['hits']['hits']
        
        products = [hit['_source'] for hit in hits]
        
        return jsonify({
            'count': len(products),
            'query': query,
            'products': products
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/searches/recent', methods=['GET'])
def get_recent_searches():
    """Get recent searches from MongoDB"""
    try:
        limit = int(request.args.get('limit', 5))
        
        if db is None:
            return jsonify([])
        
        # Get recent searches from MongoDB
        searches = list(db.search_history.find(
            {},
            {'_id': 0}
        ).sort('timestamp', -1).limit(limit))
        
        return jsonify(searches)
    except Exception as e:
        print(f"Error getting recent searches: {e}")
        return jsonify([])


@app.route('/api/searches/save', methods=['POST'])
def save_search():
    """Save search to MongoDB"""
    try:
        data = request.json
        
        if db is None:
            return jsonify({'error': 'MongoDB not connected'}), 500
        
        search_record = {
            'query': data.get('query', ''),
            'level': data.get('level'),
            'service': data.get('service'),
            'start_date': data.get('startDate'),
            'end_date': data.get('endDate'),
            'results_count': data.get('resultsCount', 0),
            'timestamp': datetime.now().isoformat()
        }
        
        result = db.search_history.insert_one(search_record)
        
        return jsonify({
            'success': True,
            'id': str(result.inserted_id)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# --- Enregistrement du blueprint d'authentification ---
app.register_blueprint(auth_bp)

print("[OK] Authentication blueprint registered at /api/auth")


# --- Routes de gestion du cache ---
@app.route('/api/cache/stats', methods=['GET'])
def cache_stats():
    """Retourne les statistiques d'utilisation du cache"""
    stats = get_cache_stats()
    return jsonify({
        "status": "success",
        "cache_stats": stats,
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/cache/invalidate/<cache_type>', methods=['POST'])
def invalidate_cache_endpoint(cache_type):
    """
    Invalide tout le cache d'un type spécifique
    Types disponibles: dashboard, search, user, product, analytics
    """
    try:
        # Mapper le string au CacheType
        cache_type_map = {
            'dashboard': CacheType.DASHBOARD,
            'search': CacheType.SEARCH,
            'user': CacheType.USER,
            'product': CacheType.PRODUCT,
            'analytics': CacheType.ANALYTICS
        }
        
        if cache_type not in cache_type_map:
            return jsonify({
                "status": "error",
                "message": f"Invalid cache type. Available: {list(cache_type_map.keys())}"
            }), 400
        
        cache_type_enum = cache_type_map[cache_type]
        deleted_count = invalidate_cache_type(cache_type_enum)
        
        return jsonify({
            "status": "success",
            "cache_type": cache_type,
            "deleted_keys": deleted_count,
            "message": f"Cache '{cache_type}' invalidated successfully",
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/cache/invalidate-pattern', methods=['POST'])
def invalidate_cache_pattern_endpoint():
    """
    Invalide le cache selon un pattern
    Body: {"pattern": "cache:dashboard:*"}
    """
    try:
        data = request.get_json()
        pattern = data.get('pattern')
        
        if not pattern:
            return jsonify({
                "status": "error",
                "message": "Pattern is required"
            }), 400
        
        deleted_count = invalidate_pattern(pattern)
        
        return jsonify({
            "status": "success",
            "pattern": pattern,
            "deleted_keys": deleted_count,
            "message": f"Cache invalidated for pattern: {pattern}",
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/cache/clear-all', methods=['POST'])
def clear_all_cache():
    """Invalide TOUT le cache - À utiliser avec précaution"""
    try:
        deleted_count = invalidate_pattern("cache:*")
        
        return jsonify({
            "status": "success",
            "deleted_keys": deleted_count,
            "message": "All cache cleared",
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# --- Gestion CORS manuelle ---
@app.after_request
def add_cors_headers(response):
    """Ajoute les headers CORS à toutes les réponses"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Max-Age'] = '3600'
    return response


@app.before_request
def handle_options():
    """Gère les requêtes OPTIONS (preflight)"""
    if request.method == 'OPTIONS':
        response = make_response('', 200)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Max-Age'] = '3600'
        return response


# Route de test CORS
@app.route('/api/test-cors', methods=['GET', 'POST', 'OPTIONS'])
def test_cors():
    """Route de test pour vérifier CORS"""
    return jsonify({
        'message': 'CORS is working!',
        'method': request.method,
        'origin': request.headers.get('Origin', 'No origin header')
    })


# Route de debug pour lister toutes les routes
@app.route('/api/routes')
def list_routes():
    """Liste toutes les routes disponibles"""
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': sorted(rule.methods - {'HEAD', 'OPTIONS'}),
            'path': str(rule)
        })
    return jsonify({'routes': routes})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
