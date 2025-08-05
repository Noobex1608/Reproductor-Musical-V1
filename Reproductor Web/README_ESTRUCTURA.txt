# 🎵 MUSIC PLAYER PRO - DOCUMENTACIÓN ARQUITECTURA
# ============================================================
# Fecha: 2024 | Versión: 1.0 | Tipo: Reproductor Web Profesional
# ============================================================

## 📁 ESTRUCTURA GENERAL DEL PROYECTO

```
Reproductor Web/
├── 🏠 Archivos Raíz                    # Scripts principales y configuración base
├── 📂 src/                            # Código fuente principal - MODULAR
├── 🌐 static/                         # Recursos web frontend (CSS, JS, imágenes)
├── 📄 templates/                      # Plantillas HTML para interfaz web
├── 💾 data/                          # Bases de datos y almacenamiento persistente
├── 📁 assets/, cache/, covers/       # Recursos multimedia y cache
├── ⚙️ config/                        # Archivos de configuración
├── 📝 logs/, playlists/, plugins/    # Logs, listas y extensiones
└── 🎨 themes/                        # Temas personalizables
```

## 🔄 FLUJO DE COMUNICACIÓN PRINCIPAL

### 1️⃣ CAPA DE PRESENTACIÓN (Frontend)
```
📱 Navegador Web → 🌐 templates/index.html → 📊 static/js/app.js
```

### 2️⃣ CAPA DE API (Backend Web)
```
🔄 static/js/app.js → 🌐 src/web/flask_app.py → 📡 REST API Endpoints
```

### 3️⃣ CAPA DE LÓGICA (Core Application)
```
📡 Flask API → 🧠 src/core/app.py → 🎵 Audio Engine
```

### 4️⃣ CAPA DE AUDIO (Motor de Reproducción)
```
🧠 Core App → 🎵 src/audio/vlc_engine.py → 🔊 VLC Media Player
```

## 🔗 INTERCONEXIONES CLAVE

### 🌐 WEB INTERFACE → CORE LOGIC
- `static/js/app.js` llama endpoints en `src/web/flask_app.py`
- Flask app instancia y controla `src/core/app.py`
- Core app maneja toda la lógica de reproducción y shuffle/repeat

### 🎵 AUDIO PROCESSING → DATABASE
- `src/audio/vlc_engine.py` reproduce archivos físicos
- `src/core/database.py` gestiona metadatos y biblioteca
- Base de datos SQLite en `data/music_library.db`

### 🎨 VISUALIZACIÓN → EFECTOS
- `src/effects/visual_manager.py` genera espectros en tiempo real
- `static/js/visualizer.js` renderiza efectos en el navegador
- WebSocket para sincronización en tiempo real

## 📊 COMPONENTES MODULARES

### 🧠 CORE (src/core/)
- **app.py**: Controlador principal - maneja toda la lógica
- **database.py**: Gestor de base de datos SQLite
- **config_manager.py**: Configuración centralizada

### 🌐 WEB (src/web/)
- **flask_app.py**: API REST para interfaz web
- Endpoints: /api/player/*, /api/library/*, /api/playlists/*

### 🎵 AUDIO (src/audio/)
- **vlc_engine.py**: Motor de audio con VLC bindings
- Gestiona reproducción, volumen, shuffle, repeat

### 🎨 EFFECTS (src/effects/)
- **visual_manager.py**: Efectos visuales y espectrogramas
- Análisis de frecuencias con matplotlib

### 🤖 AI (src/ai/)
- **music_ai.py**: Inteligencia artificial musical (opcional)
- Recomendaciones y análisis automático

## ⚡ CARACTERÍSTICAS TÉCNICAS

### 🔄 FLUJO DE DATOS EN TIEMPO REAL
1. Usuario interactúa con interfaz web
2. JavaScript envía petición a Flask API
3. Flask llama métodos del Core App
4. Core App controla VLC Engine
5. Audio se reproduce + efectos visuales se sincronizan
6. WebSocket actualiza interfaz en tiempo real

### 🔀 FUNCIONALIDAD SHUFFLE/REPEAT
- **Frontend**: `static/js/app.js` - Botones UI y estado visual
- **API**: `src/web/flask_app.py` - Endpoints /api/player/shuffle|repeat
- **Logic**: `src/core/app.py` - toggle_shuffle() y cycle_repeat_mode()
- **Engine**: `src/audio/vlc_engine.py` - Ejecución de reproducción

### 💾 PERSISTENCIA DE DATOS
- **Biblioteca**: `data/music_library.db` (SQLite)
- **Configuración**: `config/app_config.json`
- **Preferencias**: `data/user_preferences.json`
- **Logs**: `logs/music_player_pro.log`

## 🚀 ARQUITECTURA ESCALABLE

Este proyecto está diseñado con arquitectura modular que permite:
- ✅ Agregar nuevos efectos visuales en `src/effects/`
- ✅ Desarrollar plugins en `plugins/`
- ✅ Personalizar temas en `themes/`
- ✅ Extender la API web en `src/web/`
- ✅ Integrar nuevos motores de audio además de VLC

## 🔧 PUNTOS DE EXTENSIÓN

1. **Nuevos Formatos Audio**: Modificar `src/audio/vlc_engine.py`
2. **Nuevas APIs Web**: Extender `src/web/flask_app.py`
3. **Efectos Visuales**: Agregar clases en `src/effects/`
4. **Temas UI**: Crear archivos CSS en `static/css/`
5. **Plugins**: Desarrollar módulos en `plugins/`
