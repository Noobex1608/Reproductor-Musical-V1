# 📁 DIRECTORIOS AUXILIARES - DOCUMENTACIÓN
# =============================================
# Carpetas de Soporte y Recursos Adicionales
# =============================================

## 📂 ESTRUCTURA DE CARPETAS AUXILIARES

```
Reproductor Web/
├── 🎨 assets/                 # Recursos multimedia adicionales
├── ⚡ cache/                  # Cache temporal del sistema
├── ⚙️ config/                 # Archivos de configuración
├── 🖼️ covers/                 # Portadas de álbumes
├── 📝 logs/                   # Archivos de registro
├── 📋 playlists/              # Archivos de playlists exportadas
├── 🔌 plugins/                # Extensiones y plugins
└── 🎨 themes/                 # Temas personalizables
```

## 🎨 ASSETS/ - RECURSOS MULTIMEDIA

### PROPÓSITO
Almacena recursos multimedia adicionales que no son estáticos del web

### CONTENIDO TÍPICO
```
assets/
├── 🖼️ album_covers/           # Portadas descargadas automáticamente
├── 🎵 sample_tracks/          # Canciones de demostración
├── 🔊 sound_effects/          # Efectos de sonido (clicks, notificaciones)
├── 🎨 visualizer_presets/     # Presets guardados del visualizador
├── 📄 export_templates/       # Plantillas para exportar datos
└── 🌐 web_assets/            # Assets adicionales para web
```

### FUNCIONALIDADES
- **Auto-download**: Descarga automática de portadas desde internet
- **Gestión de cache**: Limpieza automática de archivos antiguos
- **Organización**: Subdirectorios por artista/álbum
- **Formatos múltiples**: Soporte para diferentes tipos de archivos

## ⚡ CACHE/ - SISTEMA DE CACHE

### PROPÓSITO
Cache temporal para mejorar rendimiento y experiencia de usuario

### ESTRUCTURA
```
cache/
├── 🖼️ images/                 # Cache de imágenes procesadas
│   ├── thumbnails/           # Miniaturas de portadas
│   ├── resized/              # Imágenes redimensionadas
│   └── compressed/           # Imágenes comprimidas
├── 🎵 audio/                  # Cache de audio procesado
│   ├── spectrum_data/        # Datos de espectro pre-calculados
│   ├── waveforms/            # Formas de onda generadas
│   └── analysis/             # Análisis de audio (BPM, key, etc.)
├── 🌐 web/                    # Cache web
│   ├── api_responses/        # Respuestas de API cacheadas
│   ├── static_files/         # Archivos estáticos comprimidos
│   └── sessions/             # Datos de sesión temporal
└── 💾 database/              # Cache de consultas de DB
    ├── search_results/       # Resultados de búsqueda
    └── library_views/        # Vistas de biblioteca procesadas
```

### GESTIÓN AUTOMÁTICA
```python
# Limpieza automática de cache
def cleanup_cache():
    """Limpia archivos de cache antiguos"""
    cache_dirs = ['cache/images', 'cache/audio', 'cache/web']
    max_age = 7 * 24 * 3600  # 7 días
    
    for cache_dir in cache_dirs:
        for file_path in Path(cache_dir).rglob('*'):
            if file_path.is_file():
                age = time.time() - file_path.stat().st_mtime
                if age > max_age:
                    file_path.unlink()
```

## ⚙️ CONFIG/ - CONFIGURACIÓN

### PROPÓSITO
Archivos de configuración centralizados del sistema

