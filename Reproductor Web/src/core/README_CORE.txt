# 🧠 CORE/ - LÓGICA CENTRAL DE LA APLICACIÓN
# =============================================
# Directorio: src/core/ - Núcleo del Sistema
# =============================================

## 📁 CONTENIDO DE CORE/

```
core/
├── 🎯 app.py                  # Controlador principal - MusicApp class
├── 💾 database.py             # Gestor de base de datos SQLite
├── ⚙️ config_manager.py       # Gestión de configuración centralizada
└── 📁 __pycache__/           # Cache de Python compilado
```

## 🎯 app.py - CONTROLADOR MAESTRO

### PROPÓSITO
**Clase MusicApp**: Hub central que coordina todos los componentes del reproductor

### RESPONSABILIDADES CLAVE
```python
class MusicApp:
    # 🎵 Control de reproducción
    def play_song(song_path)           # Reproducir canción específica
    def play_pause()                   # Toggle play/pause
    def next_song()                    # Siguiente canción
    def previous_song()                # Canción anterior
    def stop()                         # Detener reproducción
    
    # 🔀 Modos de reproducción  
    def toggle_shuffle()               # Activar/desactivar shuffle
    def cycle_repeat_mode()            # Cambiar modo repeat (off/one/all)
    
    # 🔊 Control de audio
    def set_volume(level)              # Ajustar volumen (0-100)
    def get_volume()                   # Obtener volumen actual
    
    # 📚 Gestión de biblioteca
    def scan_library()                 # Escanear carpetas de música
    def get_library()                  # Obtener lista de canciones
    def search_songs(query)            # Buscar en biblioteca
    
    # 📋 Gestión de playlists
    def create_playlist(name)          # Crear nueva playlist
    def add_to_playlist(song, playlist) # Agregar canción a playlist
    def load_playlist(name)            # Cargar playlist específica
```

### INTERCONEXIONES
- **Controla**: `src/audio/vlc_engine.py` para reproducción
- **Usa**: `src/core/database.py` para persistencia
- **Usa**: `src/core/config_manager.py` para configuración
- **Controlado por**: `src/web/flask_app.py` via API calls

### CARACTERÍSTICAS TÉCNICAS
- ✅ **Shuffle Algorithm**: Genera índices aleatorios sin repetición
- ✅ **Repeat Modes**: None, One (repeat current), All (repeat playlist)
- ✅ **State Management**: Mantiene estado actual de reproducción
- ✅ **Thread Safe**: Maneja concurrencia para web requests

## 💾 database.py - GESTOR DE BASE DE DATOS

### PROPÓSITO
Gestiona toda la persistencia de datos usando SQLite

### FUNCIONALIDADES
```python
class DatabaseManager:
    # 📚 Biblioteca musical
    def add_song(metadata)             # Agregar canción a biblioteca
    def get_all_songs()                # Obtener todas las canciones
    def search_songs(query)            # Búsqueda por título/artista/álbum
    def update_song_metadata(song_id)  # Actualizar metadatos
    
    # 📋 Playlists
    def create_playlist(name)          # Crear nueva playlist
    def get_playlists()                # Obtener todas las playlists
    def add_song_to_playlist(song_id, playlist_id)
    def get_playlist_songs(playlist_id)
    
    # 📊 Estadísticas
    def update_play_count(song_id)     # Incrementar contador de reproducciones
    def get_most_played()              # Canciones más reproducidas
    def track_listening_history()      # Historial de reproducción
```

### ESQUEMA DE BASE DE DATOS
```sql
-- Tabla principal de canciones
songs:
    id (INTEGER PRIMARY KEY)
    title (TEXT)
    artist (TEXT)
    album (TEXT)
    file_path (TEXT UNIQUE)
    duration (INTEGER)
    play_count (INTEGER DEFAULT 0)
    date_added (TIMESTAMP)

-- Playlists del usuario
playlists:
    id (INTEGER PRIMARY KEY)
    name (TEXT UNIQUE)
    date_created (TIMESTAMP)

-- Relación muchos-a-muchos
playlist_songs:
    playlist_id (INTEGER)
    song_id (INTEGER)
    order_index (INTEGER)
```

