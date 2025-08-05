# 🌐 WEB/ - SERVIDOR WEB Y API REST
# =============================================
# Directorio: src/web/ - Backend Web y APIs
# =============================================

## 📁 CONTENIDO DE WEB/

```
web/
├── 🌐 flask_app.py            # Servidor Flask principal - API REST
├── 📄 flask_app_backup.py     # Backup de versión anterior
└── 📁 __pycache__/           # Cache de Python compilado
```

## 🌐 flask_app.py - SERVIDOR FLASK PRINCIPAL

### PROPÓSITO
**Clase FlaskMusicApp**: Servidor web que expone API REST para controlar el reproductor desde interfaz web

### ARQUITECTURA DEL SERVIDOR
```python
class FlaskMusicApp:
    def __init__(self):
        self.app = Flask(__name__)        # Servidor Flask
        self.socketio = SocketIO(app)     # WebSockets para tiempo real
        self.music_app = MusicApp()       # Instancia del core de la aplicación
        self._setup_routes()              # Configurar endpoints
        self._setup_websockets()          # Configurar eventos WebSocket
```

### 📡 ENDPOINTS DE LA API REST

#### 🎵 CONTROL DE REPRODUCTOR
```python
# Control básico de reproducción
GET    /api/player/status         # Estado actual del reproductor
POST   /api/player/play           # Reproducir/pausar
POST   /api/player/stop           # Detener reproducción
POST   /api/player/next           # Siguiente canción
POST   /api/player/previous       # Canción anterior

# Control de volumen
GET    /api/player/volume         # Obtener volumen actual
POST   /api/player/volume         # Establecer volumen (0-100)

# Modos de reproducción
POST   /api/player/shuffle        # Toggle shuffle on/off
POST   /api/player/repeat         # Cycle repeat mode (none/one/all)
GET    /api/player/modes          # Obtener estado shuffle/repeat

# Control de posición
GET    /api/player/time           # Tiempo actual y duración
POST   /api/player/seek           # Saltar a posición específica
```

#### 📚 GESTIÓN DE BIBLIOTECA
```python
# Biblioteca musical
GET    /api/library              # Obtener toda la biblioteca
GET    /api/library/scan         # Escanear nuevas canciones
POST   /api/library/search       # Buscar canciones
GET    /api/library/song/:id     # Detalles de canción específica

# Metadatos y covers
GET    /api/song/:id/metadata    # Metadatos completos
GET    /api/song/:id/cover       # Imagen de portada
POST   /api/song/:id/play        # Reproducir canción específica
```

#### 📋 GESTIÓN DE PLAYLISTS
```python
# Playlists del usuario
GET    /api/playlists            # Obtener todas las playlists
POST   /api/playlists            # Crear nueva playlist
GET    /api/playlists/:id        # Obtener canciones de playlist
POST   /api/playlists/:id/songs  # Agregar canción a playlist
DELETE /api/playlists/:id/songs/:song_id  # Quitar canción

# Playlist actual
GET    /api/player/playlist      # Playlist en reproducción
POST   /api/player/playlist      # Establecer playlist activa
```

#### 🎨 EFECTOS VISUALES
```python
# Visualización en tiempo real
GET    /api/visualizer/spectrum  # Datos de espectro de audio
GET    /api/visualizer/config    # Configuración del visualizador
POST   /api/visualizer/config    # Actualizar configuración
```

### 🔄 WEBSOCKETS PARA TIEMPO REAL

#### 📡 EVENTOS EMITIDOS AL CLIENT
```python
@socketio.emit('player_status_update')
def broadcast_player_status():
    """Emite estado actual cada 1 segundo"""
    return {
        'is_playing': self.music_app.is_playing(),
        'current_song': self.music_app.get_current_song(),
        'position': self.music_app.get_position(),
        'volume': self.music_app.get_volume(),
        'shuffle': self.music_app.get_shuffle_state(),
        'repeat': self.music_app.get_repeat_mode()
    }

@socketio.emit('song_changed')
def on_song_change(song_data):
    """Notifica cuando cambia la canción"""
    return {
        'song': song_data,
        'timestamp': time.time()
    }

@socketio.emit('spectrum_data')
def send_spectrum_data():
    """Envía datos de espectro para visualización"""
    return {
        'spectrum': self.music_app.get_spectrum_data(),
        'timestamp': time.time()
    }
```

