# 💾 DATA/ - ALMACENAMIENTO Y PERSISTENCIA
# =============================================
# Directorio: data/ - Bases de Datos y Configuración
# =============================================

## 📁 CONTENIDO DE DATA/

```
data/
├── 💾 music_library.db         # Base de datos principal SQLite
├── 🔄 music_library.db-wal     # Write-Ahead Log (SQLite)
├── 🔄 music_library.db-shm     # Shared Memory (SQLite)
├── 💾 music_database.db        # Base de datos backup/alternativa
└── ⚙️ user_preferences.json    # Preferencias del usuario
```

## 💾 BASES DE DATOS SQLITE

### 🎯 music_library.db - BASE DE DATOS PRINCIPAL
**Propósito**: Almacenamiento central de toda la información musical

#### 📊 ESQUEMA DE TABLAS

```sql
-- 🎵 Tabla principal de canciones
CREATE TABLE songs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    artist TEXT,
    album TEXT,
    genre TEXT,
    year INTEGER,
    duration INTEGER,              -- Duración en segundos
    file_path TEXT UNIQUE NOT NULL,
    file_size INTEGER,
    bitrate INTEGER,
    sample_rate INTEGER,
    channels INTEGER,
    format TEXT,                   -- MP3, FLAC, WAV, etc.
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    play_count INTEGER DEFAULT 0,
    last_played TIMESTAMP,
    rating INTEGER DEFAULT 0,     -- Rating 1-5 estrellas
    favorite BOOLEAN DEFAULT 0
);

-- 🎨 Tabla de álbumes
CREATE TABLE albums (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    artist TEXT,
    year INTEGER,
    genre TEXT,
    cover_path TEXT,              -- Ruta a imagen de portada
    total_tracks INTEGER,
    total_duration INTEGER,
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 👤 Tabla de artistas
CREATE TABLE artists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    genre TEXT,
    country TEXT,
    formed_year INTEGER,
    bio TEXT,
    image_path TEXT,
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 📋 Tabla de playlists
CREATE TABLE playlists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    cover_path TEXT,
    is_public BOOLEAN DEFAULT 0,
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_tracks INTEGER DEFAULT 0,
    total_duration INTEGER DEFAULT 0
);

-- 🔗 Relación playlist-canciones (muchos a muchos)
CREATE TABLE playlist_songs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    playlist_id INTEGER NOT NULL,
    song_id INTEGER NOT NULL,
    order_index INTEGER NOT NULL,
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (playlist_id) REFERENCES playlists(id) ON DELETE CASCADE,
    FOREIGN KEY (song_id) REFERENCES songs(id) ON DELETE CASCADE,
    UNIQUE(playlist_id, song_id)
);

-- 📊 Tabla de historial de reproducción
CREATE TABLE play_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    song_id INTEGER NOT NULL,
    played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duration_played INTEGER,      -- Segundos reproducidos
    completion_rate REAL,         -- % de la canción reproducida
    FOREIGN KEY (song_id) REFERENCES songs(id) ON DELETE CASCADE
);

-- 🏷️ Tabla de etiquetas/tags
CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    color TEXT DEFAULT '#6C5CE7',
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 🔗 Relación canción-etiquetas (muchos a muchos)
CREATE TABLE song_tags (
    song_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (song_id, tag_id),
    FOREIGN KEY (song_id) REFERENCES songs(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);
```

#### 🔍 ÍNDICES PARA PERFORMANCE
```sql
-- Índices para búsquedas rápidas
CREATE INDEX idx_songs_title ON songs(title);
CREATE INDEX idx_songs_artist ON songs(artist);
CREATE INDEX idx_songs_album ON songs(album);
CREATE INDEX idx_songs_genre ON songs(genre);
CREATE INDEX idx_songs_file_path ON songs(file_path);
CREATE INDEX idx_songs_play_count ON songs(play_count DESC);
CREATE INDEX idx_songs_date_added ON songs(date_added DESC);

-- Índices para relaciones
CREATE INDEX idx_playlist_songs_playlist ON playlist_songs(playlist_id);
CREATE INDEX idx_playlist_songs_order ON playlist_songs(playlist_id, order_index);
CREATE INDEX idx_play_history_song ON play_history(song_id);
CREATE INDEX idx_play_history_date ON play_history(played_at DESC);
```

