# 🎵 AUDIO/ - MOTOR DE AUDIO PROFESIONAL
# =============================================
# Directorio: src/audio/ - Reproducción de Audio
# =============================================

## 📁 CONTENIDO DE AUDIO/

```
audio/
├── 🎵 vlc_engine.py           # Motor principal de audio con VLC
└── 📁 __pycache__/           # Cache de Python compilado
```

## 🎵 vlc_engine.py - MOTOR DE AUDIO VLC

### PROPÓSITO
**Clase VLCEngine**: Motor de audio profesional que usa VLC Media Player para reproducción de alta calidad

### RESPONSABILIDADES CLAVE
```python
class VLCEngine:
    # 🎯 Control básico de reproducción
    def play(file_path)                # Reproducir archivo específico
    def pause()                        # Pausar reproducción actual
    def stop()                         # Detener y resetear
    def is_playing()                   # Estado de reproducción
    def get_position()                 # Posición actual (0.0-1.0)
    def set_position(position)         # Saltar a posición específica
    
    # 🔊 Control de audio
    def set_volume(level)              # Volumen 0-100
    def get_volume()                   # Obtener volumen actual
    def mute()                         # Silenciar/des-silenciar
    
    # 📋 Gestión de playlist
    def set_playlist(songs)            # Cargar lista de canciones
    def next_track()                   # Siguiente canción
    def previous_track()               # Canción anterior
    def current_track()                # Canción actual
    
    # 🔀 Modos de reproducción
    def set_shuffle(enabled)           # Activar/desactivar shuffle
    def set_repeat(mode)               # Modo repeat: 'none', 'one', 'all'
    def get_shuffle_state()            # Estado del shuffle
    def get_repeat_mode()              # Modo de repeat actual
    
    # 📊 Información de audio
    def get_duration()                 # Duración total en segundos
    def get_time()                     # Tiempo transcurrido
    def get_metadata()                 # Metadatos del archivo actual
    def get_audio_spectrum()           # Datos de espectro para visualización
```

### CARACTERÍSTICAS TÉCNICAS

#### 🎵 FORMATOS SOPORTADOS
VLC Engine soporta todos los formatos que VLC Media Player puede reproducir:
- **Audio Común**: MP3, FLAC, WAV, AAC, OGG, WMA
- **Audio HD**: DSD, APE, ALAC, Hi-Res FLAC
- **Streaming**: HTTP, HTTPS, radio online
- **Formatos Raros**: MKV audio, M4A, OPUS, etc.

#### 🔊 CALIDAD DE AUDIO
- **Bit depth**: Hasta 32-bit
- **Sample rates**: 8 kHz a 192 kHz
- **Canales**: Mono, Stereo, 5.1, 7.1
- **Sin re-sampling**: Audio nativo sin pérdida

#### ⚡ RENDIMIENTO
- **Low latency**: Reproducción inmediata
- **Hardware acceleration**: Usa GPU cuando disponible
- **Buffer inteligente**: Pre-carga para reproducción fluida
- **Multi-threading**: No bloquea la interfaz

### IMPLEMENTACIÓN DE SHUFFLE/REPEAT

#### 🔀 ALGORITMO DE SHUFFLE
```python
def _generate_shuffle_order(self):
    """Genera orden aleatorio sin repetición hasta completar playlist"""
    if not self.playlist:
        return []
    
    # Crear lista de índices disponibles
    available_indices = list(range(len(self.playlist)))
    shuffle_order = []
    
    while available_indices:
        # Seleccionar índice aleatorio
        random_index = random.choice(available_indices)
        shuffle_order.append(random_index)
        available_indices.remove(random_index)
    
    return shuffle_order
```

#### 🔁 MODOS DE REPEAT
```python
REPEAT_MODES = {
    'none': "Sin repetición - para al final",
    'one': "Repetir canción actual infinitamente", 
    'all': "Repetir toda la playlist infinitamente"
}

def next_track(self):
    if self.repeat_mode == 'one':
        # Repetir la misma canción
        self.play(self.current_song_path)
    elif self.shuffle_enabled:
        # Siguiente en orden shuffle
        self._next_shuffle_track()
    elif self.repeat_mode == 'all' and self.is_last_track():
        # Volver al inicio si repeat all
        self.current_index = 0
    else:
        # Siguiente normal
        self.current_index += 1
```

### INTEGRACIÓN CON VLC MEDIA PLAYER

#### 📦 DEPENDENCIAS VLC
```python
import vlc

# Crear instancia VLC
self.vlc_instance = vlc.Instance([
    '--intf', 'dummy',           # Sin interfaz gráfica
    '--no-video',                # Solo audio
    '--aout', 'directsound',     # Audio output Windows
    '--verbose', '0'             # Sin logs verbosos
])

self.media_player = self.vlc_instance.media_player_new()
```