### ARCHIVO PRINCIPAL: app_config.json
```json
{
    "application": {
        "name": "Music Player Pro",
        "version": "1.0.0",
        "debug": false,
        "log_level": "INFO"
    },
    
    "audio_engine": {
        "backend": "vlc",
        "buffer_size": 8192,
        "sample_rate": 44100,
        "channels": 2,
        "bit_depth": 16
    },
    
    "web_server": {
        "host": "127.0.0.1",
        "port": 5000,
        "ssl": false,
        "cors_enabled": true,
        "websocket_enabled": true
    },
    
    "database": {
        "type": "sqlite",
        "path": "data/music_library.db",
        "backup_enabled": true,
        "backup_interval": 1440,
        "wal_mode": true
    },
    
    "library": {
        "scan_folders": [],
        "auto_scan": true,
        "watch_changes": true,
        "supported_formats": ["mp3", "flac", "wav", "aac", "ogg", "m4a"],
        "min_duration": 10,
        "max_file_size": 1073741824
    },
    
    "visualizer": {
        "enabled": true,
        "type": "spectrum",
        "resolution": 256,
        "fps": 60,
        "smoothing": 0.8
    },
    
    "cache": {
        "enabled": true,
        "max_size": 1073741824,
        "cleanup_interval": 3600,
        "image_cache_size": 536870912,
        "audio_cache_size": 536870912
    },
    
    "advanced": {
        "performance_mode": false,
        "low_latency": false,
        "hardware_acceleration": true,
        "multi_threading": true,
        "memory_limit": 2147483648
    }
}
```

### CONFIGURACIONES ADICIONALES
- **audio_codecs.json**: Configuración de codecs de audio
- **theme_settings.json**: Configuración de temas y colores
- **plugin_config.json**: Configuración de plugins habilitados
- **keyboard_shortcuts.json**: Atajos de teclado personalizados

## 🖼️ COVERS/ - PORTADAS DE ÁLBUMES

### PROPÓSITO
Almacenamiento organizado de portadas de álbumes

### ESTRUCTURA JERÁRQUICA
```
covers/
├── 📁 A/                      # Artistas que empiezan con A
│   ├── Artist Name/
│   │   ├── Album 1.jpg
│   │   ├── Album 2.png
│   │   └── single_covers/
│   └── Another Artist/
├── 📁 B/                      # Artistas que empiezan con B
├── ...
├── 📁 Various/                # Compilaciones y varios artistas
├── 📁 Unknown/                # Artistas desconocidos
└── 📁 _cache/                 # Cache temporal de portadas
```

### GESTIÓN AUTOMÁTICA
```python
def organize_cover(artist, album, cover_file):
    """Organiza una portada en la estructura correcta"""
    # Sanitizar nombres
    safe_artist = sanitize_filename(artist or "Unknown")
    safe_album = sanitize_filename(album or "Unknown Album")
    
    # Crear estructura de directorios
    first_letter = safe_artist[0].upper() if safe_artist else 'U'
    cover_dir = Path(f"covers/{first_letter}/{safe_artist}")
    cover_dir.mkdir(parents=True, exist_ok=True)
    
    # Mover archivo
    cover_path = cover_dir / f"{safe_album}.jpg"
    shutil.move(cover_file, cover_path)
    
    return str(cover_path)
```

### FORMATOS SOPORTADOS
- **JPG/JPEG**: Formato principal para portadas
- **PNG**: Para portadas con transparencia
- **WebP**: Formato moderno con mejor compresión
- **Tamaños**: 300x300, 500x500, 1000x1000 (múltiples resoluciones)

## 📝 LOGS/ - SISTEMA DE LOGGING

### PROPÓSITO
Registro detallado de todas las operaciones del sistema

### ARCHIVOS DE LOG
```
logs/
├── 🎵 music_player_pro.log    # Log principal de la aplicación
├── 🌐 web_server.log          # Logs específicos del servidor web
├── 💾 database.log            # Operaciones de base de datos
├── 🎨 visualizer.log          # Logs del visualizador
├── ⚠️ errors.log              # Errores críticos del sistema
├── 🔧 debug.log               # Información de debugging detallada
└── 📊 performance.log         # Métricas de rendimiento
```

### CONFIGURACIÓN DE LOGGING
```python
import logging
from logging.handlers import RotatingFileHandler

# Configurar loggers con rotación
def setup_logging():
    """Configura el sistema de logging"""
    
    # Logger principal
    main_logger = logging.getLogger('music_player')
    main_logger.setLevel(logging.INFO)
    
    # Handler con rotación (10MB por archivo, 5 backups)
    handler = RotatingFileHandler(
        'logs/music_player_pro.log',
        maxBytes=10*1024*1024,
        backupCount=5,
        encoding='utf-8'
    )
    
    # Formato detallado
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    handler.setFormatter(formatter)
    main_logger.addHandler(handler)
    
    # Console handler para desarrollo
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(levelname)s - %(message)s'
    ))
    main_logger.addHandler(console_handler)
```