#### 📈 TRIGGERS PARA AUTOMATIZACIÓN
```sql
-- Trigger para actualizar fecha de modificación
CREATE TRIGGER update_song_modified 
    AFTER UPDATE ON songs
BEGIN
    UPDATE songs SET date_modified = CURRENT_TIMESTAMP 
    WHERE id = NEW.id;
END;

-- Trigger para actualizar contador de pistas en playlist
CREATE TRIGGER update_playlist_track_count_insert
    AFTER INSERT ON playlist_songs
BEGIN
    UPDATE playlists 
    SET total_tracks = (
        SELECT COUNT(*) FROM playlist_songs WHERE playlist_id = NEW.playlist_id
    )
    WHERE id = NEW.playlist_id;
END;

-- Trigger para limpiar historial antiguo (>6 meses)
CREATE TRIGGER cleanup_old_history
    AFTER INSERT ON play_history
BEGIN
    DELETE FROM play_history 
    WHERE played_at < datetime('now', '-6 months');
END;
```

### 🔄 ARCHIVOS WAL (Write-Ahead Logging)

#### 📝 music_library.db-wal
**Propósito**: Write-Ahead Log para transacciones SQLite
- Mejora rendimiento de escritura
- Permite lecturas concurrentes durante escrituras
- Se vacía automáticamente al hacer checkpoint

#### 🔄 music_library.db-shm  
**Propósito**: Shared Memory para sincronización WAL
- Coordina acceso entre procesos
- Metadatos del WAL file
- Se recrea automáticamente si se elimina

### 💾 music_database.db - BASE DE DATOS BACKUP
**Propósito**: Respaldo automático o base de datos alternativa
- Backup periódico de music_library.db
- Usado para testing sin afectar datos principales
- Punto de restauración en caso de corrupción

## ⚙️ user_preferences.json - CONFIGURACIÓN DE USUARIO

### ESTRUCTURA DEL ARCHIVO
```json
{
    "version": "1.0",
    "last_updated": "2024-01-15T10:30:00Z",
    
    "audio": {
        "volume": 50,
        "muted": false,
        "shuffle": false,
        "repeat": "none",
        "crossfade_duration": 3,
        "equalizer": {
            "enabled": false,
            "preset": "flat",
            "bands": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        }
    },
    
    "playback": {
        "auto_play": true,
        "remember_position": true,
        "gapless_playback": true,
        "fade_in_out": true,
        "normalize_volume": false
    },
    
    "library": {
        "scan_folders": [
            "C:\\Users\\Steven\\Music",
            "D:\\Mi Música"
        ],
        "auto_scan": true,
        "scan_interval": 1440,
        "watch_folders": true,
        "include_formats": ["mp3", "flac", "wav", "aac", "ogg", "m4a"],
        "min_file_size": 1024,
        "max_file_size": 1073741824
    },
    
    "interface": {
        "theme": "dark",
        "language": "es",
        "startup_view": "library",
        "compact_mode": false,
        "show_visualizer": true,
        "visualizer_type": "spectrum",
        "grid_view": true,
        "songs_per_page": 50
    },
    
    "visualizer": {
        "enabled": true,
        "type": "spectrum_bars",
        "resolution": 256,
        "smoothing": 0.8,
        "color_scheme": "rainbow",
        "background_opacity": 0.3,
        "bar_width": 2,
        "bar_spacing": 1,
        "animation_speed": 60
    },
    
    "web_server": {
        "port": 5000,
        "host": "127.0.0.1",
        "auto_start": true,
        "enable_cors": true,
        "websocket_enabled": true,
        "ssl_enabled": false
    },
    
    "advanced": {
        "buffer_size": 8192,
        "cache_size": 100,
        "log_level": "INFO",
        "backup_database": true,
        "backup_interval": 1440,
        "cleanup_logs": true,
        "performance_mode": false
    },
    
    "privacy": {
        "track_listening": true,
        "anonymous_stats": false,
        "crash_reports": true,
        "usage_analytics": false
    },
    
    "last_session": {
        "current_playlist": null,
        "current_song": null,
        "playback_position": 0,
        "queue": [],
        "window_state": {
            "width": 1200,
            "height": 800,
            "maximized": false
        }
    }
}
```

### 🔧 GESTIÓN DE PREFERENCIAS

#### 📥 CARGA DE CONFIGURACIÓN
```python
def load_user_preferences():
    """Carga preferencias del usuario desde JSON"""
    try:
        with open('data/user_preferences.json', 'r', encoding='utf-8') as f:
            preferences = json.load(f)
        
        # Validar versión y migrar si necesario
        if preferences.get('version') != CURRENT_VERSION:
            preferences = migrate_preferences(preferences)
            
        return preferences
        
    except FileNotFoundError:
        # Crear preferencias por defecto
        return create_default_preferences()
    except json.JSONDecodeError:
        # Archivo corrupto - usar backup o defaults
        return restore_preferences_backup()
```