### UBICACIÓN DE ARCHIVOS
- **Base de datos principal**: `data/music_library.db`
- **Backup automático**: `data/music_database.db`
- **WAL files**: `data/music_library.db-wal`, `data/music_library.db-shm`

## ⚙️ config_manager.py - GESTOR DE CONFIGURACIÓN

### PROPÓSITO
Maneja toda la configuración de la aplicación de forma centralizada

### CONFIGURACIONES GESTIONADAS
```python
class ConfigManager:
    # 🎵 Configuración de audio
    default_volume = 50                # Volumen inicial
    audio_format_preferences = [...]   # Formatos soportados
    
    # 📁 Configuración de biblioteca
    music_folders = [...]              # Carpetas a escanear
    auto_scan_enabled = True           # Escaneo automático
    
    # 🌐 Configuración web
    web_port = 5000                    # Puerto del servidor
    websocket_enabled = True           # WebSockets habilitados
    
    # 🎨 Configuración de efectos
    visualizer_enabled = True          # Efectos visuales
    spectrum_resolution = 256          # Resolución del espectro
    
    # 💾 Configuración de persistencia
    save_state_on_exit = True          # Guardar estado al salir
    backup_database = True             # Backup automático
```

### ARCHIVOS DE CONFIGURACIÓN
- **Configuración principal**: `config/app_config.json`
- **Preferencias usuario**: `data/user_preferences.json`
- **Configuración de temas**: `themes/` (múltiples archivos)

### CARGA Y GUARDADO
```python
# Carga automática al iniciar
config = ConfigManager.load_config()

# Guardado automático al cambiar
config.set_volume(75)  # Se guarda automáticamente
config.add_music_folder("/path/to/music")  # Persiste inmediatamente
```

## 🔄 FLUJO DE COMUNICACIÓN EN CORE/

### 1️⃣ INICIALIZACIÓN
```
config_manager.py → Carga configuración
        ↓
database.py → Conecta/crea base de datos
        ↓
app.py → Inicializa MusicApp con config y DB
```

### 2️⃣ OPERACIÓN NORMAL
```
web/flask_app.py → app.py (método específico)
        ↓
app.py → database.py (si necesita datos)
        ↓
app.py → audio/vlc_engine.py (para reproducción)
        ↓
app.py → config_manager.py (si necesita configuración)
```

### 3️⃣ PERSISTENCIA
```
Cualquier cambio → config_manager.py/database.py
        ↓
Guardado automático en archivos correspondientes
```

## ⚡ CARACTERÍSTICAS AVANZADAS

### 🧵 THREAD SAFETY
- Todos los métodos son thread-safe para web requests
- Uso de locks para evitar race conditions
- State management consistente

### 🔄 AUTO-RECOVERY
- Backup automático de base de datos
- Restauración de estado al reiniciar
- Manejo de errores con fallbacks

### 📊 PERFORMANCE
- Caching de consultas frecuentes
- Lazy loading de metadatos
- Optimización de queries SQLite

### 🔌 EXTENSIBILIDAD
- Plugin system compatible
- Event hooks para extensiones
- API interna documentada

## 🚀 PUNTOS DE EXTENSIÓN

1. **Nuevas Fuentes de Música**: Extender database.py para streaming
2. **Configuraciones Adicionales**: Agregar parámetros en config_manager.py
3. **Nuevos Modos de Reproducción**: Extender app.py con nuevos algoritmos
4. **Analytics**: Agregar tracking en database.py
5. **Sincronización Cloud**: Extender config_manager.py para sync

## ⚠️ DEPENDENCIAS CRÍTICAS

- **SQLite3**: Base de datos (incluido en Python)
- **JSON**: Configuración (incluido en Python)
- **Threading**: Concurrencia (incluido en Python)
- **Logging**: Debug y monitoreo (incluido en Python)
- **Mutagen**: Metadatos de audio (external dependency)