### EJEMPLOS DE LOGS
```
2024-01-15 10:30:15,123 - music_player - INFO - app.py:45 - 🎵 Aplicación iniciada
2024-01-15 10:30:16,234 - music_player - INFO - database.py:78 - 💾 Base de datos conectada
2024-01-15 10:30:17,345 - music_player - INFO - vlc_engine.py:123 - 🔊 Motor VLC inicializado
2024-01-15 10:35:22,456 - music_player - INFO - flask_app.py:67 - 🔀 Shuffle activado
2024-01-15 10:35:23,567 - music_player - ERROR - vlc_engine.py:234 - ❌ Error al cargar archivo: /path/to/song.mp3
```

## 📋 PLAYLISTS/ - PLAYLISTS EXPORTADAS

### PROPÓSITO
Almacena playlists exportadas en diferentes formatos

### FORMATOS SOPORTADOS
```
playlists/
├── 📄 m3u/                    # Formato M3U estándar
│   ├── My Favorites.m3u
│   └── Rock Classics.m3u
├── 📄 pls/                    # Formato PLS (Winamp)
│   ├── Electronic.pls
│   └── Jazz Collection.pls
├── 📄 xspf/                   # XML Shareable Playlist Format
│   └── Workout Mix.xspf
├── 📄 json/                   # Formato JSON nativo
│   ├── backup_playlists.json
│   └── shared_playlists.json
└── 📄 exports/                # Exportaciones especiales
    ├── spotify_import.csv
    └── itunes_export.xml
```

### GENERACIÓN AUTOMÁTICA
```python
def export_playlist_m3u(playlist_id, output_path):
    """Exporta playlist a formato M3U"""
    songs = get_playlist_songs(playlist_id)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        
        for song in songs:
            # Información extendida
            f.write(f"#EXTINF:{song['duration']},{song['artist']} - {song['title']}\n")
            # Ruta del archivo
            f.write(f"{song['file_path']}\n")
```

## 🔌 PLUGINS/ - SISTEMA DE PLUGINS

### PROPÓSITO
Extensiones y plugins para ampliar funcionalidad

### ESTRUCTURA
```
plugins/
├── 📁 enabled/                # Plugins activos
│   ├── last_fm_scrobbler/    # Plugin de Last.fm
│   ├── lyrics_provider/      # Proveedor de letras
│   └── discord_rich_presence/ # Discord Rich Presence
├── 📁 disabled/               # Plugins deshabilitados
│   ├── spotify_sync/
│   └── echo_nest_analysis/
├── 📁 development/            # Plugins en desarrollo
│   └── neural_recommender/
└── 📄 plugin_registry.json   # Registro de plugins
```

### API DE PLUGINS
```python
class PluginInterface:
    """Interfaz base para plugins"""
    
    def __init__(self, app_instance):
        self.app = app_instance
        self.name = "Base Plugin"
        self.version = "1.0.0"
        self.enabled = False
    
    def on_song_start(self, song_data):
        """Se llama cuando inicia una canción"""
        pass
    
    def on_song_end(self, song_data):
        """Se llama cuando termina una canción"""
        pass
    
    def on_library_scan(self, new_songs):
        """Se llama después de escanear biblioteca"""
        pass
    
    def get_settings_ui(self):
        """Retorna HTML para configuración del plugin"""
        return ""
    
    def cleanup(self):
        """Limpieza al desactivar plugin"""
        pass
```

## 🎨 THEMES/ - SISTEMA DE TEMAS

### PROPÓSITO
Temas visuales personalizables para la interfaz