#### 🎛️ CONTROL AVANZADO
```python
# Callbacks para eventos
def _setup_vlc_events(self):
    event_manager = self.media_player.event_manager()
    event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, 
                              self._on_song_finished)
    event_manager.event_attach(vlc.EventType.MediaPlayerTimeChanged,
                              self._on_time_changed)
```

#### 📊 ANÁLISIS DE ESPECTRO
```python
def get_audio_spectrum(self):
    """Obtiene datos de espectro para efectos visuales"""
    # VLC proporciona datos FFT en tiempo real
    spectrum_data = self.media_player.audio_get_spectrum()
    return self._process_spectrum_data(spectrum_data)
```

### GESTIÓN DE ERRORES Y ESTADOS

#### ⚠️ MANEJO DE ERRORES
```python
def play(self, file_path):
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
        
        media = self.vlc_instance.media_new(file_path)
        self.media_player.set_media(media)
        
        result = self.media_player.play()
        if result == -1:
            raise VLCException("Error al iniciar reproducción VLC")
            
    except Exception as e:
        self.logger.error(f"Error en reproducción: {e}")
        return False
    return True
```

#### 🔄 ESTADOS DE REPRODUCCIÓN
```python
VLC_STATES = {
    vlc.State.NothingSpecial: "idle",
    vlc.State.Opening: "loading",
    vlc.State.Buffering: "buffering", 
    vlc.State.Playing: "playing",
    vlc.State.Paused: "paused",
    vlc.State.Stopped: "stopped",
    vlc.State.Ended: "ended",
    vlc.State.Error: "error"
}
```

### INTERCONEXIONES CON OTROS MÓDULOS

#### 🧠 CONTROLADO POR CORE/APP.PY
```python
# src/core/app.py llama métodos de VLCEngine
def next_song(self):
    success = self.audio_engine.next_track()
    if success:
        self._update_current_song_info()
        self._notify_ui_update()
```

#### 🎨 DATOS PARA EFFECTS/VISUAL_MANAGER.PY
```python
# Proporciona datos de espectro para visualización
spectrum_data = vlc_engine.get_audio_spectrum()
visual_manager.update_spectrum(spectrum_data)
```

#### 🌐 ESTADO PARA WEB/FLASK_APP.PY
```python
# Flask consulta estado a través de core/app.py
player_state = {
    'is_playing': vlc_engine.is_playing(),
    'current_time': vlc_engine.get_time(),
    'duration': vlc_engine.get_duration(),
    'volume': vlc_engine.get_volume()
}
```

### CONFIGURACIÓN Y OPTIMIZACIÓN

#### ⚙️ PARÁMETROS DE VLC OPTIMIZADOS
```python
VLC_ARGS = [
    '--intf=dummy',              # Sin GUI
    '--no-video',                # Solo audio
    '--audio-resampler=soxr',    # Resampler de calidad
    '--aout=directsound',        # Windows audio output
    '--no-plugins-cache',        # Sin cache de plugins
    '--no-stats',                # Sin estadísticas
    '--no-osd',                  # Sin overlay
]
```

#### 🔧 BUFFER Y LATENCIA
- **Network caching**: 1000ms para streams
- **File caching**: 300ms para archivos locales
- **Audio buffer**: 512 samples para baja latencia

### 🚀 CARACTERÍSTICAS AVANZADAS

#### 📡 STREAMING SUPPORT
- Radio online e internet streams
- Protocolo HTTP/HTTPS
- Detección automática de codec

#### 🎛️ EFFECTS CHAIN
- Ecualizador programático
- Filtros de audio en tiempo real
- Normalización de volumen

#### 💾 MEMORY MANAGEMENT
- Liberación automática de recursos
- Garbage collection de objetos VLC
- Pool de media objects para eficiencia

### ⚠️ DEPENDENCIAS CRÍTICAS

1. **VLC Media Player**: Debe estar instalado en el sistema
   - Windows: Descargar desde videolan.org
   - Verificar que VLC esté en PATH o Program Files

2. **python-vlc**: Bindings de Python para VLC
   ```bash
   pip install python-vlc>=3.0.16120
   ```

3. **Codecs de Audio**: VLC incluye la mayoría
   - Formatos propietarios pueden requerir codecs adicionales

### 🔌 PUNTOS DE EXTENSIÓN

1. **Nuevos Formatos**: VLC soporta automáticamente
2. **Efectos de Audio**: Integrar filtros VLC
3. **Streaming Avanzado**: Implementar protocolos adicionales
4. **Hardware Audio**: Integrar ASIO, WASAPI
5. **Multi-room**: Sincronización entre dispositivos
