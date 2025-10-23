from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from functools import wraps
from datetime import datetime
import os
import logging

# App erstellen
app = Flask(__name__, static_folder='static')
CORS(app)

# Konfiguration
app.config['SECRET_KEY'] = 'dev-secret-key'
app.config['UPLOAD_FOLDER'] = './static/uploads'
app.config['MAX_IMAGE_SIZE'] = 1920

# Einfache In-Memory "Datenbank" für Tests
class MockDatabase:
    def __init__(self):
        self.api_keys = {
            'test_key_12345': {
                'user_id': 1,
                'organisation': 'Stadt Zürich - Test'
            }
        }
        self.schadenstypen = [
            {'typ_id': 1, 'bezeichnung': 'Schlagloch', 'beschreibung': 'Schlaglöcher und Fahrbahnschäden', 'icon_name': 'pothole', 'prioritaet': 1, 'sortierung': 10},
            {'typ_id': 2, 'bezeichnung': 'Beschädigtes Schild', 'beschreibung': 'Verkehrsschilder beschädigt', 'icon_name': 'sign', 'prioritaet': 2, 'sortierung': 20},
            {'typ_id': 3, 'bezeichnung': 'Defekte Beleuchtung', 'beschreibung': 'Straßenbeleuchtung defekt', 'icon_name': 'light', 'prioritaet': 2, 'sortierung': 30},
            {'typ_id': 4, 'bezeichnung': 'Kanalisationsschaden', 'beschreibung': 'Schäden an Kanalisation', 'icon_name': 'drain', 'prioritaet': 1, 'sortierung': 40},
            {'typ_id': 5, 'bezeichnung': 'Vegetationsproblem', 'beschreibung': 'Bäume/Sträucher behindern Verkehr', 'icon_name': 'tree', 'prioritaet': 3, 'sortierung': 50}
        ]
        self.schadensmeldungen = []
        self.next_id = 1

mock_db = MockDatabase()

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({
                'error': 'API-Key fehlt',
                'message': 'Bitte X-API-Key im Header mitschicken'
            }), 401
        
        if api_key not in mock_db.api_keys:
            return jsonify({
                'error': 'Ungültiger API-Key',
                'message': 'API-Key nicht gefunden'
            }), 401
        
        request.user_id = mock_db.api_keys[api_key]['user_id']
        request.organisation = mock_db.api_keys[api_key]['organisation']
        
        return f(*args, **kwargs)
    return decorated_function

def validate_coordinates(lat, lon):
    """Einfache Koordinaten-Validierung für Schweiz"""
    if not (45.0 <= lat <= 48.0):
        return False, "Latitude außerhalb Schweiz"
    if not (5.0 <= lon <= 11.0):
        return False, "Longitude außerhalb Schweiz"
    return True, "OK"

# Routes
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'environment': 'development',
        'endpoints': {
            'health': 'GET /health',
            'damage_types': 'GET /api/v1/damage/types',
            'submit_damage': 'POST /api/v1/damage/submit',
            'list_damages': 'GET /api/v1/damage/list',
            'damage_detail': 'GET /api/v1/damage/<id>'
        }
    }), 200

@app.route('/api/v1/damage/types', methods=['GET'])
@require_api_key
def get_damage_types():
    return jsonify({
        'damage_types': mock_db.schadenstypen
    }), 200