#### 💾 GUARDADO AUTOMÁTICO
```python
def save_user_preferences(preferences):
    """Guarda preferencias con backup automático"""
    try:
        # Crear backup antes de guardar
        backup_preferences()
        
        # Actualizar timestamp
        preferences['last_updated'] = datetime.utcnow().isoformat() + 'Z'
        
        # Guardar con formato legible
        with open('data/user_preferences.json', 'w', encoding='utf-8') as f:
            json.dump(preferences, f, indent=4, ensure_ascii=False)
            
    except Exception as e:
        logger.error(f"Error guardando preferencias: {e}")
        raise
```

## 🔄 OPERACIONES DE BASE DE DATOS

### 📊 GESTIÓN DE BIBLIOTECA MUSICAL

#### ➕ AGREGAR NUEVA CANCIÓN
```python
def add_song_to_library(file_path, metadata):
    """Agrega una canción a la biblioteca"""
    try:
        cursor.execute("""
            INSERT INTO songs (
                title, artist, album, genre, year, duration,
                file_path, file_size, bitrate, sample_rate, 
                channels, format
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            metadata['title'], metadata['artist'], metadata['album'],
            metadata['genre'], metadata['year'], metadata['duration'],
            file_path, metadata['file_size'], metadata['bitrate'],
            metadata['sample_rate'], metadata['channels'], metadata['format']
        ))
        
        song_id = cursor.lastrowid
        connection.commit()
        
        logger.info(f"✅ Canción agregada: {metadata['title']} (ID: {song_id})")
        return song_id
        
    except sqlite3.IntegrityError:
        logger.warning(f"⚠️ Canción ya existe: {file_path}")
        return None
```

#### 🔍 BÚSQUEDA AVANZADA
```python
def search_songs(query, filters=None):
    """Búsqueda avanzada en la biblioteca"""
    base_query = """
        SELECT s.*, a.name as album_name, ar.name as artist_name
        FROM songs s
        LEFT JOIN albums a ON s.album = a.name
        LEFT JOIN artists ar ON s.artist = ar.name
        WHERE 1=1
    """
    
    params = []
    
    # Búsqueda por texto
    if query:
        base_query += " AND (s.title LIKE ? OR s.artist LIKE ? OR s.album LIKE ?)"
        like_query = f"%{query}%"
        params.extend([like_query, like_query, like_query])
    
    # Filtros adicionales
    if filters:
        if filters.get('genre'):
            base_query += " AND s.genre = ?"
            params.append(filters['genre'])
        
        if filters.get('year_range'):
            base_query += " AND s.year BETWEEN ? AND ?"
            params.extend(filters['year_range'])
        
        if filters.get('rating_min'):
            base_query += " AND s.rating >= ?"
            params.append(filters['rating_min'])
    
    # Ordenamiento
    order_by = filters.get('order_by', 'title')
    base_query += f" ORDER BY s.{order_by}"
    
    return cursor.execute(base_query, params).fetchall()
```

### 📋 GESTIÓN DE PLAYLISTS

#### 📝 CREAR PLAYLIST
```python
def create_playlist(name, description=""):
    """Crea una nueva playlist"""
    try:
        cursor.execute("""
            INSERT INTO playlists (name, description)
            VALUES (?, ?)
        """, (name, description))
        
        playlist_id = cursor.lastrowid
        connection.commit()
        
        logger.info(f"📋 Playlist creada: {name} (ID: {playlist_id})")
        return playlist_id
        
    except sqlite3.IntegrityError:
        raise ValueError(f"Ya existe una playlist con el nombre: {name}")
```

#### ➕ AGREGAR CANCIÓN A PLAYLIST
```python
def add_song_to_playlist(playlist_id, song_id):
    """Agrega una canción a una playlist"""
    # Obtener siguiente índice de orden
    cursor.execute("""
        SELECT COALESCE(MAX(order_index), 0) + 1
        FROM playlist_songs 
        WHERE playlist_id = ?
    """, (playlist_id,))
    
    next_order = cursor.fetchone()[0]
    
    # Insertar canción
    cursor.execute("""
        INSERT INTO playlist_songs (playlist_id, song_id, order_index)
        VALUES (?, ?, ?)
    """, (playlist_id, song_id, next_order))
    
    connection.commit()
```

### 📊 ESTADÍSTICAS Y ANALYTICS

