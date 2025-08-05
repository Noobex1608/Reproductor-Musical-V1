# 🧠 SRC/ - CÓDIGO FUENTE PRINCIPAL
# =============================================
# Directorio: src/ - Backend y Lógica Central
# =============================================

## 📁 CONTENIDO DE LA CARPETA SRC/

```
src/
├── 🧠 core/           # Lógica central de la aplicación
├── 🎵 audio/          # Motor de audio y reproducción
├── 🌐 web/            # API Flask y servidor web
├── 🎨 effects/        # Efectos visuales y espectrogramas
├── 🖥️ ui/             # Interfaz de usuario (componentes desktop - legacy)
└── 🤖 ai/             # Inteligencia artificial musical
```

## 🔗 INTERCONEXIONES EN SRC/

### 1️⃣ FLUJO PRINCIPAL DE EJECUCIÓN

```
🌐 web/flask_app.py (Servidor Web)
        ↓
🧠 core/app.py (Controlador Principal)
        ↓
🎵 audio/vlc_engine.py (Motor Audio)
        ↓
🎨 effects/visual_manager.py (Efectos)
```

### 2️⃣ COMUNICACIÓN ENTRE MÓDULOS

**core/app.py** ES EL HUB CENTRAL:
- Controla `audio/vlc_engine.py` para reproducción
- Gestiona `core/database.py` para biblioteca musical
- Coordina `effects/visual_manager.py` para visualización
- Responde a peticiones de `web/flask_app.py`

**web/flask_app.py** ES LA INTERFAZ EXTERNA:
- Recibe peticiones HTTP del frontend
- Traduce peticiones a métodos de `core/app.py`
- Maneja WebSockets para tiempo real

**audio/vlc_engine.py** ES EL MOTOR DE AUDIO:
- Reproduce archivos usando VLC Media Player
- Gestiona playlist, shuffle, repeat
- Controlado por `core/app.py`

## 📂 DESCRIPCIÓN DETALLADA DE CADA SUBDIRECTORIO

### 🧠 src/core/ - LÓGICA CENTRAL
**Propósito**: Núcleo de la aplicación, orchestrador principal
**Archivos clave**:
- `app.py`: Clase MusicApp - controlador maestro
- `database.py`: Gestor SQLite para biblioteca musical
- `config_manager.py`: Configuración centralizada

**Funciones principales**:
- ✅ Coordinar todos los componentes
- ✅ Gestionar biblioteca musical
- ✅ Manejar configuración de usuario
- ✅ Implementar lógica de shuffle/repeat

### 🎵 src/audio/ - MOTOR DE AUDIO
**Propósito**: Reproducción de audio profesional
**Archivos clave**:
- `vlc_engine.py`: Wrapper de VLC Media Player

**Funciones principales**:
- ✅ Reproducir archivos de audio (MP3, FLAC, WAV, etc.)
- ✅ Control de volumen y ecualización
- ✅ Gestión de playlist con shuffle/repeat
- ✅ Análisis de espectro en tiempo real

### 🌐 src/web/ - SERVIDOR WEB
**Propósito**: API REST y servidor Flask
**Archivos clave**:
- `flask_app.py`: Servidor Flask con endpoints
- `flask_app_backup.py`: Respaldo de versión anterior

**Funciones principales**:
- ✅ Servir interfaz web en puerto 5000
- ✅ API REST para control de reproductor
- ✅ WebSocket para actualizaciones tiempo real
- ✅ Endpoints: /api/player/*, /api/library/*

### 🎨 src/effects/ - EFECTOS VISUALES
**Propósito**: Visualización y efectos gráficos
**Archivos clave**:
- `visual_manager.py`: Espectrogramas y efectos

**Funciones principales**:
- ✅ Análisis de frecuencias con FFT
- ✅ Espectrogramas en tiempo real
- ✅ Efectos visuales sincronizados con música
- ✅ Integración con matplotlib y numpy

### 🖥️ src/ui/ - INTERFAZ LEGACY (Desktop)
**Propósito**: Componentes de interfaz desktop (legacy)
**Estado**: LEGACY - La aplicación ahora es principalmente web
**Archivos**: Componentes CustomTkinter para interfaz desktop

**Nota**: Esta carpeta contiene la interfaz desktop original.
El proyecto actual se enfoca en la interfaz web.

### 🤖 src/ai/ - INTELIGENCIA ARTIFICIAL
**Propósito**: Funcionalidades de IA musical (opcional)
**Archivos clave**:
- `music_ai.py`: Algoritmos de IA para música

**Funciones principales**:
- ✅ Recomendaciones musicales
- ✅ Análisis automático de géneros
- ✅ Detección de BPM y características
- ✅ Machine learning con scikit-learn

## 🔄 PATRONES DE DISEÑO IMPLEMENTADOS

### 1️⃣ SINGLETON PATTERN
- `core/app.py` mantiene instancia única de MusicApp
- `core/config_manager.py` gestiona configuración global

### 2️⃣ FACADE PATTERN
- `web/flask_app.py` actúa como facade para el core
- Simplifica acceso a funcionalidades complejas

### 3️⃣ OBSERVER PATTERN
- WebSockets notifican cambios de estado
- Efectos visuales se sincronizan con audio

### 4️⃣ STRATEGY PATTERN
- Diferentes motores de audio pueden implementarse
- Múltiples algoritmos de efectos visuales

## ⚡ FLUJO DE DATOS INTERNO

### REPRODUCCIÓN DE MÚSICA:
```
web/flask_app.py → core/app.py → audio/vlc_engine.py → 🔊 VLC
```

### EFECTOS VISUALES:
```
audio/vlc_engine.py → effects/visual_manager.py → 📊 Matplotlib → 🌐 WebSocket
```

### GESTIÓN DE BIBLIOTECA:
```
web/flask_app.py → core/app.py → core/database.py → 💾 SQLite
```

## 🚀 PUNTOS DE EXTENSIÓN

1. **Nuevo Motor Audio**: Implementar interfaz similar a `vlc_engine.py`
2. **Nuevos Efectos**: Agregar clases en `effects/visual_manager.py`
3. **APIs Adicionales**: Extender endpoints en `web/flask_app.py`
4. **IA Avanzada**: Desarrollar algoritmos en `ai/music_ai.py`
5. **Configuración**: Agregar parámetros en `core/config_manager.py`

## ⚠️ DEPENDENCIAS CRÍTICAS

- **VLC Media Player**: Debe estar instalado en el sistema
- **Flask + SocketIO**: Para servidor web y tiempo real
- **SQLite**: Base de datos (incluido en Python)
- **Matplotlib + NumPy**: Para efectos visuales
- **Mutagen**: Para metadatos de archivos de audio