### ESTRUCTURA
```
themes/
├── 📁 default/                # Tema por defecto
│   ├── colors.css
│   ├── layout.css
│   └── theme.json
├── 📁 dark_purple/            # Tema púrpura oscuro
│   ├── colors.css
│   ├── custom_components.css
│   └── theme.json
├── 📁 light_mode/             # Tema claro
├── 📁 neon_cyberpunk/         # Tema cyberpunk
├── 📁 minimalist/             # Tema minimalista
└── 📄 theme_registry.json     # Registro de temas
```

### DEFINICIÓN DE TEMA
```json
{
    "name": "Dark Purple",
    "version": "1.0.0",
    "author": "Music Player Pro Team",
    "description": "Tema oscuro con acentos púrpura",
    
    "colors": {
        "primary": "#6C5CE7",
        "secondary": "#A29BFE", 
        "background": "#2D3436",
        "surface": "#636E72",
        "text_primary": "#FFFFFF",
        "text_secondary": "#B2BEC3",
        "accent": "#00CEC9",
        "error": "#E74C3C",
        "success": "#00B894"
    },
    
    "fonts": {
        "primary": "Inter, sans-serif",
        "secondary": "Roboto, sans-serif",
        "monospace": "Fira Code, monospace"
    },
    
    "layout": {
        "sidebar_width": "250px",
        "player_height": "80px",
        "border_radius": "8px",
        "spacing_unit": "8px"
    },
    
    "animations": {
        "duration": "300ms",
        "easing": "ease-in-out",
        "enabled": true
    },
    
    "files": [
        "colors.css",
        "layout.css",
        "components.css"
    ]
}
```

### APLICACIÓN DINÁMICA
```javascript
function applyTheme(themeName) {
    """Aplica un tema dinámicamente"""
    
    // Cargar configuración del tema
    fetch(`/themes/${themeName}/theme.json`)
        .then(response => response.json())
        .then(theme => {
            // Aplicar variables CSS
            const root = document.documentElement;
            
            Object.entries(theme.colors).forEach(([key, value]) => {
                root.style.setProperty(`--color-${key}`, value);
            });
            
            // Cargar archivos CSS del tema
            theme.files.forEach(file => {
                loadThemeCSS(`/themes/${themeName}/${file}`);
            });
            
            // Guardar preferencia
            saveUserPreference('theme', themeName);
        });
}
```

## 🔄 INTERCONEXIONES ENTRE DIRECTORIOS

### 📊 FLUJO DE DATOS
```
📁 assets/ → 🖼️ covers/ (portadas procesadas)
📁 cache/ → 💾 data/ (cache de consultas DB)
📁 config/ → 📝 logs/ (configuración de logging)
📁 playlists/ → 💾 data/ (backup de playlists)
📁 plugins/ → 📝 logs/ (logs de plugins)
📁 themes/ → 🌐 static/ (aplicación de CSS)
```

### 🔧 MANTENIMIENTO AUTOMÁTICO
```python
def maintenance_routine():
    """Rutina de mantenimiento para directorios auxiliares"""
    
    # Limpiar cache antiguo
    cleanup_cache_files()
    
    # Rotar logs
    rotate_log_files()
    
    # Backup de configuración
    backup_config_files()
    
    # Optimizar portadas
    optimize_cover_images()
    
    # Validar plugins
    validate_plugin_integrity()
    
    # Actualizar registro de temas
    update_theme_registry()
```

## 🚀 PUNTOS DE EXTENSIÓN

1. **Nuevos Tipos de Cache**: Agregar cache específico para nuevas funcionalidades
2. **Plugins Avanzados**: Sistema de plugins con sandboxing
3. **Temas Dinámicos**: Temas que cambian según la música
4. **Assets Remotos**: Descarga automática de recursos
5. **Configuración Cloud**: Sincronización de configuración
6. **Analytics**: Métricas de uso de plugins y temas

## ⚠️ CONSIDERACIONES

### 🔒 SEGURIDAD
- Validación de plugins antes de cargar
- Sandboxing para código de terceros
- Verificación de integridad de temas

### 💾 ESPACIO EN DISCO
- Limpieza automática de cache
- Compresión de logs antiguos
- Optimización de portadas

### ⚡ RENDIMIENTO
- Carga lazy de plugins
- Cache inteligente de temas
- Indexación de assets para búsqueda rápida