#### 📈 REGISTRAR REPRODUCCIÓN
```python
def log_playback(song_id, duration_played, completion_rate):
    """Registra una reproducción en el historial"""
    # Actualizar contador de reproducciones
    cursor.execute("""
        UPDATE songs 
        SET play_count = play_count + 1,
            last_played = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (song_id,))
    
    # Agregar al historial detallado
    cursor.execute("""
        INSERT INTO play_history (song_id, duration_played, completion_rate)
        VALUES (?, ?, ?)
    """, (song_id, duration_played, completion_rate))
    
    connection.commit()
```

#### 📊 ESTADÍSTICAS DE BIBLIOTECA
```python
def get_library_stats():
    """Obtiene estadísticas de la biblioteca"""
    stats = {}
    
    # Total de canciones
    stats['total_songs'] = cursor.execute("SELECT COUNT(*) FROM songs").fetchone()[0]
    
    # Total de artistas únicos
    stats['total_artists'] = cursor.execute(
        "SELECT COUNT(DISTINCT artist) FROM songs WHERE artist IS NOT NULL"
    ).fetchone()[0]
    
    # Total de álbumes únicos
    stats['total_albums'] = cursor.execute(
        "SELECT COUNT(DISTINCT album) FROM songs WHERE album IS NOT NULL"
    ).fetchone()[0]
    
    # Duración total
    stats['total_duration'] = cursor.execute(
        "SELECT SUM(duration) FROM songs"
    ).fetchone()[0] or 0
    
    # Canción más reproducida
    stats['most_played'] = cursor.execute("""
        SELECT title, artist, play_count 
        FROM songs 
        ORDER BY play_count DESC 
        LIMIT 1
    """).fetchone()
    
    return stats
```

## 🔒 SEGURIDAD Y BACKUP

### 💾 SISTEMA DE BACKUP
```python
def backup_database():
    """Crea backup de la base de datos"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"data/backups/music_library_backup_{timestamp}.db"
    
    # Crear directorio de backup si no existe
    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
    
    # Copiar base de datos
    shutil.copy2('data/music_library.db', backup_path)
    
    # Comprimir backup
    with zipfile.ZipFile(f"{backup_path}.zip", 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(backup_path, os.path.basename(backup_path))
    
    # Eliminar archivo sin comprimir
    os.remove(backup_path)
    
    logger.info(f"💾 Backup creado: {backup_path}.zip")
```

### 🔧 MANTENIMIENTO DE BASE DE DATOS
```python
def maintenance_tasks():
    """Tareas de mantenimiento de la base de datos"""
    
    # VACUUM para optimizar espacio
    cursor.execute("VACUUM")
    
    # ANALYZE para actualizar estadísticas
    cursor.execute("ANALYZE")
    
    # Limpiar archivos huérfanos (canciones sin archivo físico)
    cursor.execute("""
        DELETE FROM songs 
        WHERE id NOT IN (
            SELECT DISTINCT song_id FROM playlist_songs
        ) AND NOT EXISTS (
            SELECT 1 FROM play_history WHERE song_id = songs.id
        ) AND file_path NOT LIKE 'http%'
    """)
    
    # Limpiar historial antiguo
    cursor.execute("""
        DELETE FROM play_history 
        WHERE played_at < datetime('now', '-1 year')
    """)
    
    connection.commit()
    logger.info("🔧 Mantenimiento de base de datos completado")
```

## 🔌 PUNTOS DE EXTENSIÓN

1. **Nuevas Tablas**: Agregar entidades como géneros, moods, etc.
2. **Metadatos Extendidos**: Campos adicionales para canciones
3. **Sincronización Cloud**: Backup automático en la nube
4. **Analytics Avanzados**: ML para recomendaciones
5. **Multi-usuario**: Sistema de usuarios y permisos
6. **API Externa**: Integración con Spotify, Last.fm, etc.

## ⚠️ CONSIDERACIONES IMPORTANTES

### 🔧 PERFORMANCE
- Índices optimizados para consultas frecuentes
- PRAGMA settings para mejor rendimiento
- Cleanup automático de datos antiguos
- Connection pooling para concurrencia

### 🔒 INTEGRIDAD DE DATOS
- Foreign keys habilitadas
- Transacciones para operaciones complejas
- Validación de datos antes de insertar
- Backup automático antes de operaciones críticas

### 📊 ESCALABILIDAD
- Diseño preparado para grandes bibliotecas
- Paginación en consultas grandes
- Índices para búsquedas rápidas
- Archivo WAL para mejor concurrencia