@app.route('/api/v1/damage/submit', methods=['POST'])
@require_api_key
def submit_damage():
    try:
        data = request.get_json()
        
        # Validierung
        required_fields = ['damage_type', 'description', 'latitude', 'longitude']
        missing = [f for f in required_fields if f not in data]
        if missing:
            return jsonify({
                'error': 'Unvollständige Daten',
                'missing_fields': missing
            }), 400
        
        # Koordinaten validieren
        lat = float(data['latitude'])
        lon = float(data['longitude'])
        valid, msg = validate_coordinates(lat, lon)
        if not valid:
            return jsonify({
                'error': 'Ungültige Koordinaten',
                'message': msg
            }), 400
        
        # Schadensmeldung erstellen
        schaden_id = mock_db.next_id
        mock_db.next_id += 1
        
        new_damage = {
            'id': schaden_id,
            'schadentyp': data['damage_type'],
            'beschreibung': data['description'],
            'latitude': lat,
            'longitude': lon,
            'foto_pfad': '/static/uploads/mock_photo.jpg',
            'user_id': request.user_id,
            'organisation': request.organisation,
            'status': 'neu',
            'erstellt': datetime.now().isoformat(),
            'zusatzdaten': data.get('additional_data', {})
        }
        
        mock_db.schadensmeldungen.append(new_damage)
        
        response = {
            'success': True,
            'damage_id': schaden_id,
            'created_at': new_damage['erstellt'],
            'message': 'Schadensmeldung erfolgreich erfasst'
        }
        
        print(f"✅ Neue Schadensmeldung: ID={schaden_id}, Typ={data['damage_type']}")
        
        return jsonify(response), 201
        
    except Exception as e:
        print(f"❌ Fehler bei Schadensmeldung: {e}")
        return jsonify({
            'error': 'Server-Fehler',
            'message': str(e)
        }), 500

@app.route('/api/v1/damage/<int:damage_id>', methods=['GET'])
@require_api_key
def get_damage_details(damage_id):
    damage = next((d for d in mock_db.schadensmeldungen if d['id'] == damage_id), None)
    
    if not damage:
        return jsonify({
            'error': 'Schadensmeldung nicht gefunden'
        }), 404
    
    return jsonify(damage), 200

@app.route('/api/v1/damage/list', methods=['GET'])
@require_api_key
def list_damages():
    return jsonify({
        'damages': mock_db.schadensmeldungen,
        'total': len(mock_db.schadensmeldungen)
    }), 200

# Debug Endpoint
@app.route('/api/debug/data', methods=['GET'])
def debug_data():
    return jsonify({
        'schadenstypen': mock_db.schadenstypen,
        'schadensmeldungen': mock_db.schadensmeldungen,
        'api_keys': list(mock_db.api_keys.keys()),
        'total_damages': len(mock_db.schadensmeldungen)
    }), 200







@app.route('/api/v1/damage/map-data', methods=['GET'])
@require_api_key
def get_map_data():
    """Liefert Schadensdaten im GeoJSON Format für die Karte"""
    features = []
    
    for damage in mock_db.schadensmeldungen:
        feature = {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [damage['longitude'], damage['latitude']]
            },
            'properties': {
                'id': damage['id'],
                'schadentyp': damage['schadentyp'],
                'beschreibung': damage['beschreibung'],
                'status': damage['status'],
                'organisation': damage['organisation'],
                'erstellt': damage['erstellt']
            }
        }
        features.append(feature)
    
    geojson = {
        'type': 'FeatureCollection',
        'features': features
    }
    
    return jsonify(geojson), 200









if __name__ == '__main__':
    # Upload-Ordner erstellen
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    port = 5000
    
    print("🚀 Schadensmeldung API gestartet")
    print("=" * 50)
    print(f"📍 URL: http://localhost:{port}")
    print(f"🔑 Test-API-Key: test_key_12345")
    print("")
    print("📚 Verfügbare Endpoints:")
    print("   🌐 GET  /                    -> Web Interface")
    print("   🔍 GET  /health              -> API Status")
    print("   📋 GET  /api/v1/damage/types -> Schadenstypen")
    print("   📨 POST /api/v1/damage/submit-> Schaden melden")
    print("   📄 GET  /api/v1/damage/list  -> Schäden auflisten")
    print("   🔧 GET  /api/debug/data      -> Debug Daten")
    print("")
    print("💡 Tipp: Öffne http://localhost:5000 im Browser für die Web-Oberfläche!")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=port, debug=True)