#### 📥 EVENTOS RECIBIDOS DEL CLIENT
```python
@socketio.on('connect')
def on_client_connect():
    """Cliente se conecta - enviar estado inicial"""
    emit('player_status_update', get_current_status())

@socketio.on('disconnect') 
def on_client_disconnect():
    """Cliente se desconecta - limpiar recursos"""
    pass

@socketio.on('request_update')
def on_request_update():
    """Cliente solicita actualización manual"""
    emit('player_status_update', get_current_status())
```

### 🔗 INTEGRACIÓN CON CORE

#### 🧠 LLAMADAS A CORE/APP.PY
```python
# Ejemplo de endpoint que llama al core
@app.route('/api/player/shuffle', methods=['POST'])
def toggle_shuffle():
    try:
        # Llamar método del core
        new_state = self.music_app.toggle_shuffle()
        
        # Log para debugging
        self.logger.info(f"🔀 Shuffle toggled: {new_state}")
        
        # Notificar via WebSocket
        socketio.emit('player_status_update', get_status())
        
        # Responder al client
        return jsonify({
            'success': True,
            'shuffle_enabled': new_state,
            'message': f"Shuffle {'activado' if new_state else 'desactivado'}"
        })
        
    except Exception as e:
        self.logger.error(f"Error en shuffle: {e}")
        return jsonify({'error': str(e)}), 500
```

#### 🔄 PATRÓN DE COMUNICACIÓN
```
Frontend JS → Flask Endpoint → Core App Method → Audio Engine → Response
```

### 🌐 CONFIGURACIÓN DEL SERVIDOR

#### ⚙️ CONFIGURACIÓN FLASK
```python
# Configuración de Flask
app.config.update({
    'SECRET_KEY': 'music_player_secret_key_2024',
    'SEND_FILE_MAX_AGE_DEFAULT': 31536000,  # Cache stático 1 año
    'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # Max upload 16MB
    'JSON_SORT_KEYS': False,                 # Mantener orden JSON
    'JSONIFY_PRETTYPRINT_REGULAR': True      # JSON legible
})

# CORS para desarrollo
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:5000"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

#### 🔌 CONFIGURACIÓN SOCKETIO
```python
# WebSocket configuration
socketio = SocketIO(app, 
    cors_allowed_origins="*",      # Permitir todos los orígenes
    async_mode='threading',        # Modo threading
    ping_timeout=60,               # Timeout de ping
    ping_interval=25,              # Intervalo de ping
    logger=True,                   # Logging habilitado
    engineio_logger=False          # Sin logs de engine.io
)
```

### 🔧 MANEJO DE ERRORES

#### ⚠️ ERROR HANDLERS GLOBALES
```python
@app.errorhandler(404)
def not_found(error):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Endpoint no encontrado'}), 404
    return render_template('index.html')  # SPA fallback

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Error interno: {error}")
    return jsonify({'error': 'Error interno del servidor'}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Excepción no manejada: {e}")
    return jsonify({'error': 'Error inesperado'}), 500
```

#### 🔒 VALIDACIÓN DE DATOS
```python
def validate_volume(volume):
    """Valida nivel de volumen (0-100)"""
    try:
        vol = int(volume)
        if 0 <= vol <= 100:
            return vol
        raise ValueError("Volumen fuera de rango")
    except ValueError:
        raise ValueError("Volumen debe ser número entre 0-100")

def validate_song_id(song_id):
    """Valida ID de canción"""
    if not song_id or not str(song_id).isdigit():
        raise ValueError("ID de canción inválido")
    return int(song_id)
```

### 📊 LOGGING Y MONITOREO

#### 📝 SISTEMA DE LOGS
```python
import logging
from datetime import datetime

# Configurar logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/flask_app.log'),
        logging.StreamHandler()
    ]
)

# Logs específicos con emojis para debugging
self.logger.info("🌐 Servidor Flask iniciado en puerto 5000")
self.logger.info("🔀 Shuffle activado por usuario")
self.logger.error("❌ Error al procesar petición de reproducción")
```

#### 📈 MÉTRICAS DE RENDIMIENTO
```python
from time import time

def track_api_performance(func):
    """Decorator para medir rendimiento de endpoints"""
    def wrapper(*args, **kwargs):
        start_time = time()
        result = func(*args, **kwargs)
        end_time = time()
        
        logger.info(f"⏱️ {func.__name__}: {end_time - start_time:.3f}s")
        return result
    return wrapper
```

### 🔒 SEGURIDAD

#### 🛡️ AUTENTICACIÓN BÁSICA
```python
from functools import wraps

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Por ahora sin autenticación - local use
        # TODO: Implementar autenticación para uso remoto
        return f(*args, **kwargs)
    return decorated
```

#### 🔐 SANITIZACIÓN DE ENTRADA
```python
import os
from pathlib import Path

def sanitize_file_path(path):
    """Sanitiza rutas de archivos para prevenir path traversal"""
    safe_path = os.path.normpath(path)
    if '..' in safe_path or safe_path.startswith('/'):
        raise ValueError("Ruta de archivo no permitida")
    return safe_path
```

### 🚀 INICIALIZACIÓN Y EJECUCIÓN

#### 🏁 FUNCIÓN MAIN
```python
def run_server(host='127.0.0.1', port=5000, debug=False):
    """Inicia el servidor Flask con SocketIO"""
    try:
        logger.info(f"🌐 Iniciando servidor en http://{host}:{port}")
        
        # Configurar rutas estáticas
        app.static_folder = 'static'
        app.template_folder = 'templates'
        
        # Iniciar servidor
        socketio.run(app, 
            host=host, 
            port=port, 
            debug=debug,
            use_reloader=False,  # Evitar doble inicio
            allow_unsafe_werkzeug=True
        )
        
    except Exception as e:
        logger.error(f"❌ Error al iniciar servidor: {e}")
        raise

if __name__ == '__main__':
    run_server(debug=True)
```

### 🔄 INTERCONEXIONES

#### 🧠 CON CORE/APP.PY
- Flask instancia MusicApp como self.music_app
- Todos los endpoints llaman métodos de music_app
- Recibe callbacks de cambio de estado

#### 🎨 CON EFFECTS/VISUAL_MANAGER.PY
- Obtiene datos de espectro via music_app
- Transmite datos via WebSocket a frontend
- Configura parámetros de visualización

#### 🌐 CON FRONTEND
- Sirve archivos estáticos desde static/
- Renderiza templates desde templates/
- API REST para todas las operaciones
- WebSocket para actualizaciones tiempo real

### ⚡ OPTIMIZACIONES

#### 🚀 PERFORMANCE
- Caching de respuestas frecuentes
- Compresión gzip para responses
- Lazy loading de biblioteca musical
- Pool de threads para WebSockets

#### 💾 MEMORIA
- Garbage collection manual
- Límites de memoria para uploads
- Streaming de archivos grandes
- Cache LRU para metadatos

### 🔌 PUNTOS DE EXTENSIÓN

1. **Nuevos Endpoints**: Agregar rutas en _setup_routes()
2. **Autenticación**: Implementar sistema de usuarios
3. **API Versioning**: Agregar /api/v2/ endpoints
4. **Rate Limiting**: Implementar límites de peticiones
5. **WebRTC**: Streaming directo de audio
6. **Multi-room**: Sincronización entre dispositivos

### ⚠️ DEPENDENCIAS CRÍTICAS

- **Flask**: Framework web (>=2.3.0)
- **Flask-SocketIO**: WebSockets (>=5.3.0)
- **Flask-CORS**: CORS headers (>=4.0.0)
- **python-socketio**: Cliente SocketIO (>=5.8.0)
